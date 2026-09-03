#!/usr/bin/env python3
"""Fail-closed ownership reconciliation for both admitted G2 profiles.

The address map in ``flash-plan.json`` is exact, but non-canonical compiler
profiles deliberately reuse coarse Apple region boundaries below the appended
source tail.  Those boundaries are not an ownership authority.  This audit
binds the separately admitted A/B build receipts and component reports, then
reconciles the presentation labels without changing a package byte or target
address.
"""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import analyze_g2_completion_readiness as readiness
import apply_g2_canonical_observations as canonical_admission


ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT / "tools/manifests/g2-dual-profile-ownership.json"
BASE_MANIFEST = ROOT / "manifests/g2-2.2.6.10.json"
OBSERVATIONS = {
    "apple-clang": (
        ROOT / "build/canonical-observation-g2-final9/apple-a/build-report.json",
        ROOT / "build/canonical-observation-g2-final9/apple-b/build-report.json",
    ),
    "linux-clang": (
        ROOT / "build/canonical-observation-g2-final9/linux-a/build-report.json",
        ROOT / "build/canonical-observation-g2-final9/linux-b/build-report.json",
    ),
}
BOOT_REPORTS = {
    "apple-clang": (
        ROOT / "components/bootloader/core_overlay/build/build-report.json"
    ),
    "linux-clang": (
        ROOT
        / "build/canonical-provider/linux-clang/apollo_bootloader/build-report.json"
    ),
}
EM9305_REPORT = ROOT / "components/em9305/source_overlay/build/build-report.json"
EM9305_PROVIDER = {
    "kind": "source_build",
    "path": "components/em9305/source_overlay/build/firmware_ble_em9305.bin",
    "size": 212_984,
    "sha256": "1a4ccc61cae6e9b90d0eb3d694179d726c935171788167d28ea45060d7431c42",
}
PACKAGE_DIRS = {
    "apple-clang": ROOT / "build/source",
    "linux-clang": ROOT / "build/source-linux",
}
APOLLO_PROVIDER_PATHS = {
    "apple-clang": {
        "apollo_bootloader": "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
        "apollo_main": "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
    },
    "linux-clang": {
        "apollo_bootloader": (
            "build/canonical-provider/linux-clang/apollo_bootloader/"
            "ota_s200_bootloader.bin"
        ),
        "apollo_main": (
            "build/canonical-provider/linux-clang/apollo_main/ota_s200_firmware_ota.bin"
        ),
    },
}

PRODUCTION = "production_source"
GENERATED = "generated_or_reconstructible"
CANDIDATE = "candidate_source_not_routed"
RETAINED = "typed_retained_or_external"
UNCLASSIFIED = "unclassified"
BUCKETS = (PRODUCTION, GENERATED, CANDIDATE, RETAINED, UNCLASSIFIED)
EM9305_ACCOUNTING = {
    PRODUCTION: 1_174,
    GENERATED: 1_226,
    CANDIDATE: 0,
    RETAINED: 210_584,
    UNCLASSIFIED: 0,
}
GENERATED_ADDRESS_STATUSES = frozenset(
    {
        "generated_alignment",
        "generated_padding",
        "generated_source_data_replacement",
        "generated_source_entry_replacement",
        "generated_source_exact_load_image",
        "generated_source_exact_replacement",
    }
)
SOURCE_ADDRESS_STATUSES = frozenset(
    {"source_compiled", "source_compiled_rodata"}
)
APOLLO_COMPONENTS = frozenset({"apollo_main", "apollo_bootloader"})
COMPONENT_IDS = frozenset(
    {"codec", "ble_em9305", "touch", "case", *APOLLO_COMPONENTS}
)
ASSESSMENT_NAMES = {
    "codec": "GX8002 codec/DSP",
    "touch": "PSoC touch controller",
    "case": "STM32 charging case",
}

NEMAVG_COORDINATOR_BOUNDARY = {
    "stock_functions": 3,
    "stock_physical_bytes": 6_614,
    "source_routed_functions": 3,
    "source_routed_stock_bytes": 6_614,
    "retained_unpatched_functions": 0,
    "retained_unpatched_stock_bytes": 0,
    "candidate_source_not_routed_functions": 0,
    "candidate_source_not_routed_bytes": 0,
    "coordinator_production_routed": True,
    "endpoint_stock_entries_unpatched": False,
    "whole_candidate_production_routed": True,
    "ownership_accounting": (
        "all three authenticated stroke-cap stock functions are replaced by "
        "production-routed MIT C; emitted component totals remain authoritative "
        "from the independently admitted builder reports"
    ),
}


class OwnershipError(RuntimeError):
    """Raised when admitted ownership evidence no longer agrees."""


def _require(value: bool, message: str) -> None:
    if not value:
        raise OwnershipError(message)


def _stable_file(path: Path, role: str) -> tuple[bytes, tuple[int, ...]]:
    """Read one G2-local regular, single-link file through O_NOFOLLOW."""
    root = ROOT.resolve()
    lexical = Path(os.path.abspath(path))
    try:
        lexical.relative_to(root)
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError, RuntimeError) as error:
        raise OwnershipError(f"{role}: path escapes the G2 tree") from error
    _require(lexical == resolved, f"{role}: path contains a symlink")
    try:
        return canonical_admission._read_regular_with_identity(resolved, role)
    except canonical_admission.AdmissionError as error:
        raise OwnershipError(str(error)) from error


def _record(path: Path, payload: bytes) -> dict[str, Any]:
    return {
        "path": path.resolve().relative_to(ROOT.resolve()).as_posix(),
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _read_with_record(path: Path, role: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, _identity = _stable_file(path, role)
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OwnershipError(f"cannot read {path}: {error}") from error
    _require(isinstance(value, dict), f"{path}: top level is not an object")
    return value, _record(path, payload)


def _read(path: Path) -> dict[str, Any]:
    return _read_with_record(path, str(path))[0]


def _sha256(path: Path) -> str:
    return hashlib.sha256(_stable_file(path, str(path))[0]).hexdigest()


def _exact_keys(value: dict[str, Any], expected: set[str], role: str) -> None:
    _require(set(value) == expected, f"{role}: schema keys changed")


def _integer(value: Any, role: str, *, minimum: int = 0) -> int:
    _require(type(value) is int and value >= minimum, f"{role}: invalid integer")
    return value


def _boolean(value: Any, role: str) -> bool:
    _require(type(value) is bool, f"{role}: invalid boolean")
    return value


def _digest(value: Any, role: str) -> str:
    _require(
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value),
        f"{role}: invalid SHA-256",
    )
    return value


def _artifact(root: Path, record: dict[str, Any], role: str) -> dict[str, Any]:
    path_value = record.get("artifact")
    size = _integer(record.get("size"), f"{role} size", minimum=1)
    digest = _digest(record.get("sha256"), f"{role} digest")
    _require(isinstance(path_value, str) and path_value, f"{role}: artifact missing")
    relative = Path(path_value)
    _require(
        not relative.is_absolute()
        and relative.parts
        and all(part not in ("", ".", "..") for part in relative.parts),
        f"{role}: artifact path is not a safe relative path",
    )
    path = root / relative
    payload, _identity = _stable_file(path, role)
    _require(len(payload) == size, f"{role}: artifact size changed")
    _require(hashlib.sha256(payload).hexdigest() == digest,
             f"{role}: artifact digest changed")
    return _record(path, payload)


def _component_accounting(component: dict[str, Any], role: str) -> dict[str, int]:
    required = {
        "size", "source_owned_bytes", "opaque_base_bytes",
        "generated_patch_site_bytes",
    }
    _require(required <= set(component), f"{role}: component accounting missing")
    size = _integer(component["size"], f"{role} size", minimum=1)
    source = _integer(component["source_owned_bytes"], f"{role} source")
    retained = _integer(component["opaque_base_bytes"], f"{role} retained")
    generated_patch = _integer(
        component["generated_patch_site_bytes"], f"{role} generated patch"
    )
    generated_alignment = _integer(
        component.get("generated_alignment_bytes", 0),
        f"{role} generated alignment",
    )
    container = _integer(
        component.get("generated_wrapper_bytes", 0), f"{role} container"
    )
    generated_addressed = generated_patch + generated_alignment
    _require(
        source + retained + generated_addressed + container == size,
        f"{role}: builder accounting does not conserve bytes",
    )
    return {
        "size": size,
        "source": source,
        "generated_addressed": generated_addressed,
        "retained": retained,
        "component_container_metadata": container,
    }


def _canonical_main(
    profile: str,
    admitted: tuple[dict[str, Any], dict[str, Any]] | None = None,
) -> tuple[dict[str, int], dict[str, Any], dict[str, Any]]:
    if admitted is None:
        try:
            admitted = canonical_admission.admit_reproducible_pair(
                list(OBSERVATIONS[profile]), profile
            )
        except canonical_admission.AdmissionError as error:
            raise OwnershipError(f"{profile}: {error}") from error
    reports = [item["report"] for item in admitted]
    canonical = [report.get("canonical_observation") for report in reports]
    _require(all(isinstance(item, dict) for item in canonical),
             f"{profile}: canonical observation missing")
    first, second = canonical
    _require(first.get("profile") == profile and second.get("profile") == profile,
             f"{profile}: observation profile changed")
    _require(first.get("complete") is True and second.get("complete") is True,
             f"{profile}: observation is incomplete")
    first_source = first.get("source_inputs")
    second_source = second.get("source_inputs")
    _require(isinstance(first_source, dict) and first_source == second_source,
             f"{profile}: A/B source-input closure differs")
    source_digest = _digest(first_source.get("sha256"), f"{profile} source closure")
    _require(
        isinstance(first_source.get("entries"), list)
        and len(first_source["entries"]) == 1252,
             f"{profile}: source-input entry count changed")
    _require(first.get("final") == second.get("final"),
             f"{profile}: A/B final identity differs")
    final = first["final"]
    report_records: list[dict[str, Any]] = []
    for index, (path, report, receipt) in enumerate(
        zip(OBSERVATIONS[profile], reports, admitted)
    ):
        report_records.append(_record(path, receipt["report_payload"]))
        component = report.get("component")
        _require(isinstance(component, dict), f"{profile}: component report missing")
        _require(
            (component.get("size"), component.get("sha256"))
            == (final.get("component_size"), final.get("component_sha256")),
            f"{profile}: observation component identity differs from receipt",
        )
        expected_component_path = receipt["artifact_paths"]["component"]
        _require(
            component.get("artifact")
            == expected_component_path.relative_to(ROOT).as_posix(),
            f"{profile}: observation component path differs from receipt",
        )
        overlay = report.get("overlay")
        _require(isinstance(overlay, dict), f"{profile}: overlay report missing")
        _require(
            (overlay.get("size"), overlay.get("sha256"))
            == (final.get("overlay_size"), final.get("overlay_sha256")),
            f"{profile}: observation overlay identity differs from receipt",
        )
        expected_overlay_path = receipt["artifact_paths"]["overlay"]
        _require(
            overlay.get("artifact") == expected_overlay_path.relative_to(ROOT).as_posix(),
            f"{profile}: observation overlay path differs from receipt",
        )
    accounting = _component_accounting(reports[0]["component"], f"{profile} main")
    second_accounting = _component_accounting(
        reports[1]["component"], f"{profile} main replay"
    )
    _require(accounting == second_accounting, f"{profile}: A/B accounting differs")
    identity = {
        "source_inputs_sha256": source_digest,
        "source_input_entries": len(first_source["entries"]),
        "component_sha256": _digest(final.get("component_sha256"), "main component"),
        "component_size": _integer(final.get("component_size"), "main size", minimum=1),
        "overlay_sha256": _digest(final.get("overlay_sha256"), "main overlay"),
        "overlay_size": _integer(final.get("overlay_size"), "main overlay size", minimum=1),
        "observation_reports": report_records,
    }
    return accounting, identity, first_source


def _boot(profile: str) -> tuple[dict[str, int], dict[str, Any]]:
    path = BOOT_REPORTS[profile]
    report, report_record = _read_with_record(path, f"{profile} boot report")
    component = report.get("component")
    _require(isinstance(component, dict), f"{profile}: boot component report missing")
    _artifact(path.parent, component, f"{profile} boot component")
    accounting = _component_accounting(component, f"{profile} boot")
    return accounting, {
        "component_size": accounting["size"],
        "component_sha256": _digest(component.get("sha256"), f"{profile} boot digest"),
        "report": report_record,
    }


def _em9305() -> tuple[dict[str, Any], dict[str, Any]]:
    """Authenticate the mixed-source EM9305 production-provider receipt."""
    report, report_record = _read_with_record(
        EM9305_REPORT, "EM9305 production provider report"
    )
    _require(
        report.get("status") == "em9305-runtime-production-routed"
        and report.get("production_routed") is True,
        "EM9305 production route is not admitted",
    )
    provider = report.get("provider")
    _require(isinstance(provider, dict), "EM9305 provider receipt missing")
    expected_receipt = {key: EM9305_PROVIDER[key] for key in ("path", "size", "sha256")}
    _require(provider == expected_receipt, "EM9305 provider receipt identity changed")
    artifact = _artifact(
        ROOT,
        {"artifact": provider["path"], "size": provider["size"],
         "sha256": provider["sha256"]},
        "EM9305 production provider",
    )
    accounting = report.get("accounting")
    expected_report_accounting = {
        "production_source_bytes": EM9305_ACCOUNTING[PRODUCTION],
        "generated_or_reconstructible_bytes": EM9305_ACCOUNTING[GENERATED],
        "candidate_source_not_routed_bytes": EM9305_ACCOUNTING[CANDIDATE],
        "typed_retained_or_external_bytes": EM9305_ACCOUNTING[RETAINED],
        "unclassified_bytes": EM9305_ACCOUNTING[UNCLASSIFIED],
    }
    _require(
        accounting == expected_report_accounting,
        "EM9305 production-provider accounting changed",
    )
    _require(
        sum(EM9305_ACCOUNTING.values()) == EM9305_PROVIDER["size"],
        "EM9305 production-provider accounting does not conserve",
    )
    _require(
        report.get("hardware_validation")
        == "blocked by unavailable physical evidence"
        and report.get("hardware_operations") == [],
        "EM9305 hardware-evidence boundary changed",
    )
    return {
        "size": EM9305_PROVIDER["size"],
        "buckets": dict(EM9305_ACCOUNTING),
    }, {
        "provider": dict(EM9305_PROVIDER),
        "artifact": artifact,
        "report": report_record,
        "production_routed": True,
        "hardware_validation": report["hardware_validation"],
        "hardware_operations": [],
    }


def _status_totals(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for row in rows:
        status = row.get("address_status")
        _require(isinstance(status, str) and status, "flash row status missing")
        record = result.setdefault(status, {"regions": 0, "bytes": 0})
        record["regions"] += 1
        record["bytes"] += _integer(row.get("size"), "flash row size", minimum=1)
    return dict(sorted(result.items()))


def _package(profile: str) -> tuple[dict[str, Any], dict[str, dict[str, int]]]:
    root = PACKAGE_DIRS[profile]
    build, build_record = _read_with_record(
        root / "build-report.json", f"{profile} package report"
    )
    plan_path = root / "flash-plan.json"
    plan, plan_record = _read_with_record(plan_path, f"{profile} flash plan")
    _require(build.get("toolchain_profile") == profile, f"{profile}: build profile changed")
    _require(plan.get("toolchain_profile") == profile, f"{profile}: plan profile changed")
    package = build.get("package")
    _require(isinstance(package, dict), f"{profile}: package report missing")
    _artifact(root, package, f"{profile} package")
    _require(package.get("byte_identical_to_reference") is True,
             f"{profile}: package is not byte-identical to its pin")
    _require(package.get("sha256") == plan.get("package_sha256"),
             f"{profile}: plan/package identity differs")
    semantics = plan.get("address_status_semantics")
    _require(isinstance(semantics, dict),
             f"{profile}: address-status ownership semantics missing")
    _exact_keys(
        semantics,
        {
            "address_and_artifact_mapping", "ownership_labels",
            "authoritative_ownership_companion", "typed_mixed_profile_spans",
        },
        f"{profile} address-status semantics",
    )
    _require(
        semantics["address_and_artifact_mapping"] == "authoritative"
        and semantics["authoritative_ownership_companion"]
        == "tools/manifests/g2-dual-profile-ownership.json",
        f"{profile}: ownership authority pointer changed",
    )
    expected_mode = (
        "non_authoritative_requires_checked_reconciliation"
        if profile == "apple-clang"
        else "non_authoritative_profile_coarse"
    )
    _require(semantics["ownership_labels"] == expected_mode,
             f"{profile}: ownership label qualification changed")
    unresolved = plan.get("unresolved_flash_regions")
    flash = plan.get("flash_regions")
    container = plan.get("container_only_regions")
    providers = build.get("providers")
    _require(
        isinstance(unresolved, list) and not unresolved
        and isinstance(flash, list) and isinstance(container, list)
        and isinstance(providers, list),
        f"{profile}: plan/provider rows are invalid",
    )
    provider_sizes: dict[str, int] = {}
    provider_identities: dict[str, dict[str, Any]] = {}
    for provider in providers:
        _require(isinstance(provider, dict), f"{profile}: provider row is invalid")
        _exact_keys(
            provider, {"component", "kind", "path", "sha256", "size"},
            f"{profile} provider row",
        )
        name = provider.get("component")
        _require(isinstance(name, str) and name not in provider_sizes,
                 f"{profile}: duplicate provider")
        provider_sizes[name] = _integer(provider.get("size"), "provider size", minimum=1)
        kind = provider.get("kind")
        path_value = provider.get("path")
        provider_path = Path(path_value) if isinstance(path_value, str) else Path("/")
        _require(
            kind in {"official_blob", "source_build"}
            and isinstance(path_value, str)
            and path_value
            and not provider_path.is_absolute()
            and all(part not in ("", ".", "..") for part in provider_path.parts),
            f"{profile}: provider identity is invalid",
        )
        # Source-build receipts name the manifest output path.  That path is
        # shared by profile builds and can therefore be overwritten by a
        # later build of the other profile.  Authenticate Apollo providers
        # against their admitted, profile-specific canonical copies instead;
        # retain the receipt path validation above so an unexpected manifest
        # path still fails closed.
        authenticated_path = APOLLO_PROVIDER_PATHS.get(profile, {}).get(
            name, path_value
        )
        provider_identities[name] = {
            "kind": kind,
            "path": authenticated_path,
            "size": provider_sizes[name],
            "sha256": _digest(provider.get("sha256"), "provider digest"),
        }
        _artifact(
            ROOT,
            {
                "artifact": authenticated_path,
                "size": provider_sizes[name],
                "sha256": provider_identities[name]["sha256"],
            },
            f"{profile} provider {name}",
        )
    _require(set(provider_identities) == COMPONENT_IDS,
             f"{profile}: package must contain the exact six providers")
    partition: dict[str, int] = {}
    for row in flash + container:
        name = row.get("component")
        _require(isinstance(name, str), f"{profile}: region component missing")
        partition[name] = partition.get(name, 0) + _integer(
            row.get("size"), f"{profile} region size", minimum=1
        )
        _artifact(root, row, f"{profile} region {row.get('region')}")
    _require(partition == provider_sizes, f"{profile}: component regions do not conserve")
    payload = sum(provider_sizes.values())
    package_size = _integer(package.get("size"), f"{profile} package size", minimum=1)
    physical = sum(_integer(row["size"], "physical row", minimum=1) for row in flash)
    internal_container = sum(
        _integer(row["size"], "container row", minimum=1) for row in container
    )
    _require(physical + internal_container == payload,
             f"{profile}: physical/container partition changed")
    outer = package_size - payload
    _require(outer == 944 and internal_container == 300,
             f"{profile}: package/container envelope changed")
    mixed_spans = semantics["typed_mixed_profile_spans"]
    _require(isinstance(mixed_spans, list),
             f"{profile}: typed mixed spans are invalid")
    if profile == "apple-clang":
        _require(not mixed_spans, "Apple plan unexpectedly claims a coarse profile span")
    else:
        expected_spans = [
            {
                "component": "ble_em9305",
                "component_file_offset": 0,
                "end_exclusive": provider_sizes["ble_em9305"],
                "size": provider_sizes["ble_em9305"],
                "classification": "typed_mixed_profile_ownership",
                "reason": (
                    "exact bytes and addresses; no complete per-byte "
                    "source-vs-generated-vs-retained mask is claimed"
                ),
            },
            {
                "component": "apollo_bootloader",
                "component_file_offset": 148599,
                "end_exclusive": provider_sizes["apollo_bootloader"],
                "size": provider_sizes["apollo_bootloader"] - 148599,
                "classification": "typed_mixed_profile_ownership",
                "reason": (
                    "exact bytes and addresses; no complete per-byte "
                    "source-vs-generated-vs-retained mask is claimed"
                ),
            },
            {
                "component": "apollo_main",
                "component_file_offset": 0,
                "end_exclusive": provider_sizes["apollo_main"],
                "size": provider_sizes["apollo_main"],
                "classification": "typed_mixed_profile_ownership",
                "reason": (
                    "exact bytes and addresses; no complete per-byte "
                    "source-vs-generated-vs-retained mask is claimed"
                ),
            },
        ]
        _require(mixed_spans == expected_spans,
                 "Linux typed mixed profile boundary changed")
    apollo_rows = [row for row in flash if row.get("component") in APOLLO_COMPONENTS]
    apollo_container = [
        row for row in container if row.get("component") in APOLLO_COMPONENTS
    ]
    labels = {
        "source": sum(
            row["size"] for row in apollo_rows
            if row.get("address_status") in SOURCE_ADDRESS_STATUSES
        ),
        "generated_addressed": sum(
            row["size"] for row in apollo_rows
            if row.get("address_status") in GENERATED_ADDRESS_STATUSES
        ),
        "retained": sum(
            row["size"] for row in apollo_rows
            if row.get("address_status") == "official_blob"
        ),
        "component_container_metadata": sum(row["size"] for row in apollo_container),
    }
    _require(sum(labels.values()) == sum(
        provider_sizes[name] for name in APOLLO_COMPONENTS
    ), f"{profile}: Apollo label partition has an unknown status")
    return {
        "package_size": package_size,
        "package_sha256": _digest(package.get("sha256"), "package digest"),
        "package_report_sha256": build_record["sha256"],
        "package_report": build_record,
        "flash_plan_sha256": plan_record["sha256"],
        "flash_plan": plan_record,
        "component_payload_bytes": payload,
        "physical_flash_bytes": physical,
        "internal_component_container_bytes": internal_container,
        "outer_evenota_envelope_bytes": outer,
        "flash_regions": len(flash),
        "container_regions": len(container),
        "unresolved_regions": 0,
        "address_status_ownership_mode": semantics["ownership_labels"],
        "typed_mixed_profile_spans": mixed_spans,
        "providers": provider_identities,
    }, {"labels": labels, "statuses": _status_totals(flash + container)}


def _buckets(size: int, source: int, generated: int, candidate: int,
             retained: int) -> dict[str, int]:
    _require(
        all(type(value) is int and value >= 0
            for value in (size, source, generated, candidate, retained)),
        "component buckets contain an invalid integer",
    )
    result = {
        PRODUCTION: source,
        GENERATED: generated,
        CANDIDATE: candidate,
        RETAINED: retained,
        UNCLASSIFIED: 0,
    }
    _require(sum(result.values()) == size, "component buckets do not conserve")
    return result


def _nemavg_boundary(details: Any) -> dict[str, Any]:
    """Authenticate the complete three-function NemaVG stroke-cap route."""
    _require(isinstance(details, dict), "Apollo completion details are invalid")
    observed = {
        "stock_functions": (
            _integer(
                details.get("nemavg_stroke_cap_source_routed_functions"),
                "Apollo NemaVG source-routed functions",
            )
            + _integer(
                details.get("nemavg_stroke_cap_retained_unpatched_functions"),
                "Apollo NemaVG retained unpatched functions",
            )
        ),
        "stock_physical_bytes": (
            _integer(
                details.get("nemavg_stroke_cap_source_routed_stock_bytes"),
                "Apollo NemaVG source-routed stock bytes",
            )
            + _integer(
                details.get("nemavg_stroke_cap_retained_unpatched_stock_bytes"),
                "Apollo NemaVG retained unpatched stock bytes",
            )
        ),
        "source_routed_functions": _integer(
            details.get("nemavg_stroke_cap_source_routed_functions"),
            "Apollo NemaVG source-routed functions",
        ),
        "source_routed_stock_bytes": _integer(
            details.get("nemavg_stroke_cap_source_routed_stock_bytes"),
            "Apollo NemaVG source-routed stock bytes",
        ),
        "retained_unpatched_functions": _integer(
            details.get("nemavg_stroke_cap_retained_unpatched_functions"),
            "Apollo NemaVG retained unpatched functions",
        ),
        "retained_unpatched_stock_bytes": _integer(
            details.get("nemavg_stroke_cap_retained_unpatched_stock_bytes"),
            "Apollo NemaVG retained unpatched stock bytes",
        ),
        "candidate_source_not_routed_functions": _integer(
            details.get("nemavg_stroke_cap_candidate_functions"),
            "Apollo NemaVG candidate functions",
        ),
        "candidate_source_not_routed_bytes": _integer(
            details.get("nemavg_stroke_cap_candidate_bytes"),
            "Apollo NemaVG candidate bytes",
        ),
        "coordinator_production_routed": _boolean(
            details.get("nemavg_stroke_cap_coordinator_production_routed"),
            "Apollo NemaVG coordinator production route",
        ),
        "endpoint_stock_entries_unpatched": _boolean(
            details.get("nemavg_stroke_cap_endpoint_stock_entries_unpatched"),
            "Apollo NemaVG endpoint stock-entry state",
        ),
        "whole_candidate_production_routed": _boolean(
            details.get("nemavg_stroke_cap_production_routed"),
            "Apollo NemaVG whole-candidate production route",
        ),
        "ownership_accounting": NEMAVG_COORDINATOR_BOUNDARY[
            "ownership_accounting"
        ],
    }
    _require(
        observed == NEMAVG_COORDINATOR_BOUNDARY,
        "Apollo NemaVG complete ownership boundary changed",
    )
    return observed


def _observed() -> dict[str, Any]:
    # Authenticate both pairs as one globally independent evidence set before
    # consuming readiness, manifest, boot, package, or source-closure inputs.
    # Pair-local reproducibility alone cannot exclude a cross-profile hardlink.
    try:
        admitted_observations = {
            profile: canonical_admission.admit_reproducible_pair(
                list(OBSERVATIONS[profile]), profile
            )
            for profile in ("apple-clang", "linux-clang")
        }
        canonical_admission.validate_observation_independence(
            (
                *admitted_observations["apple-clang"],
                *admitted_observations["linux-clang"],
            )
        )
    except canonical_admission.AdmissionError as error:
        raise OwnershipError(f"canonical observation evidence: {error}") from error

    # Derive the shared non-Apollo boundary from the live authoritative audit.
    # The checked companion must not bootstrap from the generated completion
    # assessment that it is itself responsible for gating.
    live = readiness.analyze()
    components = live.get("components")
    _require(isinstance(components, dict), "live component ledger missing")
    common: dict[str, dict[str, Any]] = {}
    for component_id, display_name in ASSESSMENT_NAMES.items():
        row = components.get(component_id)
        _require(isinstance(row, dict), f"{display_name}: live row missing")
        buckets = row.get("buckets")
        _require(isinstance(buckets, dict) and set(buckets) == set(BUCKETS),
                 f"{display_name}: bucket schema changed")
        normalized = {key: _integer(buckets[key], f"{display_name}/{key}")
                      for key in BUCKETS}
        size = _integer(row.get("size"), f"{display_name} size", minimum=1)
        _require(sum(normalized.values()) == size,
                 f"{display_name}: completion bytes do not conserve")
        _require(row.get("classification_complete") is True,
                 f"{display_name}: classification is incomplete")
        common[component_id] = {"size": size, "buckets": normalized}

    em9305, em9305_identity = _em9305()
    em9305_live = components.get("ble_em9305")
    _require(isinstance(em9305_live, dict), "EM9305 live row missing")
    _require(
        em9305_live.get("size") == em9305["size"]
        and em9305_live.get("buckets") == em9305["buckets"]
        and em9305_live.get("classification_complete") is True,
        "EM9305 live readiness differs from its production-provider receipt",
    )

    apple_main_row = components.get("apollo_main")
    _require(isinstance(apple_main_row, dict), "Apple main live row missing")
    nemavg_boundary = _nemavg_boundary(apple_main_row.get("details"))
    candidate = nemavg_boundary["candidate_source_not_routed_bytes"]

    base = _read(BASE_MANIFEST)
    base_rows = base.get("components")
    _require(isinstance(base_rows, list), "base component ledger missing")
    base_components = {
        row.get("name"): row for row in base_rows if isinstance(row, dict)
    }
    _require(set(base_components) == COMPONENT_IDS,
             "base manifest component set changed")
    common_providers: dict[str, dict[str, Any]] = {}
    for component_id in ASSESSMENT_NAMES:
        provider = base_components[component_id].get("provider")
        _require(isinstance(provider, dict),
                 f"{component_id}: base provider missing")
        common_providers[component_id] = {
            "kind": "official_blob",
            "path": provider.get("path"),
            "size": _integer(provider.get("size"), f"{component_id} base size", minimum=1),
            "sha256": _digest(provider.get("sha256"), f"{component_id} base digest"),
        }

    try:
        current_source_inputs = canonical_admission.current_source_input_report()
    except canonical_admission.AdmissionError as error:
        raise OwnershipError(f"current canonical source closure: {error}") from error
    _require(
        isinstance(current_source_inputs.get("entries"), list)
        and len(current_source_inputs["entries"]) == 1252,
        "current canonical source closure entry count changed",
    )

    profile_rows: dict[str, Any] = {}
    source_closures: set[str] = set()
    for profile in ("apple-clang", "linux-clang"):
        main, main_identity, source_inputs = _canonical_main(
            profile, admitted_observations[profile]
        )
        _require(
            source_inputs == current_source_inputs,
            f"{profile}: observations are stale for current source inputs",
        )
        boot, boot_identity = _boot(profile)
        source_closures.add(main_identity["source_inputs_sha256"])
        package, plan = _package(profile)
        _require(
            package["providers"]["apollo_main"]
            == {"kind": "source_build",
                "path": APOLLO_PROVIDER_PATHS[profile]["apollo_main"],
                "size": main_identity["component_size"],
                "sha256": main_identity["component_sha256"]},
            f"{profile}: packaged main differs from admitted observation",
        )
        _require(
            package["providers"]["apollo_bootloader"]
            == {"kind": "source_build",
                "path": APOLLO_PROVIDER_PATHS[profile]["apollo_bootloader"],
                "size": boot_identity["component_size"],
                "sha256": boot_identity["component_sha256"]},
                 f"{profile}: packaged boot differs from its report")
        _require(
            package["providers"]["ble_em9305"] == EM9305_PROVIDER,
            f"{profile}: packaged EM9305 differs from its production receipt",
        )
        for component_id, expected in common_providers.items():
            _require(
                package["providers"][component_id] == expected,
                f"{profile}: packaged {component_id} differs from base/readiness evidence",
            )
            _require(
                common[component_id]["size"] == expected["size"],
                f"{profile}: {component_id} readiness size differs from provider",
            )
        apollo_exact = {
            "source": main["source"] + boot["source"],
            "generated_addressed": (
                main["generated_addressed"] + boot["generated_addressed"]
            ),
            "retained": main["retained"] + boot["retained"],
            "component_container_metadata": (
                main["component_container_metadata"]
                + boot["component_container_metadata"]
            ),
        }
        _require(sum(apollo_exact.values()) == main["size"] + boot["size"],
                 f"{profile}: exact Apollo accounting does not conserve")
        labels = plan["labels"]
        delta = {key: labels[key] - apollo_exact[key] for key in labels}
        reconciliation_bytes = sum(value for value in delta.values() if value > 0)
        _require(sum(delta.values()) == 0, f"{profile}: label delta does not conserve")

        component_rows = {
            "apollo_main": {
                "size": main["size"],
                "buckets": _buckets(
                    main["size"], main["source"],
                    main["generated_addressed"] + main["component_container_metadata"],
                    candidate, main["retained"] - candidate,
                ),
            },
            "apollo_bootloader": {
                "size": boot["size"],
                "buckets": _buckets(
                    boot["size"], boot["source"],
                    boot["generated_addressed"] + boot["component_container_metadata"],
                    0, boot["retained"],
                ),
            },
            "ble_em9305": em9305,
            **common,
        }
        for component_id, row in component_rows.items():
            _require(
                package["providers"][component_id]["size"] == row["size"],
                f"{profile}: {component_id} provider/component size differs",
            )
        aggregate = {
            key: sum(row["buckets"][key] for row in component_rows.values())
            for key in BUCKETS
        }
        _require(sum(aggregate.values()) == package["component_payload_bytes"],
                 f"{profile}: aggregate ownership does not conserve")
        _require(aggregate[UNCLASSIFIED] == 0,
                 f"{profile}: unclassified bytes remain")
        profile_rows[profile] = {
            "main_observation": main_identity,
            "boot_provider": boot_identity,
            "em9305_provider": em9305_identity,
            "package": package,
            "components": component_rows,
            "nemavg_stroke_cap_boundary": nemavg_boundary,
            "aggregate_buckets": aggregate,
            "release_blocking_bytes": aggregate[CANDIDATE] + aggregate[RETAINED],
            "per_byte_ownership_mask_complete": profile == "apple-clang",
            "per_byte_ownership_authority": (
                "canonical Apple component builder/region mask"
                if profile == "apple-clang"
                else "aggregate totals plus explicit typed-mixed spans only"
            ),
            "flash_plan_address_status_totals": plan["statuses"],
            "apollo_flash_label_reconciliation": {
                "plan_labels": labels,
                "authoritative_builder_accounting": apollo_exact,
                "plan_minus_authoritative": delta,
                "bytes_requiring_reconciliation": reconciliation_bytes,
                "qualification": (
                    "flash addresses and bytes are exact; profile-coarse address_status "
                    "labels are non-authoritative and reconciled to admitted builder receipts"
                ),
            },
        }
    _require(len(source_closures) == 1, "profile source-input closures differ")
    _require(
        profile_rows["apple-clang"]["per_byte_ownership_mask_complete"] is True
        and not profile_rows["apple-clang"]["package"]
            ["typed_mixed_profile_spans"]
        and profile_rows["linux-clang"]
            ["per_byte_ownership_mask_complete"] is False
        and len(profile_rows["linux-clang"]["package"]
                ["typed_mixed_profile_spans"]) == 3,
        "dual-profile per-byte ownership authority policy changed",
    )

    authority = live.get("licensing", {}).get("unresolved_binary_authority")
    _require(
        authority == [
            "codec", "ble_em9305", "touch", "case",
            "apollo_bootloader", "apollo_main",
        ],
        "binary redistribution authority boundary changed",
    )
    gates = live.get("gates")
    _require(isinstance(gates, dict), "completion gates missing")
    _require(gates.get("release_authorized") is False,
             "binary release unexpectedly authorized")
    _require(gates.get("hardware_validation") == "blocked by unavailable physical evidence",
             "hardware validation policy changed")
    return {
        "schema_version": 4,
        "target": "G2 s200_v2.2.6.10 dual-profile ownership reconciliation",
        "analysis_mode": (
            "offline read-only accounting; no hardware, network, signing, flashing, "
            "staging, or publishing operation"
        ),
        "classification_policy": (
            "admitted component build reports are authoritative for source/generated/"
            "retained totals; flash-plan address_status rows remain an address map and "
            "require the checked profile reconciliation below"
        ),
        "source_inputs_sha256": next(iter(source_closures)),
        "profiles": profile_rows,
        "per_byte_ownership_policy": {
            "all_profiles_mask_complete": False,
            "sole_current_authority_profile": "apple-clang",
            "linux_per_byte_ownership_mask_complete": False,
            "qualification": (
                "Linux aggregate buckets and typed-mixed spans are exact, but no "
                "Linux per-byte source/generated/retained ownership is fabricated"
            ),
        },
        "gates": {
            "dual_profile_byte_accounting_complete": True,
            "dual_profile_classification_complete": True,
            "dual_profile_unclassified_bytes": 0,
            "source_complete": False,
            "binary_redistribution_authority_resolved": False,
            "release_authorized": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_operations": [],
        },
        "unresolved_binary_authority": authority,
    }


def _checked_projection(report: dict[str, Any]) -> dict[str, Any]:
    profile_rows: dict[str, Any] = {}
    package_keys = {
        "address_status_ownership_mode", "component_payload_bytes",
        "container_regions", "flash_plan_sha256", "flash_regions",
        "flash_plan",
        "internal_component_container_bytes", "outer_evenota_envelope_bytes",
        "package_report", "package_report_sha256", "package_sha256", "package_size",
        "physical_flash_bytes", "typed_mixed_profile_spans", "unresolved_regions",
        "providers",
    }
    for profile, row in report["profiles"].items():
        package = row["package"]
        profile_rows[profile] = {
            "main_observation": row["main_observation"],
            "boot_provider": row["boot_provider"],
            "em9305_provider": row["em9305_provider"],
            "package": {key: package[key] for key in sorted(package_keys)},
            "nemavg_stroke_cap_boundary": row["nemavg_stroke_cap_boundary"],
            "aggregate_buckets": row["aggregate_buckets"],
            "release_blocking_bytes": row["release_blocking_bytes"],
            "per_byte_ownership_mask_complete":
                row["per_byte_ownership_mask_complete"],
            "per_byte_ownership_authority":
                row["per_byte_ownership_authority"],
            "apollo_flash_label_reconciliation": (
                row["apollo_flash_label_reconciliation"]
            ),
        }
    return {
        "schema_version": report["schema_version"],
        "target": report["target"],
        "classification_policy": report["classification_policy"],
        "source_inputs_sha256": report["source_inputs_sha256"],
        "profiles": profile_rows,
        "per_byte_ownership_policy": report["per_byte_ownership_policy"],
        "gates": report["gates"],
        "unresolved_binary_authority": report["unresolved_binary_authority"],
    }


def _companion_payload(report: dict[str, Any]) -> bytes:
    """Render the exact checked projection in its canonical tracked form."""
    return (
        json.dumps(_checked_projection(report), indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_companion(
    report: dict[str, Any], companion_path: Path = COMPANION
) -> dict[str, Any]:
    """Atomically publish one already authenticated checked projection."""
    root = ROOT.resolve()
    lexical = Path(os.path.abspath(companion_path))
    try:
        lexical.relative_to(root)
        resolved_parent = lexical.parent.resolve(strict=True)
        resolved_parent.relative_to(root)
    except (OSError, ValueError, RuntimeError) as error:
        raise OwnershipError("companion output path escapes the G2 tree") from error
    _require(lexical.parent == resolved_parent,
             "companion output parent contains a symlink")
    _require(lexical.name not in ("", ".", ".."),
             "companion output name is invalid")
    if lexical.exists() or lexical.is_symlink():
        _stable_file(lexical, "existing ownership companion")

    payload = _companion_payload(report)
    try:
        canonical_admission.atomic_write(lexical, payload)
    except OSError as error:
        raise OwnershipError(f"cannot write ownership companion: {error}") from error
    written, _identity = _stable_file(lexical, "written ownership companion")
    _require(written == payload, "written ownership companion readback changed")
    return _record(lexical, written)


def analyze(
    companion_path: Path = COMPANION,
    *,
    verify_companion: bool = True,
) -> dict[str, Any]:
    observed = _observed()
    if verify_companion:
        expected = _read(companion_path)
        _require(
            _checked_projection(observed) == expected,
            "checked dual-profile ownership companion is stale",
        )
    return observed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--observed", action="store_true",
        help="print live calculated evidence without accepting it as the checked gate",
    )
    mode.add_argument(
        "--write-companion", action="store_true",
        help=(
            "maintainer-only atomic refresh of the checked companion from all "
            "currently authenticated live evidence"
        ),
    )
    args = parser.parse_args(argv)
    if args.write_companion:
        report = analyze(COMPANION, verify_companion=False)
        record = write_companion(report, COMPANION)
        report = analyze(COMPANION)
    else:
        report = analyze(COMPANION, verify_companion=not args.observed)
        record = None
    if args.json or args.observed:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for profile, row in report["profiles"].items():
            buckets = row["aggregate_buckets"]
            reconciliation = row["apollo_flash_label_reconciliation"]
            print(
                f"{profile}: source={buckets[PRODUCTION]} "
                f"generated={buckets[GENERATED]} candidate={buckets[CANDIDATE]} "
                f"retained={buckets[RETAINED]} unclassified={buckets[UNCLASSIFIED]} "
                f"reconciled-label-bytes={reconciliation['bytes_requiring_reconciliation']}"
            )
        if record is not None:
            print(
                "Wrote dual-profile ownership companion: "
                f"{record['size']} bytes, sha256 {record['sha256']}"
            )
        print("Dual-profile ownership companion verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
