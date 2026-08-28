#!/usr/bin/env python3
"""Create the hardware-testable openCFW 2.2.6.0 EVENOTA release image.

The reviewed source base identifies itself as 2.2.6.10.  A custom firmware
derived from that base uses 2.2.6.0.  The G2 exposes its version through two
independent Apollo-main paths: the normal settings response and product-test
command 0x24 used by the recovery case.  Both must agree with the outer
EVENOTA package identity.

This transform is deliberately fixed-layout and fail-closed.  It changes no
component sizes and accepts only the reviewed source and target identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import open_cfw
import audit_g2_release_licensing


SOURCE_PACKAGE_VERSION = "s200_v2.2.6.10"
RELEASE_PACKAGE_VERSION = "s200_v2.2.6.0"
SOURCE_RUNTIME_FIELD = b"2.2.6.10\0"
RELEASE_RUNTIME_FIELD = b"2.2.6.0\0\0"
MAIN_FILENAME = "ota/s200_firmware_ota.bin"
ROOT = Path(__file__).resolve().parents[1]
CANONICAL_SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
CANONICAL_SOURCE_BUILD_REPORT = ROOT / "build/source/build-report.json"
CANONICAL_COMPONENTS = (
    "codec",
    "ble_em9305",
    "touch",
    "case",
    "apollo_bootloader",
    "apollo_main",
)

# These are Apollo-main payload offsets, not EVENOTA package offsets.  They
# were independently confirmed against the stock 2.2.6.10 settings response
# and product-test command 0x24 response used by the USB recovery case.
RUNTIME_VERSION_FIELDS = {
    "settings": 0x003537DC,
    "product_test_0x24": 0x00353D64,
}


@dataclass(frozen=True)
class ParsedEntry:
    index: int
    entry_id: int
    toc_offset: int
    body_offset: int
    body_size: int
    payload_offset: int
    payload_size: int
    filename: str
    type_id: int
    storage_type: int
    checksum: int


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_entries(image: bytes) -> list[ParsedEntry]:
    if len(image) < open_cfw.EVENOTA_TOC_OFFSET or image[:8] != open_cfw.EVENOTA_MAGIC:
        raise open_cfw.OpenCFWError("release input lacks EVENOTA magic")
    count = open_cfw.u32le(image, 8)
    if not 1 <= count <= 32:
        raise open_cfw.OpenCFWError("release input has an invalid entry count")
    toc_end = (
        open_cfw.EVENOTA_TOC_OFFSET
        + count * open_cfw.EVENOTA_TOC_ENTRY_SIZE
    )
    trailer_end = toc_end + len(open_cfw.EVENOTA_TOC_TRAILER)
    if image[toc_end:trailer_end] != open_cfw.EVENOTA_TOC_TRAILER:
        raise open_cfw.OpenCFWError("release input has an invalid TOC trailer")

    entries: list[ParsedEntry] = []
    expected_body_offset = trailer_end
    for index in range(count):
        toc_offset = open_cfw.EVENOTA_TOC_OFFSET + index * open_cfw.EVENOTA_TOC_ENTRY_SIZE
        entry_id, body_offset, body_size, checksum = struct.unpack_from(
            "<IIII", image, toc_offset
        )
        if body_offset != expected_body_offset:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} is not contiguous"
            )
        body_end = body_offset + body_size
        if body_size < open_cfw.EVENOTA_COMPONENT_HEADER_SIZE or body_end > len(image):
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} exceeds the package"
            )
        header = image[body_offset:body_offset + open_cfw.EVENOTA_COMPONENT_HEADER_SIZE]
        payload_offset = body_offset + open_cfw.EVENOTA_COMPONENT_HEADER_SIZE
        payload = image[payload_offset:body_end]
        if open_cfw.u32le(header, 8) != len(payload):
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} payload size is invalid"
            )
        if open_cfw.u32le(header, 12) != checksum:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} checksum copies disagree"
            )
        if open_cfw.crc32c_msb(payload) != checksum:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} CRC-32C is invalid"
            )
        if open_cfw.u32le(header, 0x14) != open_cfw.EVENOTA_COMPONENT_MAGIC:
            raise open_cfw.OpenCFWError(
                f"release entry {index + 1} component magic is invalid"
            )
        filename = open_cfw.c_string(header, 0x30, 0x80)
        entries.append(
            ParsedEntry(
                index=index,
                entry_id=entry_id,
                toc_offset=toc_offset,
                body_offset=body_offset,
                body_size=body_size,
                payload_offset=payload_offset,
                payload_size=len(payload),
                filename=filename,
                type_id=open_cfw.u32le(header, 0x24),
                storage_type=open_cfw.u32le(header, 0x28),
                checksum=checksum,
            )
        )
        expected_body_offset = body_end
    if expected_body_offset != len(image):
        raise open_cfw.OpenCFWError("release entries do not close at EOF")
    return entries


def _package_version(image: bytes) -> str:
    return open_cfw.c_string(image, 0x30, 0x40)


def _main_entry(entries: list[ParsedEntry]) -> ParsedEntry:
    matches = [entry for entry in entries if entry.filename == MAIN_FILENAME]
    if len(matches) != 1:
        raise open_cfw.OpenCFWError(
            f"release input contains {len(matches)} Apollo-main components"
        )
    return matches[0]


def _profile_identity(
    record: dict[str, Any],
    profile_id: str,
    *,
    size_key: str,
    sha_key: str,
    label: str,
) -> tuple[int, str]:
    override = open_cfw.profile_pins(record, profile_id)
    selected = override if override is not None else record
    size = selected.get(size_key)
    digest = selected.get(sha_key)
    if (
        not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(character not in "0123456789abcdef" for character in digest)
    ):
        raise open_cfw.OpenCFWError(
            f"{label} lacks mandatory pins for profile {profile_id}"
        )
    return size, digest


def _receipt_entry(entry: ParsedEntry) -> dict[str, Any]:
    return {
        "entry_id": entry.entry_id,
        "type_id": entry.type_id,
        "filename": entry.filename,
        "storage_type": entry.storage_type,
        "package_offset": entry.body_offset,
        "package_offset_hex": open_cfw.hex_address(entry.body_offset),
        "entry_size": entry.body_size,
        "payload_size": entry.payload_size,
        "crc32c_msb": f"0x{entry.checksum:08X}",
    }


def _load_receipt(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise open_cfw.OpenCFWError(
            f"cannot read canonical source build receipt: {error}"
        ) from error
    if not isinstance(value, dict):
        raise open_cfw.OpenCFWError("canonical source build receipt is not an object")
    return value, sha256(raw)


def _require_regular_file_below(path: Path, root: Path, label: str) -> Path:
    """Resolve one trusted input without accepting symlinks or special files."""
    try:
        if path.is_symlink() or not path.is_file():
            raise open_cfw.OpenCFWError(f"{label} is not a regular non-symlink file")
        resolved = path.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except (OSError, ValueError) as error:
        raise open_cfw.OpenCFWError(f"{label} escapes the openCFW root") from error
    return resolved


def _canonical_build_lock_dir() -> Path:
    build_dir = CANONICAL_SOURCE_BUILD_REPORT.parent
    lock_path = build_dir / ".open-cfw-publish.lock"
    try:
        if build_dir.is_symlink() or not build_dir.is_dir():
            raise open_cfw.OpenCFWError(
                "canonical source build directory is not a regular directory"
            )
        resolved = build_dir.resolve(strict=True)
        resolved.relative_to(ROOT.resolve(strict=True))
        if lock_path.is_symlink() or (lock_path.exists() and not lock_path.is_file()):
            raise open_cfw.OpenCFWError(
                "canonical source generation lock is not a regular file"
            )
    except (OSError, ValueError) as error:
        raise open_cfw.OpenCFWError(
            "canonical source build directory escapes the openCFW root"
        ) from error
    return resolved


def _validate_canonical_source(
    image: bytes,
    *,
    source_manifest_path: Path,
    source_build_report_path: Path,
    toolchain_profile: str,
) -> dict[str, Any]:
    resolved_root = ROOT.resolve(strict=True)
    manifest_path = _require_regular_file_below(
        source_manifest_path, resolved_root, "release source manifest"
    )
    report_path = _require_regular_file_below(
        source_build_report_path, resolved_root, "release source build receipt"
    )
    canonical_manifest_path = _require_regular_file_below(
        CANONICAL_SOURCE_MANIFEST, resolved_root, "canonical source manifest"
    )
    canonical_report_path = _require_regular_file_below(
        CANONICAL_SOURCE_BUILD_REPORT,
        resolved_root,
        "canonical source build receipt",
    )
    if manifest_path != canonical_manifest_path:
        raise open_cfw.OpenCFWError("release source manifest is not canonical")
    if report_path != canonical_report_path:
        raise open_cfw.OpenCFWError("release source build receipt is not canonical")
    manifest = open_cfw.load_manifest(manifest_path)
    if (
        tuple(component.get("name") for component in manifest["components"])
        != CANONICAL_COMPONENTS
    ):
        raise open_cfw.OpenCFWError(
            "canonical release source must contain the exact six G2 components"
        )
    if manifest.get("target") != "Even Realities G2":
        raise open_cfw.OpenCFWError("canonical release source target changed")
    if manifest["package"].get("version") != SOURCE_PACKAGE_VERSION:
        raise open_cfw.OpenCFWError("canonical release source version changed")

    open_cfw.validate_evenota_image(image, manifest)
    entries = _parse_entries(image)
    package_size, package_sha = _profile_identity(
        manifest["package"],
        toolchain_profile,
        size_key="expected_size",
        sha_key="expected_sha256",
        label="canonical source package",
    )
    observed_package_sha = sha256(image)
    if (len(image), observed_package_sha) != (package_size, package_sha):
        raise open_cfw.OpenCFWError(
            "release input differs from the canonical pinned source package "
            f"for profile {toolchain_profile}"
        )

    for component, entry in zip(manifest["components"], entries):
        provider_size, provider_sha = _profile_identity(
            component["provider"],
            toolchain_profile,
            size_key="size",
            sha_key="sha256",
            label=f"{component['name']} source provider",
        )
        payload = image[entry.payload_offset:entry.payload_offset + entry.payload_size]
        if (len(payload), sha256(payload)) != (provider_size, provider_sha):
            raise open_cfw.OpenCFWError(
                f"release input provider identity changed: {component['name']}"
            )

    receipt, receipt_sha = _load_receipt(report_path)
    relative_manifest = manifest_path.relative_to(resolved_root).as_posix()
    manifest_sha = open_cfw.effective_manifest_sha256(manifest)
    manifest_sources = open_cfw.manifest_source_ledger(manifest_path)
    expected_provider_mode = "+".join(
        sorted({component["provider"]["kind"] for component in manifest["components"]})
    )
    expected_providers = []
    for component, entry in zip(manifest["components"], entries):
        payload = image[entry.payload_offset:entry.payload_offset + entry.payload_size]
        expected_providers.append(
            {
                "component": component["name"],
                "kind": component["provider"]["kind"],
                "path": component["provider"]["path"],
                "size": len(payload),
                "sha256": sha256(payload),
            }
        )
    expected_package_receipt = {
        "artifact": f"package/{manifest['package']['output_name']}",
        "size": package_size,
        "sha256": package_sha,
        "reference_sha256": package_sha,
        "byte_identical_to_reference": True,
    }
    if (
        receipt.get("schema_version") != 1
        or receipt.get("target") != manifest["target"]
        or receipt.get("manifest") != relative_manifest
        or receipt.get("manifest_sha256") != manifest_sha
        or receipt.get("manifest_sources") != manifest_sources
        or receipt.get("toolchain_profile") != toolchain_profile
        or receipt.get("provider_mode") != expected_provider_mode
        or receipt.get("providers") != expected_providers
        or receipt.get("package") != expected_package_receipt
        or receipt.get("entries") != [_receipt_entry(entry) for entry in entries]
    ):
        raise open_cfw.OpenCFWError(
            "canonical source build receipt does not authenticate the release input"
        )
    artifact_relative = receipt["package"]["artifact"]
    canonical_artifact_path = (
        report_path.parent / "package" / manifest["package"]["output_name"]
    )
    if artifact_relative != (
        Path("package") / manifest["package"]["output_name"]
    ).as_posix():
        raise open_cfw.OpenCFWError(
            "canonical source build receipt package path is not canonical"
        )
    artifact_path = _require_regular_file_below(
        canonical_artifact_path,
        report_path.parent,
        "canonical source build artifact",
    )

    # This independently reconstructs the package and every region from the
    # manifest/providers, requires exact plan/report objects, and authenticates
    # the exhaustive managed artifact set through SHA256SUMS.  A plausible
    # standalone JSON receipt is therefore insufficient for release.
    verified_receipt = open_cfw.verify_artifacts_with_lock_held(
        manifest_path,
        report_path.parent,
        toolchain_profile=toolchain_profile,
    )
    if verified_receipt != receipt:
        raise open_cfw.OpenCFWError(
            "canonical source build receipt is not the verified generation receipt"
        )
    receipt_after_verification, receipt_sha_after_verification = _load_receipt(
        report_path
    )
    if (
        receipt_after_verification != receipt
        or receipt_sha_after_verification != receipt_sha
    ):
        raise open_cfw.OpenCFWError(
            "canonical source build receipt changed during verification"
        )
    try:
        receipt_artifact = artifact_path.read_bytes()
    except OSError as error:
        raise open_cfw.OpenCFWError(
            f"canonical source build receipt package is unavailable: {error}"
        ) from error
    if receipt_artifact != image:
        raise open_cfw.OpenCFWError(
            "release input differs from the package referenced by its build receipt"
        )
    if receipt.get("unresolved_region_count") != 0:
        raise open_cfw.OpenCFWError(
            "canonical source build receipt retains unresolved flash regions"
        )
    for field in ("placed_region_count", "container_region_count"):
        value = receipt.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise open_cfw.OpenCFWError(
                f"canonical source build receipt has invalid {field}"
            )
    return {
        "manifest": relative_manifest,
        "manifest_sha256": manifest_sha,
        "manifest_sources": manifest_sources,
        "build_receipt": report_path.relative_to(resolved_root).as_posix(),
        "build_receipt_sha256": receipt_sha,
        "build_artifact": artifact_path.relative_to(resolved_root).as_posix(),
        "toolchain_profile": toolchain_profile,
        "package_size": package_size,
        "package_sha256": package_sha,
    }


def _transform_validated_image(image: bytes) -> tuple[bytes, dict[str, Any]]:
    """Apply the fixed release version transform to an already-bound image."""
    if _package_version(image) != SOURCE_PACKAGE_VERSION:
        raise open_cfw.OpenCFWError(
            f"release input version must be {SOURCE_PACKAGE_VERSION}"
        )
    entries = _parse_entries(image)
    main = _main_entry(entries)
    main_before = image[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    open_cfw.validate_apollo_main(main_before)
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        actual = main_before[relative_offset:relative_offset + len(SOURCE_RUNTIME_FIELD)]
        if actual != SOURCE_RUNTIME_FIELD:
            raise open_cfw.OpenCFWError(
                f"{label} version field changed at Apollo offset 0x{relative_offset:08X}"
            )

    released = bytearray(image)
    released[0x30:0x40] = open_cfw.fixed_ascii(
        RELEASE_PACKAGE_VERSION, 16, "release package version"
    )
    absolute_fields: dict[str, int] = {}
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        absolute_offset = main.payload_offset + relative_offset
        absolute_fields[label] = absolute_offset
        released[
            absolute_offset:absolute_offset + len(RELEASE_RUNTIME_FIELD)
        ] = RELEASE_RUNTIME_FIELD

    main_after = released[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    nested_crc = zlib.crc32(main_after[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", released, main.payload_offset + 4, nested_crc)
    main_after = released[
        main.payload_offset:main.payload_offset + main.payload_size
    ]
    component_crc = open_cfw.crc32c_msb(main_after)
    struct.pack_into("<I", released, main.toc_offset + 12, component_crc)
    struct.pack_into("<I", released, main.body_offset + 12, component_crc)

    result = bytes(released)
    if len(result) != len(image) or _package_version(result) != RELEASE_PACKAGE_VERSION:
        raise open_cfw.OpenCFWError("release transform changed package layout")
    reparsed = _parse_entries(result)
    reparsed_main = _main_entry(reparsed)
    released_main = result[
        reparsed_main.payload_offset:reparsed_main.payload_offset + reparsed_main.payload_size
    ]
    open_cfw.validate_apollo_main(released_main)
    for label, relative_offset in RUNTIME_VERSION_FIELDS.items():
        actual = released_main[
            relative_offset:relative_offset + len(RELEASE_RUNTIME_FIELD)
        ]
        if actual != RELEASE_RUNTIME_FIELD:
            raise open_cfw.OpenCFWError(f"{label} release version verification failed")

    report: dict[str, Any] = {
        "schema_version": 1,
        "source": {
            "version": SOURCE_PACKAGE_VERSION,
            "size": len(image),
            "sha256": sha256(image),
        },
        "release": {
            "version": RELEASE_PACKAGE_VERSION,
            "runtime_version": "2.2.6.0",
            "size": len(result),
            "sha256": sha256(result),
        },
        "apollo_main": {
            "payload_offset": main.payload_offset,
            "payload_size": main.payload_size,
            "source_sha256": sha256(main_before),
            "release_sha256": sha256(released_main),
            "nested_crc32": f"0x{nested_crc:08X}",
            "component_crc32c_msb": f"0x{component_crc:08X}",
            "runtime_version_fields": {
                label: {
                    "payload_offset": RUNTIME_VERSION_FIELDS[label],
                    "package_offset": absolute_fields[label],
                }
                for label in RUNTIME_VERSION_FIELDS
            },
        },
    }
    return result, report


def transform(
    image: bytes,
    *,
    source_manifest_path: Path,
    source_build_report_path: Path,
    toolchain_profile: str,
) -> tuple[bytes, dict[str, Any]]:
    """Transform only the canonical, receipt-authenticated six-entry source."""
    # Cooperate with open_cfw's transactional publisher so validation cannot
    # span two source generations.  All bytes used by the transform are then
    # held in memory after the lock is released.
    with open_cfw.output_generation_lock(_canonical_build_lock_dir()):
        source_identity = _validate_canonical_source(
            image,
            source_manifest_path=source_manifest_path,
            source_build_report_path=source_build_report_path,
            toolchain_profile=toolchain_profile,
        )
    result, report = _transform_validated_image(image)
    report["canonical_source"] = source_identity
    return result, report


def transform_test_only_synthetic(image: bytes) -> tuple[bytes, dict[str, Any]]:
    """Exercise transform mechanics without the production source gate in tests."""
    return _transform_validated_image(image)


def assert_redistribution_authorized() -> None:
    """Fail closed before writing a public-release artifact."""
    try:
        audit_g2_release_licensing.assert_release_authorized()
    except audit_g2_release_licensing.ReleaseAuthorityError as error:
        raise open_cfw.OpenCFWError(str(error)) from error


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


def _validate_cli_destinations(
    input_path: Path,
    output_path: Path,
    report_path: Path | None,
) -> None:
    """Prevent release outputs from replacing inputs or the source generation."""
    source_build_dir = CANONICAL_SOURCE_BUILD_REPORT.parent.resolve()
    protected = {
        input_path.resolve(),
        CANONICAL_SOURCE_MANIFEST.resolve(),
        CANONICAL_SOURCE_BUILD_REPORT.resolve(),
    }
    destinations = [output_path]
    if report_path is not None:
        destinations.append(report_path)
    resolved_destinations = [path.resolve() for path in destinations]
    if len(set(resolved_destinations)) != len(resolved_destinations):
        raise open_cfw.OpenCFWError("release output and report must be distinct")
    for destination in resolved_destinations:
        if destination in protected:
            raise open_cfw.OpenCFWError("release destination aliases a protected input")
        try:
            destination.relative_to(source_build_dir)
        except ValueError:
            continue
        raise open_cfw.OpenCFWError(
            "release destination must not modify the canonical source build"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--toolchain-profile",
        default=None,
        help=(
            "reviewed source-build profile (defaults to OPENCFW_TOOLCHAIN_PROFILE "
            "or apple-clang)"
        ),
    )
    args = parser.parse_args(argv)

    assert_redistribution_authorized()
    _validate_cli_destinations(args.input, args.output, args.report)
    profile_id = open_cfw.resolve_toolchain_profile_id(args.toolchain_profile)
    result, report = transform(
        args.input.read_bytes(),
        source_manifest_path=CANONICAL_SOURCE_MANIFEST,
        source_build_report_path=CANONICAL_SOURCE_BUILD_REPORT,
        toolchain_profile=profile_id,
    )
    _atomic_write(args.output, result)
    if args.report is not None:
        _atomic_write(
            args.report,
            (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
    print(f"Built {args.output}")
    print(f"  size: {len(result)} bytes")
    print(f"  sha256: {report['release']['sha256']}")
    print("  runtime version: 2.2.6.0 (settings and product-test 0x24)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
