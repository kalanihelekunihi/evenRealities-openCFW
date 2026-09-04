#!/usr/bin/env python3
"""Audit the stock and source-owned G2 CFF production routing boundary.

This is deliberately a census, not an integration helper.  It authenticates
the stock default-module and LVGL consumer paths, the guarded source-built CFF
post-link component route, and the published dual-profile package manifest.
The route is accepted only while its builder, config, core invocation, scatter
contract, component pins, package pins, and region ownership remain exact.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
CONFIG_AUDIT = G2 / "tools/freetype_g2_config_audit.py"
FONT_MANAGER_AUDIT = G2 / "tools/analyze_g2_lvgl_font_manager.py"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_cff_function_map.py"
OVERLAY = G2 / "components/apollo_main/core_overlay/overlay.json"
BUILDER = G2 / "components/apollo_main/core_overlay/build_component.py"
SCATTER_CONFIG = G2 / "components/apollo_main/freetype_cff_scatter/overlay.json"
SCATTER_BUILDER = G2 / "components/apollo_main/freetype_cff_scatter/build_component.py"
SCATTER_MANIFEST = G2 / "tools/manifests/g2-freetype-cff-scatter-link.json"
PACKAGE_MANIFEST = G2 / "manifests/g2-2.2.6.10-core-source.json"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-production-route.json"

LOAD_BASE = 0x00437FE0
IMAGE_PIN = (3_523_396, "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
GHIDRA_PIN = (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
DEPENDENCY_PINS = {
    CONFIG_AUDIT: "49bfb2fe29472fe101c709a740d3cec847fcec66f94f1d26ef1367f5659f6278",
    FONT_MANAGER_AUDIT: "c80cc920eb6da1ef1f175c62f87a6cdf6c6db0f1d4592690f9a03ef2228848a5",
    MAP_ANALYZER: "68f20cf54a36305d6c460d082c907d3d94efeff545238ff8b6f1189267322b70",
}
ROUTE_INPUT_PINS = {
    BUILDER: (90_584, "164a9fd3aeb22daa16085de2725157af4b157e8f64977a50db89986aaf97325f"),
    OVERLAY: (6_404_019, "2329b48855ecf130bbb8ea4e6f97711dc9ac9fcba1aed9c647dd896e6c488722"),
    SCATTER_BUILDER: (40_269, "b344b37620574e9cec4af153f54b23e124afbe64332126118e678401f1feb4b9"),
    SCATTER_CONFIG: (1_842, "ec7f2835ba9d04963ea6f0ca02d8f804ff4ee88485168ef0de2b230ba56ab972"),
    PACKAGE_MANIFEST: (3_812_990, "ae7c402fef4c72f3fbeae80cbfc71eb17e3907044a339b65494e8732392a150d"),
}
DEFAULT_MODULE_TABLE = 0x0073EEF8
CFF_DRIVER_CLASS = 0x006DCB74
DEFAULT_MODULES = (
    0x00752520, 0x006DED34, CFF_DRIVER_CLASS, 0x00758A18, 0x00758A60,
    0x00758A3C, 0x0075A3F8, 0x00718D9C, 0x00718DD8, 0x00718E14, 0,
)
STOCK_CALLABLES = {
    0x004B1B98: (260, "febc304352ccd239fe91d20ecb5a6830648ef0e7edc55bc641e7b1429356da44",
                 (0x0044D25C, 0x0044F730, 0x00482B00, 0x004B1FCC,
                  0x004D4CD4, 0x004D5114, 0x0052431C)),
    0x005242FC: (28, "32e95da285f105bf01c667f02c9d4ff2631fbf393b7f3876eb7264f30528b47f",
                 (0x0052729C,)),
    0x0052431C: (56, "b5b7601a9be9efc68a5b0740025aeb715cd62d308204d546d7942f67eac57ba2",
                 (0x005242FC, 0x005274B2, 0x005676A0, 0x005676C6)),
    0x0052729C: (278, "c9f520d0d156b4408be50b39543c6d4eeb804eec2f081a5c6ef68e5e6af535e7",
                 (0x0046CACC, 0x005270D2, 0x00527466, 0x00529148, 0x00529256)),
}
POLICY_SERVICE_BODIES = (0x00527F0A, 0x00527FF2)
ROUTE_TOKENS = (
    "components/shared/freetype_cff",
    "runtime_freetype_cff.c",
    "src/cff/cff.c",
    "open_cfw_freetype_cff_",
)
EXPECTED_ROUTE_TOKEN_COUNTS = {
    "components/shared/freetype_cff": 3,
    "runtime_freetype_cff.c": 3,
    "src/cff/cff.c": 3,
    "open_cfw_freetype_cff_": 1,
}
EXPECTED_PROFILE_COMPONENTS = {
    "apple-clang": {
        "size": 3_956_672,
        "sha256": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
    },
    "linux-clang": {
        "size": 3_956_672,
        "sha256": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
    },
}
EXPECTED_PROFILE_PACKAGES = {
    "apple-clang": {
        "size": 4_750_780,
        "sha256": "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771",
    },
    "linux-clang": {
        "size": 4_750_764,
        "sha256": "50f2ee3722aeaa720eed1a7c65381b02ac3ec0ceabecf9eb57d661d8e060a6d0",
    },
}
EXPECTED_ROUTE_PLACEMENT = {
    "stock_start": 0x005ABEF8,
    "stock_end_exclusive": 0x005B0114,
    "tail_start": 0x007FCEBA,
    "tail_end_exclusive": 0x007FDED4,
    "module_class_pointer": 0x0073EF00,
}


class RouteError(RuntimeError):
    """Raised when the authenticated production-routing census changes."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RouteError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> str:
    return _sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _pinned(path: Path, pin: tuple[int, str]) -> bytes:
    data = path.read_bytes()
    _require((len(data), _sha(data)) == pin, f"input pin drift: {path}")
    return data


def _route_inputs(
    overrides: dict[Path, Path] | None = None,
) -> dict[Path, bytes]:
    """Read the exact component-route inputs, allowing hostile-test substitutes."""
    overrides = overrides or {}
    result: dict[Path, bytes] = {}
    for expected_path, pin in ROUTE_INPUT_PINS.items():
        actual_path = overrides.get(expected_path, expected_path)
        data = actual_path.read_bytes()
        _require(
            (len(data), _sha(data)) == pin,
            f"authenticated CFF route input pin drift: {expected_path}",
        )
        result[expected_path] = data
    return result


def _authenticate_component_route(data: dict[Path, bytes]) -> dict[str, Any]:
    """Authenticate the guarded core -> CFF post-link component contract."""
    core_builder = data[BUILDER].decode("utf-8")
    required_core_fragments = (
        "cff_builder = _load_cff_scatter_builder()",
        "cff_report = cff_builder.build(",
        "base_component=pre_cff_component_path",
        'final_component = (\n            cff_output / "ota_s200_firmware_ota.bin"',
        '"freetype_cff": copy.deepcopy(',
    )
    _require(
        all(core_builder.count(fragment) >= 1
            for fragment in required_core_fragments),
        "canonical core CFF post-link invocation drift",
    )
    route_token_counts = {
        token: core_builder.count(token) for token in ROUTE_TOKENS
    }
    _require(
        route_token_counts == EXPECTED_ROUTE_TOKEN_COUNTS,
        "canonical core CFF source ownership token drift",
    )

    scatter_builder = data[SCATTER_BUILDER].decode("utf-8")
    required_scatter_fragments = (
        'STOCK_CLASS_BYTES = bytes.fromhex("74cb6d00")',
        'REPLACEMENT_CLASS_BYTES = bytes.fromhex("14c05a00")',
        "component[slot:slot + 4] == STOCK_CLASS_BYTES",
        "output[slot:slot + 4] = REPLACEMENT_CLASS_BYTES",
        "tuple(bodies) == SECTION_ORDER",
        "digest(component[stock_start:stock_end]) == STOCK_INTERVAL_SHA256",
    )
    _require(
        all(fragment in scatter_builder for fragment in required_scatter_fragments),
        "guarded CFF scatter builder contract drift",
    )

    core_config = json.loads(data[OVERLAY])
    provider = core_config.get("post_link_providers", {}).get("freetype_cff")
    _require(
        isinstance(provider, dict)
        and provider.get("builder")
        == "components/apollo_main/freetype_cff_scatter/build_component.py"
        and provider.get("config")
        == "components/apollo_main/freetype_cff_scatter/overlay.json"
        and provider.get("placement") == EXPECTED_ROUTE_PLACEMENT
        and provider.get("hardware", {}).get("qualification_complete") is False,
        "canonical core CFF provider declaration drift",
    )
    core_profiles = {
        "apple-clang": core_config["expected"],
        "linux-clang": core_config["toolchain_profiles"]["linux-clang"]["expected"],
    }
    for profile, expected in EXPECTED_PROFILE_COMPONENTS.items():
        observed = core_profiles[profile]
        _require(
            observed.get("component_size") == expected["size"]
            and observed.get("component_sha256") == expected["sha256"],
            f"{profile}: canonical core final CFF component pin drift",
        )

    scatter_config = json.loads(data[SCATTER_CONFIG])
    _require(
        scatter_config.get("component") == "g2-apollo-main-freetype-cff-scatter",
        "CFF scatter component identity drift",
    )
    scatter_manifest_pin = scatter_config.get("dependencies", {}).get(
        "scatter_manifest"
    )
    scatter_manifest_data = SCATTER_MANIFEST.read_bytes()
    _require(
        isinstance(scatter_manifest_pin, dict)
        and (len(scatter_manifest_data), _sha(scatter_manifest_data))
        == (scatter_manifest_pin.get("size"), scatter_manifest_pin.get("sha256")),
        "CFF final scatter manifest pin drift",
    )
    scatter_manifest = json.loads(scatter_manifest_data)
    scatter_profiles: dict[str, Any] = {}
    for profile, expected in EXPECTED_PROFILE_COMPONENTS.items():
        configured = scatter_config["profiles"][profile]["expected"]["component"]
        _require(configured == expected,
                 f"{profile}: scatter component output pin drift")
        scatter = scatter_manifest["profiles"][profile]
        _require(
            scatter["cff_driver_class"] == "0x005AC014"
            and scatter["relocations"]["total"] == 0
            and scatter["undefined_symbols"] == []
            and len(scatter["sections"]) == 4
            and scatter["required_exports"] == [
                "cff_driver_class",
                "open_cfw_freetype_cff_get_darkening_parameters",
                "open_cfw_freetype_cff_get_hinting_engine",
                "open_cfw_freetype_cff_get_no_stem_darkening",
                "open_cfw_freetype_cff_set_darkening_parameters",
                "open_cfw_freetype_cff_set_hinting_engine",
                "open_cfw_freetype_cff_set_no_stem_darkening",
            ],
            f"{profile}: authenticated scatter closure drift",
        )
        scatter_profiles[profile] = {
            "component": expected,
            "loadable_bytes": scatter["loadable_bytes"],
            "sections": scatter["sections"],
            "relocations": scatter["relocations"]["total"],
            "undefined_symbols": len(scatter["undefined_symbols"]),
        }

    package_manifest = json.loads(data[PACKAGE_MANIFEST])
    apollo = package_manifest.get("component_overrides", {}).get("apollo_main", {})
    package = package_manifest.get("package", {})
    provider = apollo.get("provider", {})
    linux_provider = provider.get("profiles", {}).get("linux-clang", {})
    _require(
        provider.get("path")
        == "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin"
        and (provider.get("size"), provider.get("sha256"))
        == (EXPECTED_PROFILE_COMPONENTS["apple-clang"]["size"],
            EXPECTED_PROFILE_COMPONENTS["apple-clang"]["sha256"])
        and linux_provider.get("path")
        == "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin"
        and (linux_provider.get("size"), linux_provider.get("sha256"))
        == (EXPECTED_PROFILE_COMPONENTS["linux-clang"]["size"],
            EXPECTED_PROFILE_COMPONENTS["linux-clang"]["sha256"]),
        "canonical package Apollo CFF provider drift",
    )
    package_profiles = {
        "apple-clang": {
            "size": package.get("expected_size"),
            "sha256": package.get("expected_sha256"),
        },
        "linux-clang": {
            "size": package.get("profiles", {}).get("linux-clang", {}).get(
                "expected_size"
            ),
            "sha256": package.get("profiles", {}).get("linux-clang", {}).get(
                "expected_sha256"
            ),
        },
    }
    _require(
        package_profiles == EXPECTED_PROFILE_PACKAGES,
        "canonical CFF package output pins drift",
    )
    apple_cff_rows = [
        row for row in apollo.get("regions", [])
        if str(row.get("name", "")).startswith("freetype_cff_")
    ]
    linux_replacements = apollo.get("profile_region_replacements", {}).get(
        "linux-clang", []
    )
    linux_cff_rows = [
        row
        for replacement in linux_replacements
        for row in replacement.get("regions", [])
        if str(row.get("name", "")).startswith("freetype_cff_")
    ]
    linux_route_rows = [
        row
        for replacement in linux_replacements
        for row in replacement.get("regions", [])
        if row.get("name") == "apollo_main_linux_canonical_lc3_cff_image"
    ]
    _require(
        len(apple_cff_rows) == 22
        and sum(row["size"] for row in apple_cff_rows
                if row["address_status"] == "container_only") == 4
        and sum(row["size"] for row in apple_cff_rows
                if row["address_status"]
                == "generated_source_data_replacement") == 20_819
        and max(row["target_address"] + row["size"]
                for row in apple_cff_rows
                if row.get("target_address") is not None) == 0x0073EF04
        and linux_cff_rows == []
        and len(linux_route_rows) == 1
        and linux_route_rows[0].get("file_offset") == 32
        and linux_route_rows[0].get("size") == 3_523_364
        and linux_route_rows[0].get("target_address") == LOAD_BASE + 32
        and linux_route_rows[0].get("address_status")
        == "generated_source_data_replacement"
        and linux_route_rows[0].get("output")
        == "apollo510b/main-linux-canonical-lc3-cff.bin",
        "canonical CFF region ownership drift",
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
        "builder": SCATTER_BUILDER.relative_to(G2).as_posix(),
        "config": SCATTER_CONFIG.relative_to(G2).as_posix(),
        "guarded_stock_interval": {
            "start": "0x005ABEF8", "end_exclusive": "0x005B0114",
            "sha256": (
                "58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b"
            ),
        },
        "module_class_patch": {
            "address": "0x0073EF00",
            "expected_stock_little_endian_hex": "74cb6d00",
            "replacement_little_endian_hex": "14c05a00",
            "replacement_symbol": "cff_driver_class",
            "replacement_address": "0x005AC014",
        },
        "profiles": scatter_profiles,
        "route_token_counts": route_token_counts,
        "canonical_package": {
            "manifest": PACKAGE_MANIFEST.relative_to(G2).as_posix(),
            "profiles": package_profiles,
            "apple_cff_region_rows": len(apple_cff_rows),
            "linux_profile_replacement_rows": len(linux_route_rows),
            "highest_cff_end_exclusive": "0x0073EF04",
        },
        "canonical_package_manifest_route_enabled": True,
    }


def _load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    _require(spec is not None and spec.loader is not None,
             f"analyzer dependency unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def analyze(
    *, image_path: Path = IMAGE, ghidra_path: Path = GHIDRA,
    route_input_overrides: dict[Path, Path] | None = None,
) -> dict[str, Any]:
    image = _pinned(image_path, IMAGE_PIN)
    ghidra_data = _pinned(ghidra_path, GHIDRA_PIN)
    for path, digest in DEPENDENCY_PINS.items():
        _require(_sha(path.read_bytes()) == digest,
                 f"routing dependency drift: {path}")

    config_module = _load(CONFIG_AUDIT, "g2_cff_route_config")
    config = config_module.authenticate(config_module.Image(image_path.resolve()))
    modules = config["configuration"]["built_in_modules"]
    _require(len(modules) == 10 and modules[2] == {
        "name": "cff", "class": "0x006DCB74", "flags": "0x00000D01",
        "object_size": 72,
    }, "stock CFF default-module identity drift")
    table = struct.unpack_from("<11I", image, DEFAULT_MODULE_TABLE - LOAD_BASE)
    _require(table == DEFAULT_MODULES, "stock default-module table drift")
    _require(config["allocator"]["lifecycle"] == {
        **config["allocator"]["lifecycle"],
        "FT_Init_FreeType": "0x0052431C",
        "FT_Add_Default_Modules": "0x005242FC",
        "FT_New_Library": "0x005274B2",
        "lv_freetype_font_create": "0x004B1C9C",
        "lv_freetype_font_delete": "0x004B1EF6",
    }, "stock FreeType lifecycle drift")

    ghidra: dict[int, dict[str, Any]] = {
        int(row["entry"], 16): row
        for row in map(json.loads, ghidra_data.splitlines())
    }
    for start, (size, digest, callees) in STOCK_CALLABLES.items():
        row = ghidra.get(start)
        _require(row is not None and row["body_bytes"] == size and
                 row["body_sha256"] == digest and
                 tuple(int(value, 16) for value in row["callees"]) == callees,
                 f"stock registration call graph drift: 0x{start:08X}")
    policy_direct_callers = sorted(
        f"0x{start:08X}"
        for start, row in ghidra.items()
        if any(int(value, 16) in POLICY_SERVICE_BODIES for value in row["callees"])
    )
    _require(not policy_direct_callers,
             "a direct stock CFF/PS policy caller appeared")

    font_manager = _load(
        FONT_MANAGER_AUDIT, "g2_cff_route_font_manager"
    ).analyze(image_path)
    _require(font_manager["production"]["production_routed"] is True and
             font_manager["production"]["guarded_redirects"] == 8 and
             font_manager["provider_boundary"]["lvgl_freetype_adapter_calls"] == 2,
             "production LVGL/FreeType consumer route drift")

    complete_map = _load(MAP_ANALYZER, "g2_cff_route_map").run_audit()
    _require(complete_map["confidence"]["mapped_total"] == {
        "functions": 101, "bytes": 16_718,
    } and complete_map["confidence"]["unresolved_code"]["bytes"] == 0,
             "complete CFF map reopened")

    route_inputs = _route_inputs(route_input_overrides)
    component_route = _authenticate_component_route(route_inputs)

    route_state = {
        "stock_cff_module_registered": True,
        "source_owned_lvgl_font_manager_consumer_routed": True,
        "retained_lvgl_freetype_adapter_calls": 2,
        "source_built_cff_translation_unit_placed": True,
        "source_built_cff_driver_class_registered": True,
        "cff_policy_adapter_placed": True,
        "authenticated_policy_adapter_callsite": False,
        "direct_stock_ps_property_service_callers": policy_direct_callers,
        "canonical_component_route_enabled": True,
        "canonical_package_manifest_route_enabled": True,
        "software_production_route_permitted": True,
        "external_cff_font_payload_authenticated": False,
    }
    blockers = [
        {
            "gate": "policy ownership",
            "evidence": (
                "the six source-built policy exports are placed and retained, but "
                "stock defaults to Adobe and no authenticated first-party caller "
                "changes CFF policy"
            ),
            "status": "blocked-no-authenticated-caller",
        },
        {
            "gate": "font payload and live rendering",
            "evidence": config["font_registration"]["qualification"],
            "status": "blocked by unavailable physical evidence",
        },
    ]
    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-canonical-package-route-authenticated",
        "analysis_mode": "read-only; no build, signing, flash, or hardware operation",
        "stock_registration": {
            "ft_init_freetype": "0x0052431C",
            "ft_add_default_modules": "0x005242FC",
            "ft_add_module": "0x0052729C",
            "default_module_table": "0x0073EEF8",
            "cff_module_index": 2,
            "cff_driver_class": "0x006DCB74",
            "default_module_table_sha256": _sha(
                image[DEFAULT_MODULE_TABLE - LOAD_BASE:
                      DEFAULT_MODULE_TABLE - LOAD_BASE + 44]
            ),
        },
        "production_consumer": {
            "source_owned_component": "components/apollo_main/core_overlay/lvgl_font_manager.c",
            "source_owned_guarded_redirects": 8,
            "retained_create": "0x004B1C9C",
            "retained_delete": "0x004B1EF6",
            "retained_initializer": "0x004B1B98",
            "consumer_payload_status": "external XIP identity unavailable",
        },
        "route_state": route_state,
        "authenticated_component_route": component_route,
        "blockers": blockers,
        "complete_map": {
            "mapping_sha256": complete_map["mapping_sha256"],
            "functions": 101, "callable_bytes": 16_718,
            "physical_bytes": 16_924, "unresolved_callable_bytes": 0,
        },
        "evidence_bounds": {
            "stock_retained_behavior_claimed": True,
            "community_source_component_placement_claimed": True,
            "community_source_component_routing_claimed": True,
            "canonical_package_publication_claimed": True,
            "software_production_route_claimed": True,
            "font_payload_identity_claimed": False,
            "hardware_validation_performed": False,
        },
        "inputs": {
            path.relative_to(G2).as_posix(): {
                "bytes": path.stat().st_size, "sha256": _sha(path.read_bytes()),
            }
            for path in (IMAGE, GHIDRA, CONFIG_AUDIT, FONT_MANAGER_AUDIT, MAP_ANALYZER)
        } | {
            path.relative_to(G2).as_posix(): {
                "bytes": pin[0], "sha256": pin[1],
            }
            for path, pin in ROUTE_INPUT_PINS.items()
        },
    }
    result["census_sha256"] = _canonical({
        "stock_registration": result["stock_registration"],
        "production_consumer": result["production_consumer"],
        "authenticated_component_route": component_route,
        "route_state": route_state,
        "blockers": blockers,
    })
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
            _require(MANIFEST.is_file() and
                     json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                     "checked-in CFF production-route manifest drift")
    except (RouteError, KeyError, OSError, ValueError) as error:
        print(f"G2 FreeType CFF production-route census failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
