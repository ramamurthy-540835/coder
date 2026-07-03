#!/usr/bin/env python3
"""
PRISM Request Flow Mapper

Traces the execution lineage of actions starting from UI client fetch triggers
through API Route handlers down to the GCS/BigQuery databases and shell subprocesses.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime, timezone

def log_info(msg):
    print(f"INFO: {msg}")

def log_success(msg):
    print(f"🟢 SUCCESS: {msg}")


def trace_ui_fetch_calls(ui_file: Path) -> list:
    """Finds all fetch() commands inside a frontend UI page."""
    if not ui_file.exists():
        return []
    code = ui_file.read_text(encoding="utf-8")
    
    # Match pattern like: fetch('/api/fetch-estimation'...)
    matches = re.findall(r'fetch\(\s*[\'"]([^\'"]+)[\'"]', code)
    return list(set(matches))


def trace_api_route_backend(route_file: Path) -> dict:
    """Parses Next.js api routes to find the target DB queries or bash wrappers called."""
    if not route_file.exists():
        return {}
    code = route_file.read_text(encoding="utf-8")

    subprocesses = re.findall(r'execAsync\(\s*[`\'"]([^`\'"]+)[`\'"]', code)
    bq_queries = re.findall(r'bq\.query\(\s*\{\s*query:\s*[`\'"]([^`\'"]+)[`\'"]', code, re.DOTALL)
    gcs_uploads = "Storage" in code or "gcs" in code
    
    return {
        "route": str(route_file.parent.name),
        "file": route_file.name,
        "triggers_subprocess": list(set(subprocesses)),
        "database_queries": len(bq_queries) > 0,
        "gcs_operations": gcs_uploads
    }


def main():
    log_info("Starting Request Flow Mapper...")
    coder_root = Path(__file__).resolve().parent.parent
    
    # Paths to search
    ui_path = coder_root.parent / "prompt-intelligence-ui" / "app" / "page.tsx"
    api_dir = coder_root.parent / "prompt-intelligence-ui" / "app" / "api"

    ui_fetch_endpoints = trace_ui_fetch_calls(ui_path)
    log_info(f"Traced {len(ui_fetch_endpoints)} UI triggers inside: {ui_path.name}")

    api_routes = []
    if api_dir.exists():
        for r_file in api_dir.rglob("route.ts"):
            api_routes.append(trace_api_route_backend(r_file))

    # Compile unified lineage flow
    flow_lineage = []
    for endpoint in ui_fetch_endpoints:
        endpoint_name = endpoint.split('?')[0].split('/').pop()
        matching_route = next((r for r in api_routes if r["route"] == endpoint_name), None)
        
        flow_lineage.append({
            "ui_trigger_endpoint": endpoint,
            "target_route": endpoint_name,
            "integration_resolved": matching_route is not None,
            "backend_details": matching_route or {
                "route": endpoint_name,
                "triggers_subprocess": [],
                "database_queries": False,
                "gcs_operations": False
            }
        })

    report_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ui_source": str(ui_path),
        "flows": flow_lineage
    }

    # Generate Markdown Flow Diagram
    md = f"""# 🛰️ PRISM END-TO-END REQUEST FLOW SPECIFICATION
- **Execution Time:** `{report_data['timestamp']}`
- **Frontend Source:** `{report_data['ui_source']}`

This document maps user interface triggers directly to their corresponding server-side API endpoints, subprocess pipelines, and database query layers.

## 🗺️ TRANSACTION SEQUENCE TIMELINE
"""
    for flow in flow_lineage:
        md += f"### Trigger: `{flow['ui_trigger_endpoint']}`\n"
        md += f"- **Next.js Router Endpoint:** `/api/{flow['target_route']}`\n"
        
        details = flow["backend_details"]
        if details.get("triggers_subprocess"):
            md += f"- **Subprocess Shell Call:** 🟢 `{' | '.join(details['triggers_subprocess'])}` (Launches background execution)\n"
        else:
            md += f"- **Subprocess Shell Call:** ⚪ None\n"
            
        md += f"- **BigQuery DB Queries:** {'🟢 YES (Reads/Writes to Lakehouse catalog)' if details.get('database_queries') else '⚪ No direct DB connection'}\n"
        md += f"- **GCS Storage Operations:** {'🟢 YES (Pulls/Pushes raw Medallion GCS assets)' if details.get('gcs_operations') else '⚪ No direct storage interaction'}\n\n"
        md += f"```\n[User Click] ──> [Next.js UI fetch] ──> [/api/{flow['target_route']}] ──> [GCS/BigQuery Backend Execution]\n```\n\n---\n"

    # Save reports
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    
    (out_dir / "request_flow_report.json").write_text(json.dumps(report_data, indent=2))
    (out_dir / "request_flow_report.md").write_text(md)
    
    log_success(f"Saved Request Flow Specification: {out_dir}/request_flow_report.md")


if __name__ == "__main__":
    main()
