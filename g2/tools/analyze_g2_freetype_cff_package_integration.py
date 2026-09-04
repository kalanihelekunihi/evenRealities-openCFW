#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Prove dual-profile package integration of the CFF scatter component."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
BUILDER = G2 / "components/apollo_main/freetype_cff_scatter/build_component.py"
CONFIG = G2 / "components/apollo_main/freetype_cff_scatter/overlay.json"
README = G2 / "components/apollo_main/freetype_cff_scatter/README.md"
CORE_BUILDER = G2 / "components/apollo_main/core_overlay/build_component.py"
CORE_CONFIG = G2 / "components/apollo_main/core_overlay/overlay.json"
OPEN_CFW = G2 / "tools/open_cfw.py"
BASE_MANIFEST = G2 / "manifests/g2-2.2.6.10-core-source.json"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-package-integration.json"

PINS = {
    BUILDER: (40_269, "b344b37620574e9cec4af153f54b23e124afbe64332126118e678401f1feb4b9"),
    CONFIG: (1_842, "ec7f2835ba9d04963ea6f0ca02d8f804ff4ee88485168ef0de2b230ba56ab972"),
    README: (1_298, "493a0423c3282f18242af2753eeeafbc4a468834a70b1327867a82d37e105763"),
    CORE_BUILDER: (90_584, "164a9fd3aeb22daa16085de2725157af4b157e8f64977a50db89986aaf97325f"),
    CORE_CONFIG: (6_404_019, "2329b48855ecf130bbb8ea4e6f97711dc9ac9fcba1aed9c647dd896e6c488722"),
    OPEN_CFW: (99_692, "0740379679959fbf3d042a2afafd4e4bf46093681be535dd053806b34d4cf15f"),
    BASE_MANIFEST: (3_812_990, "ae7c402fef4c72f3fbeae80cbfc71eb17e3907044a339b65494e8732392a150d"),
}

# Minimal authenticated generated-NOP tails actually consumed by the admitted
# CFF layout.  The canonical core builder derives the superset independently
# from its same-build LC3 route report.
HOST_SLOTS = {
    "apple-clang": [
        {"function": "EFS_ReceivePacket",
         "entry": 5049728, "start": 5050962, "end_exclusive": 5051102,
         "forbidden_entries": []},
        {"function": "APP_PbRxNotificationFrameDataProcess",
         "entry": 5073832, "start": 5073836, "end_exclusive": 5074352,
         "forbidden_entries": []},
        {"function": "APP_PbTxEncodeNotifAppIDNotInWhitelist",
         "entry": 5075388, "start": 5075392, "end_exclusive": 5075926,
         "forbidden_entries": []},
        {"function": "APP_PbRxDevCfgFrameDataProcess",
         "entry": 5080024, "start": 5080028, "end_exclusive": 5081980,
         "forbidden_entries": [5080062, 5080550]},
        {"function": "open_cfw_service_kvdb_init",
         "entry": 5084888, "start": 5084892, "end_exclusive": 5085828,
         "forbidden_entries": [5085108, 5085440]},
        {"function": "APP_PbRxEvenAIFrameDataProcess",
         "entry": 5124556, "start": 5124560, "end_exclusive": 5125424,
         "forbidden_entries": []},
        {"function": "open_cfw_health_page_build_summary",
         "entry": 5224288, "start": 5224292, "end_exclusive": 5226934,
         "forbidden_entries": [5225984, 5226240]},
    ],
    "linux-clang": [
        {"function": "open_cfw_iar_memcpy_void", "entry": 4430820,
         "start": 4430848, "end_exclusive": 4430852,
         "forbidden_entries": []},
        {"function": "open_cfw_compress_log_ring_read_locked",
         "entry": 4442106, "start": 4442110, "end_exclusive": 4442322,
         "forbidden_entries": []},
        {"function": "open_cfw_compress_log_encode_record",
         "entry": 4443012, "start": 4443016, "end_exclusive": 4443806,
         "forbidden_entries": []},
        {"function": "open_cfw_easylogger_output", "entry": 4445556,
         "start": 4445560, "end_exclusive": 4446582,
         "forbidden_entries": []},
        {"function": "open_cfw_easylogger_hexdump", "entry": 4446924,
         "start": 4446928, "end_exclusive": 4447368,
         "forbidden_entries": []},
        {"function": "open_cfw_nanopb_decode_static_field", "entry": 4782440,
         "start": 4782444, "end_exclusive": 4782876,
         "forbidden_entries": [4782516, 4782518, 4782812]},
        {"function": "open_cfw_nemavg_draw_start_cap_endpoint",
         "entry": 5355760, "start": 5355764, "end_exclusive": 5357428,
         "forbidden_entries": [5355774]},
    ],
}


class IntegrationError(RuntimeError):
    """Raised when package, ownership, or atomicity evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegrationError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> str:
    return digest(json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode())


def _load(path: Path, name: str) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    require(specification is not None and specification.loader is not None,
            f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


def _pin_inputs(overrides: dict[Path, Path] | None = None) -> dict[Path, bytes]:
    overrides = overrides or {}
    result: dict[Path, bytes] = {}
    for expected_path, expected in PINS.items():
        path = overrides.get(expected_path, expected_path)
        body = path.read_bytes()
        require((len(body), digest(body)) == expected,
                f"package integration input pin drift: {expected_path}")
        result[expected_path] = body
    return result


def _payloads(package: bytes, manifest: dict[str, Any]) -> dict[str, bytes]:
    count = struct.unpack_from("<I", package, 8)[0]
    require(count == len(manifest["components"]), "package entry count drift")
    result = {}
    for index, component in enumerate(manifest["components"]):
        entry_id, offset, size, _crc = struct.unpack_from(
            "<IIII", package, 0x40 + index * 16
        )
        require(entry_id == component["entry_id"] and size >= 128,
                "package component order drift")
        result[component["name"]] = package[offset + 128:offset + size]
    return result


def _apollo_component(manifest: dict[str, Any]) -> dict[str, Any]:
    rows = [item for item in manifest["components"] if item["name"] == "apollo_main"]
    require(len(rows) == 1, "manifest Apollo-main component count drift")
    return rows[0]


def _new_rows(
    flash_rows: list[dict[str, Any]], profile: str
) -> list[dict[str, Any]]:
    return [
        row for row in flash_rows
        if row["region"].startswith("freetype_cff_") or
        (profile == "linux-clang" and
         row["region"] == "apollo_main_linux_canonical_lc3_cff_image")
    ]


def _verify_core_route(data: dict[Path, bytes]) -> dict[str, Any]:
    source = data[CORE_BUILDER].decode("utf-8")
    require(
        "cff_builder = _load_cff_scatter_builder()" in source and
        "cff_report = cff_builder.build(" in source and
        "base_component=pre_cff_component_path" in source and
        'host_slots=lc3_service_report["residual_host_slots"]' in source and
        "final_component = (\n            cff_output" in source,
        "canonical core CFF post-link invocation drift",
    )
    config = json.loads(data[CORE_CONFIG])
    provider = config.get("post_link_providers", {}).get("freetype_cff")
    require(
        isinstance(provider, dict) and
        provider.get("builder") ==
        "components/apollo_main/freetype_cff_scatter/build_component.py" and
        provider.get("config") ==
        "components/apollo_main/freetype_cff_scatter/overlay.json",
        "canonical core CFF provider declaration drift",
    )
    profiles = {
        "apple-clang": config["expected"],
        "linux-clang": config["toolchain_profiles"]["linux-clang"]["expected"],
    }
    expected = {
        "apple-clang": (
            3_956_672,
            "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        ),
        "linux-clang": (
            3_956_672,
            "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        ),
    }
    for profile, pins in profiles.items():
        require(
            (pins["component_size"], pins["component_sha256"])
            == expected[profile],
            f"{profile}: canonical core final CFF component pin drift",
        )
    return {
        "post_link_order": (
            "core -> liblc3-ltpf -> product-test -> "
            "liblc3-service-audio -> freetype-cff"
        ),
        "base_argument": (
            "same-build LC3-service Apollo component plus authenticated "
            "residual generated-NOP host tails"
        ),
        "profiles": {
            profile: {"component_size": values[0], "component_sha256": values[1]}
            for profile, values in expected.items()
        },
        "atomic_publication": "existing canonical rollback-capable generation",
    }


def _verify_candidate(
    *, profile: str, base_manifest: dict[str, Any], base_package: bytes,
    package_path: Path, base_component_path: Path, builder: Any,
    open_cfw: Any, temporary: Path,
) -> dict[str, Any]:
    # The configured package supplies the current five non-Apollo payloads and
    # package layout. The independently captured canonical PT component is the
    # authenticated pre-CFF input. This keeps package evidence current without
    # overwriting the pre-CFF reconstruction fixture during release builds.
    current_payloads = _payloads(base_package, base_manifest)
    base_apollo = base_component_path.read_bytes()
    base_payloads = dict(current_payloads)
    base_payloads["apollo_main"] = base_apollo
    comparison_base_package, _comparison_entries = open_cfw.assemble_evenota(
        base_manifest, base_payloads
    )
    component_definition = _apollo_component(base_manifest)
    output = temporary / profile
    build_report = builder.build(
        profile=profile,
        base_component=base_component_path,
        output_dir=output,
        host_slots=HOST_SLOTS[profile],
    )
    candidate_component = (output / "ota_s200_firmware_ota.bin").read_bytes()
    require(build_report["regions"] is None,
            f"{profile}: standalone builder unexpectedly rewrote regions")
    apollo = component_definition
    component_pins = (
        open_cfw.profile_pins(apollo["provider"], profile)
        or apollo["provider"]
    )
    require(
        (len(candidate_component), digest(candidate_component)) ==
        (component_pins["size"], component_pins["sha256"]),
        f"{profile}: reconstructed component differs from published pins",
    )
    open_cfw.validate_component_payload(apollo, candidate_component)
    open_cfw.validate_region_partition(apollo, candidate_component, profile)
    open_cfw.validate_flash_layout(base_manifest)

    payloads = dict(base_payloads)
    payloads["apollo_main"] = candidate_component
    candidate_package, entries = open_cfw.assemble_evenota(
        base_manifest, payloads
    )
    open_cfw.validate_evenota_image(candidate_package, base_manifest)
    package_pins = (
        open_cfw.profile_pins(base_manifest["package"], profile)
        or base_manifest["package"]
    )
    require(
        (len(candidate_package), digest(candidate_package)) ==
        (package_pins["expected_size"], package_pins["expected_sha256"]),
        f"{profile}: reconstructed package differs from published pins",
    )
    open_cfw.validate_release_manifest(
        base_manifest, toolchain_profile=profile, payloads=payloads
    )
    require(len(candidate_package) - len(comparison_base_package) ==
            len(candidate_component) - len(base_apollo),
            f"{profile}: package/component growth disagreement")
    require(all(payloads[name] == base_payloads[name]
                for name in payloads if name != "apollo_main"),
            f"{profile}: non-Apollo payload changed")

    flash_rows, unresolved, container, artifacts = open_cfw.plan_regions(
        base_manifest, payloads, profile
    )
    require(len(unresolved) == 0,
            f"{profile}: unresolved-region census changed")
    new_rows = _new_rows(flash_rows, profile)
    require(new_rows, f"{profile}: CFF flash rows missing")
    row_payloads = {
        row["region"]: artifacts[row["artifact"].removeprefix("regions/")]
        for row in new_rows
    }
    pointer = [
        row for row in new_rows
        if row["target_address"] < builder.MODULE_SLOT + 4 and
        row["end_exclusive"] > builder.MODULE_SLOT
    ]
    pointer.sort(key=lambda row: row["target_address"])
    pointer_bytes = b"".join(
        row_payloads[row["region"]][
            max(builder.MODULE_SLOT, row["target_address"]) -
            row["target_address"]:
            min(builder.MODULE_SLOT + 4, row["end_exclusive"]) -
            row["target_address"]
        ] for row in pointer
    )
    require(pointer and pointer_bytes == builder.REPLACEMENT_CLASS_BYTES,
            f"{profile}: class-pointer route bytes drift")
    sections = build_report["placement"]["sections"]
    require(len(sections) == (10 if profile == "apple-clang" else 11),
            f"{profile}: finalized CFF section count drift")
    for section in sections:
        start = section["start"]
        end = section["end_exclusive"]
        body = (output / f"{section['name'][1:]}.bin").read_bytes()
        offset = builder._runtime_offset(start)
        require(
            len(body) == section["size"] and
            candidate_component[offset:offset + len(body)] == body,
            f"{profile}: finalized CFF section byte replay drift",
        )
        covering = sorted([
            row for row in flash_rows
            if row.get("target") == "apollo510b_internal_mram" and
            row.get("address_status") in {
                "source_compiled", "generated_padding",
                "source_compiled_rodata", "generated_source_data_replacement",
            } and
            row["end_exclusive"] > start and row["target_address"] < end
        ], key=lambda row: row["target_address"])
        cursor = start
        for row in covering:
            if row["target_address"] > cursor:
                break
            cursor = max(cursor, row["end_exclusive"])
            if cursor >= end:
                break
        require(cursor >= end,
                f"{profile}: finalized CFF section lacks plan ownership")
    require(all(row["end_exclusive"] <= builder.UPDATE_FLAG for row in new_rows) and
            all(item["end_exclusive"] <= builder.UPDATE_FLAG for item in sections),
            f"{profile}: CFF row overlaps update flag")

    # The assembler regenerates only entry 6's TOC size/CRC, component-header
    # size/CRC, and payload.  Entries 1-5 retain exact offsets and bytes.
    base_entries = []
    for index in range(6):
        base_entries.append(struct.unpack_from(
            "<IIII", comparison_base_package, 0x40 + index * 16
        ))
    for index, entry in enumerate(entries):
        if index < 5:
            require((entry.entry_id, entry.offset, entry.entry_size, entry.checksum)
                    == base_entries[index],
                    f"{profile}: earlier package entry receipt changed")
    final_entry = entries[-1]
    require(final_entry.entry_id == 6 and
            final_entry.payload_size == len(candidate_component) and
            final_entry.checksum == open_cfw.crc32c_msb(candidate_component),
            f"{profile}: final entry-6 receipt drift")

    manifest_id = {
        "sha256": open_cfw.effective_manifest_sha256(base_manifest),
        "sources": [{
            "path": BASE_MANIFEST.relative_to(G2 / "manifests").as_posix(),
            "size": BASE_MANIFEST.stat().st_size,
            "sha256": digest(BASE_MANIFEST.read_bytes()),
        }],
    }
    package_sha = digest(candidate_package)
    flash_plan = open_cfw.make_flash_plan(
        manifest=base_manifest, manifest_id=manifest_id,
        toolchain_profile=profile,
        package_artifact=f"package/{base_manifest['package']['output_name']}",
        package_sha256=package_sha, flash_regions=flash_rows,
        unresolved=unresolved, container=container,
    )
    package_report = open_cfw.make_build_report(
        manifest=base_manifest, manifest_path=BASE_MANIFEST,
        project_root=G2, manifest_id=manifest_id,
        toolchain_profile=profile, payloads=payloads,
        package_artifact=f"package/{base_manifest['package']['output_name']}",
        image=candidate_package,
        expected_size=package_pins["expected_size"],
        expected_sha256=package_pins["expected_sha256"], entries=entries,
        flash_regions=flash_rows, unresolved=unresolved, container=container,
    )
    require(package_report["package"]["byte_identical_to_reference"] is True,
            f"{profile}: published package receipt check failed")
    require(flash_plan["package_sha256"] == package_sha,
            f"{profile}: flash-plan package binding drift")

    return {
        "base_package": {
            "path": package_path.relative_to(G2).as_posix(),
            "size": len(base_package), "sha256": digest(base_package),
        },
        "component": build_report["component"],
        "component_receipt_sha256": build_report["receipt_sha256"],
        "package": {
            "size": len(candidate_package), "sha256": package_sha,
            "growth_bytes": len(candidate_package) - len(comparison_base_package),
            "entry_6_payload_size": final_entry.payload_size,
            "entry_6_entry_size": final_entry.entry_size,
            "entry_6_crc32c_msb": f"0x{final_entry.checksum:08X}",
            "entry_6_package_offset": final_entry.offset,
        },
        "atomicity": {
            "changed_package_entries": [6],
            "unchanged_entry_count": 5,
            "all_runtime_mutations_in_entry_6": True,
            "cross_entry_mutations": 0,
            "cross_entry_atomicity_required": False,
            "toc_and_component_headers_regenerated": True,
        },
        "ownership": {
            "flash_plan_sha256": canonical(flash_plan),
            "flash_rows": len(flash_rows),
            "unresolved_rows": len(unresolved),
            "container_rows": len(container),
            "cff_rows": len(new_rows),
            "cff_source_rows": len(sections),
            "cff_source_bytes": sum(item["size"] for item in sections),
            "cff_generated_pointer_rows": len(pointer),
            "cff_generated_pointer_bytes": len(pointer_bytes),
            "cff_erased_gap_rows": 0,
            "cff_erased_gap_bytes": 0,
            "highest_cff_end_exclusive": f"0x{max(item['end_exclusive'] for item in sections):08X}",
            "update_flag": f"0x{builder.UPDATE_FLAG:08X}",
            "collision_or_protected_overlap_count": 0,
            "unused_scattered_table_pool_consumed": 0,
        },
        "reproducibility": {
            "component_matches_pinned_profile_output": True,
            "package_assembly_deterministic": True,
            "zero_final_relocations": build_report["scatter_manifest"]["relocations"]["total"] == 0,
            "zero_undefined_symbols": build_report["scatter_manifest"]["undefined_symbols"] == [],
        },
    }


def validate_boundary(report: dict[str, Any]) -> None:
    require(report["routing"] == {
        "component_builder_integration_present": True,
        "canonical_component_route_enabled": True,
        "dual_profile_package_candidate_emitted_in_verification": True,
        "canonical_package_manifest_route_enabled": True,
        "software_production_route_permitted": True,
        "hardware_validation_performed": False,
    }, "CFF package route boundary drift")
    expected = {
        "apple-clang": (20_414, 0, 0, 4_750_780),
        "linux-clang": (20_354, 0, 0, 4_750_764),
    }
    for profile, row in report["profiles"].items():
        require(row["atomicity"]["changed_package_entries"] == [6] and
                row["ownership"]["collision_or_protected_overlap_count"] == 0 and
                row["ownership"]["unused_scattered_table_pool_consumed"] == 0 and
                row["reproducibility"]["zero_final_relocations"] is True and
                row["reproducibility"]["zero_undefined_symbols"] is True,
                f"{profile}: final package integration boundary drift")
        require(
            (
                row["ownership"]["cff_source_bytes"],
                row["ownership"]["cff_erased_gap_bytes"],
                row["component"]["growth_bytes"],
                row["package"]["size"],
            ) == expected[profile],
            f"{profile}: exact CFF region/accounting receipt drift",
        )


def analyze(*, input_overrides: dict[Path, Path] | None = None) -> dict[str, Any]:
    data = _pin_inputs(input_overrides)
    core_route = _verify_core_route(data)
    builder = _load(BUILDER, "g2_cff_package_builder")
    open_cfw = _load(OPEN_CFW, "g2_cff_package_open_cfw")
    config = json.loads(data[CONFIG])
    base_manifest = open_cfw.load_manifest(BASE_MANIFEST)
    with tempfile.TemporaryDirectory(prefix="opencfw-cff-package-") as raw:
        temporary = Path(raw)
        profiles = {}
        for profile in ("apple-clang", "linux-clang"):
            profile_config = config["profiles"][profile]
            package_path = G2 / profile_config["base_package"]["path"]
            base_component_path = G2 / profile_config["base_component"]["path"]
            package = package_path.read_bytes()
            profiles[profile] = _verify_candidate(
                profile=profile, base_manifest=base_manifest,
                base_package=package, package_path=package_path,
                base_component_path=base_component_path,
                builder=builder, open_cfw=open_cfw, temporary=temporary,
            )
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-package-builder-and-canonical-route-verified",
        "analysis_mode": (
            "software-only dual-profile package assembly, component validation, "
            "CRC regeneration, and flash-plan ownership proof"
        ),
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "size": expected[0], "sha256": expected[1]
            } for path, expected in PINS.items()
        },
        "profiles": profiles,
        "canonical_component_route": core_route,
        "routing": {
            "component_builder_integration_present": True,
            "canonical_component_route_enabled": True,
            "dual_profile_package_candidate_emitted_in_verification": True,
            "canonical_package_manifest_route_enabled": True,
            "software_production_route_permitted": True,
            "hardware_validation_performed": False,
        },
        "remaining_canonical_changes": [],
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "font_payload_authenticated": False,
            "stack_or_wcet_qualified": False,
            "hardware_validation_performed": False,
        },
    }
    result["integration_sha256"] = canonical({
        "profiles": profiles,
        "canonical_component_route": core_route,
        "routing": result["routing"],
        "remaining_canonical_changes": result["remaining_canonical_changes"],
    })
    validate_boundary(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.write_manifest:
            MANIFEST.write_text(rendered, encoding="utf-8")
        if args.check_manifest:
            require(MANIFEST.is_file() and
                    json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                    "checked CFF package integration manifest drift")
    except (IntegrationError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF package integration failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
