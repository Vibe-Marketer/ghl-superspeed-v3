#!/usr/bin/env python3
"""AI Simple GHL launcher for listing, previewing, configuring, and deploying workflows."""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BLUEPRINTS_PATH = ROOT / "templates" / "blueprints.json"
LOG_DIR = ROOT / "logs" / "campaigns"

TEMPLATES = {
    "webinar-funnel": ROOT / "campaigns" / "webinar-funnel.py",
    "follow-up": ROOT / "campaigns" / "my-campaign.py",
    "example-simple": ROOT / "campaigns" / "example-simple.py",
}

CONFIG_KEYS = [
    ("CAMPAIGN_NAME", "Campaign name", "Client Campaign"),
    ("CAMPAIGN_BUSINESS_NAME", "Business name", "Client Business"),
    ("CAMPAIGN_SENDER_NAME", "Sender/team name", "Client Team"),
    ("CAMPAIGN_SERVICE_CATEGORY", "Service category", "your services"),
    ("CAMPAIGN_WEBINAR_TITLE", "Webinar title", "The Growth System Workshop"),
    ("CAMPAIGN_WEBINAR_DAY", "Webinar day", "Thursday"),
    ("CAMPAIGN_WEBINAR_TIME", "Webinar time", "7 PM ET"),
    ("CAMPAIGN_WEBINAR_LINK", "Webinar/replay link", "{{custom_values.webinar_link}}"),
    ("CAMPAIGN_OFFER_NAME", "Offer/program name", "Implementation Program"),
    ("CAMPAIGN_PRICE_TEXT", "Price/enrollment text", "your enrollment option"),
    ("CAMPAIGN_DEADLINE_TEXT", "Deadline text", "Sunday at midnight"),
    ("CAMPAIGN_TAG_PREFIX", "Tag prefix", "webinar"),
]


def parse_env_file(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def write_env_file(path: Path, values: dict[str, str]) -> None:
    known_order = [
        "GHL_LOCATION_ID",
        "GHL_COMPANY_ID",
        "GHL_USER_ID",
        "GHL_TEST_FOLDER",
        "GHL_PARENT_FOLDER",
        "GHL_FIREBASE_REFRESH_TOKEN",
        "GHL_TOKEN_SERVER",
        "GHL_ADMIN_PIN",
    ] + [key for key, _, _ in CONFIG_KEYS]
    lines = ["# AI Simple GHL client config"]
    for key in known_order:
        if key in values:
            lines.append(f"{key}={values[key]}")
    extras = sorted(key for key in values if key not in set(known_order))
    if extras:
        lines.append("")
        lines.append("# Additional values")
        for key in extras:
            lines.append(f"{key}={values[key]}")
    path.write_text("\n".join(lines) + "\n")


def load_blueprints() -> dict:
    if not BLUEPRINTS_PATH.exists():
        return {}
    return json.loads(BLUEPRINTS_PATH.read_text()).get("blueprints", {})


def template_path(name: str) -> Path:
    if name in TEMPLATES:
        return TEMPLATES[name]
    candidate = ROOT / "campaigns" / name
    if candidate.suffix != ".py":
        candidate = candidate.with_suffix(".py")
    if candidate.exists():
        return candidate
    raise SystemExit(f"Unknown template or campaign: {name}")


def import_campaign(path: Path, env_values: dict[str, str] | None = None):
    old_env = os.environ.copy()
    try:
        defaults = {
            "GHL_LOCATION_ID": "preview-location",
            "GHL_COMPANY_ID": "preview-company",
            "GHL_USER_ID": "preview-user",
            "GHL_PARENT_FOLDER": "preview-folder",
        }
        os.environ.update(defaults)
        if env_values:
            os.environ.update(env_values)
        spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
        if not spec or not spec.loader:
            raise SystemExit(f"Could not load campaign: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        os.environ.clear()
        os.environ.update(old_env)


def cmd_examples(_args) -> None:
    print("\nAvailable campaign templates:\n")
    blueprints = load_blueprints()
    for key, path in TEMPLATES.items():
        bp = blueprints.get(key, {})
        name = bp.get("name", key)
        desc = bp.get("description", path.name)
        workflows = bp.get("workflows", "?")
        steps = bp.get("estimated_steps", "?")
        print(f"  {key}")
        print(f"    {name}: {desc}")
        print(f"    {workflows} workflow(s), about {steps} step(s)")
    print("\nUse: python3 ai-simple.py preview webinar-funnel")


def cmd_preview(args) -> None:
    path = template_path(args.template)
    env_values = parse_env_file(Path(args.env)) if args.env else {}
    module = import_campaign(path, env_values)
    campaign = getattr(module, "CAMPAIGN", None)
    if not campaign:
        raise SystemExit(f"No CAMPAIGN dict found in {path}")
    total_steps = sum(len(wf.get("templates", [])) for wf in campaign.values())
    print(f"\nPreview: {getattr(module, 'CAMPAIGN_NAME', path.stem)}")
    print(f"File: {path.relative_to(ROOT)}")
    print(f"Workflows: {len(campaign)}")
    print(f"Steps: {total_steps}\n")
    for key, wf in campaign.items():
        print(f"{key}. {wf.get('name', key)}")
        print(f"   Trigger tag: {wf.get('tag', '(none)')}")
        for index, step in enumerate(wf.get("templates", []), start=1):
            print(f"   {index:02d}. {step.get('name', step.get('type'))} [{step.get('type')}]")
        print()


def cmd_configure(args) -> None:
    path = ROOT / f".env.{args.client}"
    values = parse_env_file(path)
    print(f"\nConfiguring campaign values in {path.name}")
    print("Press Enter to keep the shown value.\n")
    for key, label, default in CONFIG_KEYS:
        current = values.get(key, default)
        entered = input(f"{label} [{current}]: ").strip()
        values[key] = entered or current
    write_env_file(path, values)
    print(f"\nSaved {path.name}")


def cmd_deploy(args) -> None:
    path = template_path(args.template)
    env_path = Path(args.env)
    if not env_path.exists():
        raise SystemExit(f"Env file not found: {env_path}")
    env_values = parse_env_file(env_path)
    missing = [key for key in ["GHL_LOCATION_ID", "GHL_COMPANY_ID", "GHL_USER_ID"] if not env_values.get(key)]
    if missing:
        raise SystemExit(f"Missing required env values in {env_path}: {', '.join(missing)}")
    env = os.environ.copy()
    env.update(env_values)
    env.setdefault("GHL_CAMPAIGN_LOG_DIR", str(LOG_DIR))
    print(f"\nDeploying {path.relative_to(ROOT)} using {env_path}")
    print("Target: AI GENERATED - STAGING folder from your env config\n")
    result = subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env)
    raise SystemExit(result.returncode)


def cmd_logs(args) -> None:
    if not LOG_DIR.exists():
        print("No campaign logs found yet.")
        return
    logs = sorted(LOG_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not logs:
        print("No campaign logs found yet.")
        return
    for path in logs[: args.limit]:
        try:
            data = json.loads(path.read_text())
            print(f"\n{path.relative_to(ROOT)}")
            print(f"  Campaign: {data.get('campaign_name', '')}")
            print(f"  Location: {data.get('location_id', '')}")
            print(f"  Workflows: {len(data.get('workflows', []))}")
            print(f"  Errors: {len(data.get('stats', {}).get('errors', []))}")
        except Exception as exc:
            print(f"{path}: could not read log ({exc})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Simple GHL workflow launcher")
    sub = parser.add_subparsers(dest="command", required=True)

    examples = sub.add_parser("examples", help="List available workflow examples")
    examples.set_defaults(func=cmd_examples)

    preview = sub.add_parser("preview", help="Preview a campaign without API calls")
    preview.add_argument("template", help="Template key or campaign file name")
    preview.add_argument("--env", help="Optional env file for campaign variables")
    preview.set_defaults(func=cmd_preview)

    configure = sub.add_parser("configure", help="Set campaign variables in .env.<client>")
    configure.add_argument("client", help="Client slug, e.g. phill")
    configure.set_defaults(func=cmd_configure)

    deploy = sub.add_parser("deploy", help="Deploy a campaign to GHL staging")
    deploy.add_argument("template", help="Template key or campaign file name")
    deploy.add_argument("--env", required=True, help="Env file, e.g. .env.phill")
    deploy.set_defaults(func=cmd_deploy)

    logs = sub.add_parser("logs", help="List recent campaign deployment logs")
    logs.add_argument("--limit", type=int, default=10)
    logs.set_defaults(func=cmd_logs)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
