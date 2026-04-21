#!/usr/bin/env python3
"""
A script for converting kubescape JSON results into Markdown tables.
Usage: python3 generate_report.py [--input file.json] [--output report.md]
"""

import json
import urllib.request
import argparse
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

def get_status_emoji(status):
    """Returns the emoji for a given status."""
    return '✅' if status == 'passed' else '❌'

def generate_markdown_tables(data):
    """Generates markdown tables for each resourceID."""
    results = data.get('results', [])

    if not results:
        return "No results found in the JSON data."

    output_lines = []

    for resource in results:
        resource_id = resource.get('resourceID', 'Unknown')
        if not '/Deployment/' in resource_id:  # Skip non-deployment resources
            continue
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

        # Add statistics for the resource
        total_controls = len(controls)
        passed = sum(1 for c in controls
                    if c.get('rules', [{}])[0].get('status', '') == 'passed')
        failed = total_controls - passed

        output_lines.append(f"\n**Total:** ✅ passed: {passed}, ❌ failed: {failed}\n")
        output_lines.append("---")

    return '\n'.join(output_lines)

def generate_full_report(data, title="Kubescape Hardening Scan Report"):
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
    report += generate_markdown_tables(data)

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

    args = parser.parse_args()

    try:
        print(f"Loading data from: {args.input}")
        data = load_json_data(args.input)

        print("Generating markdown report...")
        report = generate_full_report(data, args.title)

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