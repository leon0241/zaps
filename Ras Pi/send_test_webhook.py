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
    if not isinstance(payload.get("Player"), str) or not payload["Player"]:
        raise ValueError("dummy webhook 'Player' must be a non-empty string")
    if payload.get("Death") not in ("true", "false"):
        raise ValueError('dummy webhook \'Death\' must be "true" or "false"')
    if not isinstance(payload.get("Source"), str) or not payload["Source"]:
        raise ValueError("dummy webhook 'Source' must be a non-empty string")

    result = {
        "Player": payload["Player"],
        "Death": payload["Death"],
        "Source": payload["Source"],
    }
    if payload["Death"] == "false":
        damage = payload.get("Damage")
        if (
            isinstance(damage, bool)
            or not isinstance(damage, (int, float))
            or damage <= 0
        ):
            raise ValueError("dummy webhook 'Damage' must be a positive number")
        result["Damage"] = damage
    return result


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
    parser.add_argument("--player", help="override Player in the data file")
    parser.add_argument("--source", help="override Source in the data file")
    parser.add_argument(
        "--damage", type=float, help="override Damage for a non-death event"
    )
    parser.add_argument(
        "--death",
        action="store_true",
        help='send a death event (Death="true" with no Damage field)',
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = load_payload(args.data)
        if args.player is not None:
            if not args.player:
                raise ValueError("--player must not be empty")
            payload["Player"] = args.player
        if args.source is not None:
            if not args.source:
                raise ValueError("--source must not be empty")
            payload["Source"] = args.source
        if args.death:
            payload["Death"] = "true"
            payload.pop("Damage", None)
        if args.damage is not None:
            if args.damage <= 0:
                raise ValueError("--damage must be greater than zero")
            if payload["Death"] == "true":
                raise ValueError("--damage cannot be used with a death event")
            payload["Damage"] = args.damage

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
