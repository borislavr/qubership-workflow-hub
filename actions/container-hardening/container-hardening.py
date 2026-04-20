#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

# ====================== CONFIG & CHECK DEFINITION ======================
manifests_path = os.getenv("MANIFESTS_PATH")
dockerfile_path = os.getenv("DOCKERFILE_PATH") or None
config_file = os.getenv("CONFIG_FILE")
extra_image_name = os.getenv("IMAGE_NAME") or None

# Load per-repository configuration (explicit disables only)
disabled_checks: set[str] = set()
if Path(config_file).is_file():
    with open(config_file) as f:
        config = yaml.safe_load(f) or {}
    disabled_checks = set(config.get("disabled-checks", []))
    print(f"::notice::Loaded config from {config_file}. Disabled checks: {sorted(disabled_checks)}")
else:
    print("::notice::No config file found – all checks enabled by default (secure defaults)")

# All supported checks – secure defaults = enabled unless explicitly disabled
CHECKS: Dict[str, Dict[str, str]] = {
    "run-as-user-ge-1000": {"name": "runAsUser >= 1000"},
    "run-as-group-ge-1000": {"name": "runAsGroup >= 1000"},
    "run-as-non-root": {"name": "runAsNonRoot: true"},
    "image-user-not-root": {"name": "Image USER is not root (if defined in Dockerfile)"},
    "no-allow-privilege-escalation": {"name": "allowPrivilegeEscalation: false"},
    "no-host-pid": {"name": "hostPID not enabled"},
    "no-host-ipc": {"name": "hostIPC not enabled"},
    "no-host-network": {"name": "hostNetwork not enabled"},
    "read-only-root-filesystem": {"name": "readOnlyRootFilesystem: true"},
    "drop-all-capabilities": {"name": "capabilities.drop contains ALL"},
    "seccomp-profile-runtime-default": {"name": "seccompProfile.type: RuntimeDefault"},
    "no-host-path-volumes": {"name": "No hostPath volumes"},
    "no-untagged-images": {"name": "Images use explicit non-latest tag"},
    "no-restricted-ports": {"name": "No restricted/critical ports"},
    "readonly-fs-deployment-pattern": {"name": "Readonly filesystem deployment pattern properly configured"},
}

# Prohibited ports (hardening list – common privileged/reserved ports; can be extended later)
PROHIBITED_PORTS = {22, 23, 25, 53, 67, 68, 69, 110, 143, 161, 162, 389, 636, 993, 995}

# ====================== RESULTS STORAGE ======================
check_results: Dict[str, Dict[str, Optional[str]]] = {}
for cid in CHECKS:
    if cid in disabled_checks:
        check_results[cid] = {"status": "skipped", "reason": "explicitly disabled in repo config"}
    else:
        check_results[cid] = {"status": None, "reason": None}

def mark_failure(check_id: str, reason: str) -> None:
    """Mark a check as failed (any violation anywhere fails the check)."""
    if check_id in disabled_checks:
        return
    if check_results[check_id]["status"] != "failed":
        check_results[check_id]["status"] = "failed"
        check_results[check_id]["reason"] = reason

# ====================== MANIFEST LOADING ======================
def load_all_manifests(path_str: str) -> List[Dict]:
    path = Path(path_str)
    docs = []
    files = []
    if path.is_dir():
        files.extend(path.rglob("*.yaml"))
        files.extend(path.rglob("*.yml"))
    elif path.is_file():
        files.append(path)
    else:
        print(f"::warning::Manifests path {path_str} not found – skipping validation")
        return []

    for f in files:
        with open(f, encoding="utf-8") as fh:
            for doc in yaml.safe_load_all(fh):
                if isinstance(doc, dict):
                    docs.append(doc)
    return docs

manifests = load_all_manifests(manifests_path)

# ====================== HELPER FUNCTIONS ======================
def get_effective_security_context(pod_spec: Dict, container_spec: Dict) -> Dict:
    """Container securityContext overrides pod level."""
    pod_sec = pod_spec.get("securityContext") or {}
    cont_sec = container_spec.get("securityContext") or {}
    merged = dict(pod_sec)
    merged.update(cont_sec)
    return merged

def process_pod_spec(pod_spec: Dict[str, Any], doc_name: str) -> None:
    """Run all checks against one Pod/Deployment/etc. spec."""
    if not pod_spec:
        return

    containers: List[Dict] = pod_spec.get("containers", []) + pod_spec.get("initContainers", [])
    if not containers:
        return

    # ====================== POD-LEVEL CHECKS ======================
    if "no-host-pid" not in disabled_checks and pod_spec.get("hostPID") is True:
        mark_failure("no-host-pid", f"hostPID: true in {doc_name}")

    if "no-host-ipc" not in disabled_checks and pod_spec.get("hostIPC") is True:
        mark_failure("no-host-ipc", f"hostIPC: true in {doc_name}")

    if "no-host-network" not in disabled_checks and pod_spec.get("hostNetwork") is True:
        mark_failure("no-host-network", f"hostNetwork: true in {doc_name}")

    if "no-host-path-volumes" not in disabled_checks:
        volumes = pod_spec.get("volumes") or []
        if any(v.get("hostPath") for v in volumes if isinstance(v, dict)):
            mark_failure("no-host-path-volumes", f"hostPath volume detected in {doc_name}")

    # Seccomp (pod or any container)
    if "seccomp-profile-runtime-default" not in disabled_checks:
        pod_seccomp = (pod_spec.get("securityContext") or {}).get("seccompProfile", {}) or {}
        if pod_seccomp.get("type") != "RuntimeDefault":
            seccomp_ok = all(
                (c.get("securityContext") or {}).get("seccompProfile", {}).get("type") == "RuntimeDefault"
                for c in containers
            )
            if not seccomp_ok:
                mark_failure("seccomp-profile-runtime-default", f"seccompProfile.type != RuntimeDefault in {doc_name}")

    # ====================== PER-CONTAINER CHECKS ======================
    for idx, container in enumerate(containers):
        name = container.get("name", f"container-{idx}")
        full_name = f"{doc_name} → container {name}"
        sec_ctx = get_effective_security_context(pod_spec, container)
        image = container.get("image")

        # Image tag check
        if image and "no-untagged-images" not in disabled_checks:
            img_base = image.split("@")[0]
            tag_part = img_base.split(":")[-1] if ":" in img_base else "latest"
            if tag_part in ("latest", "") or ":" not in img_base:
                mark_failure("no-untagged-images", f"Untagged/latest image in {full_name}: {image}")

        # runAsUser / runAsGroup / runAsNonRoot
        if "run-as-user-ge-1000" not in disabled_checks:
            uid = sec_ctx.get("runAsUser")
            if uid is None or uid < 1000:
                mark_failure("run-as-user-ge-1000", f"runAsUser < 1000 (or unset) in {full_name}")

        if "run-as-group-ge-1000" not in disabled_checks:
            gid = sec_ctx.get("runAsGroup")
            if gid is None or gid < 1000:
                mark_failure("run-as-group-ge-1000", f"runAsGroup < 1000 (or unset) in {full_name}")

        if "run-as-non-root" not in disabled_checks and sec_ctx.get("runAsNonRoot") is not True:
            mark_failure("run-as-non-root", f"runAsNonRoot != true in {full_name}")

        if "no-allow-privilege-escalation" not in disabled_checks and sec_ctx.get("allowPrivilegeEscalation") is not False:
            mark_failure("no-allow-privilege-escalation", f"allowPrivilegeEscalation != false in {full_name}")

        if "read-only-root-filesystem" not in disabled_checks and sec_ctx.get("readOnlyRootFilesystem") is not True:
            mark_failure("read-only-root-filesystem", f"readOnlyRootFilesystem != true in {full_name}")

        # Capabilities
        if "drop-all-capabilities" not in disabled_checks:
            caps = sec_ctx.get("capabilities") or {}
            drop = caps.get("drop") or []
            if isinstance(drop, str):
                drop = [drop]
            drop_upper = {str(d).upper() for d in drop}
            if "ALL" not in drop_upper:
                mark_failure("drop-all-capabilities", f"capabilities.drop does not contain ALL in {full_name}")

        # Readonly filesystem deployment pattern (enforces readOnlyRootFilesystem + explicit writable volumes pattern)
        # The pattern requires readOnlyRootFilesystem + any writable paths provided via volumes (not root FS writes).
        # We enforce readOnlyRootFilesystem here; the explicit volume usage is implicitly validated by the
        # combination with no-host-path and the read-only check. Advanced per-app path analysis is out of scope.
        if "readonly-fs-deployment-pattern" not in disabled_checks and sec_ctx.get("readOnlyRootFilesystem") is not True:
            mark_failure("readonly-fs-deployment-pattern", f"Readonly FS pattern violated (readOnlyRootFilesystem must be true) in {full_name}")

        # Ports
        if "no-restricted-ports" not in disabled_checks:
            for port_def in container.get("ports") or []:
                cport = port_def.get("containerPort")
                hport = port_def.get("hostPort")
                if cport in PROHIBITED_PORTS or hport in PROHIBITED_PORTS:
                    mark_failure("no-restricted-ports", f"Prohibited port {cport or hport} in {full_name}")

# ====================== EXECUTE VALIDATION ======================
for doc in manifests:
    kind = doc.get("kind")
    meta = doc.get("metadata", {})
    name = meta.get("name", "unknown")
    if kind in {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}:
        pod_spec = doc.get("spec", {}).get("template", {}).get("spec", {})
        doc_name = f"{kind}/{name}"
    elif kind == "Pod":
        pod_spec = doc.get("spec", {})
        doc_name = f"Pod/{name}"
    else:
        continue
    process_pod_spec(pod_spec, doc_name)

# Extra image name check (if provided)
if extra_image_name and "no-untagged-images" not in disabled_checks:
    img_base = extra_image_name.split("@")[0]
    tag_part = img_base.split(":")[-1] if ":" in img_base else "latest"
    if tag_part in ("latest", "") or ":" not in img_base:
        mark_failure("no-untagged-images", f"Untagged/latest image supplied: {extra_image_name}")

# Dockerfile USER check (only if defined)
if dockerfile_path and Path(dockerfile_path).is_file() and "image-user-not-root" not in disabled_checks:
    with open(dockerfile_path, encoding="utf-8") as f:
        lines = f.readlines()
    user = None
    for line in reversed(lines):
        stripped = line.strip()
        if stripped.upper().startswith("USER "):
            user = stripped.split(maxsplit=1)[1].strip()
            break
    if user and user.lower() in {"root", "0"}:
        mark_failure("image-user-not-root", f"Dockerfile sets USER to root: {user}")

# ====================== FINALIZE RESULTS ======================
# Any check that was never marked failed → passed
for cid in list(check_results.keys()):
    if check_results[cid]["status"] is None:
        check_results[cid]["status"] = "passed"
        check_results[cid]["reason"] = ""

# ====================== BUILD REPORT ======================
report_lines = [
    "# Container Hardening Validation Report",
    "",
    f"**Manifests validated:** {len(manifests)} documents",
    f"**Disabled checks:** {len(disabled_checks)} (explicitly configured by repository owners)",
    "",
    "## Summary",
    ""
]

passed_count = failed_count = skipped_count = 0
for cid, res in check_results.items():
    status = res["status"]
    name = CHECKS[cid]["name"]
    if status == "passed":
        passed_count += 1
        report_lines.append(f"- ✅ **{name}** (`{cid}`)")
    elif status == "failed":
        failed_count += 1
        report_lines.append(f"- ❌ **{name}** (`{cid}`) → {res['reason']}")
    else:
        skipped_count += 1
        report_lines.append(f"- ⏭️ **{name}** (`{cid}`) → {res['reason']}")

report_lines.extend([
    "",
    f"**Passed:** {passed_count} **Failed:** {failed_count} **Skipped:** {skipped_count}",
    ""
])

if failed_count > 0:
    report_lines.extend([
        "❌ **FAILURE** – One or more enabled mandatory hardening rules were violated.",
        "Review the failed checks above and either fix the manifests or explicitly disable the check in `.github/hardening-config.yaml`.",
    ])
    exit_code = 1
else:
    report_lines.append("✅ **SUCCESS** – All enabled hardening checks passed.")
    exit_code = 0

report_md = "\n".join(report_lines)
print(report_md)

# Write to GitHub step summary (visible in UI)
with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
    f.write(report_md)

# Optional artifact
with open("hardening-report.md", "w", encoding="utf-8") as f:
    f.write(report_md)

if exit_code == 1:
    sys.exit(1)
          '

      - name: Upload hardening report (always)
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: container-hardening-report
          path: hardening-report.md
          retention-days: 7
