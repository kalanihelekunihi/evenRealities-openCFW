#!/usr/bin/env python3
"""Summarize an R1 Nordic Secure DFU package without executing or extracting it.

The report preserves the Cortex-M vector evidence and the signed init packet's public metadata.
It never verifies the signature (no trust key is present), flashes a device, or writes input data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path
from typing import Any


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data) and shift < 70:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte & 0x80 == 0:
            return value, offset
        shift += 7
    raise ValueError("truncated or oversized protobuf varint")


def protobuf_fields(data: bytes) -> dict[int, list[int | bytes]]:
    fields: dict[int, list[int | bytes]] = {}
    offset = 0
    while offset < len(data):
        key, offset = read_varint(data, offset)
        number = key >> 3
        wire_type = key & 0x07
        if number == 0:
            raise ValueError("protobuf field zero is invalid")
        if wire_type == 0:
            value, offset = read_varint(data, offset)
        elif wire_type == 2:
            length, offset = read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise ValueError("truncated protobuf length-delimited field")
            value = data[offset:end]
            offset = end
        else:
            raise ValueError(f"unsupported protobuf wire type {wire_type}")
        fields.setdefault(number, []).append(value)
    return fields


def one(fields: dict[int, list[int | bytes]], number: int) -> int | bytes | None:
    values = fields.get(number, [])
    return values[0] if values else None


def as_int(value: int | bytes | None, default: int = 0) -> int:
    if value is None:
        return default
    if not isinstance(value, int):
        raise ValueError("expected protobuf varint")
    return value


def as_bytes(value: int | bytes | None) -> bytes:
    if not isinstance(value, bytes):
        raise ValueError("expected protobuf length-delimited field")
    return value


def packed_varints(data: bytes) -> list[int]:
    values: list[int] = []
    offset = 0
    while offset < len(data):
        value, offset = read_varint(data, offset)
        values.append(value)
    return values


def signed_init_summary(data: bytes) -> dict[str, Any]:
    packet = protobuf_fields(data)
    signed = protobuf_fields(as_bytes(one(packet, 2)))
    command = protobuf_fields(as_bytes(one(signed, 1)))
    init = protobuf_fields(as_bytes(one(command, 2)))
    sd_req: list[int] = []
    for value in init.get(3, []):
        sd_req.extend(packed_varints(value) if isinstance(value, bytes) else [value])
    hash_fields = protobuf_fields(as_bytes(one(init, 8)))
    signature = as_bytes(one(signed, 3))
    return {
        "opcode": as_int(one(command, 1)),
        "firmware_version": as_int(one(init, 1)),
        "hardware_version_raw": as_int(one(init, 2)),
        "softdevice_requirements": [f"0x{value:04x}" for value in sd_req],
        "firmware_type_raw": as_int(one(init, 4)),
        "softdevice_size": as_int(one(init, 5)),
        "bootloader_size": as_int(one(init, 6)),
        "application_size": as_int(one(init, 7)),
        "hash_type_raw": as_int(one(hash_fields, 1)),
        "hash_hex": as_bytes(one(hash_fields, 2)).hex(),
        "debug": bool(as_int(one(init, 9))),
        "signature_type_raw": as_int(one(signed, 2)),
        "signature_bytes": len(signature),
    }


def vector_summary(data: bytes, load_base: int | None) -> dict[str, Any]:
    if len(data) < 8:
        raise ValueError("firmware image is too short for a Cortex-M vector table")
    stack_pointer, reset_vector = struct.unpack_from("<II", data)
    reset_entry = reset_vector & ~1
    nrf52_target = None
    if 0x20020000 < stack_pointer <= 0x20040000:
        # In the nRF52 family, only nRF52840 provides 256 KiB RAM. The next-largest nRF52833
        # ends at 0x20020000, below this image's initial stack pointer.
        nrf52_target = "nRF52840"
    summary: dict[str, Any] = {
        "image_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "initial_stack_pointer": f"0x{stack_pointer:08x}",
        "reset_vector_thumb": f"0x{reset_vector:08x}",
        "reset_entry": f"0x{reset_entry:08x}",
        "minimum_ram_offset_bytes": stack_pointer - 0x20000000,
        "nrf52_target_from_ram_map": nrf52_target,
    }
    if load_base is not None:
        summary["load_base"] = f"0x{load_base:08x}"
        summary["image_end"] = f"0x{load_base + len(data):08x}"
    return summary


def package_summary(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))
        component_name, component = next(iter(manifest["manifest"].items()))
        bin_name = component["bin_file"]
        dat_name = component["dat_file"]
        if bin_name not in names or dat_name not in names:
            raise ValueError("manifest component files are missing from archive")
        binary = archive.read(bin_name)
        init_packet = archive.read(dat_name)
    init_summary = signed_init_summary(init_packet)
    softdevice_requirements = init_summary["softdevice_requirements"]
    load_base = None
    load_base_evidence = None
    if component_name == "softdevice":
        load_base = 0x1000
        load_base_evidence = "Nordic Secure DFU SoftDevice binary convention"
    elif component_name == "application" and softdevice_requirements == ["0x0100"]:
        load_base = 0x27000
        load_base_evidence = "S140 7.2.0 firmware ID 0x0100 flash reservation"
    binary_sha256 = hashlib.sha256(binary).hexdigest()
    init_hash_reversed = bytes.fromhex(init_summary["hash_hex"])[::-1].hex()
    result = {
        "package": str(path),
        "component": component_name,
        "vector": vector_summary(binary, load_base),
        "signed_init": init_summary,
        "init_hash_matches_binary_sha256_after_byte_reversal": (
            init_hash_reversed == binary_sha256
        ),
        "signature_verified": False,
    }
    if load_base_evidence is not None:
        result["load_base_evidence"] = load_base_evidence
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packages", nargs="+", type=Path)
    args = parser.parse_args()
    print(json.dumps([package_summary(path) for path in args.packages], indent=2))


if __name__ == "__main__":
    main()
