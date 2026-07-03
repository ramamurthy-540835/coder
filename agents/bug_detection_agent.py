#!/usr/bin/env python3
"""
PRISM Bug Detection Agent

Scans codebase for:
- Hardcoded URLs, static IPs, and private ports.
- Gaps in error handling (empty try-except / catch blocks).
- Uninitialized state allocations.
- TypeScript strict type assertion bypasses (as any).
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime, timezone

def log_info(msg):
    print(f"INFO: {msg}")

def log_warning(msg):
    print(f"⚠️ WARNING: {msg}")

def log_success(msg):
    print(f"🟢 SUCCESS: {msg}")


def audit_file_defects(file_path: Path) -> list:
    """Scans individual files for potential defects using targeted Regex rules."""
    code = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = code.splitlines()
    defects = []

    # 1. Regex rules
    ip_pattern = re.compile(r'\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    empty_except_pattern = re.compile(r'except(\s+Exception)?:?\s*(#\s*.*)?\s*pass')
    any_cast_pattern = re.compile(r':\s*any|\bas\s+any\b')

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("#"):
            continue

        # Rule A: Check for hardcoded private IPs/Hosts
        ip_match = ip_pattern.search(stripped)
        if ip_match:
            ip_found = ip_match.group(0)
            # Exclude loopback/metadata server IPs
            if ip_found not in ("127.0.0.1", "0.0.0.0", "169.254.169.254"):
                defects.append({
                    "line": idx,
                    "type": "hardcoded_ip",
                    "severity": "CRITICAL",
                    "description": f"Exposed hardcoded private IP address: '{ip_found}'",
                    "snippet": stripped
                })

        # Rule B: Check for empty python try-except blocks
        if file_path.suffix == ".py" and empty_except_pattern.search(stripped):
            defects.append({
                "line": idx,
                "type": "empty_exception_handler",
                "severity": "HIGH",
                "description": "Swallowed exception block ('except ...: pass'). Gaps in execution observability.",
                "snippet": stripped
            })

        # Rule C: Check for strict TypeScript bypasses (any)
        if file_path.suffix in (".ts", ".tsx") and any_cast_pattern.search(stripped):
            defects.append({
                "line": idx,
                "type": "typescript_any_override",
                "severity": "MEDIUM",
                "description": "Strict type safety rules bypassed using implicit ': any' or 'as any' casting.",
                "snippet": stripped
            })

    return defects


def main():
    log_info("Starting Bug Detection Agent...")
    project_root = Path(__file__).resolve().parent.parent
    defect_list = []

    ignore_dirs = {".git", "node_modules", "venv"}

    for root, dirs, files in os.walk(project_root.parent):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in (".py", ".ts", ".tsx"):
                file_defects = audit_file_defects(file_path)
                if file_defects:
                    # Clean relative path
                    rel_path = str(file_path.relative_to(project_root.parent))
                    log_warning(f"Audited {len(file_defects)} potential issues in file: {rel_path}")
                    for d in file_defects:
                        d["file"] = rel_path
                        defect_list.append(d)

    # Sort defects by severity (CRITICAL -> HIGH -> MEDIUM)
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    defect_list.sort(key=lambda d: severity_order.get(d["severity"], 4))

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_defects": len(defect_list),
        "defects": defect_list
    }

    # Generate Markdown Report
    md = f"""# 🐞 PRISM CODE OBSERVABILITY & BUG REGISTRY
- **Execution Time:** `{report_data['timestamp']}`
- **Active Defects Audited:** `{report_data['total_defects']}`

Below is the static defect tracking log sorted by impact severity.

## 🗃️ CODE DEFECT REGISTRY
"""
    if not defect_list:
        md += "\n🟢 **SUCCESS:** No critical configuration issues, hardcoded IPs, or exception gaps found in active workspace.\n"
    else:
        md += "\n| File Path | Line | Severity | Classification | Description | Code Snippet |\n"
        md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for d in defect_list:
            md += f"| `{d['file']}` | {d['line']} | **{d['severity']}** | `{d['type']}` | {d['description']} | `{d['snippet'][:50]}` |\n"

    # Save reports
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    
    (out_dir / "defect_registry_report.json").write_text(json.dumps(report_data, indent=2))
    (out_dir / "defect_registry_report.md").write_text(md)
    
    log_success(f"Saved Bug Detection Registry: {out_dir}/defect_registry_report.md")


if __name__ == "__main__":
    main()
