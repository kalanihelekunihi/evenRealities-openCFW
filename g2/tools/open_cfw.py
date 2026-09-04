#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
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
import fcntl
import hashlib
import json
import os
import shutil
import stat
import struct
import sys
import tempfile
import threading
import zlib
from contextlib import contextmanager
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
DUAL_PROFILE_OWNERSHIP_PACKAGES = {
    "apple-clang": "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771",
    "linux-clang": "50f2ee3722aeaa720eed1a7c65381b02ac3ec0ceabecf9eb57d661d8e060a6d0",
}
DUAL_PROFILE_OWNERSHIP_MANIFESTS = {
    "apple-clang": "2d6230caa18fb661d438b8bcf4cfd593fd3a36366b6a73b10826bbe4add9e6c6",
    "linux-clang": "2d6230caa18fb661d438b8bcf4cfd593fd3a36366b6a73b10826bbe4add9e6c6",
}
DUAL_PROFILE_OWNERSHIP_COMPONENTS = frozenset(
    {"ble_em9305", "apollo_bootloader", "apollo_main"}
)

REQUIRED_RELEASE_COMPONENTS = {
    "codec": (1, 4, 3, "firmware/codec.bin"),
    "ble_em9305": (2, 5, 3, "firmware/ble_em9305.bin"),
    "touch": (3, 3, 3, "firmware/touch.bin"),
    "case": (4, 6, 3, "firmware/box.bin"),
    "apollo_bootloader": (5, 1, 3, "ota/s200_bootloader.bin"),
    "apollo_main": (6, 0, 3, "ota/s200_firmware_ota.bin"),
}
RELEASE_ADDRESS_STATUSES = {
    "confirmed_from_binh_headers_and_apollo_dfu_command",
    "confirmed_from_preamble_and_bootloader_code",
    "confirmed_from_record_table",
    "confirmed_from_uart_boot_header_and_vectors",
    "confirmed_from_vector_and_bootloader_code",
    "confirmed_from_vector_and_ota_code",
    "container_only",
    "controller_protocol_metadata",
    "generated_alignment",
    "generated_padding",
    "generated_source_data_replacement",
    "generated_source_entry_replacement",
    "generated_source_exact_load_image",
    "generated_source_exact_replacement",
    "generated_source_redirect",
    "inferred_from_vector_table",
    "official_blob",
    "source_compiled",
    "source_compiled_rodata",
    "unknown",
}
NON_ADDRESSED_STATUSES = {
    "container_only", "controller_protocol_metadata", "unknown",
}
REQUIRED_PROTECTED_REGIONS = {
    (
        "apollo510b_internal_mram", "ambiq_secure_bootloader",
        0x00400000, 0x00410000,
        "not_present_in_evenota_do_not_overwrite",
    ),
    (
        "apollo510b_internal_mram", "update_flag",
        0x007FE000, 0x007FE010,
        "bootloader_owned_do_not_include_in_application_image",
    ),
    (
        "case_stm32g0", "bank_1_serial_16",
        0x0803F000, 0x0803F010,
        "device_specific_preserve_before_case_bank_update",
    ),
    (
        "case_stm32g0", "bank_1_serial_8",
        0x0803F800, 0x0803F808,
        "device_specific_preserve_before_case_bank_update",
    ),
    (
        "case_stm32g0", "bank_2_serial_16",
        0x0807F000, 0x0807F010,
        "device_specific_preserve_before_case_bank_update",
    ),
    (
        "case_stm32g0", "bank_2_serial_8",
        0x0807F800, 0x0807F808,
        "device_specific_preserve_before_case_bank_update",
    ),
}
_OUTPUT_THREAD_LOCK = threading.Lock()
G2_ROOT = Path(__file__).resolve().parents[1]
PROFILE_RECORDING_MANIFESTS = frozenset({
    (G2_ROOT / "manifests/g2-2.2.6.10-ring-source.json").resolve(),
})


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


def effective_provider_path(record: dict[str, Any], profile_id: str) -> str:
    """Return the provider path actually selected for ``profile_id``.

    Build reports are security evidence as well as presentation output.  They
    must therefore name the same profile-specific artifact that
    :func:`read_providers` authenticated rather than always echoing the
    canonical top-level path.
    """

    override = profile_pins(record, profile_id)
    path = (
        override.get("path", record.get("path"))
        if override is not None else record.get("path")
    )
    if not isinstance(path, str):
        raise OpenCFWError("provider path is missing")
    return path


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
    if not isinstance(manifest, dict):
        raise OpenCFWError(f"manifest {path} must contain a JSON object")
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
    try:
        candidate = (root / relative).resolve()
    except (OSError, RuntimeError) as error:
        raise OpenCFWError(f"path cannot be resolved below openCFW: {relative}") \
            from error
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise OpenCFWError(f"path escapes openCFW root: {relative}") from error
    return candidate


def _read_regular_file(path: Path, role: str) -> bytes:
    """Read one immutable input without following a final symlink."""
    descriptor: int | None = None
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise OpenCFWError(f"{role} is not a regular file")
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise OpenCFWError(f"{role} is not a regular file")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = None
            return handle.read()
    except OSError as error:
        raise OpenCFWError(f"cannot read {role}: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _read_regular_file_below(root: Path, relative: str, role: str) -> bytes:
    """Read a contained regular file and reject symlinks in its relative path."""
    resolved_root = root.resolve()
    candidate = resolve_below(resolved_root, relative)
    lexical = Path(os.path.abspath(resolved_root / relative))
    if lexical != candidate:
        raise OpenCFWError(f"{role} path contains a symlink: {relative}")
    return _read_regular_file(candidate, role)


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
    replacements_by_profile = component.get("profile_region_replacements", {})
    if not isinstance(replacements_by_profile, dict):
        raise OpenCFWError(
            f"{component['name']}: profile_region_replacements must be an object"
        )
    selected_replacements = replacements_by_profile.get(toolchain_profile, [])
    if not isinstance(selected_replacements, list):
        raise OpenCFWError(
            f"{component['name']}: profile region replacements must be a list"
        )
    if selected_replacements:
        if toolchain_profile == DEFAULT_TOOLCHAIN_PROFILE:
            raise OpenCFWError(
                f"{component['name']}: canonical profile cannot replace regions"
            )
        working = copy.deepcopy(regions)
        previous_end = -1
        for replacement in sorted(
            selected_replacements,
            key=lambda item: item.get("start", -1) if isinstance(item, dict) else -1,
        ):
            if not isinstance(replacement, dict):
                raise OpenCFWError(
                    f"{component['name']}: profile region replacement is invalid"
                )
            start = replacement.get("start")
            end = replacement.get("end_exclusive")
            replacement_regions = replacement.get("regions")
            if (
                not isinstance(start, int)
                or not isinstance(end, int)
                or start < 0
                or end <= start
                or start < previous_end
                or not isinstance(boundary, int)
                or end > boundary
                or not isinstance(replacement_regions, list)
                or not replacement_regions
            ):
                raise OpenCFWError(
                    f"{component['name']}: profile region replacement span is invalid"
                )
            overlapping = []
            for index, region in enumerate(working):
                offset = region.get("file_offset")
                size = region.get("size")
                if not isinstance(offset, int) or not isinstance(size, int) or size <= 0:
                    raise OpenCFWError(
                        f"{component['name']}: base region span is invalid"
                    )
                if offset < end and offset + size > start:
                    overlapping.append((index, region))
            if not overlapping:
                raise OpenCFWError(
                    f"{component['name']}: profile replacement captures no base region"
                )
            cursor = start
            for _index, region in overlapping:
                if region.get("file_offset") != cursor:
                    raise OpenCFWError(
                        f"{component['name']}: profile replacement partially captures "
                        "a base region"
                    )
                cursor += region.get("size", -1)
            if cursor != end:
                raise OpenCFWError(
                    f"{component['name']}: profile replacement does not exactly tile "
                    "base regions"
                )
            cursor = start
            for region in replacement_regions:
                if (
                    not isinstance(region, dict)
                    or region.get("file_offset") != cursor
                    or not isinstance(region.get("size"), int)
                    or region["size"] <= 0
                ):
                    raise OpenCFWError(
                        f"{component['name']}: profile replacement regions have a gap "
                        "or overlap"
                    )
                cursor += region["size"]
            if cursor != end:
                raise OpenCFWError(
                    f"{component['name']}: profile replacement regions have wrong extent"
                )
            first = overlapping[0][0]
            last = overlapping[-1][0]
            working = (
                working[:first]
                + copy.deepcopy(replacement_regions)
                + working[last + 1:]
            )
            previous_end = end
        regions = working
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
        override = profile_pins(provider, toolchain_profile)
        provider_path = effective_provider_path(provider, toolchain_profile)
        data = _read_regular_file_below(
            project_root,
            provider_path,
            f"{name} provider",
        )
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


def _release_pin(
    record: dict[str, Any], size_key: str, sha_key: str, role: str
) -> None:
    size = record.get(size_key)
    digest = record.get(sha_key)
    if not isinstance(size, int) or size <= 0:
        raise OpenCFWError(f"{role}: mandatory size pin is missing")
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise OpenCFWError(f"{role}: mandatory SHA-256 pin is missing")


def _release_output_path(value: Any, role: str) -> str:
    if not isinstance(value, str) or not value:
        raise OpenCFWError(f"{role}: output path is missing")
    path = Path(value)
    if (
        path.is_absolute()
        or value != path.as_posix()
        or any(part in ("", ".", "..") for part in path.parts)
    ):
        raise OpenCFWError(f"{role}: output path is not a safe relative path")
    return value


def validate_release_manifest(
    manifest: dict[str, Any],
    *,
    toolchain_profile: str,
    record: bool = False,
    payloads: dict[str, bytes] | None = None,
) -> None:
    """Enforce the complete six-controller public-release contract."""
    package = manifest.get("package")
    if not isinstance(package, dict):
        raise OpenCFWError("release manifest package is missing")
    _release_pin(package, "expected_size", "expected_sha256", "package")
    _release_output_path(package.get("output_name"), "package")
    package_profiles = package.get("profiles", {})
    if not isinstance(package_profiles, dict):
        raise OpenCFWError("package profiles must be an object")
    for profile_id, pins in package_profiles.items():
        if not isinstance(profile_id, str) or not isinstance(pins, dict):
            raise OpenCFWError("package profile pins are invalid")
        _release_pin(
            pins, "expected_size", "expected_sha256",
            f"package profile {profile_id}",
        )
    if toolchain_profile != DEFAULT_TOOLCHAIN_PROFILE:
        selected = package_profiles.get(toolchain_profile)
        if selected is None and not record:
            raise OpenCFWError(
                f"package profile {toolchain_profile!r} pins are mandatory"
            )

    components = manifest.get("components")
    if not isinstance(components, list) or len(components) != 6:
        raise OpenCFWError("release manifest requires exactly six components")
    observed_identities: dict[str, tuple[int, int, int, str]] = {}
    entry_ids: set[int] = set()
    type_ids: set[int] = set()
    package_filenames: set[str] = set()
    all_outputs: set[str] = set()
    for component in components:
        if not isinstance(component, dict):
            raise OpenCFWError("release component record is invalid")
        name = component.get("name")
        identity = (
            component.get("entry_id"), component.get("type_id"),
            component.get("storage_type"), component.get("package_filename"),
        )
        if not isinstance(name, str) or name in observed_identities:
            raise OpenCFWError("release component names must be unique")
        observed_identities[name] = identity
        entry_id, type_id, _storage_type, package_filename = identity
        if entry_id in entry_ids or type_id in type_ids:
            raise OpenCFWError("release entry/type identities must be unique")
        if package_filename in package_filenames:
            raise OpenCFWError("release package filenames must be unique")
        entry_ids.add(entry_id)
        type_ids.add(type_id)
        package_filenames.add(package_filename)
        provider = component.get("provider")
        if not isinstance(provider, dict):
            raise OpenCFWError(f"{name}: release provider is missing")
        _release_pin(provider, "size", "sha256", f"{name} provider")
        profiles = provider.get("profiles", {})
        if not isinstance(profiles, dict):
            raise OpenCFWError(f"{name}: provider profiles must be an object")
        for profile_id, pins in profiles.items():
            if not isinstance(profile_id, str) or not isinstance(pins, dict):
                raise OpenCFWError(f"{name}: provider profile pins are invalid")
            _release_pin(
                pins, "size", "sha256", f"{name} profile {profile_id}",
            )
        region_profiles = component.get("profile_region_replacements", {})
        if not isinstance(region_profiles, dict):
            raise OpenCFWError(
                f"{name}: profile_region_replacements must be an object"
            )
        for profile_id in region_profiles:
            if (
                not isinstance(profile_id, str)
                or profile_id == DEFAULT_TOOLCHAIN_PROFILE
                or profile_id not in profiles
            ):
                raise OpenCFWError(
                    f"{name}: profile region replacement names an invalid profile"
                )
        if (
            toolchain_profile != DEFAULT_TOOLCHAIN_PROFILE
            and provider.get("kind") == "source_build"
            and toolchain_profile not in profiles
            and not record
        ):
            raise OpenCFWError(
                f"{name}: profile {toolchain_profile!r} pins are mandatory"
            )

        regions = component.get("regions")
        if not isinstance(regions, list) or not regions:
            raise OpenCFWError(f"{name}: release regions are missing")
        for region in regions:
            if not isinstance(region, dict):
                raise OpenCFWError(f"{name}: release region is invalid")
            status = region.get("address_status")
            if status not in RELEASE_ADDRESS_STATUSES:
                raise OpenCFWError(
                    f"{name}/{region.get('name')}: address status is not allowed"
                )
            has_target = "target" in region or "target_address" in region
            if ("target" in region) != ("target_address" in region):
                raise OpenCFWError(
                    f"{name}/{region.get('name')}: target contract is incomplete"
                )
            if status in NON_ADDRESSED_STATUSES and has_target:
                raise OpenCFWError(
                    f"{name}/{region.get('name')}: non-addressed region has a target"
                )
            if status not in NON_ADDRESSED_STATUSES and not has_target:
                raise OpenCFWError(
                    f"{name}/{region.get('name')}: addressed region lacks a target"
                )
            output = _release_output_path(
                region.get("output"), f"{name}/{region.get('name')}"
            )
            if output in all_outputs:
                raise OpenCFWError(
                    f"release region output path is duplicated: {output}"
                )
            all_outputs.add(output)

    if observed_identities != REQUIRED_RELEASE_COMPONENTS:
        raise OpenCFWError("release component identities changed")

    protected = manifest.get("protected_regions")
    if not isinstance(protected, list):
        raise OpenCFWError("release protected boundaries are missing")
    try:
        observed_protected = {
            (
                item["target"], item["name"], item["start"],
                item["end_exclusive"], item["policy"],
            )
            for item in protected
            if isinstance(item, dict)
        }
    except (KeyError, TypeError):
        raise OpenCFWError("release protected boundary is invalid") from None
    if (
        len(observed_protected) != len(protected)
        or observed_protected != REQUIRED_PROTECTED_REGIONS
    ):
        raise OpenCFWError("release protected boundaries changed")

    if payloads is not None:
        effective_outputs: set[str] = set()
        for component in components:
            data = payloads[component["name"]]
            effective_names: set[str] = set()
            for region in effective_component_regions(
                component, len(data), toolchain_profile
            ):
                region_name = region.get("name")
                if not isinstance(region_name, str) or region_name in effective_names:
                    raise OpenCFWError(
                        f"{component['name']}: effective region names are not unique"
                    )
                effective_names.add(region_name)
                status = region.get("address_status")
                if status not in RELEASE_ADDRESS_STATUSES:
                    raise OpenCFWError(
                        f"{component['name']}/{region.get('name')}: "
                        "effective address status is not allowed"
                    )
                has_target = "target" in region or "target_address" in region
                if ("target" in region) != ("target_address" in region):
                    raise OpenCFWError(
                        f"{component['name']}/{region.get('name')}: "
                        "effective target contract is incomplete"
                    )
                if status in NON_ADDRESSED_STATUSES and has_target:
                    raise OpenCFWError(
                        f"{component['name']}/{region.get('name')}: "
                        "effective non-addressed region has a target"
                    )
                if status not in NON_ADDRESSED_STATUSES and not has_target:
                    raise OpenCFWError(
                        f"{component['name']}/{region.get('name')}: "
                        "effective addressed region lacks a target"
                    )
                output = _release_output_path(
                    region.get("output"),
                    f"{component['name']}/{region.get('name')}",
                )
                if output in effective_outputs:
                    raise OpenCFWError(
                        f"release region output path is duplicated: {output}"
                    )
                effective_outputs.add(output)


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
    strict_release: bool = False,
) -> tuple[dict[str, Any], Path, dict[str, bytes]]:
    toolchain_profile = resolve_toolchain_profile_id(toolchain_profile)
    manifest_path = manifest_path.resolve()
    manifest = load_manifest(manifest_path)
    project_root = project_root_for_manifest(manifest_path)
    if strict_release:
        validate_release_manifest(
            manifest,
            toolchain_profile=toolchain_profile,
            record=record,
        )
    payloads = read_providers(
        manifest,
        project_root,
        toolchain_profile=toolchain_profile,
        record=record,
        recorded_providers=recorded_providers,
    )
    if strict_release:
        validate_release_manifest(
            manifest,
            toolchain_profile=toolchain_profile,
            record=record,
            payloads=payloads,
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
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


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


def require_build_dir(project_root: Path, build_dir: Path) -> None:
    resolved_root = project_root.resolve()
    resolved_build = build_dir.resolve()
    try:
        relative = resolved_build.relative_to(resolved_root)
    except ValueError as error:
        raise OpenCFWError("build directory must remain below openCFW") from error
    if not relative.parts or relative.parts[0] != "build":
        raise OpenCFWError("output directory must remain below openCFW/build")


@contextmanager
def output_generation_lock(build_dir: Path):
    build_dir.mkdir(parents=True, exist_ok=True)
    lock_path = build_dir / ".open-cfw-publish.lock"
    with _OUTPUT_THREAD_LOCK:
        try:
            if lock_path.exists() or lock_path.is_symlink():
                if not stat.S_ISREG(lock_path.lstat().st_mode):
                    raise OpenCFWError(
                        "output generation lock is not a regular file"
                    )
            descriptor = os.open(
                lock_path,
                os.O_RDWR
                | os.O_CREAT
                | getattr(os, "O_NOFOLLOW", 0),
                0o644,
            )
        except OSError as error:
            raise OpenCFWError(f"cannot open output generation lock: {error}") \
                from error
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise OpenCFWError("output generation lock is not a regular file")
            with os.fdopen(descriptor, "a+b") as handle:
                descriptor = -1
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            if descriptor >= 0:
                os.close(descriptor)


def split_regions(
    manifest: dict[str, Any],
    payloads: dict[str, bytes],
    build_dir: Path,
    toolchain_profile: str = DEFAULT_TOOLCHAIN_PROFILE,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    flash_regions, unresolved_regions, container_regions, artifacts = (
        plan_regions(manifest, payloads, toolchain_profile)
    )
    regions_root = build_dir / "regions"
    for relative, payload in artifacts.items():
        atomic_write(resolve_below(regions_root, relative), payload)
    return flash_regions, unresolved_regions, container_regions


def plan_regions(
    manifest: dict[str, Any],
    payloads: dict[str, bytes],
    toolchain_profile: str = DEFAULT_TOOLCHAIN_PROFILE,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, bytes],
]:
    """Return exact region records and bytes without touching the filesystem."""
    flash_regions: list[dict[str, Any]] = []
    unresolved_regions: list[dict[str, Any]] = []
    container_regions: list[dict[str, Any]] = []
    artifacts: dict[str, bytes] = {}
    for component in manifest["components"]:
        payload = payloads[component["name"]]
        for region in effective_component_regions(
            component, len(payload), toolchain_profile
        ):
            start = region["file_offset"]
            end = start + region["size"]
            region_data = payload[start:end]
            output = _release_output_path(
                region["output"],
                f"{component['name']}/{region['name']}",
            )
            if output in artifacts:
                raise OpenCFWError(f"duplicate region artifact: {output}")
            artifacts[output] = region_data
            record: dict[str, Any] = {
                "component": component["name"],
                "region": region["name"],
                "function": region["function"],
                "component_file_offset": start,
                "size": len(region_data),
                "sha256": sha256_bytes(region_data),
                "artifact": f"regions/{output}",
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
    return flash_regions, unresolved_regions, container_regions, artifacts


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


def write_sha256s(
    build_dir: Path, relative_paths: Iterable[str] | None = None
) -> None:
    build_dir = build_dir.resolve()
    if relative_paths is None:
        relative_names = sorted(
            path.relative_to(build_dir).as_posix()
            for path in build_dir.rglob("*")
            if path.is_file()
            and path.name not in ("SHA256SUMS", ".open-cfw-publish.lock")
            and not path.name.startswith(".")
        )
    else:
        relative_names = sorted(set(relative_paths))
    lines = []
    for relative in relative_names:
        payload = _read_regular_file_below(
            build_dir, relative, f"managed artifact {relative}"
        )
        lines.append(f"{sha256_bytes(payload)}  {relative}")
    atomic_write(build_dir / "SHA256SUMS", ("\n".join(lines) + "\n").encode())


def parse_sha256s(build_dir: Path) -> dict[str, str]:
    ledger_path = build_dir / "SHA256SUMS"
    try:
        lines = _read_regular_file(
            ledger_path, "checksum ledger"
        ).decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise OpenCFWError(f"cannot read checksum ledger: {error}") from error
    if not lines:
        raise OpenCFWError("checksum ledger is empty")
    result: dict[str, str] = {}
    for line in lines:
        fields = line.split("  ", 1)
        if len(fields) != 2:
            raise OpenCFWError("checksum ledger line is malformed")
        digest, relative = fields
        if (
            len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or relative in result
            or relative == "SHA256SUMS"
        ):
            raise OpenCFWError("checksum ledger identity is invalid")
        try:
            payload = _read_regular_file_below(
                build_dir, relative, f"checksum ledger artifact {relative}"
            )
        except OpenCFWError as error:
            raise OpenCFWError(f"checksum ledger mismatch: {relative}") from error
        if sha256_bytes(payload) != digest:
            raise OpenCFWError(f"checksum ledger mismatch: {relative}")
        result[relative] = digest
    return result


def effective_manifest_sha256(manifest: dict[str, Any]) -> str:
    encoded = json.dumps(
        manifest, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def manifest_source_ledger(manifest_path: Path) -> list[dict[str, Any]]:
    manifest_root = manifest_path.resolve().parent
    records: list[dict[str, Any]] = []
    loading: set[Path] = set()

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in loading:
            raise OpenCFWError("manifest inheritance cycle in source ledger")
        loading.add(path)
        try:
            payload = path.read_bytes()
            value = json.loads(payload.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise OpenCFWError(f"cannot ledger manifest source {path}: {error}") \
                from error
        extends = value.get("extends") if isinstance(value, dict) else None
        if extends is not None:
            if not isinstance(extends, str) or not extends:
                raise OpenCFWError("manifest ledger extends path is invalid")
            parent = (path.parent / extends).resolve()
            try:
                parent.relative_to(manifest_root)
            except ValueError as error:
                raise OpenCFWError(
                    "manifest ledger extends path escapes manifests directory"
                ) from error
            visit(parent)
        records.append({
            "path": path.relative_to(manifest_root).as_posix(),
            "size": len(payload),
            "sha256": sha256_bytes(payload),
        })
        loading.remove(path)

    visit(manifest_path)
    return records


def manifest_identity(
    manifest_path: Path, manifest: dict[str, Any]
) -> dict[str, Any]:
    return {
        "sha256": effective_manifest_sha256(manifest),
        "sources": manifest_source_ledger(manifest_path),
    }


def make_flash_plan(
    *,
    manifest: dict[str, Any],
    manifest_id: dict[str, Any],
    toolchain_profile: str,
    package_artifact: str,
    package_sha256: str,
    flash_regions: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
    container: list[dict[str, Any]],
) -> dict[str, Any]:
    source_build_components = [
        component for component in manifest["components"]
        if component.get("provider", {}).get("kind") == "source_build"
    ]
    source_build_names = {component.get("name") for component in source_build_components}
    dual_profile_companion_applies = (
        manifest.get("target") == "Even Realities G2"
        and {component.get("name") for component in manifest["components"]}
        == set(REQUIRED_RELEASE_COMPONENTS)
        and source_build_names == set(DUAL_PROFILE_OWNERSHIP_COMPONENTS)
        and package_sha256 == DUAL_PROFILE_OWNERSHIP_PACKAGES.get(toolchain_profile)
        and manifest_id.get("sha256")
        == DUAL_PROFILE_OWNERSHIP_MANIFESTS.get(toolchain_profile)
    )
    if not source_build_components:
        ownership_mode = "authoritative_provider_origin_only"
        ownership_companion = None
        typed_mixed_profile_spans: list[dict[str, Any]] = []
    elif (dual_profile_companion_applies
          and toolchain_profile == DEFAULT_TOOLCHAIN_PROFILE):
        ownership_mode = "non_authoritative_requires_checked_reconciliation"
        ownership_companion = (
            "tools/manifests/g2-dual-profile-ownership.json"
        )
        typed_mixed_profile_spans = []
    else:
        reconciled_noncanonical = (
            dual_profile_companion_applies
            and toolchain_profile != DEFAULT_TOOLCHAIN_PROFILE
        )
        ownership_mode = "non_authoritative_profile_coarse"
        if toolchain_profile == DEFAULT_TOOLCHAIN_PROFILE:
            ownership_mode = "non_authoritative_unreconciled_source_build"
        elif not reconciled_noncanonical:
            ownership_mode = "non_authoritative_profile_coarse_unreconciled"
        ownership_companion = (
            "tools/manifests/g2-dual-profile-ownership.json"
            if reconciled_noncanonical else None
        )
        # Non-canonical profiles retain exact target addresses, region bytes,
        # and artifact hashes.  Their source-build presentation rows below the
        # appended tail inherit canonical region boundaries, however, and are
        # therefore not a per-byte ownership map.  Publish the ambiguity as an
        # explicit typed mixed boundary; the checked companion supplies exact
        # aggregate source/generated/retained conservation from the admitted
        # component build reports.
        by_component: dict[str, list[dict[str, Any]]] = {}
        for row in flash_regions + container:
            by_component.setdefault(row["component"], []).append(row)
        typed_mixed_profile_spans = []
        for component in source_build_components:
            name = component["name"]
            rows = by_component.get(name, [])
            if not rows:
                raise OpenCFWError(
                    f"{name}: source-build profile has no planned regions"
                )
            end = max(
                row["component_file_offset"] + row["size"] for row in rows
            )
            start = 0
            if name != "apollo_main":
                boundary = component.get("source_appended_boundary")
                if type(boundary) is int:
                    start = boundary
            if not 0 <= start <= end:
                raise OpenCFWError(
                    f"{name}: typed mixed profile boundary is invalid"
                )
            typed_mixed_profile_spans.append(
                {
                    "component": name,
                    "component_file_offset": start,
                    "end_exclusive": end,
                    "size": end - start,
                    "classification": "typed_mixed_profile_ownership",
                    "reason": (
                        "exact bytes and addresses; no complete per-byte "
                        "source-vs-generated-vs-retained mask is claimed"
                    ),
                }
            )
    return {
        "schema_version": 1,
        "target": manifest["target"],
        "manifest_sha256": manifest_id["sha256"],
        "manifest_sources": manifest_id["sources"],
        "toolchain_profile": toolchain_profile,
        "package_artifact": package_artifact,
        "package_sha256": package_sha256,
        "flash_regions": flash_regions,
        "unresolved_flash_regions": unresolved,
        "container_only_regions": container,
        "address_status_semantics": {
            "address_and_artifact_mapping": "authoritative",
            "ownership_labels": ownership_mode,
            "authoritative_ownership_companion": ownership_companion,
            "typed_mixed_profile_spans": typed_mixed_profile_spans,
        },
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


def make_build_report(
    *,
    manifest: dict[str, Any],
    manifest_path: Path,
    project_root: Path,
    manifest_id: dict[str, Any],
    toolchain_profile: str,
    payloads: dict[str, bytes],
    package_artifact: str,
    image: bytes,
    expected_size: Any,
    expected_sha256: Any,
    entries: list[PackageEntry],
    flash_regions: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
    container: list[dict[str, Any]],
) -> dict[str, Any]:
    package_sha256 = sha256_bytes(image)
    reference_match: bool | None = (
        package_sha256 == expected_sha256 and len(image) == expected_size
        if expected_sha256 is not None and expected_size is not None
        else None
    )
    return {
        "schema_version": 1,
        "target": manifest["target"],
        "manifest": str(manifest_path.resolve().relative_to(project_root)),
        "manifest_sha256": manifest_id["sha256"],
        "manifest_sources": manifest_id["sources"],
        "toolchain_profile": toolchain_profile,
        "provider_mode": "+".join(
            sorted(
                {
                    component["provider"]["kind"]
                    for component in manifest["components"]
                }
            )
        ),
        "providers": [
            {
                "component": component["name"],
                "kind": component["provider"]["kind"],
                "path": effective_provider_path(
                    component["provider"], toolchain_profile
                ),
                "size": len(payloads[component["name"]]),
                "sha256": sha256_bytes(payloads[component["name"]]),
            }
            for component in manifest["components"]
        ],
        "package": {
            "artifact": package_artifact,
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


def validate_profile_recording_manifest(manifest_path: Path) -> Path:
    """Allow direct pin recording only for the reviewed ring-only workflow."""
    resolved_manifest = manifest_path.resolve()
    if resolved_manifest not in PROFILE_RECORDING_MANIFESTS:
        raise OpenCFWError(
            "direct --record-profile is restricted to the reviewed ring-source "
            "manifest; Apollo core-source pins require the independent "
            "canonical observation/admission workflow"
        )
    try:
        metadata = resolved_manifest.lstat()
    except OSError as error:
        raise OpenCFWError(
            "profile-recording manifest cannot be inspected safely"
        ) from error
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise OpenCFWError(
            "profile-recording manifest must be an independent regular file"
        )
    return resolved_manifest


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
    manifest_path = validate_profile_recording_manifest(manifest_path)
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


def _read_json_object(path: Path, role: str) -> dict[str, Any]:
    try:
        value = json.loads(_read_regular_file(path, role).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenCFWError(f"cannot read {role}: {error}") from error
    if not isinstance(value, dict):
        raise OpenCFWError(f"{role} must be a JSON object")
    return value


def verify_artifacts_with_lock_held(
    manifest_path: Path,
    build_dir: Path,
    *,
    toolchain_profile: str | None = None,
) -> dict[str, Any]:
    """Verify a generation while its ``output_generation_lock`` is held."""
    profile = resolve_toolchain_profile_id(toolchain_profile)
    manifest_path = manifest_path.resolve()
    build_dir = build_dir.resolve()
    manifest, project_root, payloads = verify_manifest(
        manifest_path,
        toolchain_profile=profile,
        strict_release=True,
    )
    require_build_dir(project_root, build_dir)
    identity = manifest_identity(manifest_path, manifest)
    image, entries = assemble_evenota(manifest, payloads)
    package_relative = f"package/{manifest['package']['output_name']}"
    package_bytes = _read_regular_file_below(
        build_dir, package_relative, "published package"
    )
    if package_bytes != image:
        raise OpenCFWError("published package differs from manifest providers")
    package_override = profile_pins(manifest["package"], profile)
    expected = package_override or manifest["package"]
    expected_size = expected.get("expected_size")
    expected_sha256 = expected.get("expected_sha256")
    if len(image) != expected_size or sha256_bytes(image) != expected_sha256:
        raise OpenCFWError("published package differs from selected profile pins")

    flash_regions, unresolved, container, region_payloads = plan_regions(
        manifest, payloads, profile
    )
    for relative, payload in region_payloads.items():
        observed = _read_regular_file_below(
            build_dir,
            f"regions/{relative}",
            f"region artifact regions/{relative}",
        )
        if observed != payload:
            raise OpenCFWError(f"region artifact differs: regions/{relative}")

    expected_plan = make_flash_plan(
        manifest=manifest,
        manifest_id=identity,
        toolchain_profile=profile,
        package_artifact=package_relative,
        package_sha256=sha256_bytes(image),
        flash_regions=flash_regions,
        unresolved=unresolved,
        container=container,
    )
    actual_plan = _read_json_object(build_dir / "flash-plan.json", "flash plan")
    if actual_plan != expected_plan:
        raise OpenCFWError("published flash plan differs from verified regions")

    expected_report = make_build_report(
        manifest=manifest,
        manifest_path=manifest_path,
        project_root=project_root,
        manifest_id=identity,
        toolchain_profile=profile,
        payloads=payloads,
        package_artifact=package_relative,
        image=image,
        expected_size=expected_size,
        expected_sha256=expected_sha256,
        entries=entries,
        flash_regions=flash_regions,
        unresolved=unresolved,
        container=container,
    )
    actual_report = _read_json_object(
        build_dir / "build-report.json", "build report"
    )
    if actual_report != expected_report:
        raise OpenCFWError(
            "published build report differs from manifest/profile/providers"
        )

    ledger = parse_sha256s(build_dir)
    expected_paths = {
        package_relative,
        "flash-plan.json",
        "build-report.json",
        *(f"regions/{relative}" for relative in region_payloads),
    }
    if set(ledger) != expected_paths:
        raise OpenCFWError("checksum ledger artifact set differs")
    return actual_report


def verify_artifacts(
    manifest_path: Path,
    build_dir: Path,
    *,
    toolchain_profile: str | None = None,
) -> dict[str, Any]:
    """Verify one complete generation under its publication lock."""
    resolved_manifest = manifest_path.resolve()
    resolved_build_dir = build_dir.resolve()
    require_build_dir(
        project_root_for_manifest(resolved_manifest), resolved_build_dir
    )
    with output_generation_lock(resolved_build_dir):
        return verify_artifacts_with_lock_held(
            resolved_manifest,
            resolved_build_dir,
            toolchain_profile=toolchain_profile,
        )


def _authenticated_previous_managed_paths(build_dir: Path) -> set[str]:
    """Return old managed paths only when their complete ledger is coherent."""
    try:
        ledger = parse_sha256s(build_dir)
        report = _read_json_object(build_dir / "build-report.json", "build report")
        plan = _read_json_object(build_dir / "flash-plan.json", "flash plan")
        package = report["package"]
        package_relative = package["artifact"]
        if (
            not isinstance(package, dict)
            or not isinstance(package_relative, str)
            or not package_relative.startswith("package/")
            or plan.get("package_artifact") != package_relative
            or plan.get("package_sha256") != package.get("sha256")
        ):
            return set()
        package_payload = _read_regular_file_below(
            build_dir, package_relative, "managed package artifact"
        )
        if (
            len(package_payload) != int(package["size"])
            or sha256_bytes(package_payload) != package["sha256"]
        ):
            return set()
        regions: list[dict[str, Any]] = []
        for key in (
            "flash_regions", "unresolved_flash_regions",
            "container_only_regions",
        ):
            value = plan.get(key)
            if not isinstance(value, list):
                return set()
            regions.extend(value)
        region_paths: set[str] = set()
        for region in regions:
            relative = region.get("artifact") if isinstance(region, dict) else None
            if (
                not isinstance(relative, str)
                or not relative.startswith("regions/")
                or relative in region_paths
            ):
                return set()
            payload = _read_regular_file_below(
                build_dir, relative, f"managed region artifact {relative}"
            )
            if (
                len(payload) != int(region["size"])
                or sha256_bytes(payload) != region["sha256"]
            ):
                return set()
            region_paths.add(relative)
        managed = {
            "flash-plan.json", "build-report.json", package_relative,
            *region_paths,
        }
        if set(ledger) != managed:
            return set()
        return managed
    except (KeyError, TypeError, ValueError, OSError, OpenCFWError):
        return set()


def _capture_paths(
    build_dir: Path, relative_paths: Iterable[str]
) -> dict[str, tuple[bool, bytes]]:
    result: dict[str, tuple[bool, bytes]] = {}
    for relative in relative_paths:
        path = resolve_below(build_dir, relative)
        lexical = Path(os.path.abspath(build_dir.resolve() / relative))
        if lexical != path:
            raise OpenCFWError(
                f"managed artifact path contains a symlink: {relative}"
            )
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            result[relative] = (False, b"")
            continue
        if not stat.S_ISREG(mode):
            raise OpenCFWError(f"managed artifact is not regular: {relative}")
        result[relative] = (
            True,
            _read_regular_file(path, f"managed artifact {relative}"),
        )
    return result


def _restore_paths(
    build_dir: Path, previous: dict[str, tuple[bool, bytes]]
) -> None:
    marker_order = ("build-report.json", "SHA256SUMS")
    for relative in marker_order:
        resolve_below(build_dir, relative).unlink(missing_ok=True)
    for relative, (existed, payload) in previous.items():
        if relative in marker_order:
            continue
        path = resolve_below(build_dir, relative)
        if existed:
            atomic_write(path, payload)
        else:
            path.unlink(missing_ok=True)
    for relative in marker_order:
        existed, payload = previous.get(relative, (False, b""))
        path = resolve_below(build_dir, relative)
        if existed:
            atomic_write(path, payload)
        else:
            path.unlink(missing_ok=True)
    for relative, (existed, payload) in previous.items():
        path = resolve_below(build_dir, relative)
        if existed:
            try:
                matches = (
                    _read_regular_file(path, f"restored artifact {relative}")
                    == payload
                )
            except OpenCFWError:
                matches = False
        else:
            matches = not path.exists() and not path.is_symlink()
        if not matches:
            resolve_below(build_dir, "SHA256SUMS").unlink(missing_ok=True)
            raise OpenCFWError("artifact generation rollback failed")


def publish_staged_generation(staging: Path, build_dir: Path) -> None:
    """Publish one prevalidated managed generation, ledger last."""
    new_ledger = parse_sha256s(staging)
    new_managed = set(new_ledger)
    with output_generation_lock(build_dir):
        old_managed = _authenticated_previous_managed_paths(build_dir)
        affected = old_managed | new_managed | {
            "build-report.json", "SHA256SUMS",
        }
        previous = _capture_paths(build_dir, affected)
        resolve_below(build_dir, "SHA256SUMS").unlink(missing_ok=True)
        resolve_below(build_dir, "build-report.json").unlink(missing_ok=True)
        try:
            for relative in sorted(old_managed - new_managed):
                resolve_below(build_dir, relative).unlink(missing_ok=True)
            ordinary = sorted(
                new_managed - {"build-report.json"}
            )
            for relative in ordinary:
                atomic_write(
                    resolve_below(build_dir, relative),
                    _read_regular_file_below(
                        staging, relative, f"staged managed artifact {relative}"
                    ),
                )
            atomic_write(
                build_dir / "build-report.json",
                _read_regular_file(
                    staging / "build-report.json", "staged build report"
                ),
            )
            for relative, digest in new_ledger.items():
                payload = _read_regular_file_below(
                    build_dir, relative, f"published artifact {relative}"
                )
                if sha256_bytes(payload) != digest:
                    raise OpenCFWError(
                        f"published artifact readback changed: {relative}"
                    )
            atomic_write(
                build_dir / "SHA256SUMS",
                _read_regular_file(staging / "SHA256SUMS", "staged checksum ledger"),
            )
            if parse_sha256s(build_dir) != new_ledger:
                raise OpenCFWError("published checksum ledger readback changed")
        except Exception:
            try:
                _restore_paths(build_dir, previous)
            except Exception as rollback_error:
                (build_dir / "SHA256SUMS").unlink(missing_ok=True)
                raise OpenCFWError("artifact generation rollback failed") \
                    from rollback_error
            raise


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
    if record_profile:
        validate_profile_recording_manifest(manifest_path)
    recorded_providers: dict[str, dict[str, Any]] = {}
    manifest, project_root, payloads = verify_manifest(
        manifest_path,
        toolchain_profile=toolchain_profile,
        record=record_profile,
        recorded_providers=recorded_providers,
        strict_release=True,
    )
    require_build_dir(project_root, build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    image, entries = assemble_evenota(manifest, payloads)
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
        manifest, project_root, payloads = verify_manifest(
            manifest_path,
            toolchain_profile=toolchain_profile,
            strict_release=True,
        )
        recorded_image, entries = assemble_evenota(manifest, payloads)
        if recorded_image != image:
            raise OpenCFWError("recorded manifest changed assembled package bytes")
        package_override = profile_pins(manifest["package"], toolchain_profile)
        if package_override is None:
            raise OpenCFWError("recorded package profile pins are missing")
        expected_size = package_override.get("expected_size")
        expected_sha256 = package_override.get("expected_sha256")
    if len(image) != expected_size:
        raise OpenCFWError(
            "assembly size differs from the pinned reference "
            f"(profile {toolchain_profile})"
        )
    if package_sha256 != expected_sha256:
        raise OpenCFWError(
            "assembly hash differs from the pinned reference "
            f"(profile {toolchain_profile}): observed {package_sha256}"
        )
    identity = manifest_identity(manifest_path, manifest)
    with tempfile.TemporaryDirectory(
        prefix=".open-cfw-stage-", dir=build_dir
    ) as temporary:
        staging = Path(temporary)
        package_relative = f"package/{manifest['package']['output_name']}"
        atomic_write(resolve_below(staging, package_relative), image)
        flash_regions, unresolved, container = split_regions(
            manifest, payloads, staging, toolchain_profile
        )
        flash_plan = make_flash_plan(
            manifest=manifest,
            manifest_id=identity,
            toolchain_profile=toolchain_profile,
            package_artifact=package_relative,
            package_sha256=package_sha256,
            flash_regions=flash_regions,
            unresolved=unresolved,
            container=container,
        )
        atomic_write_json(staging / "flash-plan.json", flash_plan)
        report = make_build_report(
            manifest=manifest,
            manifest_path=manifest_path,
            project_root=project_root,
            manifest_id=identity,
            toolchain_profile=toolchain_profile,
            payloads=payloads,
            package_artifact=package_relative,
            image=image,
            expected_size=expected_size,
            expected_sha256=expected_sha256,
            entries=entries,
            flash_regions=flash_regions,
            unresolved=unresolved,
            container=container,
        )
        atomic_write_json(staging / "build-report.json", report)
        managed_paths = {
            package_relative,
            "flash-plan.json",
            "build-report.json",
            *(
                item["artifact"]
                for group in (flash_regions, unresolved, container)
                for item in group
            ),
        }
        write_sha256s(staging, managed_paths)
        verify_artifacts(
            manifest_path,
            staging,
            toolchain_profile=toolchain_profile,
        )
        publish_staged_generation(staging, build_dir)
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

    artifacts_parser = subparsers.add_parser(
        "verify-artifacts",
        help="validate a published package/regions/plan/report/checksum generation",
        epilog=(
            "Community smoke example: python3 g2/tools/open_cfw.py "
            "verify-artifacts --manifest "
            "g2/manifests/g2-2.2.6.10-core-source.json --output-dir "
            "g2/build/source --toolchain-profile apple-clang"
        ),
    )
    artifacts_parser.add_argument(
        "--manifest", type=Path, default=default_manifest
    )
    artifacts_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "build",
    )
    artifacts_parser.add_argument(
        "--toolchain-profile",
        default=profile_default,
        help=(
            "reviewed toolchain profile for the published generation "
            f"(default {DEFAULT_TOOLCHAIN_PROFILE!r})"
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
            "maintainer-only ring-source recorder: capture observed provider "
            "and package pins into profiles[<--toolchain-profile>]; Apollo "
            "core-source recording is rejected and requires independent "
            "canonical observation/admission"
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
            strict_release=True,
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

    if args.command == "verify-artifacts":
        profile_id = resolve_toolchain_profile_id(args.toolchain_profile)
        report = verify_artifacts(
            args.manifest,
            args.output_dir,
            toolchain_profile=profile_id,
        )
        print(
            "Verified published openCFW artifacts "
            f"[profile {profile_id}]; package SHA-256 "
            f"{report['package']['sha256']}"
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
