#!/usr/bin/env python3
"""Fail-closed, offline qualification for G2 hardware-test candidates.

This tool never opens BLE or serial devices.  It compares the Apollo main
payload in a candidate package with the reviewed stock package and emits the
smallest facts needed to decide whether the image belongs on the next rung of
the hardware qualification ladder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Any


RUN_BASE = 0x00438000
PREAMBLE_BYTES = 32
VECTOR_BYTES = 0x100
SOURCE_PACKAGE_VERSION = "s200_v2.2.6.10"
RELEASE_PACKAGE_VERSION = "s200_v2.2.6.0"
SOURCE_RUNTIME_FIELD = b"2.2.6.10\0"
RELEASE_RUNTIME_FIELD = b"2.2.6.0\0\0"
EVENOTA_MAGIC = b"EVENOTA\0"
EVENOTA_TOC_OFFSET = 0x40
EVENOTA_TOC_ENTRY_SIZE = 0x10
EVENOTA_TOC_TRAILER = b"evenota\0" + b"\0" * 8
EVENOTA_COMPONENT_HEADER_SIZE = 0x80
EVENOTA_COMPONENT_MAGIC = 0x4E455645
MAIN_FILENAME = "ota/s200_firmware_ota.bin"
RUNTIME_VERSION_FIELDS = {
    "settings": 0x003537DC,
    "product_test_0x24": 0x00353D64,
}
CANONICAL_ENTRY_IDENTITIES = (
    (1, 4, 3, "firmware/codec.bin"),
    (2, 5, 3, "firmware/ble_em9305.bin"),
    (3, 3, 3, "firmware/touch.bin"),
    (4, 6, 3, "firmware/box.bin"),
    (5, 1, 3, "ota/s200_bootloader.bin"),
    (6, 0, 3, MAIN_FILENAME),
)
CRITICAL_RUNTIME_RE = re.compile(
    r"(?:freertos_|cmsis_|rtos_|iar_mem|iar_errno|iar_domain|iar_range|"
    r"watchdog|kernel_(?:initialize|start)|start_scheduler)",
    re.IGNORECASE,
)


class QualificationError(ValueError):
    """The input cannot be proven eligible for the requested stage."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _crc32c_msb(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x1EDC6F41) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
    return crc


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise QualificationError(f"{path} must contain a JSON object")
    return value


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _c_string(data: bytes, start: int, end: int) -> str:
    raw = data[start:end].split(b"\0", 1)[0]
    try:
        return raw.decode("ascii")
    except UnicodeDecodeError as error:
        raise QualificationError("package metadata is not ASCII") from error


def _independent_apollo_range(package: bytes) -> tuple[int, int]:
    if len(package) < EVENOTA_TOC_OFFSET or package[:8] != EVENOTA_MAGIC:
        raise QualificationError("package lacks EVENOTA magic")
    count = struct.unpack_from("<I", package, 8)[0]
    if count != len(CANONICAL_ENTRY_IDENTITIES):
        raise QualificationError("package does not contain the canonical six entries")
    if struct.unpack_from("<I", package, 12)[0] != 0:
        raise QualificationError("package header reserved metadata is invalid")
    toc_end = EVENOTA_TOC_OFFSET + count * EVENOTA_TOC_ENTRY_SIZE
    trailer_end = toc_end + len(EVENOTA_TOC_TRAILER)
    if package[toc_end:trailer_end] != EVENOTA_TOC_TRAILER:
        raise QualificationError("package has an invalid TOC trailer")
    expected_offset = trailer_end
    matches: list[tuple[int, int]] = []
    for index in range(count):
        entry_id, body_offset, body_size, toc_checksum = struct.unpack_from(
            "<IIII", package, EVENOTA_TOC_OFFSET + index * EVENOTA_TOC_ENTRY_SIZE
        )
        if body_offset != expected_offset:
            raise QualificationError("package entries are not contiguous")
        body_end = body_offset + body_size
        if body_size < EVENOTA_COMPONENT_HEADER_SIZE or body_end > len(package):
            raise QualificationError("package entry exceeds the package")
        header = package[body_offset:body_offset + EVENOTA_COMPONENT_HEADER_SIZE]
        payload_offset = body_offset + EVENOTA_COMPONENT_HEADER_SIZE
        payload_size = body_size - EVENOTA_COMPONENT_HEADER_SIZE
        payload = package[payload_offset:body_end]
        expected_entry_id, expected_type_id, expected_storage_type, expected_name = (
            CANONICAL_ENTRY_IDENTITIES[index]
        )
        if (
            entry_id != expected_entry_id
            or struct.unpack_from("<I", header, 8)[0] != payload_size
            or struct.unpack_from("<I", header, 12)[0] != toc_checksum
            or struct.unpack_from("<I", header, 0x14)[0] != EVENOTA_COMPONENT_MAGIC
            or struct.unpack_from("<I", header, 0x24)[0] != expected_type_id
            or struct.unpack_from("<I", header, 0x28)[0] != expected_storage_type
            or _c_string(header, 0x30, 0x80) != expected_name
            or any(
                struct.unpack_from("<I", header, offset)[0] != expected
                for offset, expected in (
                    (0x00, 0),
                    (0x04, 0),
                    (0x10, 0),
                    (0x18, 0xFFFFFFFF),
                    (0x1C, 0xFFFFFFFF),
                    (0x20, 0),
                    (0x2C, 0xFFFFFFFF),
                )
            )
        ):
            raise QualificationError("package entry metadata is invalid")
        if _crc32c_msb(payload) != toc_checksum:
            raise QualificationError("package entry CRC-32C is invalid")
        if expected_name == MAIN_FILENAME:
            matches.append((payload_offset, payload_size))
        expected_offset = body_end
    if expected_offset != len(package):
        raise QualificationError("package entries do not close at EOF")
    if len(matches) != 1:
        raise QualificationError(
            f"package contains {len(matches)} Apollo-main components"
        )
    return matches[0]


def _report_identity(
    report: dict[str, Any], role: str
) -> tuple[int, str, str]:
    identity = report.get(role)
    if not isinstance(identity, dict):
        raise QualificationError(f"release report has no {role} package identity")
    size = identity.get("size")
    digest = identity.get("sha256")
    version = identity.get("version")
    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
        or not isinstance(digest, str)
        or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        or not isinstance(version, str)
    ):
        raise QualificationError(f"release report {role} identity is invalid")
    expected_version = (
        SOURCE_PACKAGE_VERSION if role == "source" else RELEASE_PACKAGE_VERSION
    )
    if version != expected_version:
        raise QualificationError(f"release report {role} version changed")
    if role == "release" and identity.get("runtime_version") != "2.2.6.0":
        raise QualificationError("release report runtime version changed")
    return size, digest, version


def _validated_runtime_fields(
    report: dict[str, Any], payload_offset: int, payload_size: int
) -> dict[str, int]:
    apollo = report["apollo_main"]
    fields = apollo.get("runtime_version_fields")
    if not isinstance(fields, dict) or set(fields) != set(RUNTIME_VERSION_FIELDS):
        raise QualificationError("release report lacks the two runtime fields")
    result: dict[str, int] = {}
    occupied: set[int] = set()
    for name, expected_relative in RUNTIME_VERSION_FIELDS.items():
        field = fields[name]
        if not isinstance(field, dict):
            raise QualificationError(f"runtime field {name} is not an object")
        relative = field.get("payload_offset")
        package_relative = field.get("package_offset")
        if (
            not isinstance(relative, int)
            or isinstance(relative, bool)
            or relative != expected_relative
            or not isinstance(package_relative, int)
            or isinstance(package_relative, bool)
            or package_relative != payload_offset + relative
            or relative < 0
            or relative + len(RELEASE_RUNTIME_FIELD) > payload_size
        ):
            raise QualificationError(f"runtime field {name} range or identity changed")
        span = set(range(relative, relative + len(RELEASE_RUNTIME_FIELD)))
        if occupied & span:
            raise QualificationError("runtime version fields overlap")
        occupied.update(span)
        result[name] = relative
    return result


def _apollo_payload(package: bytes, report: dict[str, Any]) -> tuple[bytes, int, str]:
    if report.get("schema_version") != 1:
        raise QualificationError("release report schema is invalid")
    package_size = len(package)
    package_sha = _sha256(package)
    matches = [
        role
        for role in ("source", "release")
        if _report_identity(report, role)[:2] == (package_size, package_sha)
    ]
    if len(matches) != 1:
        raise QualificationError(
            "package identity does not match exactly one release-report role"
        )
    role = matches[0]
    expected_package_version = (
        SOURCE_PACKAGE_VERSION if role == "source" else RELEASE_PACKAGE_VERSION
    )
    if _c_string(package, 0x30, 0x40) != expected_package_version:
        raise QualificationError(
            f"{role} package version does not match its authenticated report role"
        )
    discovered_offset, discovered_size = _independent_apollo_range(package)
    apollo = report.get("apollo_main")
    if not isinstance(apollo, dict):
        raise QualificationError("release report has no apollo_main object")
    offset = apollo.get("payload_offset")
    size = apollo.get("payload_size")
    if not isinstance(offset, int) or not isinstance(size, int):
        raise QualificationError("Apollo payload offset/size are not integers")
    if (offset, size) != (discovered_offset, discovered_size):
        raise QualificationError(
            "release-report Apollo range differs from independently parsed package"
        )
    payload = package[offset : offset + size]
    digest_field = "source_sha256" if role == "source" else "release_sha256"
    expected_payload_sha = apollo.get(digest_field)
    if (
        not isinstance(expected_payload_sha, str)
        or _sha256(payload) != expected_payload_sha
    ):
        raise QualificationError(
            f"computed Apollo payload hash differs from report {digest_field}"
        )
    fields = _validated_runtime_fields(report, discovered_offset, discovered_size)
    if len(payload) < 8:
        raise QualificationError("Apollo payload is too short for its nested CRC")
    if struct.unpack_from("<I", payload, 4)[0] != zlib.crc32(payload[8:]) & 0xFFFFFFFF:
        raise QualificationError("Apollo payload nested CRC-32 is invalid")
    expected_runtime_field = (
        SOURCE_RUNTIME_FIELD if role == "source" else RELEASE_RUNTIME_FIELD
    )
    for name, relative in fields.items():
        actual = payload[relative:relative + len(expected_runtime_field)]
        if actual != expected_runtime_field:
            raise QualificationError(
                f"{role} package runtime field {name} differs from report contract"
            )
    if role == "release":
        reconstructed = bytearray(payload)
        for name, relative in fields.items():
            reconstructed[relative:relative + len(SOURCE_RUNTIME_FIELD)] = (
                SOURCE_RUNTIME_FIELD
            )
        if len(reconstructed) < 8:
            raise QualificationError("Apollo payload is too short for its nested CRC")
        struct.pack_into("<I", reconstructed, 4, zlib.crc32(reconstructed[8:]) & 0xFFFFFFFF)
        source_sha = apollo.get("source_sha256")
        if not isinstance(source_sha, str) or _sha256(reconstructed) != source_sha:
            raise QualificationError(
                "release report source Apollo hash is not reconstructibly bound"
            )
    return payload, discovered_offset, role


def _difference_runs(left: bytes, right: bytes) -> list[dict[str, int]]:
    limit = min(len(left), len(right))
    runs: list[dict[str, int]] = []
    index = 0
    while index < limit:
        if left[index] == right[index]:
            index += 1
            continue
        start = index
        while index < limit and left[index] != right[index]:
            index += 1
        runs.append({"start": start, "end": index, "size": index - start})
    if len(left) != len(right):
        runs.append(
            {
                "start": limit,
                "end": max(len(left), len(right)),
                "size": abs(len(left) - len(right)),
            }
        )
    return runs


def _stock_control_allowed_offsets(report: dict[str, Any]) -> set[int]:
    apollo = report["apollo_main"]
    fields = _validated_runtime_fields(
        report, apollo["payload_offset"], apollo["payload_size"]
    )
    # Bytes 4..7 are the nested Apollo CRC32.  release_cfw changes the two
    # NUL-terminated strings from 2.2.6.10 to 2.2.6.0, which may alter the last
    # two byte positions in each fixed field.
    allowed = set(range(4, 8))
    for offset in fields.values():
        allowed.update(range(offset, offset + len(RELEASE_RUNTIME_FIELD)))
    return allowed


def _overlay_metrics(
    config: dict[str, Any] | None,
    candidate_source_sha256: str,
) -> dict[str, Any]:
    if config is None:
        return {
            "patch_site_count": 0,
            "critical_runtime_patch_count": 0,
            "critical_runtime_patches": [],
            "metadata_bound_to_candidate": True,
        }
    sites = config.get("patch_sites")
    if not isinstance(sites, list) or any(not isinstance(x, dict) for x in sites):
        raise QualificationError("overlay patch_sites must be a list of objects")
    critical = []
    for site in sites:
        text = " ".join(
            str(site.get(key, "")) for key in ("name", "target_function")
        )
        if CRITICAL_RUNTIME_RE.search(text):
            critical.append(
                {
                    "name": site.get("name"),
                    "runtime_address": site.get("runtime_address"),
                    "target_function": site.get("target_function"),
                }
            )
    expected_component_sha256 = config.get("expected", {}).get("component_sha256")
    metadata_bound_to_candidate = bool(
        isinstance(expected_component_sha256, str)
        and isinstance(candidate_source_sha256, str)
        and expected_component_sha256 == candidate_source_sha256
    )
    return {
        "patch_site_count": len(sites),
        "critical_runtime_patch_count": len(critical),
        "critical_runtime_patches": critical,
        "expected_component_sha256": expected_component_sha256,
        "candidate_source_sha256": candidate_source_sha256,
        "metadata_bound_to_candidate": metadata_bound_to_candidate,
    }


def qualify(
    *,
    stock_package: bytes,
    candidate_package: bytes,
    stock_report: dict[str, Any],
    candidate_report: dict[str, Any],
    overlay_config: dict[str, Any] | None,
    stage: str,
    max_patch_sites: int,
    max_critical_runtime_patches: int,
) -> dict[str, Any]:
    stock, stock_offset, stock_role = _apollo_payload(stock_package, stock_report)
    candidate, candidate_offset, candidate_role = _apollo_payload(
        candidate_package, candidate_report
    )
    if stock_role != "source" or candidate_role != "release":
        raise QualificationError(
            "qualification requires a source stock package and release candidate"
        )
    candidate_source_sha = candidate_report["apollo_main"]["source_sha256"]
    metrics = _overlay_metrics(overlay_config, candidate_source_sha)
    vectors_equal = (
        len(stock) >= PREAMBLE_BYTES + VECTOR_BYTES
        and len(candidate) >= PREAMBLE_BYTES + VECTOR_BYTES
        and stock[PREAMBLE_BYTES : PREAMBLE_BYTES + VECTOR_BYTES]
        == candidate[PREAMBLE_BYTES : PREAMBLE_BYTES + VECTOR_BYTES]
    )
    initial_sp = reset_handler = None
    if len(candidate) >= PREAMBLE_BYTES + 8:
        initial_sp, reset_handler = struct.unpack_from("<II", candidate, PREAMBLE_BYTES)
    runs = _difference_runs(stock, candidate)
    changed_common_offsets = {
        index
        for index, (left, right) in enumerate(zip(stock, candidate))
        if left != right
    }

    reasons: list[str] = []
    if not vectors_equal:
        reasons.append("Cortex-M vector table differs from reviewed stock")
    if overlay_config is not None and not metrics["metadata_bound_to_candidate"]:
        reasons.append("overlay metadata is not hash-bound to this candidate payload")
    if stage == "stock-control":
        allowed = _stock_control_allowed_offsets(candidate_report)
        unexpected = sorted(changed_common_offsets - allowed)
        if len(stock) != len(candidate):
            reasons.append("stock-code control changed Apollo payload size")
        if unexpected:
            reasons.append(
                f"stock-code control changed {len(unexpected)} non-version/code bytes"
            )
        if overlay_config is not None or metrics["patch_site_count"]:
            reasons.append("stock-code control must not declare source patch sites")
    elif stage == "minimal-hook":
        if metrics["patch_site_count"] == 0:
            reasons.append("minimal-hook candidate has no source patch site")
        if metrics["patch_site_count"] > max_patch_sites:
            reasons.append(
                f"patch-site count {metrics['patch_site_count']} exceeds "
                f"qualification limit {max_patch_sites}"
            )
        if metrics["critical_runtime_patch_count"] > max_critical_runtime_patches:
            reasons.append(
                f"critical runtime patch count "
                f"{metrics['critical_runtime_patch_count']} exceeds qualification "
                f"limit {max_critical_runtime_patches}"
            )
    elif stage == "full-source":
        # Full-source is intentionally report-only until all earlier stages
        # have hardware evidence.  An operator must not mistake a structurally
        # valid build for an eligible first recovery flash.
        reasons.append("full-source requires recorded earlier-stage hardware passes")
    else:
        raise QualificationError(f"unknown stage {stage!r}")

    return {
        "schema_version": 1,
        "stage": stage,
        "eligible_for_next_hardware_test": not reasons,
        "blocking_reasons": reasons,
        "stock_apollo": {"size": len(stock), "sha256": _sha256(stock)},
        "candidate_apollo": {
            "size": len(candidate),
            "sha256": _sha256(candidate),
            "initial_sp": f"0x{initial_sp:08X}" if initial_sp is not None else None,
            "reset_handler": (
                f"0x{reset_handler:08X}" if reset_handler is not None else None
            ),
        },
        "vectors_equal": vectors_equal,
        "difference_run_count": len(runs),
        "changed_common_byte_count": len(changed_common_offsets),
        "difference_runs_sample": runs[:64],
        "difference_runs_omitted": max(0, len(runs) - 64),
        "overlay": {
            **metrics,
            "critical_runtime_patches": metrics["critical_runtime_patches"][:64],
            "critical_runtime_patches_omitted": max(
                0, len(metrics["critical_runtime_patches"]) - 64
            ),
        },
        "limits": {
            "max_patch_sites": max_patch_sites,
            "max_critical_runtime_patches": max_critical_runtime_patches,
        },
        "report_authentication": {
            "stock_package_sha256": _sha256(stock_package),
            "stock_report_role": stock_role,
            "stock_apollo_offset": stock_offset,
            "candidate_package_sha256": _sha256(candidate_package),
            "candidate_report_role": candidate_role,
            "candidate_apollo_offset": candidate_offset,
            "candidate_source_apollo_sha256": candidate_source_sha,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-package", type=Path, required=True)
    parser.add_argument("--candidate-package", type=Path, required=True)
    parser.add_argument("--stock-report", type=Path, required=True)
    parser.add_argument("--candidate-report", type=Path, required=True)
    parser.add_argument("--overlay-config", type=Path)
    parser.add_argument(
        "--stage",
        choices=("stock-control", "minimal-hook", "full-source"),
        required=True,
    )
    parser.add_argument("--max-patch-sites", type=int, default=8)
    parser.add_argument("--max-critical-runtime-patches", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = qualify(
        stock_package=args.stock_package.read_bytes(),
        candidate_package=args.candidate_package.read_bytes(),
        stock_report=_load_json(args.stock_report),
        candidate_report=_load_json(args.candidate_report),
        overlay_config=(
            _load_json(args.overlay_config) if args.overlay_config is not None else None
        ),
        stage=args.stage,
        max_patch_sites=args.max_patch_sites,
        max_critical_runtime_patches=args.max_critical_runtime_patches,
    )
    _atomic_write(
        args.output,
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["eligible_for_next_hardware_test"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
