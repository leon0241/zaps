#!/usr/bin/env python3
"""Send dummy damage webhook data to the Raspberry Pi relay service."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_DATA_FILE = Path(__file__).with_name("dummy_webhook.json")


def load_payload(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as payload_file:
            payload = json.load(payload_file)
    except FileNotFoundError as exc:
        raise ValueError(f"dummy data file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON in {path}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError("dummy webhook data must be a JSON object")
    if not isinstance(payload.get("name"), str) or not payload["name"]:
        raise ValueError("dummy webhook 'name' must be a non-empty string")
    damage = payload.get("damage")
    if isinstance(damage, bool) or not isinstance(damage, (int, float)) or damage <= 0:
        raise ValueError("dummy webhook 'damage' must be a positive number")

    # Return only the fields emitted by the real damage webhook.
    return {"name": payload["name"], "damage": damage}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8080/webhook",
        help="Pi webhook URL (default: %(default)s)",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="dummy webhook JSON file (default: next to this script)",
    )
    parser.add_argument("--name", help="override the name in the data file")
    parser.add_argument(
        "--damage", type=float, help="override the damage in the data file"
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args.data)
        if args.name is not None:
            if not args.name:
                raise ValueError("--name must not be empty")
            payload["name"] = args.name
        if args.damage is not None:
            if args.damage <= 0:
                raise ValueError("--damage must be greater than zero")
            payload["damage"] = args.damage

        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request = Request(
            args.url,
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        print(f"POST {args.url}")
        print(f"Payload: {encoded.decode('utf-8')}")
        with urlopen(request, timeout=args.timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"Response: HTTP {response.status}")
            print(body)
        return 0
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Pi returned HTTP {exc.code}: {body}", file=sys.stderr)
    except URLError as exc:
        print(f"Could not reach the Pi: {exc.reason}", file=sys.stderr)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
