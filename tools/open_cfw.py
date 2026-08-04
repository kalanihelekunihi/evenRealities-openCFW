#!/usr/bin/env python3
"""Build, split, and validate the first blob-backed Even Realities G2 openCFW.

The tool intentionally separates three address domains:

* offsets in the outer EVENOTA transport container;
* offsets inside a component payload; and
* physical or logical target addresses used when a controller installs bytes.

Unknown target addresses stay unknown. They are never inferred from package
ordering or EVENOTA offsets.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


EVENOTA_MAGIC = b"EVENOTA\0"
EVENOTA_TOC_OFFSET = 0x40
EVENOTA_TOC_ENTRY_SIZE = 0x10
EVENOTA_TOC_TRAILER = b"evenota\0" + b"\0" * 8
EVENOTA_COMPONENT_HEADER_SIZE = 0x80
EVENOTA_COMPONENT_MAGIC = 0x4E455645
MAIN_RUN_BASE = 0x00438000
MAIN_UPDATE_FLAG = 0x007FE000
CASE_RUN_BASE = 0x08000000

#: The canonical reviewed macOS toolchain profile.  Its pins are the
#: manifest's own top-level ``provider.size``/``provider.sha256`` and
#: ``package.expected_size``/``package.expected_sha256``, which stay
#: byte-identical to the Apple-clang reference.  Alternate reproducible
#: toolchains (for example a Linux Homebrew clang) carry their own
#: independently recorded, fail-closed pins under a ``profiles`` map on the
#: source-build provider and on the package.  Compiler-independent official
#: blobs are never given profile overrides.
DEFAULT_TOOLCHAIN_PROFILE = "apple-clang"


def resolve_toolchain_profile_id(explicit: str | None) -> str:
    """Return the active toolchain profile id.

    Falls back to the ``OPENCFW_TOOLCHAIN_PROFILE`` environment variable and
    finally to the canonical reference profile.
    """

    return (
        explicit
        or os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
        or DEFAULT_TOOLCHAIN_PROFILE
    )


def profile_pins(record: dict[str, Any], profile_id: str) -> dict[str, Any] | None:
    """Return the per-profile pin override for a provider or package record.

    The canonical profile always uses the record's own top-level pins, so this
    returns ``None`` for it.  A named profile returns its ``profiles[id]``
    object when present, otherwise ``None`` (the caller then falls back to the
    top-level pins, which fail closed unless the build is recording).
    """

    if profile_id == DEFAULT_TOOLCHAIN_PROFILE:
        return None
    profiles = record.get("profiles")
    if not isinstance(profiles, dict):
        return None
    override = profiles.get(profile_id)
    if override is None:
        return None
    if not isinstance(override, dict):
        raise OpenCFWError(
            f"profile override {profile_id!r} must be an object"
        )
    return override


class OpenCFWError(RuntimeError):
    """A manifest, integrity, or layout contract was violated."""


@dataclass(frozen=True)
class PackageEntry:
    entry_id: int
    type_id: int
    filename: str
    storage_type: int
    offset: int
    entry_size: int
    payload_size: int
    checksum: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_crc32c_msb_table() -> tuple[int, ...]:
    table: list[int] = []
    for byte in range(256):
        crc = byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x1EDC6F41) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        table.append(crc)
    return tuple(table)


CRC32C_MSB_TABLE = build_crc32c_msb_table()


def crc32c_msb(data: bytes) -> int:
    """CRC-32C/Castagnoli, non-reflected, init=0, xorout=0."""
    crc = 0
    for byte in data:
        crc = (
            ((crc << 8) & 0xFFFFFFFF)
            ^ CRC32C_MSB_TABLE[((crc >> 24) ^ byte) & 0xFF]
        )
    return crc


def crc32c_reflected(data: bytes) -> int:
    """CRC-32C/Castagnoli, reflected, init/xorout=0xffffffff."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0x82F63B78 if crc & 1 else crc >> 1
    return crc ^ 0xFFFFFFFF


def u32le(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise OpenCFWError(f"word at 0x{offset:x} exceeds a {len(data)}-byte payload")
    return struct.unpack_from("<I", data, offset)[0]


def u32be(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise OpenCFWError(f"word at 0x{offset:x} exceeds a {len(data)}-byte payload")
    return struct.unpack_from(">I", data, offset)[0]


def c_string(data: bytes, start: int, end: int) -> str:
    try:
        return data[start:end].split(b"\0", 1)[0].decode("ascii")
    except UnicodeDecodeError as error:
        raise OpenCFWError("non-ASCII string in EVENOTA metadata") from error


def fixed_ascii(value: str, size: int, field_name: str) -> bytes:
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise OpenCFWError(f"{field_name} must be ASCII") from error
    if len(encoded) > size:
        raise OpenCFWError(f"{field_name} exceeds {size} bytes")
    return encoded.ljust(size, b"\0")


def hex_address(value: int) -> str:
    return f"0x{value:08X}"


def merge_manifest(
    base: dict[str, Any],
    overlay: dict[str, Any],
) -> dict[str, Any]:
    """Apply a derived build profile without duplicating its base manifest."""
    merged = copy.deepcopy(base)
    for key, value in overlay.items():
        if key in ("extends", "component_overrides"):
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key].update(copy.deepcopy(value))
        else:
            merged[key] = copy.deepcopy(value)

    overrides = overlay.get("component_overrides", {})
    if not isinstance(overrides, dict):
        raise OpenCFWError("component_overrides must be an object")
    by_name = {component["name"]: component for component in merged["components"]}
    for name, component_overlay in overrides.items():
        if name not in by_name:
            raise OpenCFWError(f"component override names unknown component: {name}")
        if not isinstance(component_overlay, dict):
            raise OpenCFWError(f"component override for {name} must be an object")
        component = by_name[name]
        for key, value in component_overlay.items():
            if isinstance(value, dict) and isinstance(component.get(key), dict):
                component[key].update(copy.deepcopy(value))
            else:
                component[key] = copy.deepcopy(value)
    return merged


def load_manifest(
    path: Path,
    loading: tuple[Path, ...] = (),
) -> dict[str, Any]:
    path = path.resolve()
    if path in loading:
        chain = " -> ".join(str(item) for item in (*loading, path))
        raise OpenCFWError(f"manifest inheritance cycle: {chain}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OpenCFWError(f"cannot read manifest {path}: {error}") from error
    if manifest.get("schema_version") != 1:
        raise OpenCFWError("only manifest schema version 1 is supported")

    extends = manifest.get("extends")
    if extends is not None:
        if not isinstance(extends, str) or not extends:
            raise OpenCFWError("extends must be a nonempty relative path")
        parent_path = (path.parent / extends).resolve()
        try:
            parent_path.relative_to(path.parent.resolve())
        except ValueError as error:
            raise OpenCFWError("extends must remain in the manifests directory") from error
        parent = load_manifest(parent_path, (*loading, path))
        manifest = merge_manifest(parent, manifest)

    if manifest.get("package", {}).get("format") != "EVENOTA":
        raise OpenCFWError("manifest does not describe an EVENOTA package")
    components = manifest.get("components")
    if not isinstance(components, list) or not components:
        raise OpenCFWError("manifest must contain at least one component")
    return manifest


def project_root_for_manifest(manifest_path: Path) -> Path:
    return manifest_path.resolve().parent.parent


def resolve_below(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise OpenCFWError(f"path escapes openCFW root: {relative}") from error
    return candidate


def effective_component_regions(
    component: dict[str, Any],
    data_len: int,
    toolchain_profile: str,
) -> list[dict[str, Any]]:
    """Regions to tile/split for the active toolchain profile.

    Under a non-canonical toolchain the compiler-owned appended source overlay
    changes size, so its detailed per-function regions no longer tile the
    component.  The trailing regions at or above ``source_appended_boundary``
    are collapsed into a single coarse source-compiled region sized to the
    actual component.  Compiler-independent base regions (opaque spans,
    fixed-address in-place leaves, and fixed-size redirects, whose bytes may
    differ but whose sizes do not) are unchanged, so the flash map for stock
    code stays exact.
    """

    regions = component["regions"]
    boundary = component.get("source_appended_boundary")
    if toolchain_profile == DEFAULT_TOOLCHAIN_PROFILE or not isinstance(
        boundary, int
    ):
        return regions
    base = [region for region in regions if region["file_offset"] < boundary]
    tail = sorted(
        (region for region in regions if region["file_offset"] >= boundary),
        key=lambda region: region["file_offset"],
    )
    if not tail or tail[0]["file_offset"] != boundary:
        raise OpenCFWError(
            f"{component['name']}: source_appended_boundary {boundary} does "
            "not begin an appended-source region"
        )
    if data_len <= boundary:
        raise OpenCFWError(
            f"{component['name']}: component is not longer than its appended "
            f"boundary {boundary}"
        )
    head = tail[0]
    coarse: dict[str, Any] = {
        "name": f"{component['name']}_source_appended",
        "function": (
            "Toolchain-profile compiled source overlay (coarse mapping; the "
            "canonical apple-clang profile retains the per-function breakdown)"
        ),
        "file_offset": boundary,
        "size": data_len - boundary,
        "address_status": "source_compiled",
        "output": head["output"],
    }
    for key in ("target", "target_address"):
        if key in head:
            coarse[key] = head[key]
    return base + [coarse]


def read_providers(
    manifest: dict[str, Any],
    project_root: Path,
    *,
    toolchain_profile: str = DEFAULT_TOOLCHAIN_PROFILE,
    record: bool = False,
    recorded_providers: dict[str, dict[str, Any]] | None = None,
) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    seen_entry_ids: set[int] = set()
    seen_names: set[str] = set()
    for component in manifest["components"]:
        name = component.get("name")
        entry_id = component.get("entry_id")
        if not isinstance(name, str) or not name:
            raise OpenCFWError("every component requires a nonempty name")
        if name in seen_names:
            raise OpenCFWError(f"duplicate component name: {name}")
        if not isinstance(entry_id, int) or entry_id < 1 or entry_id in seen_entry_ids:
            raise OpenCFWError(f"invalid or duplicate entry_id for {name}")
        seen_names.add(name)
        seen_entry_ids.add(entry_id)

        provider = component.get("provider", {})
        if provider.get("kind") not in ("official_blob", "source_build"):
            raise OpenCFWError(f"{name}: unsupported provider kind")
        provider_path = provider.get("path")
        if not isinstance(provider_path, str):
            raise OpenCFWError(f"{name}: provider path is missing")
        path = resolve_below(project_root, provider_path)
        try:
            data = path.read_bytes()
        except OSError as error:
            raise OpenCFWError(f"{name}: cannot read {path}: {error}") from error
        override = profile_pins(provider, toolchain_profile)
        if override is not None:
            expected_size = override.get("size")
            expected_sha256 = override.get("sha256")
        else:
            expected_size = provider.get("size")
            expected_sha256 = provider.get("sha256")
        actual_sha256 = sha256_bytes(data)
        is_source_build = provider.get("kind") == "source_build"
        if record and is_source_build:
            # Recording a non-canonical toolchain: capture the observed
            # compiled component pins rather than enforcing the reviewed ones.
            if recorded_providers is not None:
                recorded_providers[name] = {
                    "size": len(data),
                    "sha256": actual_sha256,
                }
        else:
            if len(data) != expected_size:
                raise OpenCFWError(
                    f"{name}: provider size is {len(data)}, expected "
                    f"{expected_size} (profile {toolchain_profile})"
                )
            if actual_sha256 != expected_sha256:
                raise OpenCFWError(
                    f"{name}: SHA-256 {actual_sha256} does not match "
                    f"{expected_sha256} (profile {toolchain_profile})"
                )
        validate_component_payload(component, data)
        validate_region_partition(component, data, toolchain_profile)
        payloads[name] = data
    return payloads


def plausible_vector(
    data: bytes,
    *,
    vector_offset: int,
    image_base: int,
    image_size: int,
    sram_end: int = 0x3FFFFFFF,
) -> None:
    initial_sp = u32le(data, vector_offset)
    reset_handler = u32le(data, vector_offset + 4)
    handler = reset_handler & ~1
    if not 0x20000000 <= initial_sp <= sram_end or initial_sp % 4:
        raise OpenCFWError(f"implausible initial SP {hex_address(initial_sp)}")
    if reset_handler & 1 == 0:
        raise OpenCFWError("reset vector is not a Thumb address")
    if not image_base <= handler < image_base + image_size:
        raise OpenCFWError(
            f"reset vector {hex_address(reset_handler)} is outside the image"
        )


def validate_codec(data: bytes) -> None:
    if len(data) < 0x30 or data[:4] != b"FWPK":
        raise OpenCFWError("codec payload is not the reviewed FWPK format")
    count = u32le(data, 8)
    if not 1 <= count <= 16 or 0x10 + count * 0x10 > len(data):
        raise OpenCFWError("codec segment count is invalid")
    next_offset = 0x10 + count * 0x10
    for index in range(count):
        base = 0x10 + index * 0x10
        _, size, offset, expected_crc = struct.unpack_from("<IIII", data, base)
        if offset != next_offset or offset + size > len(data):
            raise OpenCFWError(f"codec segment {index + 1} is not contiguous")
        actual_crc = zlib.crc32(data[offset:offset + size]) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise OpenCFWError(f"codec segment {index + 1} CRC-32 is invalid")
        next_offset += size
    if next_offset != len(data):
        raise OpenCFWError("codec segment table does not close at EOF")


def validate_em9305(data: bytes) -> None:
    if len(data) < 0x10:
        raise OpenCFWError("EM9305 payload is too short")
    record_bytes = u32le(data, 4)
    count = u32le(data, 8)
    if not 1 <= count <= 64 or 0x10 + count * 0x0C > len(data):
        raise OpenCFWError("EM9305 record count is invalid")
    next_offset: int | None = None
    total = 0
    last_address = -1
    for index in range(count):
        file_offset, size, address = struct.unpack_from(
            "<III", data, 0x10 + index * 0x0C
        )
        if index == 0:
            next_offset = file_offset
        if file_offset != next_offset or file_offset + size > len(data):
            raise OpenCFWError(f"EM9305 record {index} is not contiguous")
        if address <= last_address:
            raise OpenCFWError("EM9305 target records are not ordered")
        next_offset = file_offset + size
        total += size
        last_address = address
    if next_offset != len(data) or total != record_bytes:
        raise OpenCFWError("EM9305 records do not match their declared size")


def validate_touch(data: bytes) -> None:
    if len(data) < 0x28 or data[:4] != b"FWPK":
        raise OpenCFWError("touch payload is not FWPK")
    size = u32le(data, 0x14)
    offset = u32le(data, 0x18)
    expected_crc = u32le(data, 0x1C)
    if offset != 0x20 or offset + size != len(data):
        raise OpenCFWError("touch FWPK span is invalid")
    if crc32c_reflected(data[offset:]) != expected_crc:
        raise OpenCFWError("touch application CRC-32C is invalid")
    plausible_vector(data, vector_offset=offset, image_base=0, image_size=size)


def case_additive_sum(raw_image: bytes) -> int:
    padded = raw_image + b"\0" * ((-len(raw_image)) % 4)
    if not padded:
        return 0
    words = struct.unpack(f">{len(padded) // 4}I", padded)
    return sum(words) & 0xFFFFFFFF


def validate_case(data: bytes) -> None:
    if len(data) < 0x28 or data[:4] != b"EVEN":
        raise OpenCFWError("case payload is not an EVEN-wrapped image")
    size = u32be(data, 8)
    expected_sum = u32be(data, 12)
    if size != len(data) - 0x20:
        raise OpenCFWError("case wrapper size is invalid")
    raw = data[0x20:]
    if case_additive_sum(raw) != expected_sum:
        raise OpenCFWError("case additive checksum is invalid")
    plausible_vector(
        raw,
        vector_offset=0,
        image_base=CASE_RUN_BASE,
        image_size=len(raw),
        sram_end=0x2002FFFF,
    )


def validate_apollo_bootloader(data: bytes) -> None:
    if not data:
        raise OpenCFWError("Apollo bootloader is empty")
    if 0x00410000 + len(data) > MAIN_RUN_BASE:
        raise OpenCFWError("Apollo bootloader overlaps the main application")
    plausible_vector(
        data,
        vector_offset=0,
        image_base=0x00410000,
        image_size=len(data),
        sram_end=0x2007FFFF,
    )


def validate_apollo_main(data: bytes) -> None:
    if len(data) < 0x28:
        raise OpenCFWError("Apollo main payload is too short")
    word_0 = u32le(data, 0)
    declared_size = word_0 & 0x00FFFFFF
    flags = word_0 >> 24
    if declared_size != len(data) or flags != 0x04:
        raise OpenCFWError("Apollo main preamble size or flags are invalid")
    if any(u32le(data, offset) != 0 for offset in (0x08, 0x0C, 0x18, 0x1C)):
        raise OpenCFWError("Apollo main reserved preamble words are nonzero")
    if u32le(data, 0x10) != 0xCB or u32le(data, 0x14) != MAIN_RUN_BASE:
        raise OpenCFWError("Apollo main type or run address is invalid")
    if u32le(data, 4) != zlib.crc32(data[8:]) & 0xFFFFFFFF:
        raise OpenCFWError("Apollo main nested CRC-32 is invalid")
    installed_size = len(data) - 0x20
    if MAIN_RUN_BASE + installed_size > MAIN_UPDATE_FLAG:
        raise OpenCFWError("Apollo main overlaps the bootloader update flag")
    plausible_vector(
        data,
        vector_offset=0x20,
        image_base=MAIN_RUN_BASE,
        image_size=installed_size,
        sram_end=0x2007FFFF,
    )


def validate_component_payload(component: dict[str, Any], data: bytes) -> None:
    name = component["name"]
    validators = {
        "codec": validate_codec,
        "ble_em9305": validate_em9305,
        "touch": validate_touch,
        "case": validate_case,
        "apollo_bootloader": validate_apollo_bootloader,
        "apollo_main": validate_apollo_main,
    }
    validator = validators.get(name)
    if validator is None:
        raise OpenCFWError(f"{name}: no component validator is defined")
    try:
        validator(data)
    except OpenCFWError as error:
        raise OpenCFWError(f"{name}: {error}") from error


def validate_region_partition(
    component: dict[str, Any],
    data: bytes,
    toolchain_profile: str = DEFAULT_TOOLCHAIN_PROFILE,
) -> None:
    base_regions = component.get("regions")
    if not isinstance(base_regions, list) or not base_regions:
        raise OpenCFWError(f"{component['name']}: no split regions are defined")
    regions = effective_component_regions(component, len(data), toolchain_profile)
    expected_offset = 0
    outputs: set[str] = set()
    for region in sorted(regions, key=lambda item: item.get("file_offset", -1)):
        offset = region.get("file_offset")
        size = region.get("size")
        output = region.get("output")
        if not isinstance(offset, int) or not isinstance(size, int) or size <= 0:
            raise OpenCFWError(f"{component['name']}: invalid region span")
        if offset != expected_offset:
            raise OpenCFWError(
                f"{component['name']}: region partition has a gap or overlap at "
                f"0x{expected_offset:x}"
            )
        if not isinstance(output, str) or output in outputs:
            raise OpenCFWError(f"{component['name']}: invalid or duplicate output")
        outputs.add(output)
        expected_offset += size
    if expected_offset != len(data):
        raise OpenCFWError(
            f"{component['name']}: regions cover {expected_offset} of {len(data)} bytes"
        )


def spans_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return start_a < end_b and start_b < end_a


def validate_flash_layout(manifest: dict[str, Any]) -> None:
    placed: dict[str, list[tuple[int, int, str]]] = {}
    protected_regions = manifest.get("protected_regions", [])
    for component in manifest["components"]:
        for region in component["regions"]:
            address = region.get("target_address")
            target = region.get("target")
            if address is None:
                continue
            if not isinstance(address, int) or address < 0 or not isinstance(target, str):
                raise OpenCFWError(f"{component['name']}/{region['name']}: bad address")
            end = address + region["size"]
            for other_start, other_end, other_name in placed.setdefault(target, []):
                if spans_overlap(address, end, other_start, other_end):
                    raise OpenCFWError(
                        f"flash overlap on {target}: {component['name']}/"
                        f"{region['name']} conflicts with {other_name}"
                    )
            placed[target].append(
                (address, end, f"{component['name']}/{region['name']}")
            )
            for protected in protected_regions:
                if protected["target"] != target:
                    continue
                if spans_overlap(
                    address,
                    end,
                    protected["start"],
                    protected["end_exclusive"],
                ):
                    raise OpenCFWError(
                        f"{component['name']}/{region['name']} overlaps protected "
                        f"region {protected['name']}"
                    )
            for alternate in region.get("alternate_target_addresses", []):
                if not isinstance(alternate, int) or alternate < 0:
                    raise OpenCFWError(
                        f"{component['name']}/{region['name']}: bad alternate address"
                    )
                alternate_end = alternate + region["size"]
                for other_start, other_end, other_name in placed[target]:
                    if spans_overlap(
                        alternate,
                        alternate_end,
                        other_start,
                        other_end,
                    ):
                        raise OpenCFWError(
                            f"flash overlap on {target}: alternate placement for "
                            f"{component['name']}/{region['name']} conflicts with "
                            f"{other_name}"
                        )
                for protected in protected_regions:
                    if protected["target"] != target:
                        continue
                    if spans_overlap(
                        alternate,
                        alternate_end,
                        protected["start"],
                        protected["end_exclusive"],
                    ):
                        raise OpenCFWError(
                            f"alternate placement for {component['name']}/"
                            f"{region['name']} overlaps protected region "
                            f"{protected['name']}"
                        )
                placed[target].append(
                    (
                        alternate,
                        alternate_end,
                        f"{component['name']}/{region['name']} alternate",
                    )
                )


def verify_manifest(
    manifest_path: Path,
    *,
    toolchain_profile: str | None = None,
    record: bool = False,
    recorded_providers: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], Path, dict[str, bytes]]:
    toolchain_profile = resolve_toolchain_profile_id(toolchain_profile)
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    project_root = project_root_for_manifest(manifest_path)
    payloads = read_providers(
        manifest,
        project_root,
        toolchain_profile=toolchain_profile,
        record=record,
        recorded_providers=recorded_providers,
    )
    validate_flash_layout(manifest)
    return manifest, project_root, payloads


def component_header(component: dict[str, Any], payload: bytes) -> bytes:
    checksum = crc32c_msb(payload)
    prefix = struct.pack(
        "<IIIIIIIIIIII",
        0,
        0,
        len(payload),
        checksum,
        0,
        EVENOTA_COMPONENT_MAGIC,
        0xFFFFFFFF,
        0xFFFFFFFF,
        0,
        component["type_id"],
        component["storage_type"],
        0xFFFFFFFF,
    )
    filename = fixed_ascii(
        component["package_filename"],
        EVENOTA_COMPONENT_HEADER_SIZE - len(prefix),
        "component filename",
    )
    return prefix + filename


def assemble_evenota(
    manifest: dict[str, Any],
    payloads: dict[str, bytes],
) -> tuple[bytes, list[PackageEntry]]:
    components = manifest["components"]
    package = manifest["package"]
    header = bytearray()
    header.extend(EVENOTA_MAGIC)
    header.extend(struct.pack("<II", len(components), 0))
    header.extend(fixed_ascii(package["build_date"], 16, "build date"))
    header.extend(fixed_ascii(package["build_time"], 16, "build time"))
    header.extend(fixed_ascii(package["version"], 16, "version"))
    if len(header) != EVENOTA_TOC_OFFSET:
        raise OpenCFWError("internal EVENOTA header size error")

    entries: list[PackageEntry] = []
    offset = (
        EVENOTA_TOC_OFFSET
        + len(components) * EVENOTA_TOC_ENTRY_SIZE
        + len(EVENOTA_TOC_TRAILER)
    )
    bodies: list[bytes] = []
    for component in components:
        payload = payloads[component["name"]]
        header_bytes = component_header(component, payload)
        body = header_bytes + payload
        checksum = crc32c_msb(payload)
        entries.append(
            PackageEntry(
                entry_id=component["entry_id"],
                type_id=component["type_id"],
                filename=component["package_filename"],
                storage_type=component["storage_type"],
                offset=offset,
                entry_size=len(body),
                payload_size=len(payload),
                checksum=checksum,
            )
        )
        bodies.append(body)
        offset += len(body)

    toc = b"".join(
        struct.pack(
            "<IIII",
            entry.entry_id,
            entry.offset,
            entry.entry_size,
            entry.checksum,
        )
        for entry in entries
    )
    image = bytes(header) + toc + EVENOTA_TOC_TRAILER + b"".join(bodies)
    validate_evenota_image(image, manifest)
    return image, entries


def validate_evenota_image(image: bytes, manifest: dict[str, Any]) -> None:
    if len(image) < EVENOTA_TOC_OFFSET or image[:8] != EVENOTA_MAGIC:
        raise OpenCFWError("assembled image lacks EVENOTA magic")
    count = u32le(image, 8)
    components = manifest["components"]
    if count != len(components):
        raise OpenCFWError("assembled image entry count is wrong")
    package = manifest["package"]
    if c_string(image, 0x10, 0x20) != package["build_date"]:
        raise OpenCFWError("assembled build date changed")
    if c_string(image, 0x20, 0x30) != package["build_time"]:
        raise OpenCFWError("assembled build time changed")
    if c_string(image, 0x30, 0x40) != package["version"]:
        raise OpenCFWError("assembled version changed")

    toc_end = EVENOTA_TOC_OFFSET + count * EVENOTA_TOC_ENTRY_SIZE
    if image[toc_end:toc_end + len(EVENOTA_TOC_TRAILER)] != EVENOTA_TOC_TRAILER:
        raise OpenCFWError("assembled TOC trailer is invalid")
    expected_offset = toc_end + len(EVENOTA_TOC_TRAILER)
    for index, component in enumerate(components):
        entry_id, offset, entry_size, toc_checksum = struct.unpack_from(
            "<IIII", image, EVENOTA_TOC_OFFSET + index * EVENOTA_TOC_ENTRY_SIZE
        )
        if entry_id != component["entry_id"] or offset != expected_offset:
            raise OpenCFWError(f"assembled TOC entry {index + 1} is invalid")
        if offset + entry_size > len(image) or entry_size < EVENOTA_COMPONENT_HEADER_SIZE:
            raise OpenCFWError(f"assembled entry {index + 1} exceeds the package")
        header = image[offset:offset + EVENOTA_COMPONENT_HEADER_SIZE]
        payload = image[offset + EVENOTA_COMPONENT_HEADER_SIZE:offset + entry_size]
        if u32le(header, 8) != len(payload):
            raise OpenCFWError(f"assembled entry {index + 1} size is invalid")
        if u32le(header, 12) != toc_checksum or crc32c_msb(payload) != toc_checksum:
            raise OpenCFWError(f"assembled entry {index + 1} checksum is invalid")
        if (
            u32le(header, 0x14) != EVENOTA_COMPONENT_MAGIC
            or u32le(header, 0x24) != component["type_id"]
            or u32le(header, 0x28) != component["storage_type"]
            or c_string(header, 0x30, 0x80) != component["package_filename"]
        ):
            raise OpenCFWError(f"assembled entry {index + 1} metadata is invalid")
        if (
            u32le(header, 0x00) != 0
            or u32le(header, 0x04) != 0
            or u32le(header, 0x10) != 0
            or u32le(header, 0x18) != 0xFFFFFFFF
            or u32le(header, 0x1C) != 0xFFFFFFFF
            or u32le(header, 0x20) != 0
            or u32le(header, 0x2C) != 0xFFFFFFFF
        ):
            raise OpenCFWError(
                f"assembled entry {index + 1} reserved metadata is invalid"
            )
        expected_offset += entry_size
    if expected_offset != len(image):
        raise OpenCFWError("assembled package does not close exactly at EOF")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    atomic_write(path, encoded)


def clean_build_dir(project_root: Path, build_dir: Path) -> None:
    resolved_root = project_root.resolve()
    resolved_build = build_dir.resolve()
    try:
        relative = resolved_build.relative_to(resolved_root)
    except ValueError as error:
        raise OpenCFWError("build directory must remain below openCFW") from error
    if not relative.parts or relative.parts[0] != "build":
        raise OpenCFWError("refusing to clean anything except openCFW/build")
    if resolved_build.exists():
        shutil.rmtree(resolved_build)


def split_regions(
    manifest: dict[str, Any],
    payloads: dict[str, bytes],
    build_dir: Path,
    toolchain_profile: str = DEFAULT_TOOLCHAIN_PROFILE,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    flash_regions: list[dict[str, Any]] = []
    unresolved_regions: list[dict[str, Any]] = []
    container_regions: list[dict[str, Any]] = []
    regions_root = build_dir / "regions"
    for component in manifest["components"]:
        payload = payloads[component["name"]]
        for region in effective_component_regions(
            component, len(payload), toolchain_profile
        ):
            start = region["file_offset"]
            end = start + region["size"]
            region_data = payload[start:end]
            output_path = resolve_below(regions_root, region["output"])
            atomic_write(output_path, region_data)
            record: dict[str, Any] = {
                "component": component["name"],
                "region": region["name"],
                "function": region["function"],
                "component_file_offset": start,
                "size": len(region_data),
                "sha256": sha256_bytes(region_data),
                "artifact": str(output_path.relative_to(build_dir)),
                "address_status": region["address_status"],
            }
            if "target_address" in region:
                address = region["target_address"]
                record.update(
                    {
                        "target": region["target"],
                        "target_address": address,
                        "target_address_hex": hex_address(address),
                        "end_exclusive": address + len(region_data),
                        "end_exclusive_hex": hex_address(address + len(region_data)),
                    }
                )
                if region.get("alternate_target_addresses"):
                    record["alternate_target_addresses"] = [
                        {
                            "address": alternate,
                            "address_hex": hex_address(alternate),
                            "end_exclusive": alternate + len(region_data),
                            "end_exclusive_hex": hex_address(
                                alternate + len(region_data)
                            ),
                        }
                        for alternate in region["alternate_target_addresses"]
                    ]
                flash_regions.append(record)
            elif region["address_status"] == "unknown":
                unresolved_regions.append(record)
            else:
                container_regions.append(record)
    return flash_regions, unresolved_regions, container_regions


def package_entry_report(entries: Iterable[PackageEntry]) -> list[dict[str, Any]]:
    return [
        {
            "entry_id": entry.entry_id,
            "type_id": entry.type_id,
            "filename": entry.filename,
            "storage_type": entry.storage_type,
            "package_offset": entry.offset,
            "package_offset_hex": hex_address(entry.offset),
            "entry_size": entry.entry_size,
            "payload_size": entry.payload_size,
            "crc32c_msb": f"0x{entry.checksum:08X}",
        }
        for entry in entries
    ]


def write_sha256s(build_dir: Path) -> None:
    paths = sorted(
        path
        for path in build_dir.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    )
    lines = [
        f"{sha256_file(path)}  {path.relative_to(build_dir)}"
        for path in paths
    ]
    atomic_write(build_dir / "SHA256SUMS", ("\n".join(lines) + "\n").encode())


def record_manifest_profile_pins(
    manifest_path: Path,
    profile_id: str,
    provider_pins: dict[str, dict[str, Any]],
    package_pins: dict[str, Any],
) -> None:
    """Persist observed source-build provider and package pins for a profile.

    The manifest's canonical top-level pins are never touched.  Recorded pins
    are written under a ``profiles`` map on each source-build provider and on
    the package.  The write preserves the hand-authored key order so the diff
    stays minimal.  Provider records are located in ``component_overrides``
    first (the ``extends`` layout) and then in a flat ``components`` list.
    """

    if profile_id == DEFAULT_TOOLCHAIN_PROFILE:
        raise OpenCFWError(
            "cannot record the canonical apple-clang profile; its pins are "
            "the reviewed reference"
        )
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    package = data.setdefault("package", {})
    package.setdefault("profiles", {})[profile_id] = {
        "expected_size": package_pins["expected_size"],
        "expected_sha256": package_pins["expected_sha256"],
    }

    def provider_for(name: str) -> dict[str, Any] | None:
        overrides = data.get("component_overrides")
        if isinstance(overrides, dict):
            component = overrides.get(name)
            if isinstance(component, dict) and isinstance(
                component.get("provider"), dict
            ):
                return component["provider"]
        for component in data.get("components", []):
            if (
                isinstance(component, dict)
                and component.get("name") == name
                and isinstance(component.get("provider"), dict)
            ):
                return component["provider"]
        return None

    for name, pins in provider_pins.items():
        provider = provider_for(name)
        if provider is None:
            raise OpenCFWError(
                f"cannot record provider pins for {name!r}: no source-build "
                "provider found in the manifest file"
            )
        provider.setdefault("profiles", {})[profile_id] = {
            "size": pins["size"],
            "sha256": pins["sha256"],
        }

    atomic_write(
        manifest_path,
        (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    )


def build(
    manifest_path: Path,
    build_dir: Path,
    *,
    toolchain_profile: str | None = None,
    record_profile: bool = False,
) -> dict[str, Any]:
    toolchain_profile = resolve_toolchain_profile_id(toolchain_profile)
    manifest_path = manifest_path.resolve()
    build_dir = build_dir.resolve()
    recorded_providers: dict[str, dict[str, Any]] = {}
    manifest, project_root, payloads = verify_manifest(
        manifest_path,
        toolchain_profile=toolchain_profile,
        record=record_profile,
        recorded_providers=recorded_providers,
    )
    clean_build_dir(project_root, build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    image, entries = assemble_evenota(manifest, payloads)
    package_path = build_dir / "package" / manifest["package"]["output_name"]
    atomic_write(package_path, image)
    package_sha256 = sha256_bytes(image)
    package_override = profile_pins(manifest["package"], toolchain_profile)
    if package_override is not None:
        expected_sha256 = package_override.get("expected_sha256")
        expected_size = package_override.get("expected_size")
    else:
        expected_sha256 = manifest["package"].get("expected_sha256")
        expected_size = manifest["package"].get("expected_size")
    if record_profile:
        record_manifest_profile_pins(
            manifest_path,
            toolchain_profile,
            recorded_providers,
            {"expected_size": len(image), "expected_sha256": package_sha256},
        )
        expected_size = len(image)
        expected_sha256 = package_sha256
    if expected_size is not None and len(image) != expected_size:
        raise OpenCFWError(
            "assembly size differs from the pinned reference "
            f"(profile {toolchain_profile})"
        )
    if expected_sha256 is not None and package_sha256 != expected_sha256:
        raise OpenCFWError(
            "assembly hash differs from the pinned reference "
            f"(profile {toolchain_profile})"
        )
    reference_match: bool | None = (
        package_sha256 == expected_sha256 and len(image) == expected_size
        if expected_sha256 is not None and expected_size is not None
        else None
    )

    flash_regions, unresolved, container = split_regions(
        manifest,
        payloads,
        build_dir,
        toolchain_profile,
    )
    flash_plan = {
        "schema_version": 1,
        "target": manifest["target"],
        "package_artifact": str(package_path.relative_to(build_dir)),
        "package_sha256": package_sha256,
        "flash_regions": flash_regions,
        "unresolved_flash_regions": unresolved,
        "container_only_regions": container,
        "protected_regions": [
            {
                **region,
                "start_hex": hex_address(region["start"]),
                "end_exclusive_hex": hex_address(region["end_exclusive"]),
            }
            for region in manifest.get("protected_regions", [])
        ],
        "safety": {
            "automatic_flashing": False,
            "notes": [
                "This plan describes bytes and addresses; it does not authorize a write.",
                "Back up per-device state before any direct-flash experiment.",
                "Ordinary G2 application OTA is single-slot and has no proven rollback.",
                "Never translate EVENOTA package offsets into controller addresses.",
            ],
        },
    }
    atomic_write_json(build_dir / "flash-plan.json", flash_plan)

    report = {
        "schema_version": 1,
        "target": manifest["target"],
        "manifest": str(manifest_path.resolve().relative_to(project_root)),
        "provider_mode": "+".join(
            sorted(
                {
                    component["provider"]["kind"]
                    for component in manifest["components"]
                }
            )
        ),
        "package": {
            "artifact": str(package_path.relative_to(build_dir)),
            "size": len(image),
            "sha256": package_sha256,
            "reference_sha256": expected_sha256,
            "byte_identical_to_reference": reference_match,
        },
        "entries": package_entry_report(entries),
        "placed_region_count": len(flash_regions),
        "unresolved_region_count": len(unresolved),
        "container_region_count": len(container),
    }
    atomic_write_json(build_dir / "build-report.json", report)
    write_sha256s(build_dir)
    return report


def wrap_main_image(raw_image: bytes, run_base: int = MAIN_RUN_BASE) -> bytes:
    total_size = len(raw_image) + 0x20
    if total_size > 0x00FFFFFF:
        raise OpenCFWError("Apollo main image exceeds the 24-bit size field")
    if run_base + len(raw_image) > MAIN_UPDATE_FLAG:
        raise OpenCFWError("Apollo main image would overlap the update flag")
    plausible_vector(
        raw_image,
        vector_offset=0,
        image_base=run_base,
        image_size=len(raw_image),
        sram_end=0x2007FFFF,
    )
    preamble = bytearray(
        struct.pack(
            "<IIIIIIII",
            0x04000000 | total_size,
            0,
            0,
            0,
            0xCB,
            run_base,
            0,
            0,
        )
    )
    payload = preamble + raw_image
    struct.pack_into("<I", payload, 4, zlib.crc32(payload[8:]) & 0xFFFFFFFF)
    return bytes(payload)


def wrap_case_image(
    raw_image: bytes,
    version: tuple[int, int, int] = (1, 2, 57),
) -> bytes:
    if len(raw_image) > 0xFFFFFFFF:
        raise OpenCFWError("case image exceeds its 32-bit size field")
    if any(not 0 <= value <= 0xFF for value in version):
        raise OpenCFWError("case version fields must fit in one byte")
    plausible_vector(
        raw_image,
        vector_offset=0,
        image_base=CASE_RUN_BASE,
        image_size=len(raw_image),
        sram_end=0x2002FFFF,
    )
    header = (
        b"EVEN"
        + bytes((*version, 0))
        + struct.pack(">II", len(raw_image), case_additive_sum(raw_image))
        + b"\0" * 16
    )
    return header + raw_image


def wrap_touch_image(raw_image: bytes) -> bytes:
    plausible_vector(
        raw_image,
        vector_offset=0,
        image_base=0,
        image_size=len(raw_image),
    )
    header = bytearray(
        b"FWPK"
        + bytes.fromhex("01000202")
        + struct.pack("<II", 1, 0)
        + struct.pack(
            "<IIII",
            3,
            len(raw_image),
            0x20,
            crc32c_reflected(raw_image),
        )
    )
    return bytes(header) + raw_image


def parse_version(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("version must be MAJOR.MINOR.PATCH")
    try:
        version = tuple(int(part, 10) for part in parts)
    except ValueError as error:
        raise argparse.ArgumentTypeError("version fields must be decimal") from error
    if any(not 0 <= field <= 255 for field in version):
        raise argparse.ArgumentTypeError("version fields must be between 0 and 255")
    return version  # type: ignore[return-value]


def print_summary(report: dict[str, Any]) -> None:
    package = report["package"]
    print(f"Built {package['artifact']}")
    print(f"  size: {package['size']} bytes")
    print(f"  sha256: {package['sha256']}")
    print(
        "  reference: " + (
            "byte-identical"
            if package["byte_identical_to_reference"] is True
            else (
                "different"
                if package["byte_identical_to_reference"] is False
                else "not pinned"
            )
        )
    )
    print(f"  placed flash regions: {report['placed_region_count']}")
    print(f"  unresolved flash regions: {report['unresolved_region_count']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_manifest = (
        Path(__file__).resolve().parent.parent
        / "manifests"
        / "g2-2.2.6.10.json"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profile_default = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")

    verify_parser = subparsers.add_parser("verify", help="validate all inputs")
    verify_parser.add_argument("--manifest", type=Path, default=default_manifest)
    verify_parser.add_argument(
        "--toolchain-profile",
        default=profile_default,
        help=(
            "reviewed toolchain profile to verify against (default "
            f"{DEFAULT_TOOLCHAIN_PROFILE!r})"
        ),
    )

    build_parser = subparsers.add_parser(
        "build",
        help="assemble EVENOTA and address-split artifacts",
    )
    build_parser.add_argument("--manifest", type=Path, default=default_manifest)
    build_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "build",
    )
    build_parser.add_argument(
        "--toolchain-profile",
        default=profile_default,
        help=(
            "reviewed toolchain profile to build and verify against (default "
            f"{DEFAULT_TOOLCHAIN_PROFILE!r})"
        ),
    )
    build_parser.add_argument(
        "--record-profile",
        action="store_true",
        help=(
            "capture the observed source-build provider and package pins into "
            "the manifest's profiles[<--toolchain-profile>] instead of "
            "enforcing the reviewed ones"
        ),
    )

    wrap_parser = subparsers.add_parser(
        "wrap",
        help="wrap a future raw source-built controller image",
    )
    wrap_parser.add_argument("kind", choices=("main", "case", "touch"))
    wrap_parser.add_argument("input", type=Path)
    wrap_parser.add_argument("output", type=Path)
    wrap_parser.add_argument(
        "--case-version",
        type=parse_version,
        default=(1, 2, 57),
    )

    args = parser.parse_args(argv)
    if args.command == "verify":
        profile_id = resolve_toolchain_profile_id(args.toolchain_profile)
        manifest, _, payloads = verify_manifest(
            args.manifest,
            toolchain_profile=profile_id,
        )
        image, _ = assemble_evenota(manifest, payloads)
        package = manifest["package"]
        package_override = profile_pins(package, profile_id)
        if package_override is not None:
            expected_size = package_override.get("expected_size")
            expected_sha256 = package_override.get("expected_sha256")
        else:
            expected_size = package.get("expected_size")
            expected_sha256 = package.get("expected_sha256")
        if expected_size is not None and len(image) != expected_size:
            raise OpenCFWError(
                "assembled package size differs from the reference "
                f"(profile {profile_id})"
            )
        if expected_sha256 is not None and sha256_bytes(image) != expected_sha256:
            raise OpenCFWError(
                "assembled package hash differs from the reference "
                f"(profile {profile_id})"
            )
        print(
            f"Verified {len(payloads)} providers [profile {profile_id}]; "
            f"deterministic package SHA-256 {sha256_bytes(image)}"
        )
        return 0

    if args.command == "build":
        profile_id = resolve_toolchain_profile_id(args.toolchain_profile)
        if args.record_profile and profile_id == DEFAULT_TOOLCHAIN_PROFILE:
            parser.error(
                "--record-profile requires a non-default --toolchain-profile"
            )
        report = build(
            args.manifest,
            args.output_dir,
            toolchain_profile=profile_id,
            record_profile=args.record_profile,
        )
        print_summary(report)
        return 0

    raw = args.input.read_bytes()
    if args.kind == "main":
        wrapped = wrap_main_image(raw)
    elif args.kind == "case":
        wrapped = wrap_case_image(raw, args.case_version)
    else:
        wrapped = wrap_touch_image(raw)
    atomic_write(args.output, wrapped)
    print(f"Wrote {args.output} ({len(wrapped)} bytes, sha256 {sha256_bytes(wrapped)})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OpenCFWError, OSError) as error:
        print(f"openCFW: error: {error}", file=sys.stderr)
        raise SystemExit(1)
