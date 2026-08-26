#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 LVGL font-manager closure."""

import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
SOURCE = ROOT / "components/apollo_main/core_overlay/lvgl_font_manager.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE_ROOT = ROOT / "build/source/package"
RECORDER = "apple-font-manager-record"
BASE_ADDRESS = 0x00437FE0
LEAF_DEFINE_PREFIX = "OPEN_CFW_FONT_MANAGER_"
PATCH_PREFIX = "replace_lvgl_font_manager_"
EVIDENCE = "docs/research/g2-lvgl-font-manager-recovery.md"
ORIGIN = (
    "clean-room G2 LVGL font-chain and XIP-header manager over retained "
    "LVGL/FreeType/media ABIs"
)
LICENSE = "GPL-3.0-only"

SELECTORS = (
    ("CREATE_CHAIN", "open_cfw_font_manager_create_chain", 0x0046CAE0, 0x0046CF56),
    ("GET_FONT", "open_cfw_font_manager_get_font", 0x0046CF56, 0x0046CFA6),
    ("CREATE_SINGLE", "open_cfw_font_manager_create_single", 0x0046CFA6, 0x0046D158),
    ("ADD", "open_cfw_font_manager_add", 0x0046D158, 0x0046D1C6),
    ("CLEANUP_SINGLE", "open_cfw_font_manager_cleanup_single", 0x0046D1C6, 0x0046D238),
    ("CONFIGURE_XIP", "open_cfw_font_manager_configure_xip", 0x0046D29A, 0x0046D444),
    ("INIT", "open_cfw_font_manager_init", 0x0046D464, 0x0046D57C),
    ("XIP_NAME", "open_cfw_font_manager_xip_name", 0x0046D584, 0x0046D588),
)

PROVIDERS = {
    "open_cfw_retained_font_manager_alloc": 0x00474CD2,
    "open_cfw_retained_font_manager_free": 0x00474D16,
    "open_cfw_retained_font_manager_freetype_create": 0x004B1C9C,
    "open_cfw_retained_font_manager_freetype_delete": 0x004B1EF6,
    "open_cfw_retained_font_manager_mspi_lock": 0x0046F65E,
    "open_cfw_retained_font_manager_mspi_unlock": 0x0046F674,
    "open_cfw_retained_font_manager_memset": 0x0043C0E4,
    "open_cfw_retained_font_manager_memcpy": 0x00439BE4,
}

FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]
INCLUDE_DIRS = []


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def overlay_module():
    path = ROOT / "tools/apollo_overlay.py"
    spec = importlib.util.spec_from_file_location("font_manager_overlay", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def compile_inventory():
    tool = overlay_module()
    type_names = {
        tool.R_ARM_REL32: "R_ARM_REL32",
        tool.R_ARM_THM_CALL: "R_ARM_THM_CALL",
        tool.R_ARM_THM_JUMP24: "R_ARM_THM_JUMP24",
        tool.R_ARM_THM_MOVW_ABS_NC: "R_ARM_THM_MOVW_ABS_NC",
        tool.R_ARM_THM_MOVT_ABS: "R_ARM_THM_MOVT_ABS",
        tool.R_ARM_THM_MOVW_PREL_NC: "R_ARM_THM_MOVW_PREL_NC",
        tool.R_ARM_THM_MOVT_PREL: "R_ARM_THM_MOVT_PREL",
    }
    result = {}
    with tempfile.TemporaryDirectory() as directory:
        for selector, function, _start, _end in SELECTORS:
            object_path = Path(directory) / f"{selector}.o"
            subprocess.run(
                [
                    "clang", "--target=thumbv7em-none-eabi", *FLAGS,
                    *(value for directory in INCLUDE_DIRS for value in (
                        "-I", str(ROOT / directory)
                    )),
                    f"-D{LEAF_DEFINE_PREFIX}{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(object_path),
                ],
                check=True,
            )
            data, sections = tool.parse_elf32(object_path)
            symbols = tool.parse_elf32_symbols(data, sections)
            symbol = next(
                item for item in symbols
                if item["name"] == function and item["type"] == tool.STT_FUNC
            )
            text = sections[symbol["section_index"]]
            code = data[text["offset"]:text["offset"] + text["size"]]
            relocations = []
            for section in sections:
                if not (
                    section["type"] == tool.SHT_REL
                    and section["info"] == text["index"]
                    and section["size"]
                ):
                    continue
                for index in range(section["size"] // section["entry_size"]):
                    offset, info = struct.unpack_from(
                        "<II", data,
                        section["offset"] + index * section["entry_size"],
                    )
                    referenced = symbols[info >> 8]
                    relocations.append({
                        "offset": offset,
                        "type": type_names[info & 0xFF],
                        "symbol": referenced["name"],
                        "symbol_type": (
                            "STT_FUNC"
                            if referenced["type"] == tool.STT_FUNC
                            else (
                                "STT_OBJECT"
                                if referenced["type"] == tool.STT_OBJECT
                                else "STT_NOTYPE"
                            )
                        ),
                        "symbol_record": referenced,
                    })
            result[function] = {
                "size": len(code),
                "alignment": text["alignment"],
                "unrelocated_sha256": sha(code),
                "relocations": sorted(relocations, key=lambda item: item["offset"]),
            }
    return result


def prepare() -> None:
    config = json.loads(CONFIG.read_text())
    names = {function for _selector, function, _start, _end in SELECTORS}
    config["functions"] = [item for item in config["functions"] if item not in names]
    config["relocated_leaves"] = [
        item for item in config["relocated_leaves"]
        if item.get("function") not in names
    ]
    config["patch_sites"] = [
        item for item in config["patch_sites"]
        if not item.get("name", "").startswith(PATCH_PREFIX)
    ]
    config.get("toolchain_profiles", {}).pop(RECORDER, None)
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves", "patch_sites"):
        for item in config.get(key, []):
            allowed = item.get("profiles")
            if isinstance(allowed, list):
                item["profiles"] = [profile for profile in allowed if profile != RECORDER]
            profiles = item.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(RECORDER, None)
                if not profiles:
                    item.pop("toolchain_profiles", None)

    inventory = compile_inventory()
    source_bytes = SOURCE.read_bytes()
    source = {
        "evidence": EVIDENCE,
        "license": LICENSE,
        "origin": ORIGIN,
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "sha256": sha(source_bytes),
        "size": len(source_bytes),
    }
    cursor = config["expected"]["overlay_size"]
    offsets = {}
    for _selector, function, _start, _end in SELECTORS:
        item = inventory[function]
        cursor = (cursor + item["alignment"] - 1) & ~(item["alignment"] - 1)
        offsets[function] = cursor
        cursor += item["size"]

    config["functions"].extend(
        function for _selector, function, _start, _end in SELECTORS
        if function not in config["functions"]
    )
    for selector, function, _start, _end in SELECTORS:
        observed = inventory[function]
        relocations = []
        for relocation in observed["relocations"]:
            symbol = relocation["symbol"]
            record = {
                "offset": relocation["offset"],
                "type": relocation["type"],
                "symbol": symbol,
            }
            if symbol in names:
                if symbol in offsets and offsets[symbol] > offsets[function]:
                    record["target_address"] = config["run_base"] + offsets[symbol]
                else:
                    record["target_function"] = symbol
                record["symbol_type"] = (
                    "STT_FUNC"
                    if relocation["type"] in (
                        "R_ARM_THM_MOVW_PREL_NC",
                        "R_ARM_THM_MOVT_PREL",
                    )
                    else relocation["symbol_type"]
                )
            elif relocation["symbol_record"]["section_index"] != 0:
                raise SystemExit(f"unexpected defined font-manager relocation: {symbol}")
            elif symbol in PROVIDERS:
                provider = PROVIDERS[symbol]
                if isinstance(provider, str):
                    record["target_function"] = provider
                else:
                    record["target_address"] = provider
                record["symbol_type"] = relocation["symbol_type"]
            else:
                raise SystemExit(f"unmapped font-manager relocation: {symbol}")
            relocations.append(record)
        config["relocated_leaves"].append({
            "expected": {
                "size": observed["size"],
                "sha256": "0" * 64,
                "alignment": observed["alignment"],
                "offset": offsets[function],
                "unrelocated_sha256": observed["unrelocated_sha256"],
            },
            "function": function,
            "profiles": ["apple-clang", RECORDER],
            "relocations": relocations,
            "source": source,
            "strict_relocation_contract": True,
            "toolchain": {
                "flags": [*FLAGS, f"-D{LEAF_DEFINE_PREFIX}{selector}_ONLY=1"],
                **({"include_dirs": INCLUDE_DIRS} if INCLUDE_DIRS else {}),
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
        })
    image = IMAGE.read_bytes()
    for index, (_selector, function, start, end) in enumerate(SELECTORS, 1):
        raw = image[start - BASE_ADDRESS:end - BASE_ADDRESS]
        config["patch_sites"].append({
            "branch": "b_w",
            "expected_sha256": sha(raw),
            "expected_size": len(raw),
            "name": f"{PATCH_PREFIX}{index:02d}",
            "profiles": ["apple-clang", RECORDER],
            "runtime_address": start,
            "target_function": function,
        })
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves", "patch_sites"):
        for item in config.get(key, []):
            profiles = item.get("profiles")
            if isinstance(profiles, list) and "apple-clang" in profiles and RECORDER not in profiles:
                profiles.append(RECORDER)
    config.setdefault("toolchain_profiles", {})[RECORDER] = {}
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def promote() -> None:
    config = json.loads(CONFIG.read_text())
    profile = config.get("toolchain_profiles", {}).get(RECORDER)
    if not isinstance(profile, dict) or not isinstance(profile.get("expected"), dict):
        raise SystemExit("recorder profile has not been built")
    config["expected"] = profile["expected"]
    names = {function for _selector, function, _start, _end in SELECTORS}
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in config.get(key, []):
            recorded = leaf.get("toolchain_profiles", {}).get(RECORDER)
            if leaf.get("function") in names:
                if not isinstance(recorded, dict) or "expected" not in recorded:
                    raise SystemExit(f"missing recorded pins for {leaf.get('function')}")
                leaf["expected"] = recorded["expected"]
                if "relocations" in recorded:
                    leaf["relocations"] = recorded["relocations"]
            profiles = leaf.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(RECORDER, None)
                if not profiles:
                    leaf.pop("toolchain_profiles", None)
            allowed = leaf.get("profiles")
            if isinstance(allowed, list):
                leaf["profiles"] = [item for item in allowed if item != RECORDER]
    for site in config.get("patch_sites", []):
        allowed = site.get("profiles")
        if isinstance(allowed, list):
            site["profiles"] = [item for item in allowed if item != RECORDER]
    config["toolchain_profiles"].pop(RECORDER, None)
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def region(name, function, status, file_offset, size, target_address, output):
    return {
        "address_status": status,
        "file_offset": file_offset,
        "function": function,
        "name": name,
        "output": output,
        "size": size,
        "target": "apollo510b_internal_mram",
        "target_address": target_address,
    }


def sync_manifest() -> None:
    manifest = json.loads(MANIFEST.read_text())
    report = json.loads(REPORT.read_text())
    run_base = json.loads(CONFIG.read_text())["run_base"]
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    provider_path = ROOT / provider["path"]
    provider["size"] = provider_path.stat().st_size
    provider["sha256"] = sha(provider_path.read_bytes())
    override["function"] = (
        "Even Apollo510B main firmware with maintained source overlays including "
        "clean-room display, sensor, health-page, and LVGL font-manager policy"
    )
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("lvgl_font_manager_")
    ]
    stock = sorted(SELECTORS, key=lambda item: item[2])
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
            split.append(region(
                f"lvgl_font_manager_retained_gap_{index:02d}",
                "Official font-manager compatibility bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-lvgl-font-manager-gap-0x{cursor:08x}.bin",
            ))
        split.append(region(
            f"lvgl_font_manager_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-lvgl-font-manager-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(region(
            "opaque_after_lvgl_font_manager",
            "Official Apollo bytes after the source-replaced LVGL font manager",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("lvgl_font_manager.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_font_manager_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(region(
                f"lvgl_font_manager_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-lvgl-font-manager-{slug}-alignment.bin",
            ))
        regions.append(region(
            f"lvgl_font_manager_{slug}_source_text",
            f"Clean-room LVGL font-manager leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-lvgl-font-manager-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(f"manifest tiling ends at {final}, provider has {provider['size']} bytes")
    override["regions"] = regions
    manifest["package"].pop("expected_size", None)
    manifest["package"].pop("expected_sha256", None)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def pin_package() -> None:
    manifest = json.loads(MANIFEST.read_text())
    package = PACKAGE_ROOT / manifest["package"]["output_name"]
    manifest["package"]["expected_size"] = package.stat().st_size
    manifest["package"]["expected_sha256"] = sha(package.read_bytes())
    manifest["package"].get("profiles", {}).pop(RECORDER, None)
    manifest["component_overrides"]["apollo_main"]["provider"].get(
        "profiles", {}
    ).pop(RECORDER, None)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "promote", "sync-manifest", "pin-package")
    )
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        promote()
    elif args.action == "sync-manifest":
        sync_manifest()
    else:
        pin_package()


if __name__ == "__main__":
    main()
