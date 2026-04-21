#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
error_count=0
checked_charts=0
checked_files=0
total_images=0

# Temporary directory for helm template output
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Function to check image
check_image() {
    local image=$1
    local file=$2
    local line=$3
    local chart=$4
    local source=$5  # "source" or "rendered"

    # Check if image contains a tag (colon)
    if [[ ! "$image" =~ : ]]; then
        echo -e "${RED}✗ Missing tag:${NC} [$source] $chart -> $file (line $line): $image"
        ((error_count++))
        return 1
    fi

    # Extract tag (part after last colon)
    local tag="${image##*:}"

    # Check that tag is not empty and not equal to 'latest'
    if [[ -z "$tag" ]]; then
        echo -e "${RED}✗ Empty tag:${NC} [$source] $chart -> $file (line $line): $image"
        ((error_count++))
        return 1
    elif [[ "$tag" == "latest" ]]; then
        echo -e "${RED}✗ Tag 'latest' is not allowed:${NC} [$source] $chart -> $file (line $line): $image"
        ((error_count++))
        return 1
    else
        echo -e "${GREEN}✓ OK:${NC} [$source] $image"
        return 0
    fi
}

# Function to check YAML file for images
check_yaml_file() {
    local file=$1
    local chart=$2
    local source=$3
    local images_found=0

    # Search for lines with image: using grep
    while IFS= read -r line; do
        # Extract line number and content
        local line_num=$(echo "$line" | cut -d: -f1)
        local line_content=$(echo "$line" | cut -d: -f2- | sed 's/^[^#]*image:[[:space:]]*//I')

        # Remove possible quotes
        line_content=$(echo "$line_content" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")

        # For source files, remove helm template directives
        if [[ "$source" == "source" ]]; then
            line_content=$(echo "$line_content" | sed -e 's/{{.*}}//g' -e 's/|.*//g' | xargs)
        fi

        # Skip empty lines
        if [[ -n "$line_content" ]]; then
            check_image "$line_content" "$file" "$line_num" "$chart" "$source"
            ((images_found++))
            ((total_images++))
        fi
    done < <(grep -ni "^[^#]*image:" "$file")

    return $images_found
}

# Function to recursively find and check all YAML files in a directory
check_directory_yamls() {
    local dir=$1
    local chart=$2
    local source=$3
    local images_in_dir=0

    # Find all YAML/YML files in the directory recursively
    local yaml_files=$(find "$dir" -type f \( -name "*.yaml" -o -name "*.yml" \) 2>/dev/null | sort)

    if [[ -z "$yaml_files" ]]; then
        return 0
    fi

    while IFS= read -r yaml_file; do
        # Get relative path from chart directory
        local relative_path="${yaml_file#$dir/}"
        # Remove temp directory prefix if present
        relative_path=$(echo "$relative_path" | sed "s|^$TEMP_DIR/||")
        echo -e "${YELLOW}  Checking $source file:${NC} $relative_path"
        check_yaml_file "$yaml_file" "$chart" "$source"
        local result=$?
        images_in_dir=$((images_in_dir + result))
        ((checked_files++))
    done < <(echo "$yaml_files")

    return $images_in_dir
}

# Function to process a helm chart
process_chart() {
    local chart_file=$1
    local chart_dir=$(dirname "$chart_file")
    local chart_name=$(basename "$chart_dir")

    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Processing Helm chart:${NC} $chart_dir"
    echo -e "${BLUE}Chart name:${NC} $chart_name"

    # Check source YAML files
    echo -e "${YELLOW}Checking source YAML files in chart directory...${NC}"
    check_directory_yamls "$chart_dir" "$chart_name" "source"
    local source_images=$?

    # Generate and check rendered templates
    echo -e "${YELLOW}Generating and checking rendered templates with 'helm template'...${NC}"
    local chart_temp_dir="$TEMP_DIR/$chart_name"
    mkdir -p "$chart_temp_dir"

    if helm template "$chart_name" "$chart_dir" --output-dir="$chart_temp_dir" > /dev/null 2>&1; then
        check_directory_yamls "$chart_temp_dir" "$chart_name" "rendered"
        local rendered_images=$?
    else
        echo -e "${YELLOW}  ⚠ Failed to generate templates, trying with different release name...${NC}"
        local release_name="test-$(echo "$chart_name" | sed 's/[^a-zA-Z0-9-]/-/g' | tr '[:upper:]' '[:lower:]')"
        if helm template "$release_name" "$chart_dir" --output-dir="$chart_temp_dir" > /dev/null 2>&1; then
            check_directory_yamls "$chart_temp_dir" "$chart_name" "rendered"
            local rendered_images=$?
        else
            echo -e "${RED}  ✗ Failed to generate templates for $chart_dir${NC}"
        fi
    fi

    if [[ $source_images -eq 0 && $rendered_images -eq 0 ]]; then
        echo -e "${YELLOW}  ⚠ No images found in any YAML files${NC}"
    fi

    echo ""
    return 0
}

# Main execution
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Helm Chart Image Tag Validator${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# Find all Chart.yaml files
echo -e "${YELLOW}Searching for Chart.yaml files...${NC}\n"

chart_files=$(find . -type f -name "Chart.yaml" -not -path "./.git/*" 2>/dev/null | sort)

if [[ -z "$chart_files" ]]; then
    echo -e "${RED}✗ No Chart.yaml files found!${NC}"
    exit 1
fi

# Process each chart
while IFS= read -r chart_file; do
    process_chart "$chart_file"
    ((checked_charts++))
done < <(echo "$chart_files")

# Print summary
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Charts processed: $checked_charts"
echo -e "YAML files checked: $checked_files"
echo -e "Total images checked: $total_images"
echo -e "Issues found: $error_count"

if [[ $error_count -eq 0 ]]; then
    echo -e "\n${GREEN}✓ All images across all charts have valid tags (not 'latest')${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Issues found with images in Helm charts!${NC}"
    exit 1
fi
