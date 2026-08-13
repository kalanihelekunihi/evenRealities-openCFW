#!/usr/bin/env python3
"""Compile and inject the source-owned G2 bootloader core overlay.

This builder performs local file and compiler operations only. It emits a raw
bootloader provider for the existing EVENOTA assembler; it does not assemble,
sign, transmit, flash, erase, reset, or otherwise communicate with hardware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
OPENCFW_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402
    BuildError,
    DEFAULT_TOOLCHAIN_PROFILE,
    align_up,
    append_isolated_leaves,
    append_relocated_leaves,
    compile_isolated_leaf,
    compile_overlay,
    decode_thumb_branch,
    encode_thumb_b_w,
    record_leaf_profile_pins,
    resolve_below,
    resolve_toolchain_include_dirs,
    resolve_toolchain_profile,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write(
        path,
        (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BuildError(f"cannot read {path}: {error}") from error
    if config.get("schema_version") != 1:
        raise BuildError("unsupported bootloader-overlay schema")
    if config.get("target") != "apollo_bootloader":
        raise BuildError("bootloader overlay target must be apollo_bootloader")
    if config.get("preamble_bytes") != 0:
        raise BuildError("the G2 bootloader provider is a raw image")
    return config


def verify_expected(
    label: str,
    actual_size: int,
    actual_sha256: str,
    expected: dict[str, Any],
) -> None:
    expected_size = expected.get(f"{label}_size")
    expected_sha256 = expected.get(f"{label}_sha256")
    if actual_size != expected_size:
        raise BuildError(
            f"{label} size {actual_size} differs from reviewed {expected_size}"
        )
    if actual_sha256 != expected_sha256:
        raise BuildError(
            f"{label} SHA-256 {actual_sha256} differs from reviewed "
            f"{expected_sha256}"
        )


def validate_vector(
    image: bytes,
    *,
    run_base: int,
    image_end_exclusive: int,
) -> dict[str, int | str]:
    if len(image) < 8:
        raise BuildError("bootloader image is too short for a vector table")
    stack_pointer, reset_vector = struct.unpack_from("<II", image, 0)
    if not 0x20000000 <= stack_pointer <= 0x2007FFFF:
        raise BuildError("bootloader initial stack pointer is outside Apollo SRAM")
    reset_entry = reset_vector & ~1
    if reset_vector & 1 == 0:
        raise BuildError("bootloader reset vector is not a Thumb address")
    if not run_base <= reset_entry < image_end_exclusive:
        raise BuildError("bootloader reset vector is outside the provider")
    return {
        "initial_stack_pointer": stack_pointer,
        "initial_stack_pointer_hex": f"0x{stack_pointer:08X}",
        "reset_vector": reset_vector,
        "reset_vector_hex": f"0x{reset_vector:08X}",
        "reset_entry": reset_entry,
        "reset_entry_hex": f"0x{reset_entry:08X}",
    }


def patch_bootloader(
    *,
    base: bytes,
    overlay: bytes,
    functions: dict[str, dict[str, int]],
    config: dict[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    run_base = int(config["run_base"])
    partition_end = int(config["partition_end_exclusive"])
    alignment = int(config["alignment"])
    padding_byte = int(config["padding_byte"])
    if not 0 <= padding_byte <= 0xFF:
        raise BuildError("padding_byte must fit in one byte")
    if partition_end <= run_base:
        raise BuildError("bootloader partition is empty or inverted")
    if run_base + len(base) > partition_end:
        raise BuildError("stock bootloader exceeds its declared partition")

    stock_end = run_base + len(base)
    overlay_address = align_up(stock_end, alignment)
    configured_address = int(config["placement"]["runtime_address"])
    if config["placement"].get("strategy") != (
        "fixed_aligned_after_authenticated_stock_eof"
    ):
        raise BuildError("unsupported bootloader overlay placement strategy")
    if overlay_address != configured_address:
        raise BuildError(
            "reviewed overlay address no longer equals aligned stock EOF"
        )
    padding_size = overlay_address - stock_end
    provider_end = overlay_address + len(overlay)
    if provider_end > partition_end:
        raise BuildError("source overlay overlaps the Apollo main application")

    vector = validate_vector(
        base,
        run_base=run_base,
        image_end_exclusive=stock_end,
    )
    patched = bytearray(base)
    patched.extend(bytes((padding_byte,)) * padding_size)
    patched.extend(overlay)

    reviewed_sites: list[tuple[int, int, dict[str, Any]]] = []
    for site in config["patch_sites"]:
        address = int(site["runtime_address"])
        offset = address - run_base
        size = int(site["expected_size"])
        if size < 4 or size % 2 or offset < 0 or offset + size > len(base):
            raise BuildError(
                "bootloader B.W patch sites must be even stock spans "
                "of at least four bytes"
            )
        reviewed_sites.append((offset, size, site))
    reviewed_sites.sort(key=lambda item: item[0])
    for previous, current in zip(reviewed_sites, reviewed_sites[1:]):
        if previous[0] + previous[1] > current[0]:
            raise BuildError("bootloader source-entry patch spans overlap")

    patched_sites: list[dict[str, Any]] = []
    for offset, size, site in reviewed_sites:
        if site.get("branch") != "b_w":
            raise BuildError("bootloader entry replacements must use B.W")
        address = int(site["runtime_address"])
        expected = bytes(base[offset:offset + size])
        expected_digest = sha256(expected)
        if expected_digest != site["expected_sha256"]:
            raise BuildError(
                f"{site['name']}: stock span SHA-256 differs from config"
            )
        function = functions.get(site["target_function"])
        if function is None:
            raise BuildError(f"missing function {site['target_function']}")
        target = overlay_address + int(function["offset"])
        redirect = encode_thumb_b_w(address, target)
        replacement = redirect + b"\x00\xbf" * ((size - 4) // 2)
        decoded = decode_thumb_branch(address, redirect, link=False)
        if decoded != target:
            raise BuildError("generated bootloader branch failed round-trip")
        patched[offset:offset + size] = replacement
        patched_sites.append(
            {
                "name": site["name"],
                "runtime_address": address,
                "runtime_address_hex": f"0x{address:08X}",
                "file_offset": offset,
                "expected_size": size,
                "expected_sha256": expected_digest,
                "replacement_hex": replacement.hex(),
                "branch": "b_w",
                "displacement": target - (address + 4),
                "target_function": site["target_function"],
                "target_address": target,
                "target_address_hex": f"0x{target:08X}",
            }
        )

    details: dict[str, Any] = {
        "raw_provider": True,
        "internal_header_bytes": 0,
        "run_base": run_base,
        "run_base_hex": f"0x{run_base:08X}",
        "partition_end_exclusive": partition_end,
        "partition_end_exclusive_hex": f"0x{partition_end:08X}",
        "stock_end_exclusive": stock_end,
        "stock_end_exclusive_hex": f"0x{stock_end:08X}",
        "stock_headroom_bytes": partition_end - stock_end,
        "alignment": alignment,
        "padding_byte": padding_byte,
        "padding_size": padding_size,
        "padding_address": stock_end,
        "padding_address_hex": f"0x{stock_end:08X}",
        "overlay_runtime_address": overlay_address,
        "overlay_runtime_address_hex": f"0x{overlay_address:08X}",
        "overlay_end_exclusive": provider_end,
        "overlay_end_exclusive_hex": f"0x{provider_end:08X}",
        "remaining_headroom_bytes": partition_end - provider_end,
        "patched_sites": patched_sites,
        "vector": vector,
    }
    return bytes(patched), details


def provider_regions(
    *,
    base_size: int,
    primary_overlay_size: int,
    overlay_size: int,
    appended_leaf_reports: list[dict[str, Any]],
    details: dict[str, Any],
) -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    cursor = 0
    sites = sorted(details["patched_sites"], key=lambda item: item["file_offset"])
    for site in sites:
        offset = int(site["file_offset"])
        size = int(site["expected_size"])
        if offset < cursor:
            raise BuildError("bootloader source-entry patch spans overlap")
        if offset > cursor:
            regions.append(
                {
                    "name": f"opaque_before_{site['name']}",
                    "file_offset": cursor,
                    "size": offset - cursor,
                    "target_address": details["run_base"] + cursor,
                    "address_status": "official_blob",
                }
            )
        regions.append(
            {
                "name": f"{site['name']}_source_redirect",
                "file_offset": offset,
                "size": size,
                "target_address": site["runtime_address"],
                "address_status": "generated_source_entry_replacement",
            }
        )
        cursor = offset + size
    if cursor < base_size:
        regions.append(
            {
                "name": "opaque_after_source_redirects",
                "file_offset": cursor,
                "size": base_size - cursor,
                "target_address": details["run_base"] + cursor,
                "address_status": "official_blob",
            }
        )
    if details["padding_size"]:
        regions.append(
            {
                "name": "source_overlay_alignment_padding",
                "file_offset": base_size,
                "size": details["padding_size"],
                "target_address": details["padding_address"],
                "address_status": "generated_alignment",
            }
        )

    overlay_file_offset = base_size + details["padding_size"]
    overlay_runtime_address = int(details["overlay_runtime_address"])
    if primary_overlay_size:
        regions.append(
            {
                "name": "bootloader_core_source_overlay",
                "file_offset": overlay_file_offset,
                "size": primary_overlay_size,
                "target_address": overlay_runtime_address,
                "address_status": "source_compiled",
            }
        )

    overlay_cursor = primary_overlay_size
    for report in appended_leaf_reports:
        placement = report.get("placement")
        extraction = report.get("extraction")
        if not isinstance(placement, dict) or not isinstance(extraction, dict):
            raise BuildError("appended leaf report lacks placement metadata")
        function_name = extraction.get("function")
        if not isinstance(function_name, str) or not function_name:
            raise BuildError("appended leaf report lacks a function name")
        padding_before = int(placement["padding_before"])
        leaf_offset = int(placement["offset"])
        leaf_size = int(placement["size"])
        if (
            padding_before < 0
            or leaf_size < 1
            or leaf_offset != overlay_cursor + padding_before
        ):
            raise BuildError("appended leaf placement does not partition overlay")
        if padding_before:
            regions.append(
                {
                    "name": f"{function_name}_alignment_padding",
                    "file_offset": overlay_file_offset + overlay_cursor,
                    "size": padding_before,
                    "target_address": overlay_runtime_address + overlay_cursor,
                    "address_status": "generated_alignment",
                }
            )
        regions.append(
            {
                "name": f"{function_name}_source_leaf",
                "file_offset": overlay_file_offset + leaf_offset,
                "size": leaf_size,
                "target_address": overlay_runtime_address + leaf_offset,
                "address_status": "source_compiled",
            }
        )
        overlay_cursor = leaf_offset + leaf_size
    if overlay_cursor != overlay_size:
        raise BuildError("source and appended-leaf regions do not cover overlay")
    return regions


def build(
    *,
    root: Path,
    config_path: Path,
    output_dir: Path,
    clang: str,
    toolchain_profile: str | None = None,
    record_profile: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    if toolchain_profile is None:
        toolchain_profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
    effective_toolchain, effective_expected, resolved_profile = (
        resolve_toolchain_profile(
            config,
            toolchain_profile,
            record=record_profile,
        )
    )
    config = {
        **config,
        "toolchain": effective_toolchain,
        "expected": effective_expected,
    }
    include_dirs, normalized_include_dirs = resolve_toolchain_include_dirs(
        root,
        config["toolchain"],
    )
    isolated_leaf_configs = config.get("isolated_leaves", [])
    if (
        not isinstance(isolated_leaf_configs, list)
        or any(not isinstance(item, dict) for item in isolated_leaf_configs)
    ):
        raise BuildError("isolated_leaves must be a list of records")
    isolated_function_names = [
        item.get("function") for item in isolated_leaf_configs
    ]
    if any(not isinstance(name, str) for name in isolated_function_names):
        raise BuildError("every isolated leaf requires a function name")
    if len(set(isolated_function_names)) != len(isolated_function_names):
        raise BuildError("isolated leaf function names must be unique")
    relocated_leaf_configs = config.get("relocated_leaves", [])
    if (
        not isinstance(relocated_leaf_configs, list)
        or any(not isinstance(item, dict) for item in relocated_leaf_configs)
    ):
        raise BuildError("relocated_leaves must be a list of records")
    relocated_function_names = [
        item.get("function") for item in relocated_leaf_configs
    ]
    if any(not isinstance(name, str) for name in relocated_function_names):
        raise BuildError("every relocated leaf requires a function name")
    if len(set(relocated_function_names)) != len(relocated_function_names):
        raise BuildError("relocated leaf function names must be unique")
    configured_functions = config.get("functions")
    if (
        not isinstance(configured_functions, dict)
        or any(
            not isinstance(name, str) or not isinstance(details, dict)
            for name, details in configured_functions.items()
        )
    ):
        raise BuildError(
            "bootloader overlay functions must map names to ABI records"
        )
    unknown_isolated_functions = (
        set(isolated_function_names) - set(configured_functions)
    )
    if unknown_isolated_functions:
        raise BuildError(
            "isolated leaves are absent from the bootloader function ABI: "
            f"{sorted(unknown_isolated_functions)}"
        )
    unknown_relocated_functions = (
        set(relocated_function_names) - set(configured_functions)
    )
    if unknown_relocated_functions:
        raise BuildError(
            "relocated leaves are absent from the bootloader function ABI: "
            f"{sorted(unknown_relocated_functions)}"
        )
    ambiguous_appended_functions = set(isolated_function_names) & set(
        relocated_function_names
    )
    if ambiguous_appended_functions:
        raise BuildError(
            "bootloader functions cannot be both isolated and relocated "
            f"leaves: {sorted(ambiguous_appended_functions)}"
        )
    primary_functions = set(configured_functions) - set(
        isolated_function_names
    ) - set(relocated_function_names)
    if not primary_functions:
        raise BuildError(
            "bootloader overlay requires at least one primary source function"
        )

    source_configs = config.get("sources")
    if (
        not isinstance(source_configs, list)
        or not source_configs
        or any(not isinstance(item, dict) for item in source_configs)
    ):
        raise BuildError("bootloader overlay requires one or more sources")
    primary_source_paths = {
        resolve_below(root, item["path"]).resolve()
        for item in source_configs
        if isinstance(item.get("path"), str)
    }
    relocated_source_paths = {
        resolve_below(root, item["source"]["path"]).resolve()
        for item in relocated_leaf_configs
        if isinstance(item.get("source"), dict)
        and isinstance(item["source"].get("path"), str)
    }
    ambiguous_relocated_sources = (
        primary_source_paths & relocated_source_paths
    )
    if ambiguous_relocated_sources:
        raise BuildError(
            "relocated leaf source cannot enter the primary combined "
            "translation unit: "
            f"{sorted(str(path) for path in ambiguous_relocated_sources)}"
        )
    source_paths: list[Path] = []
    source_records: list[dict[str, Any]] = []
    for source_config in source_configs:
        source_path = resolve_below(root, source_config["path"])
        source = source_path.read_bytes()
        source_digest = sha256(source)
        if source_digest != source_config["sha256"]:
            raise BuildError(
                f"{source_config['path']}: source SHA-256 differs from config"
            )
        source_paths.append(source_path)
        source_records.append(
            {
                **{
                    key: value
                    for key, value in source_config.items()
                    if key != "sha256"
                },
                "size": len(source),
                "sha256": source_digest,
            }
        )

    base_path = resolve_below(root, config["base"]["path"])
    base = base_path.read_bytes()
    base_digest = sha256(base)
    if (
        len(base) != config["base"]["size"]
        or base_digest != config["base"]["sha256"]
    ):
        raise BuildError("official bootloader provider differs from overlay.json")

    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"openCFW-{config['name']}-"
    ) as directory:
        temporary_root = Path(directory)
        if len(source_paths) == 1:
            translation_unit = source_paths[0]
        else:
            translation_unit = temporary_root / "overlay_translation_unit.c"
            includes: list[str] = []
            for source_path in source_paths:
                source_text = str(source_path)
                if '"' in source_text or "\\" in source_text:
                    raise BuildError(
                        "source path cannot be represented in a C include"
                    )
                includes.append(f'#include "{source_text}"')
            atomic_write(
                translation_unit,
                ("\n".join(includes) + "\n").encode("utf-8"),
            )
        object_path = temporary_root / "overlay.o"
        overlay, functions, version, link_report = compile_overlay(
            clang=clang,
            source_path=translation_unit,
            object_path=object_path,
            config=config,
            include_dirs=include_dirs,
            expected_functions=primary_functions,
        )
        primary_overlay_size = len(overlay)
        isolated_leaves = []
        for index, leaf_config in enumerate(isolated_leaf_configs):
            isolated_leaves.append(
                compile_isolated_leaf(
                    root=root,
                    clang=clang,
                    leaf_config=leaf_config,
                    object_path=temporary_root / f"isolated-leaf-{index}.o",
                    toolchain_profile=resolved_profile,
                    record=record_profile,
                )
            )
        (
            overlay,
            functions,
            link_report,
            isolated_leaf_reports,
        ) = append_isolated_leaves(
            overlay=overlay,
            functions=functions,
            link_report=link_report,
            leaves=isolated_leaves,
        )
        (
            overlay,
            functions,
            link_report,
            relocated_leaf_reports,
        ) = append_relocated_leaves(
            root=root,
            clang=clang,
            overlay=overlay,
            overlay_runtime_address=int(
                config["placement"]["runtime_address"]
            ),
            functions=functions,
            link_report=link_report,
            leaf_configs=relocated_leaf_configs,
            object_root=temporary_root,
            toolchain_profile=resolved_profile,
            record=record_profile,
        )

    # The compiled function ABI (offsets/sizes within the overlay) is
    # toolchain-specific.  Under a non-canonical profile, verify against that
    # profile's recorded ABI; while recording, capture the observed ABI.
    effective_function_abi = configured_functions
    if not record_profile and resolved_profile != DEFAULT_TOOLCHAIN_PROFILE:
        function_profiles = config.get("function_profiles")
        if isinstance(function_profiles, dict) and resolved_profile in (
            function_profiles
        ):
            effective_function_abi = function_profiles[resolved_profile]
    if not record_profile:
        for name, expected_function in effective_function_abi.items():
            function = functions[name]
            if (
                function["offset"] != expected_function["expected_offset"]
                or function["size"] != expected_function["expected_size"]
            ):
                raise BuildError(
                    f"{name}: compiled ABI span differs from config "
                    f"(profile {resolved_profile})"
                )

    overlay_digest = sha256(overlay)
    if not record_profile:
        verify_expected(
            "overlay", len(overlay), overlay_digest, config["expected"]
        )
    provider, details = patch_bootloader(
        base=base,
        overlay=overlay,
        functions=functions,
        config=config,
    )
    provider_digest = sha256(provider)
    if not record_profile:
        verify_expected(
            "component",
            len(provider),
            provider_digest,
            config["expected"],
        )

    overlay_name = config["overlay_artifact"]
    provider_name = config["provider_artifact"]
    if any(
        not isinstance(name, str) or Path(name).name != name
        for name in (overlay_name, provider_name)
    ):
        raise BuildError("artifact names must be plain filenames")
    overlay_path = output_dir / overlay_name
    provider_path = output_dir / provider_name
    atomic_write(overlay_path, overlay)
    atomic_write(provider_path, provider)

    regions = provider_regions(
        base_size=len(base),
        primary_overlay_size=primary_overlay_size,
        overlay_size=len(overlay),
        appended_leaf_reports=(
            isolated_leaf_reports + relocated_leaf_reports
        ),
        details=details,
    )
    generated_isolated_alignment_bytes = sum(
        int(report["placement"]["padding_before"])
        for report in isolated_leaf_reports
    )
    generated_relocated_alignment_bytes = sum(
        int(report["placement"]["padding_before"])
        for report in relocated_leaf_reports
    )
    source_owned_bytes = primary_overlay_size + sum(
        int(report["placement"]["size"])
        for report in isolated_leaf_reports + relocated_leaf_reports
    )
    provider_contract = {
        "schema_version": 1,
        "component": "apollo_bootloader",
        "firmware_version": config["firmware_version"],
        "provider": {
            "kind": "source_build",
            "path": (
                "components/bootloader/core_overlay/build/"
                + provider_name
            ),
            "size": len(provider),
            "sha256": provider_digest,
        },
        "regions": regions,
        "transport": config["transport_contract"],
        "hardware_operations": [],
    }
    atomic_write_json(output_dir / "provider-contract.json", provider_contract)

    toolchain_report = {
        "executable": clang,
        "version": version,
        "profile": resolved_profile,
        "target": config["toolchain"]["target"],
        "flags": config["toolchain"]["flags"],
    }
    if normalized_include_dirs is not None:
        toolchain_report["include_dirs"] = normalized_include_dirs

    report = {
        "schema_version": 1,
        "name": config["name"],
        "firmware_version": config["firmware_version"],
        "sources": source_records,
        "toolchain": toolchain_report,
        "base": {
            "path": config["base"]["path"],
            "size": len(base),
            "sha256": base_digest,
        },
        "overlay": {
            "artifact": overlay_name,
            "size": len(overlay),
            "sha256": overlay_digest,
            "functions": functions,
            "link": link_report,
            **details,
        },
        "component": {
            "artifact": provider_name,
            "size": len(provider),
            "sha256": provider_digest,
            "opaque_base_bytes": (
                len(base)
                - sum(site["expected_size"] for site in details["patched_sites"])
            ),
            "generated_patch_site_bytes": sum(
                site["expected_size"] for site in details["patched_sites"]
            ),
            "generated_alignment_bytes": (
                details["padding_size"]
                + generated_isolated_alignment_bytes
                + generated_relocated_alignment_bytes
            ),
            "generated_stock_to_overlay_alignment_bytes": (
                details["padding_size"]
            ),
            "generated_isolated_alignment_bytes": (
                generated_isolated_alignment_bytes
            ),
            "generated_relocated_alignment_bytes": (
                generated_relocated_alignment_bytes
            ),
            "source_owned_bytes": source_owned_bytes,
        },
        "provider_contract": provider_contract,
        "safety": {
            "hardware_operations": [],
            "package_assembly_performed": False,
            "flashing_performed": False,
            "erasing_performed": False,
        },
    }
    if isolated_leaf_reports:
        report["isolated_leaves"] = isolated_leaf_reports
    if relocated_leaf_reports:
        report["relocated_leaves"] = relocated_leaf_reports
    if len(source_records) == 1:
        report["source"] = source_records[0]
    atomic_write_json(output_dir / "build-report.json", report)
    return report


def record_profile_pins(
    config_path: Path,
    profile_id: str,
    report: dict[str, Any],
) -> None:
    """Persist observed overlay/component, function-ABI, and leaf pins.

    Mirrors the Apollo-main recorder, adding the bootloader's per-function ABI
    table.  The canonical apple-clang pins are never touched.
    """

    if profile_id == DEFAULT_TOOLCHAIN_PROFILE:
        raise BuildError(
            "cannot record the canonical apple-clang profile; its pins are "
            "the reviewed reference"
        )
    data = json.loads(config_path.read_text(encoding="utf-8"))
    version = report["toolchain"]["version"]

    profiles = data.setdefault("toolchain_profiles", {})
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        profile = {}
    profile["reviewed_version_prefix"] = version
    profile["expected"] = {
        "overlay_size": report["overlay"]["size"],
        "overlay_sha256": report["overlay"]["sha256"],
        "component_size": report["component"]["size"],
        "component_sha256": report["component"]["sha256"],
    }
    profiles[profile_id] = profile

    # Per-function compiled ABI (offset/size within the overlay).
    observed_functions = report["overlay"]["functions"]
    function_profiles = data.setdefault("function_profiles", {})
    function_profiles[profile_id] = {
        name: {
            "expected_offset": int(observed_functions[name]["offset"]),
            "expected_size": int(observed_functions[name]["size"]),
        }
        for name in data.get("functions", {})
        if name in observed_functions
    }

    record_leaf_profile_pins(data, profile_id, version, report)

    atomic_write(
        config_path,
        (json.dumps(data, indent=2) + "\n").encode("utf-8"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=COMPONENT_ROOT / "overlay.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=COMPONENT_ROOT / "build",
    )
    parser.add_argument(
        "--clang",
        default=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
    )
    parser.add_argument(
        "--toolchain-profile",
        default=os.environ.get("OPENCFW_TOOLCHAIN_PROFILE"),
        help=(
            "reviewed toolchain profile to build and verify against "
            f"(default {DEFAULT_TOOLCHAIN_PROFILE!r})"
        ),
    )
    parser.add_argument(
        "--record-profile",
        action="store_true",
        help=(
            "capture the observed overlay/component, function-ABI, and leaf "
            "pins into toolchain_profiles[<--toolchain-profile>]"
        ),
    )
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    if args.record_profile and not args.toolchain_profile:
        parser.error("--record-profile requires --toolchain-profile")
    report = build(
        root=OPENCFW_ROOT,
        config_path=config_path,
        output_dir=args.output_dir.resolve(),
        clang=args.clang,
        toolchain_profile=args.toolchain_profile,
        record_profile=args.record_profile,
    )
    if args.record_profile:
        record_profile_pins(config_path, args.toolchain_profile, report)
        print(
            f"Recorded toolchain profile {args.toolchain_profile!r} into "
            f"{config_path.name}"
        )
    overlay = report["overlay"]
    component = report["component"]
    print(
        f"Built {report['name']}: {overlay['size']} overlay bytes at "
        f"{overlay['overlay_runtime_address_hex']}"
    )
    print(
        f"  raw provider: {component['size']} bytes, sha256 "
        f"{component['sha256']}"
    )
    print("  hardware operations: none")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"openCFW bootloader component build: error: {error}", file=sys.stderr)
        raise SystemExit(1)
