#!/usr/bin/env python3
"""HTTP webhook that turns Raspberry Pi GPIO relay outputs on for damage events."""

from __future__ import annotations

import argparse
import json
import logging
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


LOG = logging.getLogger("webhook-relay")


class DryRunOutputDevice:
    """Small gpiozero-compatible output used for development and testing."""

    def __init__(self, pin: int, *, active_high: bool, initial_value: bool) -> None:
        self.pin = pin
        self.active_high = active_high
        self.value = initial_value

    def on(self) -> None:
        self.value = True
        LOG.info("DRY RUN: GPIO %s on", self.pin)

    def off(self) -> None:
        self.value = False
        LOG.info("DRY RUN: GPIO %s off", self.pin)

    def close(self) -> None:
        self.off()


class RelayController:
    def __init__(self, config: dict[str, Any], *, dry_run: bool = False) -> None:
        settings = config.get("settings", {})
        self.seconds_per_damage = positive_number(
            settings.get("seconds_per_damage", 0.1), "settings.seconds_per_damage"
        )
        self.max_duration = positive_number(
            settings.get("max_duration_seconds", 2.0),
            "settings.max_duration_seconds",
        )
        self.high_damage_threshold = positive_number(
            settings.get("high_damage_threshold", 5.0),
            "settings.high_damage_threshold",
        )
        self.active_high = bool(settings.get("active_high", False))
        self._outputs: dict[str, list[Any]] = {}
        self._pulse_lock = threading.Lock()

        names = config.get("names")
        if not isinstance(names, dict) or not names:
            raise ValueError("config must contain a non-empty 'names' mapping")

        if dry_run:
            device_class = DryRunOutputDevice
        else:
            try:
                from gpiozero import DigitalOutputDevice
            except ImportError as exc:
                raise RuntimeError(
                    "gpiozero is required on the Pi; install requirements.txt "
                    "or run with --dry-run"
                ) from exc
            device_class = DigitalOutputDevice

        high_damage_pins = validate_pins(
            settings.get("high_damage_pins"), "settings.high_damage_pins"
        )
        used_pins: set[int] = set(high_damage_pins)
        self._high_damage_outputs = [
            device_class(pin, active_high=self.active_high, initial_value=False)
            for pin in high_damage_pins
        ]
        for name, pins in names.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("each configured name must be a non-empty string")
            pins = validate_pins(pins, f"pins for {name!r}")
            duplicates = used_pins.intersection(pins)
            if duplicates:
                raise ValueError(f"GPIO pins used more than once: {sorted(duplicates)}")
            used_pins.update(pins)
            self._outputs[name] = [
                device_class(
                    pin, active_high=self.active_high, initial_value=False
                )
                for pin in pins
            ]

        # Explicitly reset every configured relay output before accepting any
        # webhook requests. This is intentionally limited to configured pins
        # so unrelated GPIO peripherals are not disturbed.
        self.all_off()
        LOG.info("Set all configured GPIO relay pins to off")

    @property
    def names(self) -> list[str]:
        return sorted(self._outputs)

    def duration_for(self, damage: float) -> float:
        return min(damage * self.seconds_per_damage, self.max_duration)

    def pulse(self, name: str, damage: float | None, *, death: bool = False) -> float:
        if name not in self._outputs:
            raise KeyError(name)
        if not death and (damage is None or damage <= 0):
            raise ValueError("damage must be greater than zero")

        duration = self.max_duration if death else self.duration_for(damage)
        high_damage = damage is not None and damage > self.high_damage_threshold
        # The high/low selector is shared by every player, so serialize all
        # pulses to prevent simultaneous events from selecting different modes.
        with self._pulse_lock:
            outputs = self._outputs[name]
            LOG.info(
                "Activating %s for %.3f seconds "
                "(death=%s, damage=%s, high_damage=%s)",
                name,
                duration,
                death,
                damage,
                high_damage,
            )
            try:
                if high_damage:
                    for output in self._high_damage_outputs:
                        output.on()
                else:
                    for output in self._high_damage_outputs:
                        output.off()
                for output in outputs:
                    output.on()
                threading.Event().wait(duration)
            finally:
                for output in outputs:
                    output.off()
                for output in self._high_damage_outputs:
                    output.off()
        return duration

    def close(self) -> None:
        self.all_off()
        for outputs in self._outputs.values():
            for output in outputs:
                output.close()
        for output in self._high_damage_outputs:
            output.close()

    def all_off(self) -> None:
        for outputs in self._outputs.values():
            for output in outputs:
                output.off()
        for output in self._high_damage_outputs:
            output.off()


def positive_number(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a positive number") from exc
    if number <= 0:
        raise ValueError(f"{field} must be a positive number")
    return number


def validate_pins(value: Any, field: str) -> list[int]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    if any(type(pin) is not int or pin < 0 for pin in value):
        raise ValueError(f"{field} must contain non-negative integers")
    if len(set(value)) != len(value):
        raise ValueError(f"{field} contains duplicate pins")
    return value


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as config_file:
        try:
            # JSON is a subset of YAML. Keeping the config JSON-compatible
            # avoids a native PyYAML dependency on the Raspberry Pi.
            config = json.load(config_file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path} must use JSON-compatible YAML: {exc.msg} "
                f"(line {exc.lineno}, column {exc.colno})"
            ) from exc
    if not isinstance(config, dict):
        raise ValueError("config root must be a mapping")
    return config


def make_handler(controller: RelayController) -> type[BaseHTTPRequestHandler]:
    class WebhookHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path.rstrip("/") == "/health":
                self.send_json(200, {"status": "ok", "names": controller.names})
            else:
                self.send_json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path.rstrip("/") != "/webhook":
                self.send_json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16_384:
                    raise ValueError("request body must be between 1 and 16384 bytes")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("JSON body must be an object")
                player = payload.get("Player")
                if not isinstance(player, str) or not player:
                    raise ValueError("Player must be a non-empty string")
                death_value = payload.get("Death")
                if death_value not in ("true", "false"):
                    raise ValueError('Death must be the string "true" or "false"')
                death = death_value == "true"
                source = payload.get("Source")
                if not isinstance(source, str) or not source:
                    raise ValueError("Source must be a non-empty string")
                damage = None if death else positive_number(payload.get("Damage"), "Damage")
                duration = controller.pulse(player, damage, death=death)
            except KeyError:
                self.send_json(404, {"error": "Player is not configured"})
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
            except Exception:
                LOG.exception("Could not process webhook")
                self.send_json(500, {"error": "internal server error"})
            else:
                self.send_json(
                    200,
                    {
                        "status": "activated",
                        "Player": player,
                        "Death": death_value,
                        "Source": source,
                        "Damage": damage,
                        "duration": duration,
                    },
                )

        def send_json(self, status: int, body: dict[str, Any]) -> None:
            encoded = json.dumps(body).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, message: str, *args: Any) -> None:
            LOG.info("%s - %s", self.client_address[0], message % args)

    return WebhookHandler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("relay_config.yaml"),
        help="path to the YAML configuration file",
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--dry-run", action="store_true", help="log GPIO activity without hardware"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    controller = RelayController(load_config(args.config), dry_run=args.dry_run)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(controller))

    def stop_server(_signum: int, _frame: Any) -> None:
        # shutdown() must run outside the serve_forever thread.
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)
    LOG.info("Listening on http://%s:%s/webhook", args.host, args.port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        controller.close()


if __name__ == "__main__":
    main()
