#!/usr/bin/env python3
"""Prepare, promote, and package AM-040's 64 Apollo leaves.

Registers the 28 LVGL flex/grid helpers in
`core_overlay/lvgl_grid_engine.c`, the 25 style getters in
`core_overlay/lvgl_layout_style_getters.c`, and the 11 trailing
string/state helpers in `core_overlay/runtime_string_helpers.c` and
`core_overlay/runtime_peripheral_state_helpers.c`
(0x0048C7B4..0x0048D866 in G2 firmware 2.2.6.10, modulo the already
generated bounded-string-length entry, two 2-byte pads, the grid
literal pool, and the state holder words) as relocated leaves in the
Apollo core overlay, redirecting each stock entry point to the new
leaf. Modeled on `integrate_g2_apollo_draw_style_getters_overlay.py`.
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
GRID_ENGINE = ROOT / "components/apollo_main/core_overlay/lvgl_grid_engine.c"
STYLE_GETTERS = ROOT / "components/apollo_main/core_overlay/lvgl_layout_style_getters.c"
STRING_HELPERS = ROOT / "components/apollo_main/core_overlay/runtime_string_helpers.c"
STATE_HELPERS = ROOT / "components/apollo_main/core_overlay/runtime_peripheral_state_helpers.c"
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE_ROOT = ROOT / "build/source/package"
RECORDER = "apollo-am040-grid-state-record"
BASE_ADDRESS = 0x00437FE0
PATCH_PREFIX = "replace_apollo_am040_"
REGION_PREFIX = "apollo_am040_"
LICENSE = "MIT"

GRID_EVIDENCE = "docs/research/lvgl-grid-engine-closure.md"
GRID_ORIGIN = (
    "clean-room LVGL 9.3-dev flex/grid layout helpers and style "
    "getters over the retained lv_obj_get_style_prop core"
)
STATE_EVIDENCE = "docs/research/g2-display-state-string-helpers-closure.md"
STRING_ORIGIN = (
    "clean-room libc-shaped strcpy/strtoul over retained locale "
    "callees; upstream family unclaimed"
)
STATE_ORIGIN = (
    "clean-room first-party peripheral-state cluster over retained "
    "sample/irq/channel callees; peripheral identity open"
)

# (selector, function, source, stock_start, stock_end, evidence, origin)
SELECTORS = (
    ("GETTER_WIDTH", "open_cfw_lvgl_get_style_width", STYLE_GETTERS, 0x0048C81A, 0x0048C824, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_HEIGHT", "open_cfw_lvgl_get_style_height", STYLE_GETTERS, 0x0048C824, 0x0048C82E, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_TRANSLATE_X", "open_cfw_lvgl_get_style_translate_x", STYLE_GETTERS, 0x0048C82E, 0x0048C838, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_TRANSLATE_Y", "open_cfw_lvgl_get_style_translate_y", STYLE_GETTERS, 0x0048C838, 0x0048C842, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_PAD_TOP", "open_cfw_lvgl_get_style_pad_top", STYLE_GETTERS, 0x0048C842, 0x0048C84C, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_PAD_LEFT", "open_cfw_lvgl_get_style_pad_left", STYLE_GETTERS, 0x0048C84C, 0x0048C856, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_PAD_ROW", "open_cfw_lvgl_get_style_pad_row", STYLE_GETTERS, 0x0048C856, 0x0048C860, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_PAD_COLUMN", "open_cfw_lvgl_get_style_pad_column", STYLE_GETTERS, 0x0048C860, 0x0048C86A, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_MARGIN_TOP", "open_cfw_lvgl_get_style_margin_top", STYLE_GETTERS, 0x0048C86A, 0x0048C874, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_MARGIN_BOTTOM", "open_cfw_lvgl_get_style_margin_bottom", STYLE_GETTERS, 0x0048C874, 0x0048C87E, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_MARGIN_LEFT", "open_cfw_lvgl_get_style_margin_left", STYLE_GETTERS, 0x0048C87E, 0x0048C888, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_MARGIN_RIGHT", "open_cfw_lvgl_get_style_margin_right", STYLE_GETTERS, 0x0048C888, 0x0048C892, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_BORDER_WIDTH", "open_cfw_lvgl_get_style_border_width", STYLE_GETTERS, 0x0048C892, 0x0048C89C, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_BORDER_SIDE", "open_cfw_lvgl_get_style_border_side", STYLE_GETTERS, 0x0048C89C, 0x0048C8A8, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_BASE_DIR", "open_cfw_lvgl_get_style_base_dir", STYLE_GETTERS, 0x0048C8A8, 0x0048C8B4, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_GRID_COLUMN_DSC", "open_cfw_lvgl_get_style_grid_column_dsc_array", STYLE_GETTERS, 0x0048C8B4, 0x0048C8BE, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_GRID_COLUMN_ALIGN", "open_cfw_lvgl_get_style_grid_column_align", STYLE_GETTERS, 0x0048C8BE, 0x0048C8CA, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_GRID_ROW_DSC", "open_cfw_lvgl_get_style_grid_row_dsc_array", STYLE_GETTERS, 0x0048C8CA, 0x0048C8D4, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_GRID_ROW_ALIGN", "open_cfw_lvgl_get_style_grid_row_align", STYLE_GETTERS, 0x0048C8D4, 0x0048C8E0, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_COL_POS", "open_cfw_lvgl_get_style_grid_cell_column_pos", STYLE_GETTERS, 0x0048C8E0, 0x0048C8EA, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_X_ALIGN", "open_cfw_lvgl_get_style_grid_cell_x_align", STYLE_GETTERS, 0x0048C8EA, 0x0048C8F6, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_COL_SPAN", "open_cfw_lvgl_get_style_grid_cell_column_span", STYLE_GETTERS, 0x0048C8F6, 0x0048C900, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_ROW_POS", "open_cfw_lvgl_get_style_grid_cell_row_pos", STYLE_GETTERS, 0x0048C900, 0x0048C90A, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_Y_ALIGN", "open_cfw_lvgl_get_style_grid_cell_y_align", STYLE_GETTERS, 0x0048C90A, 0x0048C916, GRID_EVIDENCE, GRID_ORIGIN),
    ("GETTER_CELL_ROW_SPAN", "open_cfw_lvgl_get_style_grid_cell_row_span", STYLE_GETTERS, 0x0048C916, 0x0048C920, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_WIDTH_WITH_MARGIN", "open_cfw_lvgl_obj_get_width_with_margin", GRID_ENGINE, 0x0048C7B4, 0x0048C7D8, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_HEIGHT_WITH_MARGIN", "open_cfw_lvgl_obj_get_height_with_margin", GRID_ENGINE, 0x0048C7D8, 0x0048C7FC, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_AREA_COPY", "open_cfw_lvgl_area_copy", GRID_ENGINE, 0x0048C7FC, 0x0048C80E, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_MEMZERO", "open_cfw_lvgl_memzero", GRID_ENGINE, 0x0048C80E, 0x0048C81A, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_SPACE_LEFT", "open_cfw_lvgl_get_style_space_left", GRID_ENGINE, 0x0048C920, 0x0048C94E, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_SPACE_TOP", "open_cfw_lvgl_get_style_space_top", GRID_ENGINE, 0x0048C94E, 0x0048C97C, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_COL_DSC", "open_cfw_lvgl_grid_get_col_dsc", GRID_ENGINE, 0x0048C97C, 0x0048C986, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_ROW_DSC", "open_cfw_lvgl_grid_get_row_dsc", GRID_ENGINE, 0x0048C986, 0x0048C990, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_COL_POS", "open_cfw_lvgl_grid_get_col_pos", GRID_ENGINE, 0x0048C990, 0x0048C99A, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_ROW_POS", "open_cfw_lvgl_grid_get_row_pos", GRID_ENGINE, 0x0048C99A, 0x0048C9A4, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_COL_SPAN", "open_cfw_lvgl_grid_get_col_span", GRID_ENGINE, 0x0048C9A4, 0x0048C9AE, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_ROW_SPAN", "open_cfw_lvgl_grid_get_row_span", GRID_ENGINE, 0x0048C9AE, 0x0048C9B8, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_CELL_COL_ALIGN", "open_cfw_lvgl_grid_get_cell_col_align", GRID_ENGINE, 0x0048C9B8, 0x0048C9C2, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_CELL_ROW_ALIGN", "open_cfw_lvgl_grid_get_cell_row_align", GRID_ENGINE, 0x0048C9C2, 0x0048C9CC, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_GRID_COL_ALIGN", "open_cfw_lvgl_grid_get_grid_col_align", GRID_ENGINE, 0x0048C9CC, 0x0048C9D6, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_GET_GRID_ROW_ALIGN", "open_cfw_lvgl_grid_get_grid_row_align", GRID_ENGINE, 0x0048C9D6, 0x0048C9E0, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_MARGIN_HOR", "open_cfw_lvgl_grid_get_margin_hor", GRID_ENGINE, 0x0048C9E0, 0x0048C9FC, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_MARGIN_VER", "open_cfw_lvgl_grid_get_margin_ver", GRID_ENGINE, 0x0048C9FC, 0x0048CA18, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_DIV_ROUND", "open_cfw_lvgl_grid_div_round_closest", GRID_ENGINE, 0x0048CA18, 0x0048CA26, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_INIT", "open_cfw_lvgl_grid_init", GRID_ENGINE, 0x0048CA26, 0x0048CA3A, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_CALC_FREE", "open_cfw_lvgl_grid_calc_free", GRID_ENGINE, 0x0048CBDA, 0x0048CBF8, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_COUNT_TRACKS", "open_cfw_lvgl_grid_count_tracks", GRID_ENGINE, 0x0048D4D0, 0x0048D4E6, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_ALIGN", "open_cfw_lvgl_grid_align", GRID_ENGINE, 0x0048D3C8, 0x0048D4D0, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_CALC_COLS", "open_cfw_lvgl_grid_calc_cols", GRID_ENGINE, 0x0048CBF8, 0x0048CDEC, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_CALC_ROWS", "open_cfw_lvgl_grid_calc_rows", GRID_ENGINE, 0x0048CDEC, 0x0048CFE0, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_CALC", "open_cfw_lvgl_grid_calc", GRID_ENGINE, 0x0048CAD8, 0x0048CBDA, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_ITEM_REPOS", "open_cfw_lvgl_grid_item_repos", GRID_ENGINE, 0x0048CFE0, 0x0048D3A0, GRID_EVIDENCE, GRID_ORIGIN),
    ("GRID_UPDATE", "open_cfw_lvgl_grid_update", GRID_ENGINE, 0x0048CA3C, 0x0048CAD8, GRID_EVIDENCE, GRID_ORIGIN),
    ("STR_STRCPY", "open_cfw_libc_strcpy", STRING_HELPERS, 0x0048D540, 0x0048D558, STATE_EVIDENCE, STRING_ORIGIN),
    ("STATE_INIT_PARAMS", "open_cfw_state_init_params", STATE_HELPERS, 0x0048D558, 0x0048D570, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_NIBBLE_TO_MODE", "open_cfw_state_nibble_to_mode", STATE_HELPERS, 0x0048D570, 0x0048D588, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_MODE_SWITCH", "open_cfw_state_mode_switch", STATE_HELPERS, 0x0048D588, 0x0048D620, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_FLAG_GET", "open_cfw_state_flag_get", STATE_HELPERS, 0x0048D620, 0x0048D654, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_SAMPLE_VOTE", "open_cfw_state_sample_vote", STATE_HELPERS, 0x0048D654, 0x0048D670, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_SAMPLE_RETRY", "open_cfw_state_sample_retry", STATE_HELPERS, 0x0048D670, 0x0048D6DC, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_FLAG_OR", "open_cfw_state_flag_or", STATE_HELPERS, 0x0048D6DC, 0x0048D6E6, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_LATCH_STORE", "open_cfw_state_latch_store", STATE_HELPERS, 0x0048D6E6, 0x0048D6F0, STATE_EVIDENCE, STATE_ORIGIN),
    ("STATE_VALUE_GET", "open_cfw_state_value_get", STATE_HELPERS, 0x0048D6F0, 0x0048D704, STATE_EVIDENCE, STATE_ORIGIN),
    ("STR_STRTOUL", "open_cfw_libc_strtoul", STRING_HELPERS, 0x0048D724, 0x0048D866, STATE_EVIDENCE, STRING_ORIGIN),
)
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
    spec = importlib.util.spec_from_file_location("am040_overlay", path)
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
    by_source: dict[str, list[tuple]] = {}
    for row in SELECTORS:
        by_source.setdefault(str(row[2]), []).append(row)
    with tempfile.TemporaryDirectory() as directory:
        for source, rows in by_source.items():
            object_path = Path(directory) / (Path(source).stem + ".o")
            subprocess.run(
                [
                    "clang", "--target=thumbv7em-none-eabi", *FLAGS,
                    "-c", source, "-o", str(object_path),
                ],
                check=True,
            )
            data, sections = tool.parse_elf32(object_path)
            symbols = tool.parse_elf32_symbols(data, sections)
            texts = {
                item["name"]: (item, sections[item["section_index"]])
                for item in symbols
                if item["type"] == tool.STT_FUNC
            }
            for _selector, function, _src, _start, _end, _ev, _origin in rows:
                symbol, text = texts[function]
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
                    "relocations": sorted(
                        relocations, key=lambda item: item["offset"]),
                }
    return result


def prepare() -> None:
    config = json.loads(CONFIG.read_text())
    names = {row[1] for row in SELECTORS}
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
    sources = {}
    for _selector, _function, source, _s, _e, evidence, origin in SELECTORS:
        if source not in sources:
            raw = Path(source).read_bytes()
            sources[source] = {
                "evidence": evidence,
                "license": LICENSE,
                "origin": origin,
                "path": Path(source).relative_to(ROOT).as_posix(),
                "sha256": sha(raw),
                "size": len(raw),
            }
    cursor = config["expected"]["overlay_size"]
    offsets = {}
    for _selector, function, _src, _s, _e, _ev, _origin in SELECTORS:
        item = inventory[function]
        cursor = (cursor + item["alignment"] - 1) & ~(item["alignment"] - 1)
        offsets[function] = cursor
        cursor += item["size"]

    config["functions"].extend(
        function for _s, function, _src, _st, _en, _ev, _or in SELECTORS
        if function not in config["functions"]
    )
    for _selector, function, _src, _s, _e, _ev, _origin in SELECTORS:
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
                raise SystemExit(f"unexpected defined AM-040 relocation: {symbol}")
            else:
                raise SystemExit(f"unmapped AM-040 relocation: {symbol}")
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
            "source": sources[_src],
            "strict_relocation_contract": True,
            "toolchain": {
                "flags": [*FLAGS],
                **({"include_dirs": INCLUDE_DIRS} if INCLUDE_DIRS else {}),
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
        })
    image = IMAGE.read_bytes()
    for index, (_selector, function, _src, start, end, _ev, _or) in enumerate(SELECTORS, 1):
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
    names = {row[1] for row in SELECTORS}
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
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith(REGION_PREFIX)
    ]
    stock = sorted(SELECTORS, key=lambda item: item[3])
    # Partition selectors by containing official_blob owner region.
    owners = [
        (index, item) for index, item in enumerate(regions)
        if item.get("address_status") == "official_blob"
    ]
    remaining = list(stock)
    splices: dict[int, list] = {}
    for index, owner in owners:
        owner_start = owner["target_address"]
        owner_end = owner_start + owner["size"]
        inside = [row for row in remaining
                  if row[3] >= owner_start and row[4] <= owner_end]
        if not inside:
            continue
        for row in inside:
            remaining.remove(row)
        first_start = inside[0][3]
        split = []
        if owner_start < first_start:
            before = dict(owner)
            before["size"] = first_start - owner_start
            split.append(before)
        cursor = first_start
        for number, (_selector, function, _src, start, end, _ev, _or) in enumerate(inside, 1):
            if cursor < start:
                split.append(region(
                    f"{REGION_PREFIX}retained_gap_0x{cursor:08x}",
                    "Official Apollo bytes kept between source leaves",
                    "official_blob",
                    32 + cursor - run_base, start - cursor, cursor,
                    f"apollo510b/main-opaque-0x{cursor:08x}.bin",
                ))
            split.append(region(
                f"{REGION_PREFIX}source_replacement_0x{start:08x}",
                f"Generated guarded redirect replacing {function}",
                "generated_source_entry_replacement", 32 + start - run_base,
                end - start, start,
                f"apollo510b/main-generated-am040-0x{start:08x}.bin",
            ))
            cursor = end
        if cursor < owner_end:
            split.append(region(
                f"{REGION_PREFIX}opaque_after_0x{cursor:08x}",
                "Official Apollo bytes after the source-replaced AM-040 leaves",
                "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
                f"apollo510b/main-opaque-0x{cursor:08x}.bin",
            ))
        splices[index] = split
    if remaining:
        raise SystemExit(
            "selectors outside official_blob owners: "
            + ", ".join(hex(row[3]) for row in remaining)
        )
    for index in sorted(splices, reverse=True):
        regions[index:index + 1] = splices[index]

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith(
            ("lvgl_grid_engine.c", "lvgl_layout_style_getters.c",
             "runtime_string_helpers.c", "runtime_peripheral_state_helpers.c"))
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(region(
                f"{REGION_PREFIX}{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-am040-{slug}-alignment.bin",
            ))
        regions.append(region(
            f"{REGION_PREFIX}{slug}_source_text",
            f"Clean-room AM-040 leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-am040-{slug}-0x{placement['runtime_address']:08x}.bin",
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


def compute_pins() -> None:
    """Fill reviewed placement pins without the recorder profile.

    Replicates the builder's relocated-leaf placement and
    THM_CALL/JUMP24 relocation encoding exactly (same hermetic
    compile, same align-up placement, same encode_thumb_branch), so
    the canonical build verifies them as reviewed pins. Any
    divergence fails closed in the build instead.
    """
    tool = overlay_module()
    config = json.loads(CONFIG.read_text())
    names = {row[1] for row in SELECTORS}
    run_base = config["run_base"]
    base_len = (ROOT / config["base"]["path"]).stat().st_size
    payload_offset = (
        (base_len + config["alignment"] - 1) // config["alignment"]
        * config["alignment"])
    overlay_base = run_base + payload_offset - config["preamble_bytes"]
    leaves = [
        item for item in config["relocated_leaves"]
        if item.get("function") in names
    ]
    if len(leaves) != len(names):
        raise SystemExit("AM-040 leaf set changed underfoot")
    offsets = {item["function"]: item["expected"]["offset"] for item in leaves}
    by_source: dict[str, list[dict]] = {}
    for leaf in leaves:
        by_source.setdefault(leaf["source"]["path"], []).append(leaf)
    with tempfile.TemporaryDirectory() as directory:
        for source, group in by_source.items():
            object_path = Path(directory) / (Path(source).stem + ".o")
            builtin = subprocess.run(
                ["clang", "--no-default-config", "-print-resource-dir"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(
                ["clang", "--no-default-config", "-nostdinc",
                 "-isystem", str(Path(builtin) / "include"),
                 "--target=thumbv7em-none-eabi", *FLAGS,
                 "-c", str(ROOT / source), "-o", str(object_path)],
                check=True,
            )
            data, sections = tool.parse_elf32(object_path)
            symbols = tool.parse_elf32_symbols(data, sections)
            for leaf in group:
                function = leaf["function"]
                section = next(
                    item for item in sections
                    if item["name"] == f".text.{function}"
                )
                code = bytearray(
                    data[section["offset"]:section["offset"] + section["size"]])
                runtime = overlay_base + offsets[function]
                for relocation in leaf["relocations"]:
                    rtype = relocation["type"]
                    if rtype not in ("R_ARM_THM_CALL", "R_ARM_THM_JUMP24"):
                        raise SystemExit(
                            f"unsupported pin relocation {rtype} in {function}")
                    target = relocation.get("target_function")
                    if not isinstance(target, str) or target not in offsets:
                        raise SystemExit(
                            f"unresolved pin target in {function}: {target}")
                    target_address = overlay_base + offsets[target]
                    relocation.pop("target_function", None)
                    relocation["target_address"] = target_address
                    code[relocation["offset"]:relocation["offset"] + 4] = (
                        tool.encode_thumb_branch(
                            runtime + relocation["offset"], target_address,
                            link=(rtype == "R_ARM_THM_CALL")))
                leaf["expected"]["sha256"] = sha(bytes(code))
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=("prepare", "promote", "sync-manifest", "pin-package",
                 "compute-pins"),
    )
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "compute-pins":
        compute_pins()
    elif args.action == "promote":
        promote()
    elif args.action == "sync-manifest":
        sync_manifest()
    else:
        pin_package()


if __name__ == "__main__":
    main()
