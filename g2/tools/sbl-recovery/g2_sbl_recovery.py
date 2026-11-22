#!/usr/bin/env python3
"""Host-side Apollo510 SBL stock recovery over a reviewed transport.

Sim default: drive the Renode HLE SBL endpoint (OTAP-armed wired-load).
Hardware path: USB Smart Case → YHM pogo UART. That path is implemented
only as a fail-closed stub and is never opened unless --hardware is given
with both exact risk tokens. This tool does not open a device by default.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

STOCK_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
DEVICE_RISK_TOKEN = "I_ACCEPT_DEVICE_WRITE_RISK"
FIRMWARE_RISK_TOKEN = "I_ACCEPT_FIRMWARE_LANE_RISK"

DEFAULT_WEBFLASHER = Path("/Users/kalani/Repo/SybilSight-webflasher")
DEFAULT_RENODE = Path("/Users/kalani/Repo/g2-firmware-emulator")
DEFAULT_IMAGE = Path(
    "/Users/kalani/Repo/evenRealities-OpenCFW/g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
)


def _import_protocol(webflasher_root: Path) -> None:
    scripts = webflasher_root / "scripts"
    sys.path.insert(0, str(scripts))
    # Imported by callers after this runs.


def write_frame_stream(path: Path, frames: list[bytes]) -> None:
    blob = bytearray()
    for frame in frames:
        blob.extend(struct.pack("<I", len(frame)))
        blob.extend(frame)
    path.write_bytes(blob)


def read_frame_stream(path: Path) -> list[bytes]:
    data = path.read_bytes()
    frames = []
    offset = 0
    while offset < len(data):
        if offset + 4 > len(data):
            raise ValueError("truncated reply stream length")
        length, = struct.unpack_from("<I", data, offset)
        offset += 4
        if offset + length > len(data):
            raise ValueError("truncated reply stream payload")
        frames.append(data[offset:offset + length])
        offset += length
    return frames


def build_update_frames(image: bytes, chunk: int) -> list[tuple[str, int, int, bytes]]:
    from g2_sbl_wire import (
        MSG_DATA, MSG_OTA_DESCRIPTOR, MSG_RESET, MSG_UPDATE,
        data_frame, hello_frame, ota_descriptor_frame, reset_frame, update_frame,
    )
    rows = [
        ("HELLO", 0, 0, hello_frame()),
        ("OTADESC", MSG_OTA_DESCRIPTOR, 0, ota_descriptor_frame()),
        ("UPDATE", MSG_UPDATE, 0, update_frame(image)),
    ]
    for offset in range(0, len(image), chunk):
        piece = image[offset:offset + chunk]
        rows.append((f"DATA:{offset}", MSG_DATA, offset, data_frame(offset, piece)))
    rows.append(("RESET", MSG_RESET, 0, reset_frame(1)))
    return rows


def qualify_or_raise(image: bytes, status_frame: bytes, digest: str) -> dict:
    from g2_sbl_wire import qualify_stock_update, image_segments
    qualification = qualify_stock_update(image, status_frame, expected_sha256=digest)
    segments = image_segments(image)
    if len(segments) != 1:
        raise ValueError("writer permits exactly one stock segment")
    if not qualification["capacityAccepted"]:
        raise ValueError("SBL STATUS advertises insufficient storage")
    return qualification


def run_update(transport, image: bytes, *, digest: str, chunk: int, route: str) -> dict:
    from g2_sbl_wire import parse_ack
    from g2_sbl_protocol import find_status_frames

    audit = {
        "operation": "bounded-apollo510-sbl-stock-update",
        "route": route,
        "imageSha256": hashlib.sha256(image).hexdigest(),
        "chunkBytes": chunk,
        "commandsAttempted": 0,
        "commandsAcknowledged": 0,
        "dataFramesAttempted": 0,
        "dataFramesAcknowledged": 0,
        "firmwareImageBytesAcknowledged": 0,
        "resetAcknowledged": False,
        "glassesRecovered": False,
        "physicalDevicesOpened": False,
        "transport": transport.name,
        "outcome": "not-started",
    }
    hello, *rest = build_update_frames(image, chunk)
    audit["commandsAttempted"] += 1
    status = transport.transact(hello[3], label="HELLO")
    frames = find_status_frames(status)
    if len(frames) != 1 or frames[0]["offset"] != 0 or len(status) != 96:
        raise RuntimeError(f"HELLO did not return one 96-byte STATUS (got {len(status)} bytes)")
    audit["commandsAcknowledged"] += 1
    audit["liveStatus"] = frames[0]
    qualification = qualify_or_raise(image, status, digest)
    audit["qualification"] = {
        "capacityAccepted": qualification["capacityAccepted"],
        "maxStorage": qualification["maxStorage"],
        "maxUpdateBytes": qualification["maxUpdateBytes"],
        "eligibleForReviewedWriterImplementation": qualification["eligibleForReviewedWriterImplementation"],
        "firmwareWriteAuthorized": False,
    }

    planned = [row for row in rest]
    replies = transport.transact_many([row[3] for row in planned], label="UPDATE-STREAM")
    if len(replies) != len(planned):
        raise RuntimeError(f"reply count {len(replies)} != command count {len(planned)}")
    for (label, expected_type, sequence, _frame), reply in zip(planned, replies):
        audit["commandsAttempted"] += 1
        if label.startswith("DATA:"):
            audit["dataFramesAttempted"] += 1
        ack = parse_ack(reply, expected_message_type=expected_type, expected_sequence=sequence)
        if not ack["accepted"]:
            audit["outcome"] = f"{label.lower()}-rejected"
            audit["error"] = f"{label} rejected with {ack['statusName']} ({ack['status']})"
            raise RuntimeError(audit["error"])
        audit["commandsAcknowledged"] += 1
        if label.startswith("DATA:"):
            audit["dataFramesAcknowledged"] += 1
            start = int(label.split(":")[1])
            audit["firmwareImageBytesAcknowledged"] += min(chunk, len(image) - start)
        if label == "RESET":
            audit["resetAcknowledged"] = True
    if audit["firmwareImageBytesAcknowledged"] != len(image):
        raise RuntimeError("not every stock-image byte was acknowledged")
    audit["outcome"] = "reset-acknowledged-postflight-required"
    return audit


class RenodeSblTransport:
    name = "renode-sblwired-hle"

    def __init__(self, console, workdir: Path):
        self.console = console
        self.workdir = workdir
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.seq = 0

    def transact(self, frame: bytes, timeout: float = 12.0, label: str = "") -> bytes:
        self.seq += 1
        rx = self.workdir / f"{self.seq:04d}-{label or 'frame'}.rx"
        tx = self.workdir / f"{self.seq:04d}-{label or 'frame'}.tx"
        rx.write_bytes(frame)
        self.console.command(f"sblwired TransactFile @{rx} @{tx}")
        if not tx.is_file():
            raise RuntimeError(f"{label or 'frame'} produced no reply file")
        return tx.read_bytes()

    def transact_many(self, frames: list[bytes], label: str = "stream") -> list[bytes]:
        self.seq += 1
        rx = self.workdir / f"{self.seq:04d}-{label}.rxstream"
        tx = self.workdir / f"{self.seq:04d}-{label}.txstream"
        write_frame_stream(rx, frames)
        self.console.command(f"sblwired ProcessFrameStream @{rx} @{tx}", timeout=300)
        return read_frame_stream(tx)


class HardwareCaseTransport:
    """Fail-closed: documents the stock case/pogo path, does not open a device."""

    name = "case-pogo-refused"

    def __init__(self, **_kwargs):
        raise RuntimeError(
            "Hardware case/pogo transport is intentionally not opened by this "
            "invocation. Re-run only with --hardware after a CRC-valid STATUS "
            "and both risk tokens. See README.md for the hookup."
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("sim", "hardware"), default="sim")
    p.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    p.add_argument("--image-sha256", default=STOCK_SHA256)
    p.add_argument("--webflasher-root", type=Path, default=DEFAULT_WEBFLASHER)
    p.add_argument("--renode-root", type=Path, default=DEFAULT_RENODE)
    p.add_argument("--workdir", type=Path, required=True)
    p.add_argument("--route", choices=("left", "right"), default="right")
    p.add_argument("--chunk", choices=("case", "uart"), default="uart",
                   help="case=997-byte Case-bridge chunks; uart=8180-byte direct SBL chunks")
    p.add_argument("--hardware", action="store_true",
                   help="Required to select the case/pogo path. Still refused unless tokens match.")
    p.add_argument("--device-risk-token", default="")
    p.add_argument("--firmware-risk-token", default="")
    p.add_argument("--audit", type=Path, help="Write the audit JSON here")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.mode == "hardware" or args.hardware:
        print(
            "Refusing hardware execution: this tool must not be run against a "
            "physical temple from this invocation. Hookup is in README.md.",
            file=sys.stderr,
        )
        return 2
    _import_protocol(args.webflasher_root)
    from g2_sbl_wire import CASE_BRIDGE_MAX_DATA_BYTES, MAX_DATA_BYTES
    image = args.image.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != args.image_sha256.lower():
        raise SystemExit(f"image SHA-256 {digest} != {args.image_sha256}")
    chunk = CASE_BRIDGE_MAX_DATA_BYTES if args.chunk == "case" else MAX_DATA_BYTES
    # The sim transport is constructed by sim_verify, which calls run_update
    # directly. This CLI entry is a dry qualification plus a usage reminder
    # unless a transport is injected via --mode sim with an already-running
    # monitor, which sim_verify handles.
    print(
        f"image {args.image} sha256={digest} bytes={len(image)} chunk={chunk} "
        f"mode={args.mode}. Use sim_verify.py to drive Renode end-to-end.",
        file=sys.stderr,
    )
    if args.audit:
        args.audit.write_text(json.dumps({
            "mode": args.mode,
            "imageSha256": digest,
            "bytes": len(image),
            "chunkBytes": chunk,
            "physicalDevicesOpened": False,
            "note": "CLI without a live transport only qualifies the image path",
        }, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
