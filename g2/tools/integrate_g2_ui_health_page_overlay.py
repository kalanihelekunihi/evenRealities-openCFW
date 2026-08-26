#!/usr/bin/env python3
"""Prepare/promote the reviewed G2 health-page relocated overlay closure."""

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
SOURCE = ROOT / "components/apollo_main/core_overlay/ui_health_page.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE_ROOT = ROOT / "build/source/package"
RECORDER = "apple-health-record"
BASE_ADDRESS = 0x00437FE0

SELECTORS = (
    ("INDICATOR", "open_cfw_health_page_update_indicator", 0x004FB1FA, 0x004FB290),
    ("SWITCH", "open_cfw_health_page_switch", 0x004FB290, 0x004FB360),
    ("REFLASH", "open_cfw_health_page_reflash", 0x004FB5E8, 0x004FB700),
    ("WIDGET_EVENT", "open_cfw_health_page_widget_event", 0x004FB360, 0x004FB55A),
    ("ANIM_EXEC", "open_cfw_health_page_anim_exec", 0x004FB55A, 0x004FB568),
    ("ANIMATE", "open_cfw_health_page_animate", 0x004FB568, 0x004FB5E8),
    ("SUMMARY", "open_cfw_health_page_build_summary", 0x004FB760, 0x004FC1B6),
    ("INPUT", "open_cfw_health_page_input_event", 0x004FC1DC, 0x004FC32E),
    ("EXTERNAL", "open_cfw_health_page_external_event", 0x004FC360, 0x004FC580),
    ("DETAIL", "open_cfw_health_page_build_detail", 0x004FC644, 0x004FD786),
    ("INIT", "open_cfw_health_page_init", 0x004FD7B0, 0x004FD836),
    ("DEINIT", "open_cfw_health_page_deinit", 0x004FD840, 0x004FD870),
)

PROVIDERS = {
    "open_cfw_retained_health_page_memset": 0x0043C0E4,
    "open_cfw_retained_health_page_object_create": 0x0043DE82,
    "open_cfw_retained_health_page_set_pos": 0x0043F09A,
    "open_cfw_retained_health_page_set_x": 0x0043F0E0,
    "open_cfw_retained_health_page_set_size": 0x0043F4C0,
    "open_cfw_retained_health_page_set_width": 0x0043F506,
    "open_cfw_retained_health_page_set_height": 0x0043F568,
    "open_cfw_retained_health_page_align": 0x0043F6B8,
    "open_cfw_retained_health_page_add_flags": 0x0043DED4,
    "open_cfw_retained_health_page_clear_flags": 0x0043DFA4,
    "open_cfw_retained_health_page_set_layout": 0x0044E368,
    "open_cfw_retained_health_page_set_scrollbar": 0x0044146A,
    "open_cfw_retained_health_page_color": 0x0044104C,
    "open_cfw_retained_health_page_set_bg_color": 0x0044127E,
    "open_cfw_retained_health_page_set_bg_opacity": 0x0044129E,
    "open_cfw_retained_health_page_set_text_color": 0x0044140E,
    "open_cfw_retained_health_page_set_text_align": 0x0044131C,
    "open_cfw_retained_health_page_set_font": 0x0044143E,
    "open_cfw_retained_health_page_delete_children": 0x0044D878,
    "open_cfw_retained_health_page_image_create": 0x00498668,
    "open_cfw_retained_health_page_image_set_source": 0x00498680,
    "open_cfw_retained_health_page_label_create": 0x00499416,
    "open_cfw_retained_health_page_label_set_text": 0x0049942E,
    "open_cfw_retained_health_page_translation": 0x0045FFFE,
    "open_cfw_retained_health_page_translation_id": 0x00460084,
    "open_cfw_retained_health_page_format": 0x004B4728,
    "open_cfw_retained_health_page_fifo_create": 0x00509C1C,
    "open_cfw_retained_health_page_fifo_delete": 0x00509C96,
    "open_cfw_retained_health_page_fifo_push": 0x00509CA2,
    "open_cfw_retained_health_page_fifo_empty": 0x00509DFA,
    "open_cfw_retained_health_page_fifo_pop": 0x00509E14,
    "open_cfw_retained_health_page_anim_init": 0x004503D6,
    "open_cfw_retained_health_page_anim_set_values": 0x004506CE,
    "open_cfw_retained_health_page_anim_start": 0x00450408,
    "open_cfw_retained_health_page_notify_page": 0x0050029C,
    "open_cfw_retained_health_page_send_action": 0x00464BB2,
    "open_cfw_retained_health_page_post_exit": 0x004E92F4,
    "open_cfw_retained_health_page_post_event": 0x005000CC,
    "open_cfw_retained_health_page_minimize": 0x004E8A90,
    "open_cfw_retained_health_page_common_data": 0x004E8970,
    "open_cfw_retained_health_page_get_x": 0x0044E498,
}

FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def overlay_module():
    path = ROOT / "tools/apollo_overlay.py"
    spec = importlib.util.spec_from_file_location("open_cfw_apollo_overlay", path)
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
                    f"-DOPEN_CFW_HEALTH_PAGE_{selector}_ONLY=1",
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
                        "symbol_record": referenced,
                    })
            rodata = None
            for section in sections:
                if section["name"] == ".rodata.str1.1":
                    raw = data[section["offset"]:section["offset"] + section["size"]]
                    rodata = {
                        "alignment": section["alignment"],
                        "section": section["name"],
                        "sha256": sha(raw),
                        "size": section["size"],
                        "symbols": sorted(
                            [
                                {
                                    "name": item["name"],
                                    "offset": item["value"],
                                    "size": item["size"],
                                }
                                for item in symbols
                                if item["section_index"] == section["index"]
                            ],
                            key=lambda item: (item["offset"], item["name"]),
                        ),
                    }
            result[function] = {
                "selector": selector,
                "size": len(code),
                "alignment": text["alignment"],
                "unrelocated_sha256": sha(code),
                "relocations": sorted(relocations, key=lambda item: item["offset"]),
                "rodata": rodata,
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
        if not item.get("name", "").startswith("replace_ui_health_page_")
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
        "evidence": "docs/research/g2-ui-health-page-dependency-boundary.md",
        "license": "GPL-3.0-only",
        "origin": "clean-room G2 health-page lifecycle and rendering policy over retained platform/LVGL ABIs",
        "path": "components/apollo_main/core_overlay/ui_health_page.c",
        "sha256": sha(source_bytes),
        "size": len(source_bytes),
    }
    run_base = config["run_base"]
    cursor = config["expected"]["overlay_size"]
    offsets = {}
    for _selector, function, _start, _end in SELECTORS:
        item = inventory[function]
        cursor = (cursor + item["alignment"] - 1) & ~(item["alignment"] - 1)
        offsets[function] = cursor
        cursor += item["size"]
        if item["rodata"] is not None:
            alignment = item["rodata"]["alignment"]
            cursor = (cursor + alignment - 1) & ~(alignment - 1)
            cursor += item["rodata"]["size"]

    existing = set(config["functions"])
    for _selector, function, _start, _end in SELECTORS:
        if function not in existing:
            config["functions"].append(function)
    internal = names | {"open_cfw_health_lock_storage", "open_cfw_health_unlock_storage"}
    leaves = []
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
            if relocation["symbol_record"]["section_index"] != 0:
                pass
            elif symbol in internal:
                if relocation["type"] in (
                    "R_ARM_THM_MOVW_PREL_NC", "R_ARM_THM_MOVT_PREL"
                ):
                    record["target_address"] = run_base + offsets[symbol] + 1
                elif symbol in offsets and offsets[symbol] > offsets[function]:
                    record["target_address"] = run_base + offsets[symbol]
                else:
                    record["target_function"] = symbol
                record["symbol_type"] = "STT_NOTYPE"
            elif symbol in PROVIDERS:
                record["target_address"] = PROVIDERS[symbol]
                record["symbol_type"] = "STT_NOTYPE"
            else:
                raise SystemExit(f"unmapped health-page relocation: {symbol}")
            relocations.append(record)
        expected = {
            "size": observed["size"],
            "sha256": "0" * 64,
            "alignment": observed["alignment"],
            "offset": offsets[function],
            "unrelocated_sha256": observed["unrelocated_sha256"],
        }
        leaf = {
            "expected": expected,
            "function": function,
            "profiles": ["apple-clang", RECORDER],
            "relocations": relocations,
            "source": source,
            "strict_relocation_contract": True,
            "toolchain": {
                "flags": [*FLAGS, f"-DOPEN_CFW_HEALTH_PAGE_{selector}_ONLY=1"],
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
        }
        if observed["rodata"] is not None:
            rodata_offset = observed["size"]
            alignment = observed["rodata"]["alignment"]
            rodata_offset = (rodata_offset + alignment - 1) & ~(alignment - 1)
            leaf["closure"] = {
                "rodata": observed["rodata"],
                "text_section": f".text.{function}",
            }
            expected.update({
                "closure_size": rodata_offset + observed["rodata"]["size"],
                "closure_sha256": "0" * 64,
                "rodata_offset": rodata_offset,
            })
        leaves.append(leaf)
    config["relocated_leaves"].extend(leaves)

    image = IMAGE.read_bytes()
    for index, (_selector, function, start, end) in enumerate(SELECTORS, 1):
        raw = image[start - BASE_ADDRESS:end - BASE_ADDRESS]
        config["patch_sites"].append({
            "branch": "b_w",
            "expected_sha256": sha(raw),
            "expected_size": len(raw),
            "name": f"replace_ui_health_page_{index:02d}",
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
                if "closure" in recorded:
                    leaf["closure"] = recorded["closure"]
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


def region(
    *, name: str, function: str, status: str, file_offset: int,
    size: int, target_address: int, output: str,
) -> dict:
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
    provider = manifest["component_overrides"]["apollo_main"]["provider"]
    provider_path = ROOT / provider["path"]
    provider["size"] = provider_path.stat().st_size
    provider["sha256"] = sha(provider_path.read_bytes())
    manifest["component_overrides"]["apollo_main"]["function"] = (
        "Even Apollo510B main firmware with maintained source overlays including "
        "clean-room Sensor Hub, ALS/OPT3007, TDK ICM45608, and complete health-page "
        "lifecycle/rendering routing"
    )
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    regions = [item for item in regions if not item["name"].startswith("ui_health_page_")]

    stock = sorted(SELECTORS, key=lambda item: item[2])
    first_start = stock[0][2]
    last_end = stock[-1][3]
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
                name=f"ui_health_page_retained_gap_{index:02d}",
                function="Official health-page inter-function compatibility bytes",
                status="official_blob",
                file_offset=32 + cursor - run_base,
                size=start - cursor,
                target_address=cursor,
                output=f"apollo510b/main-opaque-ui-health-page-gap-0x{cursor:08x}.bin",
            ))
        split.append(region(
            name=f"ui_health_page_{index:02d}_source_replacement",
            function=f"Generated guarded redirect replacing {function}",
            status="generated_source_entry_replacement",
            file_offset=32 + start - run_base,
            size=end - start,
            target_address=start,
            output=f"apollo510b/main-generated-ui-health-page-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(region(
            name="opaque_after_ui_health_page_before_ring_battery_service",
            function="Official Apollo application bytes after the source-replaced health page",
            status="official_blob",
            file_offset=32 + cursor - run_base,
            size=owner_end - cursor,
            target_address=cursor,
            output=f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("ui_health_page.c")
    ]
    for item in leaves:
        extraction = item["extraction"]
        placement = item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_health_page_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(region(
                name=f"ui_health_page_{slug}_overlay_alignment",
                function=f"Generated runtime alignment before {function}",
                status="generated_alignment",
                file_offset=32 + address - run_base,
                size=placement["padding_before"],
                target_address=address,
                output=f"apollo510b/main-source-ui-health-{slug}-alignment.bin",
            ))
        text_size = extraction["size"]
        regions.append(region(
            name=f"ui_health_page_{slug}_source_text",
            function=f"Clean-room health-page leaf ({function}) compiled from C",
            status="source_compiled",
            file_offset=32 + placement["runtime_address"] - run_base,
            size=text_size,
            target_address=placement["runtime_address"],
            output=f"apollo510b/main-source-ui-health-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
        rodata = extraction.get("rodata")
        if rodata is not None:
            internal_padding = rodata["offset"] - text_size
            if internal_padding:
                regions.append(region(
                    name=f"ui_health_page_{slug}_closure_alignment",
                    function=f"Generated closure alignment before {function} read-only data",
                    status="generated_alignment",
                    file_offset=32 + placement["runtime_address"] + text_size - run_base,
                    size=internal_padding,
                    target_address=placement["runtime_address"] + text_size,
                    output=f"apollo510b/main-source-ui-health-{slug}-rodata-alignment.bin",
                ))
            regions.append(region(
                name=f"ui_health_page_{slug}_source_rodata",
                function=f"Authenticated health-page read-only string closure for {function}",
                status="source_compiled",
                file_offset=32 + rodata["runtime_address"] - run_base,
                size=rodata["size"],
                target_address=rodata["runtime_address"],
                output=f"apollo510b/main-source-ui-health-{slug}-rodata-0x{rodata['runtime_address']:08x}.bin",
            ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(f"manifest tiling ends at {final}, provider has {provider['size']} bytes")
    manifest["component_overrides"]["apollo_main"]["regions"] = regions
    manifest["package"].pop("expected_size", None)
    manifest["package"].pop("expected_sha256", None)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def pin_package() -> None:
    manifest = json.loads(MANIFEST.read_text())
    package = PACKAGE_ROOT / manifest["package"]["output_name"]
    manifest["package"]["expected_size"] = package.stat().st_size
    manifest["package"]["expected_sha256"] = sha(package.read_bytes())
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
