import os
import yaml
import re
import requests
import tempfile
import subprocess
from pathlib import Path

def clone_repo(org, repo, token):
    """Clone repository and return path"""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir) / repo
    
    # Clone using token for authentication
    clone_url = f"https://x-access-token:{token}@github.com/{org}/{repo}.git"
    subprocess.run(["git", "clone", "--depth", "1", clone_url, str(repo_path)], 
                  check=True, capture_output=True)
    return repo_path

def find_helm_charts(repo_path):
    """Find all directories containing Chart.yaml"""
    charts = []
    for path in repo_path.rglob("Chart.yaml"):
        charts.append(path.parent)
    return charts

def extract_images_from_values(values_file):
    """Extract all Docker images from values.yaml"""
    images = set()
    print(f"  Processing {values_file}")
    
    try:
        with open(values_file, 'r') as f:
            content = f.read()
        
        # Parse YAML
        try:
            data = yaml.safe_load(content)
        except:
            # If YAML parsing fails, try regex fallback
            content = content
        else:
            # Convert parsed YAML to string for regex search
            content = yaml.dump(data)
        
        # Regex patterns for Docker images
        patterns = [
            # Формат: domain.com/org/image:tag
            r'[a-z0-9\-_.]+\.[a-z0-9\-_.]+/[a-z0-9\-_./]+:[a-z0-9\-_.]+',
            
            # Формат: org/image:tag или org/suborg/image:tag
            r'[a-z0-9\-_.]+/[a-z0-9\-_./]+:[a-z0-9\-_.]+',
            
            # Формат: image:tag (library images)
            r'^[a-z0-9\-_.]+:[a-z0-9\-_.]+$'
        ]
        
        # Find all potential image strings
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                print(f"  processing match: {match}")
                image = match.group()
                print(f"  image: {image}")

                images.add(image)
                # Skip if it looks like a URL path or invalid image
                #if '/' in image or ':' in image:
                    # Validate it looks like an image
                    #if re.match(r'^[a-zA-Z0-9\-_.:/]+$', image):
                        #images.add(image)
                #elif ':' in image:  # Simple image:tag like "alpine:3.14"
                    #images.add(image)
    
    except Exception as e:
        print(f"  Error processing {values_file}: {e}")
    
    return images

def is_external_image(image, org):
    """Check if image is external (not from the organization)"""
    # Skip if image is from the organization
    if image.startswith(f"{org}/") or f"/{org}/" in image:
        return False
    
    # Skip common internal patterns
    internal_patterns = [
        f"ghcr.io/{org}",
        f"docker.io/{org}",
        f"quay.io/{org}",
        f"registry.{org}.com"
    ]
    
    for pattern in internal_patterns:
        if pattern in image:
            return False
    
    # Handle Docker Hub library images (no slash)
    if '/' not in image:
        return True  # External library image
    
    return True

def main():
    # Get inputs from environment
    repos_input = os.environ.get('REPOSITORIES', '')
    org = os.environ.get('ORGANIZATION', '')
    token = os.environ.get('GITHUB_TOKEN', '')
    
    if not repos_input or not org:
        print("Error: REPOSITORIES and ORGANIZATION must be provided")
        exit(1)
    
    # Parse repositories list
    repositories = [repo.strip() for repo in repos_input.split(',') if repo.strip()]
    
    result = {}
    
    for repo in repositories:
        print(f"Processing {repo}...")
        repo_images = set()
        
        try:
            # Clone repository
            repo_path = clone_repo(org, repo, token)
            
            # Find all helm charts
            chart_dirs = find_helm_charts(repo_path)
            
            for chart_dir in chart_dirs:
                values_file = chart_dir / "values.yaml"
                if values_file.exists():
                    print(f"  Found chart in {chart_dir.relative_to(repo_path)}")
                    images = extract_images_from_values(values_file)
                    
                    # Filter external images
                    for image in images:
                        if is_external_image(image, org):
                            repo_images.add(image)
                            print(f"    External image: {image}")
            
            if repo_images:
                result[repo] = sorted(list(repo_images))
            
        except Exception as e:
            print(f"Error processing {repo}: {e}")
    
    # Save result to YAML
    with open('external_images.yaml', 'w') as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    
    print("\nResults saved to external_images.yaml")

if __name__ == "__main__":
    main()
