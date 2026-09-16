#!/usr/bin/env python3
"""Prepare, promote, and package AM-019's 27 LVGL draw-style-getter leaves.

Registers the 27 `lv_obj_get_style_prop` forwards recovered in
`runtime_obj_draw_style_getters.c` (0x0045246E..0x00452616 in G2 firmware
2.2.6.10) as relocated leaves in the Apollo core overlay, redirecting each
stock entry point to the new leaf. Modeled on
`integrate_g2_lvgl_font_manager_overlay.py`.
"""

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
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_obj_draw_style_getters.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE_ROOT = ROOT / "build/source/package"
RECORDER = "apollo-am019-draw-style-getters-record"
BASE_ADDRESS = 0x00437FE0
LEAF_DEFINE_PREFIX = "OPEN_CFW_AM019_"
PATCH_PREFIX = "replace_apollo_draw_style_getter_"
EVIDENCE = "docs/research/g2-lvgl-obj-draw-style-getters-source-admission.md"
ORIGIN = (
    "clean-room forward of official LVGL 9.3-dev src/core/lv_obj_style_gen.h "
    "draw-property getters over the retained lv_obj_get_style_prop core"
)
LICENSE = "MIT"

# (selector, function, stock_start, stock_end) in stock address order.
SELECTORS = (
    ("SHADOW_SPREAD", "open_cfw_runtime_obj_get_style_shadow_spread", 0x0045246E, 0x00452478),
    ("SHADOW_COLOR", "open_cfw_runtime_obj_get_style_shadow_color", 0x00452478, 0x00452498),
    ("SHADOW_OPA", "open_cfw_runtime_obj_get_style_shadow_opa", 0x00452498, 0x004524A4),
    ("IMAGE_OPA", "open_cfw_runtime_obj_get_style_image_opa", 0x004524A4, 0x004524B0),
    ("IMAGE_RECOLOR", "open_cfw_runtime_obj_get_style_image_recolor", 0x004524B0, 0x004524D0),
    ("IMAGE_RECOLOR_OPA", "open_cfw_runtime_obj_get_style_image_recolor_opa", 0x004524D0, 0x004524DC),
    ("LINE_WIDTH", "open_cfw_runtime_obj_get_style_line_width", 0x004524DC, 0x004524E6),
    ("LINE_DASH_WIDTH", "open_cfw_runtime_obj_get_style_line_dash_width", 0x004524E6, 0x004524F0),
    ("LINE_DASH_GAP", "open_cfw_runtime_obj_get_style_line_dash_gap", 0x004524F0, 0x004524FA),
    ("LINE_ROUNDED", "open_cfw_runtime_obj_get_style_line_rounded", 0x004524FA, 0x00452510),
    ("LINE_COLOR", "open_cfw_runtime_obj_get_style_line_color", 0x00452510, 0x00452530),
    ("LINE_OPA", "open_cfw_runtime_obj_get_style_line_opa", 0x00452530, 0x0045253C),
    ("ARC_WIDTH", "open_cfw_runtime_obj_get_style_arc_width", 0x0045253C, 0x00452546),
    ("ARC_ROUNDED", "open_cfw_runtime_obj_get_style_arc_rounded", 0x00452546, 0x0045255C),
    ("ARC_COLOR", "open_cfw_runtime_obj_get_style_arc_color", 0x0045255C, 0x0045257C),
    ("ARC_OPA", "open_cfw_runtime_obj_get_style_arc_opa", 0x0045257C, 0x00452588),
    ("ARC_IMG_SRC", "open_cfw_runtime_obj_get_style_arc_img_src", 0x00452588, 0x00452592),
    ("TEXT_COLOR", "open_cfw_runtime_obj_get_style_text_color", 0x00452592, 0x004525B2),
    ("TEXT_OPA", "open_cfw_runtime_obj_get_style_text_opa", 0x004525B2, 0x004525BE),
    ("TEXT_FONT", "open_cfw_runtime_obj_get_style_text_font", 0x004525BE, 0x004525C8),
    ("TEXT_LETTER_SPACE", "open_cfw_runtime_obj_get_style_text_letter_space", 0x004525C8, 0x004525D2),
    ("TEXT_LINE_SPACE", "open_cfw_runtime_obj_get_style_text_line_space", 0x004525D2, 0x004525DC),
    ("TEXT_DECOR", "open_cfw_runtime_obj_get_style_text_decor", 0x004525DC, 0x004525E8),
    ("TEXT_ALIGN", "open_cfw_runtime_obj_get_style_text_align", 0x004525E8, 0x004525F4),
    ("RADIUS", "open_cfw_runtime_obj_get_style_radius", 0x004525F4, 0x004525FE),
    ("OPA", "open_cfw_runtime_obj_get_style_opa", 0x004525FE, 0x0045260A),
    ("BLEND_MODE", "open_cfw_runtime_obj_get_style_blend_mode", 0x0045260A, 0x00452616),
)

# Still-stock provider this leaf family forwards into. FUN_0044BDEA
# (`lv_obj_get_style_prop`) is AM-011's target (0x0044B8AC..0x0044CAD8);
# it is not routed by this file.
PROVIDERS = {
    "open_cfw_retained_obj_get_style_prop": 0x0044BDEA,
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
    spec = importlib.util.spec_from_file_location("draw_style_getters_overlay", path)
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
                raise SystemExit(f"unexpected defined draw-style relocation: {symbol}")
            elif symbol in PROVIDERS:
                provider = PROVIDERS[symbol]
                if isinstance(provider, str):
                    record["target_function"] = provider
                else:
                    record["target_address"] = provider
                record["symbol_type"] = relocation["symbol_type"]
            else:
                raise SystemExit(f"unmapped draw-style relocation: {symbol}")
            relocations.append(record)
        config["relocated_leaves"].append({
            "allow_discarded_alloc_sections": True,
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


def compute_pins() -> None:
    """Fill reviewed placement pins without the obsolete recorder profile."""
    tool = overlay_module()
    config = json.loads(CONFIG.read_text())
    names = {function for _selector, function, _start, _end in SELECTORS}
    run_base = config["run_base"]
    base_len = (ROOT / config["base"]["path"]).stat().st_size
    payload_offset = (
        (base_len + config["alignment"] - 1)
        // config["alignment"]
        * config["alignment"]
    )
    overlay_base = run_base + payload_offset - config["preamble_bytes"]
    leaves = [
        item for item in config["relocated_leaves"]
        if item.get("function") in names
    ]
    if len(leaves) != len(names):
        raise SystemExit("AM-019 leaf set changed underfoot")
    offsets = {item["function"]: item["expected"]["offset"] for item in leaves}

    with tempfile.TemporaryDirectory() as directory:
        builtin = subprocess.run(
            ["clang", "--no-default-config", "-print-resource-dir"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        for selector, function, _start, _end in SELECTORS:
            object_path = Path(directory) / f"{selector}.o"
            subprocess.run(
                [
                    "clang", "--no-default-config", "-nostdinc",
                    "-isystem", str(Path(builtin) / "include"),
                    "--target=thumbv7em-none-eabi", *FLAGS,
                    f"-D{LEAF_DEFINE_PREFIX}{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(object_path),
                ],
                check=True,
            )
            data, sections = tool.parse_elf32(object_path)
            leaf = next(item for item in leaves if item["function"] == function)
            section = next(
                item for item in sections if item["name"] == f".text.{function}"
            )
            code = bytearray(
                data[section["offset"]:section["offset"] + section["size"]]
            )
            runtime = overlay_base + offsets[function]
            for relocation in leaf["relocations"]:
                rtype = relocation["type"]
                if rtype not in ("R_ARM_THM_CALL", "R_ARM_THM_JUMP24"):
                    raise SystemExit(
                        f"unsupported pin relocation {rtype} in {function}"
                    )
                target = relocation.get("target_function")
                if isinstance(target, str):
                    if target not in offsets:
                        raise SystemExit(
                            f"unresolved pin target in {function}: {target}"
                        )
                    target_address = overlay_base + offsets[target]
                    relocation.pop("target_function", None)
                    relocation["target_address"] = target_address
                else:
                    target_address = relocation.get("target_address")
                    if not isinstance(target_address, int):
                        raise SystemExit(
                            f"unresolved pin target in {function}: {relocation}"
                        )
                code[relocation["offset"]:relocation["offset"] + 4] = (
                    tool.encode_thumb_branch(
                        runtime + relocation["offset"], target_address,
                        link=(rtype == "R_ARM_THM_CALL")
                    )
                )
            leaf["expected"]["sha256"] = sha(bytes(code))

    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves", "patch_sites"):
        for item in config.get(key, []):
            allowed = item.get("profiles")
            if isinstance(allowed, list):
                item["profiles"] = [
                    profile for profile in allowed if profile != RECORDER
                ]
            profiles = item.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(RECORDER, None)
                if not profiles:
                    item.pop("toolchain_profiles", None)
    config.get("toolchain_profiles", {}).pop(RECORDER, None)
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
    regions = list(override["regions"])

    def splice_region(items, replacement):
        """Replace the bytes covered by `replacement` inside the existing tiling."""
        replacement_start = replacement["file_offset"]
        replacement_end = replacement_start + replacement["size"]
        owner_index = next(
            (
                index for index, item in enumerate(items)
                if item["file_offset"] <= replacement_start
                and item["file_offset"] + item["size"] >= replacement_end
            ),
            None,
        )
        if owner_index is None:
            raise SystemExit(
                "manifest has no owner for "
                f"{replacement['name']} at file offset 0x{replacement_start:x}"
            )
        owner = items[owner_index]
        owner_start = owner["file_offset"]
        owner_end = owner_start + owner["size"]
        split = []
        if owner_start < replacement_start:
            before = dict(owner)
            before["size"] = replacement_start - owner_start
            split.append(before)
        split.append(replacement)
        if replacement_end < owner_end:
            after = dict(owner)
            after["name"] = f"{owner['name']}_after_0x{replacement_end:x}"
            if "target_address" in owner:
                after["target_address"] = owner["target_address"] + replacement_end - owner_start
            after["file_offset"] = replacement_end
            after["size"] = owner_end - replacement_end
            split.append(after)
        items[owner_index:owner_index + 1] = split

    stock = sorted(SELECTORS, key=lambda item: item[2])
    first_start, last_end = stock[0][2], stock[-1][3]
    owner_index = next(
        (
            index for index, item in enumerate(regions)
            if item.get("target_address", 0) <= first_start
            and item.get("target_address", 0) + item["size"] >= last_end
        ),
        None,
    )
    owner_end_index = owner_index
    if owner_index is None:
        owner_index = next(
            (
                index for index, item in enumerate(regions)
                if item.get("target_address", 0) <= first_start
                and item.get("target_address", 0) + item["size"] == first_start
            ),
            None,
        )
        owner_end_index = next(
            (
                index for index, item in enumerate(regions)
                if item.get("target_address") == last_end
            ),
            None,
        )
        if owner_index is None or owner_end_index is None:
            raise SystemExit("manifest has no owner span for AM-019 stock getters")
    owner = regions[owner_index]
    owner_tail = regions[owner_end_index]
    owner_start = owner["target_address"]
    owner_end = owner_tail["target_address"] + owner_tail["size"]
    split = []
    if owner_start < first_start:
        before = dict(owner)
        before["size"] = first_start - owner_start
        split.append(before)
    cursor = first_start
    for index, (_selector, function, start, end) in enumerate(stock, 1):
        if cursor < start:
            split.append(region(
                f"apollo_draw_style_getter_retained_gap_{index:02d}",
                "Official draw-style-getter compatibility bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-apollo-draw-style-getter-gap-0x{cursor:08x}.bin",
            ))
        split.append(region(
            f"apollo_draw_style_getter_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-apollo-draw-style-getter-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(region(
            "opaque_after_apollo_draw_style_getters",
            "Official Apollo bytes after the source-replaced draw-style getters",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_end_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("runtime_obj_draw_style_getters.c")
    ]
    leaf_regions = []
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_runtime_obj_get_style_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            leaf_regions.append(region(
                f"apollo_draw_style_getter_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-apollo-draw-style-getter-{slug}-alignment.bin",
            ))
        leaf_regions.append(region(
            f"apollo_draw_style_getter_{slug}_source_text",
            f"Clean-room LVGL draw-style getter leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-apollo-draw-style-getter-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    for item in sorted(leaf_regions, key=lambda entry: entry["target_address"]):
        splice_region(regions, item)
    regions.sort(key=lambda item: item["file_offset"])
    for previous, current in zip(regions, regions[1:]):
        previous_end = previous["file_offset"] + previous["size"]
        if previous_end != current["file_offset"]:
            raise SystemExit(
                "manifest tiling gap/overlap between "
                f"{previous['name']} and {current['name']}: "
                f"0x{previous_end:x} != 0x{current['file_offset']:x}"
            )
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
        "action",
        choices=("prepare", "promote", "sync-manifest", "pin-package", "compute-pins"),
    )
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        promote()
    elif args.action == "compute-pins":
        compute_pins()
    elif args.action == "sync-manifest":
        sync_manifest()
    else:
        pin_package()


if __name__ == "__main__":
    main()
