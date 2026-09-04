#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 audio-algorithm closure."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_service_algo_integration_base", BASE_HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/service_algo.c"
base.RECORDER = "apple-service-algo-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_SERVICE_ALGO_"
base.PATCH_PREFIX = "replace_service_algo_"
base.EVIDENCE = "docs/research/g2-service-algo-recovery.md"
base.ORIGIN = (
    "clean-room G2 stereo preprocessing, rolling energy ratio, bounded lag "
    "correlation, and acoustic source-angle estimator"
)
base.LICENSE = "MIT"
base.FLAGS = [
    *base.FLAGS,
    "-mfloat-abi=hard",
    "-mfpu=fpv5-d16",
]
base.SELECTORS = (
    ("BUFFER_GET", "open_cfw_service_algo_front_buffer_get", 0x005915DC, 0x005915EA),
    ("PREPROCESS", "algo_front_data_preprocess", 0x005915EA, 0x0059173A),
    ("SSR", "SVC_SSRProcess", 0x0059173A, 0x0059187A),
    ("QUIET_NAN", "open_cfw_service_algo_quiet_nan", 0x0059187A, 0x0059188E),
    ("FLOAT_HOOK", "open_cfw_service_algo_float_hook", 0x0059188E, 0x005918B0),
    ("DELAY_TO_ANGLE", "open_cfw_service_algo_delay_to_angle", 0x005918B0, 0x005918CC),
    ("CORRELATION", "open_cfw_service_algo_cross_correlation", 0x005918CC, 0x00591BA4),
    ("SOURCE_ANGLE", "open_cfw_service_algo_source_angle", 0x00591BA4, 0x00591BFC),
    ("PROCESS", "open_cfw_service_algo_process", 0x00591BFC, 0x00591C26),
    ("ENERGY_UPDATE", "open_cfw_service_algo_energy_window_update", 0x00591C26, 0x00591C8C),
)
base.PROVIDERS = {
    "__aeabi_uldivmod": 0x0047CC60,
}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    header = ROOT / "components/apollo_main/core_overlay/service_algo.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public interface for the clean-room G2 audio algorithm",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def enable_linux() -> None:
    config = json.loads(base.CONFIG.read_text())
    functions = {item[1] for item in base.SELECTORS}
    for leaf in config.get("relocated_leaves", []):
        if leaf.get("function") in functions:
            profiles = leaf.setdefault("profiles", ["apple-clang"])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
    for site in config.get("patch_sites", []):
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            profiles = site.setdefault("profiles", ["apple-clang"])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def normalize_linux_in_place() -> None:
    config = json.loads(base.CONFIG.read_text())
    for leaf in config.get("in_place_leaves", []):
        profile = leaf.get("toolchain_profiles", {}).get("linux-clang")
        if not isinstance(profile, dict) or "expected" not in profile:
            continue
        expected = profile["expected"]
        canonical = leaf.get("expected", {})
        if any(expected.get(key) != canonical.get(key) for key in ("size", "sha256")):
            continue
        if profile.get("relocations", leaf.get("relocations", [])) != leaf.get(
            "relocations", []
        ):
            continue
        profile.pop("expected", None)
        profile.pop("relocations", None)
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def promote() -> None:
    base.promote()
    enable_linux()


def sync_manifest() -> None:
    manifest = json.loads(base.MANIFEST.read_text())
    report = json.loads(base.REPORT.read_text())
    run_base = json.loads(base.CONFIG.read_text())["run_base"]
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    provider_path = ROOT / provider["path"]
    provider["size"] = provider_path.stat().st_size
    provider["sha256"] = base.sha(provider_path.read_bytes())
    override["function"] = (
        "Even Apollo510B main firmware with maintained source overlays including "
        "protocol, security, platform, health, storage, sensor, display, and "
        "clean-room audio direction policy"
    )
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("service_algo_")
    ]
    stock = sorted(base.SELECTORS, key=lambda item: item[2])
    first_start, last_end = stock[0][2], stock[-1][3]
    owner_index = next(
        index for index, item in enumerate(regions)
        if item.get("address_status") == "official_blob"
        and item.get("target_address", 0) <= first_start
        and item.get("target_address", 0) + item["size"] >= last_end
    )
    owner = regions[owner_index]
    owner_start = owner["target_address"]
    owner_end = owner_start + owner["size"]
    split = []
    if owner_start < first_start:
        before = dict(owner)
        before["size"] = first_start - owner_start
        split.append(before)
    cursor = first_start
    for index, (_selector, function, start, end) in enumerate(stock, 1):
        if cursor < start:
            split.append(base.region(
                f"service_algo_retained_gap_{index:02d}",
                "Official audio-algorithm literal/alignment bytes",
                "official_blob", 32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-service-algo-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"service_algo_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-service-algo-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "service_algo_opaque_after",
            "Official Apollo bytes after the source-replaced audio algorithm",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split
    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("service_algo.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_service_algo_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"service_algo_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-service-algo-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"service_algo_{slug}_source_text",
            f"Clean-room audio-algorithm leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-service-algo-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(
            f"manifest tiling ends at {final}, provider has {provider['size']} bytes"
        )
    override["regions"] = regions
    manifest["package"]["expected_size"] = None
    manifest["package"]["expected_sha256"] = None
    base.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=(
            "prepare", "promote", "enable-linux", "normalize-linux-in-place",
            "sync-manifest", "pin-package"
        )
    )
    action = parser.parse_args().action
    if action == "prepare":
        prepare()
    elif action == "promote":
        promote()
    elif action == "enable-linux":
        enable_linux()
    elif action == "normalize-linux-in-place":
        normalize_linux_in_place()
    elif action == "sync-manifest":
        sync_manifest()
    else:
        base.pin_package()


if __name__ == "__main__":
    main()
