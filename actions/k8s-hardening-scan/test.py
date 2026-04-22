import yaml
config_path = 'hardening-config.yaml'
ports = [22, 69, 80, 443, 8080]
critical_ports = []
config = {}
with open(config_path, 'r', encoding='utf-8') as f:
    print(f"Loading data from: {config_path}")
    config = yaml.safe_load(f)
    critical_ports = config.get('hardening_rules', {}).get('Critical-Ports', {}).get('critical_ports', [])
    print(critical_ports)

intersection = list(set(critical_ports) & set(ports))
if intersection:
    print(f"| Critical-Ports | Critical Ports: {', '.join(map(str, sorted(intersection)))} | ❌ |")
else:
    print(f"| Critical-Ports | Critical Ports | ✅ |")

print(f"Critical-Ports: {critical_ports}")
print(f"Ports: {ports}")
print(f"Intersection: {intersection}")
print(f"Config hardening_rules: {config.get('hardening_rules', {})}")

mandatory_checks = [
    rule_id
    for rule_id, rule_data in config.get('hardening_rules', {}).items()
    if rule_data.get('mandatory') is True
]
print(f"Mandatory checks: {mandatory_checks}")

print(f"Config: {config}")