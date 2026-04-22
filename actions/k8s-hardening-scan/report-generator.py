#!/usr/bin/env python3
"""
A script for converting kubescape JSON results into Markdown tables.
Usage: python3 generate_report.py [--input file.json] [--output report.md]
"""

import json
import urllib.request
import argparse
import os
import sys
from pathlib import Path

def load_json_data(source):
    """Loads JSON from a file or URL."""
    if source.startswith(('http://', 'https://')):
        with urllib.request.urlopen(source) as response:
            return json.loads(response.read().decode('utf-8'))
    else:
        with open(source, 'r', encoding='utf-8') as f:
            return json.load(f)

def load_yaml_config(config_path):
    """Loads YAML configuration from a file."""
    import yaml
    default_config_path = os.getenv('GITHUB_ACTION_PATH') + '/hardening-config.yaml'
    default_config_data = {}
    config_data = {}
    if not Path(config_path).is_file():
        print(f"⚠️  Warning: Config file '{config_path}' not found. Using default config path '{default_config_path}'.")
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    with open(default_config_path, 'r', encoding='utf-8') as f:
        default_config_data = yaml.safe_load(f)
    # Merge default config with user config, giving precedence to user config
    merged_config = {**default_config_data, **config_data}
    print(f"[DEBUG]: {merged_config}")
    return merged_config

def get_resource_ports(resource):
    """Extracts ports from a resource definition."""
    ports = []
    spec = resource.get('spec', {})
    template = spec.get('template', {})
    spec_template = template.get('spec', {})
    containers = spec_template.get('containers', [])

    for container in containers:
        container_ports = container.get('ports', [])
        for port in container_ports:
            ports.append(port.get('containerPort'))

    return ports

def get_resource_images(resource):
    """Extracts container images from a resource definition."""
    images = []
    spec = resource.get('spec', {})
    template = spec.get('template', {})
    spec_template = template.get('spec', {})
    containers = spec_template.get('containers', [])

    for container in containers:
        image = container.get('image', '')
        if image:
            images.append(image)

    return images

def get_status_emoji(status):
    """Returns the emoji for a given status."""
    return '✅' if status == 'passed' else '❌'

def generate_markdown_tables(data, config):
    """Generates markdown tables for each resourceID."""
    results = data.get('results', [])
    resources = data.get('resources', [])

    if not results:
        return "No results found in the JSON data."

    output_lines = []

    for resource in results:
        resource_id = resource.get('resourceID', 'Unknown')
        if not '/Deployment/' in resource_id:  # Skip non-deployment resources
            continue
        resource_data = next((r for r in resources if r.get('resourceID') == resource_id), {})
        resource_ports = get_resource_ports(resource_data)
        resource_images = get_resource_images(resource_data)
        controls = resource.get('controls', [])

        # Resource header
        output_lines.append(f"\n## Resource: `{resource_id}`\n")
        output_lines.append("| ControlID | Control name | Status |")
        output_lines.append("|-----------|--------------|--------|")

        # Processing each control
        for control in controls:
            control_id = control.get('controlID', '')
            control_name = control.get('name', '')
            rules = control.get('rules', [])

            # Each rule in a separate line.
            if len(rules) > 1:
                for rule in rules:
                    status = rule.get('status', '')
                    status_emoji = get_status_emoji(status)
                    output_lines.append(f"| {control_id} | {control_name} ({rule.get('name', '')}) | {status_emoji} |")
            else:
                # Normal case - single rule
                status = rules[0].get('status', '') if rules else control.get('status', {}).get('status', '')
                status_emoji = get_status_emoji(status)
                output_lines.append(f"| {control_id} | {control_name} | {status_emoji} |")

        # TODO: here need to compare resource ports with prohibited ports list from config file and add a line to the table if there is a match.
        intersection = list(set(config.get('hardening_rules', {}).get('Critical-Ports', {}).get('critical_ports', [])) & set(resource_ports))
        if intersection:
            output_lines.append(f"| Critical-Ports | Critical Ports: {', '.join(map(str, sorted(intersection)))} | ❌ |")
        else:
            output_lines.append("| Critical-Ports | Critical Ports | ✅ |")
        # TODO: here need to check if any of the container images used in the resource are using the 'latest' tag and add a line to the table if there is a match.
        latest_images = [img for img in resource_images if img.endswith(':latest')]
        if latest_images:
            output_lines.append(f"| Latest-Tag | Images using 'latest' tag: {', '.join(latest_images)} | ❌ |")
        else:
            output_lines.append("| Latest-Tag | No images using 'latest' tag | ✅ |")

        # Add statistics for the resource
        total_controls = len(controls)
        passed = sum(1 for c in controls
                    if c.get('rules', [{}])[0].get('status', '') == 'passed')
        failed = total_controls - passed

        output_lines.append(f"\n**Total:** ✅ passed: {passed}, ❌ failed: {failed}\n")
        output_lines.append("---")

    return '\n'.join(output_lines)

def generate_full_report(data, config, title="Kubescape Hardening Scan Report"):
    """Generates a full markdown report."""
    timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# {title}

**Generation date:** {timestamp}

## Summary by resources

"""

    results = data.get('results', [])
    for resource in results:
        resource_id = resource.get('resourceID', 'Unknown')
        if not '/Deployment/' in resource_id:  # Skip non-deployment resources
            continue

        controls = resource.get('controls', [])
        passed = sum(1 for c in controls
                    if c.get('rules', [{}])[0].get('status', '') == 'passed')
        failed = len(controls) - passed
        report += f"- `{resource_id}`: ✅ {passed} / ❌ {failed}\n"

    report += "\n---\n"
    report += generate_markdown_tables(data, config)

    return report

def main():
    parser = argparse.ArgumentParser(
        description='Converts kubescape JSON results into Markdown tables.'
    )
    parser.add_argument(
        '--input', '-i',
        help='Path to the JSON file or URL (default: specified URL)'
    )
    parser.add_argument(
        '--output', '-o',
        default='kubescape-report.md',
        help='Path for saving the markdown file (default: kubescape-report.md)'
    )
    parser.add_argument(
        '--title', '-t',
        default='Kubescape Hardening Scan Report',
        help='Report title'
    )
    parser.add_argument(
        '--config', '-c',
        default='hardening-config.yaml',
        help='Path to the YAML configuration file (default: hardening-config.yaml)'
    )

    args = parser.parse_args()

    try:
        config = load_yaml_config(args.config)
        print(f"Loading data from: {args.input}")
        data = load_json_data(args.input)

        print("Generating markdown report...")
        report = generate_full_report(data, config, args.title)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Report successfully saved to: {args.output}")

        # Display brief statistics
        results = data.get('results', [])
        print(f"\n📊 Statistics:")
        print(f"   Total resources: {len(results)}")
        for resource in results:
            resource_id = resource.get('resourceID', 'Unknown')
            controls = resource.get('controls', [])
            passed = sum(1 for c in controls
                        if c.get('rules', [{}])[0].get('status', '') == 'passed')
            print(f"   - {resource_id}: {passed}/{len(controls)} passed")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()