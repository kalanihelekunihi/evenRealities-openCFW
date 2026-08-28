#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the canonical Apollo core image and its bounded post-link providers."""

from __future__ import annotations

import argparse
import copy
import fcntl
import importlib.util
import json
import os
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
OPENCFW_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402,F401
    BuildError,
    atomic_write,
    build as overlay_build,
    decode_thumb_branch,
    resolve_toolchain_profile,
    sha256,
)


_INPUT_EXCLUDED_DIRECTORIES = {"build", "__pycache__", "blobs"}
_INPUT_EXCLUDED_SUFFIXES = {
    ".a", ".bin", ".dylib", ".elf", ".map", ".o", ".pyc", ".so",
}
_CANONICAL_OUTPUT_THREAD_LOCK = threading.Lock()


def _walk_config(value: Any):
    """Yield every nested mapping in a canonical component config."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_config(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_config(child)


def _resolve_input(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise BuildError(f"canonical build input escapes repository: {value}") \
            from error
    return path


def _excluded_recursive_input(root: Path, path: Path) -> bool:
    relative = path.relative_to(root.resolve())
    if path.name == ".DS_Store" or path.suffix.lower() in _INPUT_EXCLUDED_SUFFIXES:
        return True
    return any(
        part in _INPUT_EXCLUDED_DIRECTORIES
        or part.startswith("build-")
        or part.startswith(".tmp-")
        for part in relative.parts
    )


def _canonical_input_paths(
    root: Path, config_path: Path, config: dict[str, Any]
) -> tuple[Path, ...]:
    """Return the complete declared source/config closure for a core build."""
    root = root.resolve()
    liblc3_root = COMPONENT_ROOT.parent / "liblc3_ltpf"
    pt_root = COMPONENT_ROOT.parent / "pt_protocol"
    fixed = {
        config_path.resolve(),
        Path(__file__).resolve(),
        (root / "tools/apollo_overlay.py").resolve(),
        (liblc3_root / "build_component.py").resolve(),
        (liblc3_root / "overlay.json").resolve(),
        (pt_root / "build_component.py").resolve(),
    }
    liblc3_config = json.loads(
        (liblc3_root / "overlay.json").read_text(encoding="utf-8")
    )
    configs = (config, liblc3_config)
    include_dirs: set[Path] = set()
    for candidate_config in configs:
        for record in _walk_config(candidate_config):
            relative = record.get("path")
            if isinstance(relative, str):
                fixed.add(_resolve_input(root, relative))
            configured_includes = record.get("include_dirs")
            if isinstance(configured_includes, list):
                for relative_include in configured_includes:
                    if not isinstance(relative_include, str):
                        raise BuildError(
                            "canonical build include directory is not a string"
                        )
                    include_dirs.add(_resolve_input(root, relative_include))

    # The bounded PT builder carries its source list in code rather than a
    # separate JSON config. Include both its translation units and headers.
    fixed.update(COMPONENT_ROOT.glob("pt_protocol_*.c"))
    fixed.update(COMPONENT_ROOT.glob("pt_protocol_*.h"))

    for directory in include_dirs:
        if not directory.is_dir():
            raise BuildError(
                f"canonical build include directory is missing: {directory}"
            )
        for path in directory.rglob("*"):
            if path.is_file() and not _excluded_recursive_input(root, path):
                fixed.add(path.resolve())

    missing = [path for path in fixed if not path.is_file()]
    if missing:
        raise BuildError(f"canonical build input is missing: {sorted(missing)[0]}")
    return tuple(sorted(fixed, key=lambda path: path.as_posix()))


def _canonical_input_snapshot(
    root: Path, config_path: Path, config: dict[str, Any]
) -> dict[str, tuple[int, str]]:
    root = root.resolve()
    snapshot: dict[str, tuple[int, str]] = {}
    for path in _canonical_input_paths(root, config_path, config):
        payload = path.read_bytes()
        snapshot[path.relative_to(root).as_posix()] = (len(payload), sha256(payload))
    return snapshot


def _require_canonical_inputs_unchanged(
    root: Path,
    config_path: Path,
    config: dict[str, Any],
    expected: dict[str, tuple[int, str]],
) -> None:
    try:
        observed = _canonical_input_snapshot(root, config_path, config)
    except (BuildError, OSError):
        raise BuildError("canonical build inputs changed during build") from None
    if observed != expected:
        raise BuildError("canonical build inputs changed during build")


@contextmanager
def _canonical_output_lock(output_dir: Path):
    """Serialize the complete artifact/report generation publication."""
    output_dir.mkdir(parents=True, exist_ok=True)
    lock_path = output_dir / ".open-cfw-canonical.lock"
    with _CANONICAL_OUTPUT_THREAD_LOCK:
        with lock_path.open("a+b") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _capture_canonical_generation(
    overlay_path: Path, component_path: Path, report_path: Path
) -> dict[Path, tuple[bool, bytes]]:
    previous = {
        path: (path.is_file(), path.read_bytes() if path.is_file() else b"")
        for path in (overlay_path, component_path, report_path)
    }
    if previous[report_path][0]:
        try:
            report = json.loads(previous[report_path][1].decode("utf-8"))
            overlay = report["overlay"]
            component = report["component"]
            if not isinstance(overlay, dict) or not isinstance(component, dict):
                raise TypeError
            observed = (
                int(overlay.get("size", -1)),
                overlay.get("sha256"),
                int(component.get("size", -1)),
                component.get("sha256"),
            )
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ):
            raise BuildError("canonical existing generation identity changed") \
                from None
        if (
            not previous[overlay_path][0]
            or not previous[component_path][0]
            or observed[0] != len(previous[overlay_path][1])
            or observed[1] != sha256(previous[overlay_path][1])
            or observed[2] != len(previous[component_path][1])
            or observed[3] != sha256(previous[component_path][1])
        ):
            raise BuildError("canonical existing generation identity changed")
    return previous


def _restore_canonical_generation(
    previous: dict[Path, tuple[bool, bytes]],
    overlay_path: Path,
    component_path: Path,
    report_path: Path,
) -> None:
    """Restore a prior complete generation, with its report written last."""
    report_path.unlink(missing_ok=True)
    for path in (overlay_path, component_path):
        existed, payload = previous[path]
        if existed:
            atomic_write(path, payload)
        else:
            path.unlink(missing_ok=True)
    for path in (overlay_path, component_path):
        existed, payload = previous[path]
        if path.is_file() != existed or (existed and path.read_bytes() != payload):
            raise BuildError("canonical generation rollback failed")
    report_existed, report_payload = previous[report_path]
    if report_existed:
        atomic_write(report_path, report_payload)
    if (report_path.is_file() != report_existed or
            (report_existed and report_path.read_bytes() != report_payload)):
        report_path.unlink(missing_ok=True)
        raise BuildError("canonical generation rollback failed")


def _publish_canonical_outputs(
    *,
    root: Path,
    config_path: Path,
    config: dict[str, Any],
    input_snapshot: dict[str, tuple[int, str]],
    overlay_path: Path,
    final_overlay: bytes,
    component_path: Path,
    final_component: bytes,
    report_path: Path,
    report: dict[str, Any],
) -> None:
    """Publish a validated artifact pair, then its report as commit marker."""
    report_payload = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    expected_overlay = report.get("overlay", {})
    expected_component = report.get("component", {})
    if (expected_overlay.get("size") != len(final_overlay) or
            expected_overlay.get("sha256") != sha256(final_overlay) or
            expected_component.get("size") != len(final_component) or
            expected_component.get("sha256") != sha256(final_component)):
        raise BuildError("canonical report artifact identity changed")
    parents = {
        overlay_path.resolve().parent,
        component_path.resolve().parent,
        report_path.resolve().parent,
    }
    if len(parents) != 1:
        raise BuildError("canonical outputs must share one publication directory")
    with _canonical_output_lock(report_path.parent):
        _require_canonical_inputs_unchanged(
            root, config_path, config, input_snapshot
        )
        previous = _capture_canonical_generation(
            overlay_path, component_path, report_path
        )
        # The report is the completed-generation marker.  Remove it before
        # changing either artifact so no reader can bless an in-flight pair.
        report_path.unlink(missing_ok=True)
        try:
            atomic_write(overlay_path, final_overlay)
            atomic_write(component_path, final_component)
            if (overlay_path.read_bytes() != final_overlay or
                    component_path.read_bytes() != final_component):
                raise BuildError("canonical published artifact readback changed")
            # Catch source drift during the two artifact renames before
            # committing the new generation with its report.
            _require_canonical_inputs_unchanged(
                root, config_path, config, input_snapshot
            )
            atomic_write(report_path, report_payload)
            if (report_path.read_bytes() != report_payload or
                    overlay_path.read_bytes() != final_overlay or
                    component_path.read_bytes() != final_component):
                raise BuildError("canonical published generation readback changed")
        except Exception:
            try:
                _restore_canonical_generation(
                    previous, overlay_path, component_path, report_path
                )
            except Exception as rollback_error:
                report_path.unlink(missing_ok=True)
                raise BuildError("canonical generation rollback failed") \
                    from rollback_error
            raise


def _load_liblc3_builder() -> Any:
    path = COMPONENT_ROOT.parent / "liblc3_ltpf" / "build_component.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_liblc3_ltpf_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load bounded liblc3 provider builder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _load_pt_protocol_builder() -> Any:
    path = COMPONENT_ROOT.parent / "pt_protocol" / "build_component.py"
    specification = importlib.util.spec_from_file_location(
        "open_cfw_pt_protocol_builder", path
    )
    if specification is None or specification.loader is None:
        raise BuildError(f"cannot load bounded PT protocol builder: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _stage_config(config: dict[str, Any], profile: str) -> dict[str, Any]:
    """Return the byte-identical pre-provider core configuration."""
    stage = copy.deepcopy(config)
    expected = stage.get("core_stage_expected")
    if not isinstance(expected, dict):
        raise BuildError("canonical core config lacks core_stage_expected")
    stage["expected"] = expected
    profiles = stage.get("toolchain_profiles", {})
    if profile != "apple-clang":
        selected = profiles.get(profile)
        if not isinstance(selected, dict):
            raise BuildError(f"unknown canonical toolchain profile {profile!r}")
        selected_expected = selected.get("core_stage_expected")
        if not isinstance(selected_expected, dict):
            raise BuildError(
                f"canonical profile {profile!r} lacks core_stage_expected"
            )
        selected["expected"] = selected_expected
    return stage


def _provider_profile(config: dict[str, Any], profile: str) -> dict[str, Any]:
    providers = config.get("post_link_providers")
    if not isinstance(providers, dict):
        raise BuildError("canonical core config lacks post_link_providers")
    provider = providers.get("liblc3_ltpf")
    if not isinstance(provider, dict):
        raise BuildError("canonical core config lacks liblc3_ltpf provider")
    profiles = provider.get("profiles")
    if not isinstance(profiles, dict) or not isinstance(profiles.get(profile), dict):
        raise BuildError(f"liblc3 provider lacks profile {profile!r}")
    return profiles[profile]


def _verify_pt_provider_profile(
    config: dict[str, Any], profile: str, report: dict[str, Any]
) -> None:
    provider = config.get("post_link_providers", {}).get("pt_protocol")
    profiles = provider.get("profiles") if isinstance(provider, dict) else None
    expected = profiles.get(profile) if isinstance(profiles, dict) else None
    if not isinstance(expected, dict):
        raise BuildError(f"PT protocol provider lacks profile {profile!r}")
    placement = report.get("placement")
    if not isinstance(placement, dict):
        raise BuildError("PT protocol provider placement report missing")
    observed = {
        "payload_size": int(placement.get("loadable_size", -1)),
        "payload_sha256": placement.get("payload_sha256"),
        "interval_sha256": placement.get("interval_sha256"),
    }
    if observed != expected:
        raise BuildError(
            f"PT protocol provider profile {profile!r} differs: "
            f"expected {expected!r}, observed {observed!r}"
        )


PT_SOURCE_UART_ROUTES = (
    ("open_cfw_retained_box_uart_product_test", "R_ARM_THM_CALL",
     0x0056F4A0, 88, 10),
    ("open_cfw_retained_box_uart_execute", "R_ARM_THM_CALL", 0x0056F92C,
     148, 10),
)


def _verify_pt_source_uart_ingress(
    config: dict[str, Any], stage_report: dict[str, Any], profile: str,
    stage_expected: dict[str, Any]
) -> tuple[bool, dict[str, Any]]:
    matches = [item for item in config.get("relocated_leaves", [])
               if item.get("function") == "open_cfw_box_uart_handle"]
    if len(matches) != 1 or matches[0].get("strict_relocation_contract") is not True:
        raise BuildError("canonical PT source-UART ingress contract missing")
    configured = tuple(sorted(
        (item.get("symbol"), item.get("type"),
         int(item.get("target_address", -1)), int(item.get("offset", -1)))
        for item in matches[0].get("relocations", [])
        if item.get("symbol") in {
            "open_cfw_retained_box_uart_product_test",
            "open_cfw_retained_box_uart_execute",
        }
    ))
    expected_configured = tuple(sorted(
        (symbol, kind, target, offset)
        for symbol, kind, target, offset, _type_id in PT_SOURCE_UART_ROUTES
    ))
    if configured != expected_configured:
        raise BuildError("canonical PT source-UART ingress addresses changed")
    stage_profile = stage_report.get("toolchain", {}).get("profile")
    stage_overlay = stage_report.get("overlay")
    if (stage_profile != profile or not isinstance(stage_overlay, dict) or
            int(stage_overlay.get("size", -1)) !=
            int(stage_expected.get("overlay_size", -2)) or
            stage_overlay.get("sha256") != stage_expected.get("overlay_sha256")):
        raise BuildError("canonical PT source-UART stage identity changed")
    enabled_profiles = matches[0].get("profiles")
    if (enabled_profiles is not None and
            (not isinstance(enabled_profiles, list) or
             any(not isinstance(item, str) for item in enabled_profiles))):
        raise BuildError("canonical PT source-UART profile contract changed")
    routed = enabled_profiles is None or profile in enabled_profiles
    reports = [
        item for item in stage_report.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function") ==
        "open_cfw_box_uart_handle"
    ]
    if routed:
        if len(reports) != 1:
            raise BuildError("canonical PT source-UART route receipt missing")
        extraction = reports[0].get("extraction", {})
        pins = reports[0].get("pins", {})
        leaf_expected = matches[0].get("expected")
        if not isinstance(leaf_expected, dict):
            raise BuildError("canonical PT source-UART leaf pins missing")
        for source in (extraction, pins):
            if any(source.get(key) != leaf_expected.get(key) for key in (
                "size", "sha256", "unrelocated_sha256", "alignment"
            )):
                raise BuildError("canonical PT source-UART leaf identity changed")
            observed = tuple(sorted(
                (item.get("symbol"), item.get("type"),
                 int(item.get("target_address", -1)),
                 int(item.get("offset", -1)),
                 int(item.get("type_id", 10 if source is pins else -1)))
                for item in source.get("relocations", [])
                if item.get("symbol") in {
                    "open_cfw_retained_box_uart_product_test",
                    "open_cfw_retained_box_uart_execute",
                }
            ))
            if observed != tuple(sorted(PT_SOURCE_UART_ROUTES)):
                raise BuildError(
                    "canonical PT source-UART route receipt changed"
                )
        if pins.get("offset") != leaf_expected.get("offset"):
            raise BuildError("canonical PT source-UART leaf identity changed")
    elif reports:
        raise BuildError("inactive PT source-UART leaf appeared in stage report")
    receipt = {
        "mode": (
            "source_overlay_relocation" if routed
            else "authenticated_donor_direct"
        ),
        "profile": profile,
        "function": "open_cfw_box_uart_handle",
        "strict_relocation_contract": True,
        "profile_route_active": routed,
        "stage_overlay": {
            "size": int(stage_overlay["size"]),
            "sha256": stage_overlay["sha256"],
        },
        "leaf": {
            "size": int(matches[0]["expected"]["size"]),
            "sha256": matches[0]["expected"]["sha256"],
            "unrelocated_sha256": matches[0]["expected"][
                "unrelocated_sha256"
            ],
            "alignment": int(matches[0]["expected"]["alignment"]),
            "offset": int(matches[0]["expected"]["offset"]),
        },
        "relocations": [
            {
                "symbol": symbol,
                "type": kind,
                "target_address": target,
                "offset": offset,
                "type_id": type_id,
            }
            for symbol, kind, target, offset, type_id in PT_SOURCE_UART_ROUTES
        ],
    }
    return routed, receipt


def _verify_final(
    observed: dict[str, Any], expected: dict[str, Any], *, record: bool
) -> None:
    if record:
        return
    for key in (
        "overlay_size",
        "overlay_sha256",
        "component_size",
        "component_sha256",
    ):
        if observed[key] != expected.get(key):
            raise BuildError(
                f"canonical post-link {key} differs: expected "
                f"{expected.get(key)!r}, observed {observed[key]!r}"
            )


def build(
    *,
    root: Path,
    config_path: Path,
    output_dir: Path,
    clang: str,
    toolchain_profile: str | None = None,
    record_profile: bool = False,
    record_canonical: bool = False,
) -> dict[str, Any]:
    """Build the default Apollo-main provider path, including liblc3 LTPF."""
    if record_profile:
        raise BuildError(
            "recording a core-stage profile alone would bypass canonical "
            "post-link providers; review and pin both stages together"
        )
    config_payload = config_path.read_bytes()
    config = json.loads(config_payload.decode("utf-8"))
    input_snapshot = _canonical_input_snapshot(root, config_path, config)
    config_key = config_path.resolve().relative_to(root.resolve()).as_posix()
    if input_snapshot.get(config_key) != (
        len(config_payload), sha256(config_payload)
    ):
        raise BuildError("canonical build inputs changed during build")
    _toolchain, final_expected, profile = resolve_toolchain_profile(
        config, toolchain_profile
    )
    stage = _stage_config(config, profile)
    provider_expected = _provider_profile(config, profile)

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".tmp-open-cfw-apollo-canonical-", dir=root
    ) as tmp:
        temporary = Path(tmp)
        stage_output = temporary / "core-stage"
        stage_config_path = temporary / "core-stage.json"
        stage_config_path.write_text(
            json.dumps(stage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        stage_report = overlay_build(
            root=root,
            config_path=stage_config_path,
            output_dir=stage_output,
            clang=clang,
            toolchain_profile=profile,
            record_profile=False,
        )
        stage_expected = (
            stage["expected"] if profile == "apple-clang" else
            stage["toolchain_profiles"][profile]["expected"]
        )
        source_uart_routed, source_uart_route_receipt = (
            _verify_pt_source_uart_ingress(
                config, stage_report, profile, stage_expected
            )
        )
        stage_component_path = stage_output / "ota_s200_firmware_ota.bin"
        stage_component = stage_component_path.read_bytes()
        stage_overlay = (stage_output / config["overlay_artifact"]).read_bytes()
        stage_component_pin = {
            "size": len(stage_component),
            "sha256": sha256(stage_component),
        }

        provider_output = temporary / "liblc3"
        provider_builder = _load_liblc3_builder()
        provider_report = provider_builder.build(
            config_path=COMPONENT_ROOT.parent / "liblc3_ltpf" / "overlay.json",
            output_dir=provider_output,
            clang=clang,
            profile=profile,
            record=record_canonical,
            base_path_override=stage_component_path,
            base_expected_override=stage_component_pin,
            expected_override=provider_expected,
            placement_override=provider_expected.get("placement"),
        )
        liblc3_component_path = provider_output / "ota_s200_firmware_ota.bin"
        liblc3_component = liblc3_component_path.read_bytes()
        pt_output = temporary / "pt-protocol"
        pt_builder = _load_pt_protocol_builder()
        pt_report = pt_builder.build(
            base_path=liblc3_component_path,
            output_dir=pt_output,
            clang=clang,
            profile=profile,
            base_expected={
                "size": len(liblc3_component),
                "sha256": sha256(liblc3_component),
            },
            ingress_authentication_base_path=root / config["base"]["path"],
            ingress_authentication_base_expected={
                "size": int(config["base"]["size"]),
                "sha256": config["base"]["sha256"],
            },
            source_uart_routed=source_uart_routed,
            source_uart_route_receipt=source_uart_route_receipt,
        )
        _verify_pt_provider_profile(config, profile, pt_report)
        final_component = (pt_output / "ota_s200_firmware_ota.bin").read_bytes()
        official_size = int(stage_report["base"]["size"])
        placement_sections = provider_report["placement"].get("sections")
        final_overlay = (
            stage_overlay
            if isinstance(placement_sections, dict)
            else final_component[official_size:]
        )

    observed = {
        "overlay_size": len(final_overlay),
        "overlay_sha256": sha256(final_overlay),
        "component_size": len(final_component),
        "component_sha256": sha256(final_component),
    }
    _verify_final(observed, final_expected, record=record_canonical)

    overlay_report = stage_report["overlay"]
    component_report = stage_report["component"]
    stage_overlay_size = int(overlay_report["size"])
    stage_component_size = int(component_report["size"])
    provider_runtime = int(provider_report["placement"]["runtime_address"])
    provider_payload_size = int(provider_report["overlay"]["size"])
    cave_placement = isinstance(placement_sections, dict)
    if cave_placement:
        if len(final_component) != stage_component_size:
            raise BuildError("canonical cave provider changed component size")
        admitted_source_bytes = sum(
            int(item["size"]) for item in placement_sections.values()
        )
        if admitted_source_bytes != provider_payload_size:
            raise BuildError("canonical liblc3 cave byte accounting changed")
        generated_delta = -admitted_source_bytes + 4
    else:
        admitted_source_bytes = len(final_component) - stage_component_size
        if admitted_source_bytes < provider_payload_size:
            raise BuildError("canonical appended provider accounting changed")
        generated_delta = 4
        provider_start = int(provider_report["placement"]["file_offset"])
        for name, function in provider_report["overlay"]["functions"].items():
            overlay_report["functions"][name] = {
                "offset": provider_start - official_size + int(function["offset"]),
                "size": int(function["size"]),
            }
        overlay_report["overlay_end_exclusive"] = (
            config["run_base"] + len(final_component) - config["preamble_bytes"]
        )
        overlay_report["overlay_end_exclusive_hex"] = (
            f"0x{overlay_report['overlay_end_exclusive']:08X}"
        )
    patch = provider_report["patch_site"]
    overlay_report["patched_sites"].append(
        {
            "branch": "bl",
            **(
                {"expected_hex": patch["expected_hex"]}
                if "expected_hex" in patch
                else {
                    "expected_size": patch["expected_size"],
                    "expected_sha256": patch["expected_sha256"],
                }
            ),
            "name": patch["name"],
            "payload_offset": int(patch["file_offset"]),
            "replacement_hex": patch["replacement_hex"],
            "runtime_address": int(patch["runtime_address"]),
            "runtime_address_hex": f"0x{int(patch['runtime_address']):08X}",
            "target_address": int(patch["decoded_target"]),
            "target_address_hex": f"0x{int(patch['decoded_target']):08X}",
            "target_function": patch["target_function"],
        }
    )
    if pt_report["patch_sites"]:
        raise BuildError("canonical PT provider unexpectedly requires patch sites")
    overlay_report.update(
        {
            "size": len(final_overlay),
            "sha256": sha256(final_overlay),
            **(
                {
                    "cave_functions": {
                        name: {
                            "runtime_address": provider_runtime
                            + int(function["offset"]),
                            "runtime_address_hex": (
                                f"0x{provider_runtime + int(function['offset']):08X}"
                            ),
                            "size": int(function["size"]),
                        }
                        for name, function in provider_report["overlay"][
                            "functions"
                        ].items()
                    }
                }
                if cave_placement
                else {}
            ),
            "post_link_providers": {
                "liblc3_ltpf": {
                    "license": "Apache-2.0",
                    "placement": (
                        placement_sections
                        if cave_placement
                        else {
                            "file_offset": provider_report["placement"][
                                "file_offset"
                            ],
                            "runtime_address": provider_runtime,
                        }
                    ),
                    "payload": {
                        "size": provider_payload_size,
                        "sha256": provider_report["overlay"]["sha256"],
                    },
                    "link": {
                        key: provider_report["overlay"][key]
                        for key in (
                            "text_size",
                            "rodata",
                            "text_relocations",
                            "dispatch_entries",
                            "discarded_cantunwind_rows",
                            "runtime_dependencies",
                            "section_runtime_addresses",
                        )
                    },
                    "historical_non_corpus_routing": (
                        provider_report["historical_non_corpus_routing"]
                    ),
                },
                "pt_protocol": {
                    "license": "MIT",
                    "placement": pt_report["placement"],
                    "payload": {
                        "size": int(pt_report["placement"]["loadable_size"]),
                        "sha256": pt_report["placement"]["payload_sha256"],
                    },
                    "source_provider_routes": pt_report[
                        "source_provider_routes"
                    ],
                    "entry_symbols": pt_report["symbols"],
                    "ingress_sites": pt_report["ingress_sites"],
                    "source_uart_route_receipt": pt_report[
                        "source_uart_route_receipt"
                    ],
                    "hardware": pt_report["hardware"],
                },
            },
        }
    )
    patch_bytes = len(bytes.fromhex(patch["replacement_hex"]))
    pt_patch_bytes = 0
    pt_capacity = int(pt_report["placement"]["capacity"])
    pt_payload_size = int(pt_report["placement"]["loadable_size"])
    pt_padding_size = int(pt_report["placement"]["padding_size"])
    if pt_payload_size + pt_padding_size != pt_capacity:
        raise BuildError("canonical PT in-place byte accounting changed")
    component_report.update(
        {
            "size": len(final_component),
            "sha256": sha256(final_component),
            "opaque_base_bytes": int(component_report["opaque_base_bytes"])
            - patch_bytes - pt_capacity - pt_patch_bytes,
            "source_owned_bytes": int(component_report["source_owned_bytes"])
            + admitted_source_bytes + pt_payload_size,
            "generated_patch_site_bytes": int(
                component_report["generated_patch_site_bytes"]
            )
            + generated_delta + pt_padding_size + pt_patch_bytes,
        }
    )
    stage_report["sources"].extend(provider_report["sources"])
    stage_report["sources"].extend(
        {
            **item,
            "license": "MIT",
            "role": "production PT protocol and source-owned board provider",
        }
        for item in pt_report["source"]["files"]
    )
    stage_report["canonical_stages"] = {
        "core": {
            "overlay_size": stage_overlay_size,
            "overlay_sha256": stage["expected"]["overlay_sha256"]
            if profile == "apple-clang"
            else stage["toolchain_profiles"][profile]["expected"]["overlay_sha256"],
            **stage_component_pin,
        },
        "liblc3_ltpf": {
            "license": "Apache-2.0",
            "payload_size": provider_payload_size,
            "payload_sha256": provider_report["overlay"]["sha256"],
            "historical_non_corpus_routing": provider_report[
                "historical_non_corpus_routing"
            ],
        },
        "pt_protocol": {
            "license": "MIT",
            "payload_size": pt_payload_size,
            "payload_sha256": pt_report["placement"]["payload_sha256"],
            "source_provider_routes": len(pt_report["source_provider_routes"]),
            "patch_sites": len(pt_report["patch_sites"]),
            "writable_bytes": int(pt_report["placement"]["writable_bytes"]),
            "hardware": pt_report["hardware"],
        },
    }

    overlay_path = output_dir / config.get("overlay_artifact", "apollo_core_overlay.bin")
    component_path = output_dir / "ota_s200_firmware_ota.bin"
    try:
        overlay_report["artifact"] = str(overlay_path.relative_to(root))
        component_report["artifact"] = str(component_path.relative_to(root))
    except ValueError:
        overlay_report["artifact"] = str(overlay_path)
        component_report["artifact"] = str(component_path)
    _publish_canonical_outputs(
        root=root,
        config_path=config_path,
        config=config,
        input_snapshot=input_snapshot,
        overlay_path=overlay_path,
        final_overlay=final_overlay,
        component_path=component_path,
        final_component=final_component,
        report_path=output_dir / "build-report.json",
        report=stage_report,
    )
    return stage_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=COMPONENT_ROOT / "overlay.json")
    parser.add_argument("--output-dir", type=Path, default=COMPONENT_ROOT / "build")
    parser.add_argument("--clang", default=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"))
    parser.add_argument(
        "--toolchain-profile", default=os.environ.get("OPENCFW_TOOLCHAIN_PROFILE")
    )
    parser.add_argument("--record-profile", action="store_true")
    parser.add_argument(
        "--record-canonical",
        action="store_true",
        help="print unpinned dual-stage observations for reviewed admission",
    )
    args = parser.parse_args(argv)
    report = build(
        root=OPENCFW_ROOT,
        config_path=args.config.resolve(),
        output_dir=args.output_dir.resolve(),
        clang=args.clang,
        toolchain_profile=args.toolchain_profile,
        record_profile=args.record_profile,
        record_canonical=args.record_canonical,
    )
    print(
        f"Built {report['name']} canonical source image: "
        f"{report['overlay']['size']} overlay bytes "
        f"[profile {report['toolchain']['profile']}]"
    )
    print(f"  overlay sha256: {report['overlay']['sha256']}")
    print(
        f"  component: {report['component']['size']} bytes, "
        f"sha256 {report['component']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"openCFW canonical component build: error: {error}", file=sys.stderr)
        raise SystemExit(1)
