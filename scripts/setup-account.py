#!/usr/bin/env python3
"""
Setup a new (or existing) GHL account in this codebase.

Creates two folders in the target GHL location:
  - "TEST WORKFLOWS"          → for test/verification script output
  - "AI GENERATED - STAGING"  → for engine-generated campaigns awaiting human review

Saves all credentials + folder IDs to .env.<account-name>.

Usage:
    python3 scripts/setup-account.py aisimple
    python3 scripts/setup-account.py leveragedva

Re-running on an existing account: keeps existing values, only creates folders
that don't already have an ID set in the env file.
"""

import os, sys, getpass
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.engine import TokenManager, GHLClient


TEST_FOLDER_NAME = "TEST WORKFLOWS"
STAGING_FOLDER_NAME = "AI GENERATED - STAGING"

REQUIRED_VARS = ["GHL_LOCATION_ID", "GHL_COMPANY_ID", "GHL_USER_ID"]
AUTH_VARS = ["GHL_FIREBASE_REFRESH_TOKEN", "GHL_TOKEN_SERVER", "GHL_ADMIN_PIN"]
FOLDER_VARS = ["GHL_TEST_FOLDER", "GHL_PARENT_FOLDER"]


def parse_env_file(path: Path) -> dict:
    """Parse a simple KEY=VALUE .env file. Strips quotes."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def write_env_file(path: Path, env: dict, header_comment: str = ""):
    """Write env dict back to file, preserving order of known keys + appending unknown ones."""
    lines = []
    if header_comment:
        lines.append(f"# {header_comment}")
    lines.append(f"GHL_LOCATION_ID={env.get('GHL_LOCATION_ID', '')}")
    lines.append(f"GHL_COMPANY_ID={env.get('GHL_COMPANY_ID', '')}")
    lines.append(f"GHL_USER_ID={env.get('GHL_USER_ID', '')}")
    lines.append(f"GHL_TEST_FOLDER={env.get('GHL_TEST_FOLDER', '')}")
    lines.append(f"GHL_PARENT_FOLDER={env.get('GHL_PARENT_FOLDER', '')}")
    lines.append("")
    lines.append("# Auth (refresh token auto-refreshes via Google securetoken; never expires)")
    lines.append(f"GHL_FIREBASE_REFRESH_TOKEN={env.get('GHL_FIREBASE_REFRESH_TOKEN', '')}")
    lines.append("")
    lines.append("# Optional: Cloudflare Worker token server (alternative to refresh token)")
    lines.append(f"GHL_TOKEN_SERVER={env.get('GHL_TOKEN_SERVER', '')}")
    lines.append(f"GHL_ADMIN_PIN={env.get('GHL_ADMIN_PIN', '')}")

    # Preserve any extra unknown keys
    known = set(REQUIRED_VARS + AUTH_VARS + FOLDER_VARS)
    extras = [k for k in env.keys() if k not in known]
    if extras:
        lines.append("")
        lines.append("# Custom keys (preserved from existing file)")
        for k in extras:
            lines.append(f"{k}={env[k]}")

    path.write_text("\n".join(lines) + "\n")


NON_INTERACTIVE = not sys.stdin.isatty() or os.environ.get("SETUP_NON_INTERACTIVE", "") == "1"


def prompt(label: str, default: str = "", secret: bool = False) -> str:
    """Prompt the user with optional default. Returns trimmed input.
    In non-interactive mode (no TTY), accepts default without prompting."""
    if NON_INTERACTIVE:
        if default:
            display = default[:8] + "…" if secret else default
            print(f"{label} [auto: {display}]")
            return default
        print(f"{label} [auto: <empty>]")
        return ""
    suffix = f" [{default[:8] + '…' if secret and default else default}]" if default else ""
    fn = getpass.getpass if secret else input
    val = fn(f"{label}{suffix}: ").strip()
    return val or default


def find_existing_folder(client: GHLClient, loc: str, name: str) -> str:
    """Search existing workflow items for a folder with the given name. Returns ID or ''."""
    try:
        items = client.request("GET", f"/workflow/{loc}")
        if not items:
            return ""
        # Response shape varies; handle list or {"workflows": [...]}
        candidates = items if isinstance(items, list) else items.get("workflows", [])
        for it in candidates:
            if it.get("type") == "directory" and it.get("name") == name and not it.get("parentId"):
                return it.get("id", "")
    except Exception:
        pass
    return ""


def ensure_folder(client: GHLClient, loc: str, name: str, current_id: str) -> str:
    """Ensure a top-level folder with this name exists. Returns its ID."""
    if current_id:
        print(f"  ✓ {name} already configured: {current_id}")
        return current_id

    existing = find_existing_folder(client, loc, name)
    if existing:
        print(f"  ✓ Found existing {name}: {existing}")
        return existing

    print(f"  → Creating {name}...")
    result = client.request("POST", f"/workflow/{loc}", {"name": name, "type": "directory"})
    if not result or not result.get("id"):
        print(f"  ✗ Failed to create {name}: {result}")
        return ""
    print(f"  ✓ Created {name}: {result['id']}")
    return result["id"]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/setup-account.py <account-name>")
        print("Example: python3 scripts/setup-account.py aisimple")
        sys.exit(1)

    account = sys.argv[1]
    repo_root = Path(__file__).parent.parent
    env_path = repo_root / f".env.{account}"

    print(f"\n=== Setup account: {account} ===")
    print(f"Env file: {env_path}\n")

    env = parse_env_file(env_path)

    # 1. Required IDs
    print("Required GHL IDs (from app.gohighlevel.com URL):")
    env["GHL_LOCATION_ID"] = prompt("  Location ID", env.get("GHL_LOCATION_ID", ""))
    env["GHL_COMPANY_ID"] = prompt("  Company ID", env.get("GHL_COMPANY_ID", ""))
    env["GHL_USER_ID"] = prompt("  User ID", env.get("GHL_USER_ID", ""))

    missing = [v for v in REQUIRED_VARS if not env.get(v)]
    if missing:
        sys.exit(f"\n✗ Missing required values: {missing}")

    # 2. Auth
    print("\nAuth (provide refresh token OR token-server + admin pin):")
    env["GHL_FIREBASE_REFRESH_TOKEN"] = prompt(
        "  Firebase refresh token (or blank to use token server)",
        env.get("GHL_FIREBASE_REFRESH_TOKEN", ""),
        secret=True,
    )
    if not env["GHL_FIREBASE_REFRESH_TOKEN"]:
        env["GHL_TOKEN_SERVER"] = prompt(
            "  Token server URL", env.get("GHL_TOKEN_SERVER", "")
        )
        env["GHL_ADMIN_PIN"] = prompt(
            "  Admin PIN", env.get("GHL_ADMIN_PIN", ""), secret=True
        )
    else:
        env.setdefault("GHL_TOKEN_SERVER", env.get("GHL_TOKEN_SERVER", ""))
        env.setdefault("GHL_ADMIN_PIN", env.get("GHL_ADMIN_PIN", ""))

    # Apply env to current process so engine picks it up
    for k, v in env.items():
        if v:
            os.environ[k] = v

    # 3. Verify auth via the internal workflow API (the only endpoint set we know works)
    print("\nVerifying auth...")
    tm = TokenManager(env["GHL_LOCATION_ID"])
    if env.get("GHL_FIREBASE_REFRESH_TOKEN"):
        tm.set_refresh_token(env["GHL_FIREBASE_REFRESH_TOKEN"])
    client = GHLClient(tm, env["GHL_LOCATION_ID"])

    # Hit a known-working internal endpoint to prove auth + location access
    items = client.request("GET", f"/workflow/{env['GHL_LOCATION_ID']}")
    if items is None:
        sys.exit("✗ Auth failed or location inaccessible. Check refresh token and location ID.")

    candidates = items if isinstance(items, list) else items.get("workflows", [])
    loc_name = f"location {env['GHL_LOCATION_ID']}"
    print(f"  ✓ Authenticated. {loc_name} — {len(candidates)} existing workflow item(s)")

    if NON_INTERACTIVE:
        print(f"\n[non-interactive] Auto-confirming setup on '{loc_name}'")
    else:
        confirm = input(f"\nProceed with setup on '{loc_name}'? [y/N]: ").strip().lower()
        if confirm != "y":
            sys.exit("Cancelled.")

    # 4. Ensure folders
    print("\nEnsuring folders exist:")
    env["GHL_TEST_FOLDER"] = ensure_folder(
        client, env["GHL_LOCATION_ID"], TEST_FOLDER_NAME, env.get("GHL_TEST_FOLDER", "")
    )
    env["GHL_PARENT_FOLDER"] = ensure_folder(
        client, env["GHL_LOCATION_ID"], STAGING_FOLDER_NAME, env.get("GHL_PARENT_FOLDER", "")
    )

    # 5. Write env file
    write_env_file(env_path, env, header_comment=f"GHL credentials for: {loc_name} ({account})")

    print(f"\n✓ Setup complete. Wrote {env_path}")
    print(f"\nTo use this account:")
    print(f"  export $(grep -v '^#' {env_path.name} | xargs)")
    print(f"  python3 campaigns/my-campaign.py")


if __name__ == "__main__":
    main()
