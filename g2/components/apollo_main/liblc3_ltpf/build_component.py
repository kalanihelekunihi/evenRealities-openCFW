#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build and inject the bounded Apache-2.0 liblc3 LTPF overlay.

The repository-wide mini-linker intentionally does not admit absolute
function-pointer tables.  liblc3's authenticated seven-rate dispatch table
needs exactly that relocation class, so this component keeps a smaller local
linker: 16 MOVW/MOVT data references and seven ABS32 Thumb function pointers
are the only accepted relocation closure.  Any new section, symbol, or
relocation fails closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
G2_ROOT = COMPONENT_ROOT.parents[2]
sys.path.insert(0, str(G2_ROOT / "tools"))

from apollo_overlay import (  # noqa: E402
    BuildError,
    EM_ARM,
    SHF_ALLOC,
    SHF_EXECINSTR,
    SHF_WRITE,
    SHT_ARM_EXIDX,
    SHT_PROGBITS,
    SHT_REL,
    STB_GLOBAL,
    STB_LOCAL,
    STT_FUNC,
    STT_SECTION,
    align_up,
    atomic_write,
    compiler_version,
    decode_thumb_bl,
    encode_thumb_branch,
    parse_elf32,
    parse_elf32_symbols,
    sha256,
    thumb_movwt_immediate,
    thumb_movwt_with_immediate,
    validate_compiler_version,
)


R_ARM_ABS32 = 2
R_ARM_PREL31 = 42
R_ARM_THM_MOVW_ABS_NC = 47
R_ARM_THM_MOVT_ABS = 48
EXPECTED_GLOBAL_FUNCTIONS = {
    "lc3_ltpf_analyse",
    "open_cfw_liblc3_memmove",
    "open_cfw_liblc3_sqrtf_nonnegative",
}
EXPECTED_TEXT_RELOCATIONS = (
    (0x50, R_ARM_THM_MOVW_ABS_NC, "resample_12k8"),
    (0x5A, R_ARM_THM_MOVT_ABS, "resample_12k8"),
    (0x8DC, R_ARM_THM_MOVW_ABS_NC, "interpolate.h4_q15"),
    (0x8E8, R_ARM_THM_MOVT_ABS, "interpolate.h4_q15"),
    (0x1150, R_ARM_THM_MOVW_ABS_NC, "h_8k_12k8_q15"),
    (0x1156, R_ARM_THM_MOVT_ABS, "h_8k_12k8_q15"),
    (0x1234, R_ARM_THM_MOVW_ABS_NC, "h_16k_12k8_q15"),
    (0x1244, R_ARM_THM_MOVT_ABS, "h_16k_12k8_q15"),
    (0x12EA, R_ARM_THM_MOVW_ABS_NC, "h_24k_12k8_q15"),
    (0x12F6, R_ARM_THM_MOVT_ABS, "h_24k_12k8_q15"),
    (0x1374, R_ARM_THM_MOVW_ABS_NC, "h_32k_12k8_q15"),
    (0x137C, R_ARM_THM_MOVT_ABS, "h_32k_12k8_q15"),
    (0x145E, R_ARM_THM_MOVW_ABS_NC, "h_48k_12k8_q15"),
    (0x146A, R_ARM_THM_MOVT_ABS, "h_48k_12k8_q15"),
    (0x1482, R_ARM_THM_MOVW_ABS_NC, "h_96k_12k8_q15"),
    (0x148E, R_ARM_THM_MOVT_ABS, "h_96k_12k8_q15"),
)
EXPECTED_DISPATCH_SYMBOLS = (
    "resample_8k_12k8",
    "resample_16k_12k8",
    "resample_24k_12k8",
    "resample_32k_12k8",
    "resample_48k_12k8",
    "resample_48k_12k8",
    "resample_96k_12k8",
)


def _section_by_name(sections: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [item for item in sections if item["name"] == name]
    if len(matches) != 1:
        raise BuildError(f"expected one {name} section, observed {len(matches)}")
    return matches[0]


def _relocations(
    data: bytes,
    sections: list[dict[str, Any]],
    target_index: int,
) -> list[tuple[int, int, int]]:
    records: list[tuple[int, int, int]] = []
    for section in sections:
        if int(section["type"]) != SHT_REL or int(section["info"]) != target_index:
            continue
        if int(section["entry_size"]) != 8 or int(section["size"]) % 8:
            raise BuildError(f"malformed relocation section {section['name']}")
        for offset in range(0, int(section["size"]), 8):
            place, information = struct.unpack_from(
                "<II", data, int(section["offset"]) + offset
            )
            records.append((place, information & 0xFF, information >> 8))
    return records


def _resolve_movwt_half(blob: bytearray, offset: int, target: int, *, high: bool) -> None:
    first, second = struct.unpack_from("<HH", blob, offset)
    opcode = 0xF2C0 if high else 0xF240
    if first & 0xFBF0 != opcode or second & 0x8000 or thumb_movwt_immediate(first, second) != 0:
        raise BuildError("absolute MOVW/MOVT instruction encoding changed")
    value = target >> 16 if high else target
    first, second = thumb_movwt_with_immediate(first, second, value)
    struct.pack_into("<HH", blob, offset, first, second)


def _extract_overlay(
    object_path: Path,
    runtime_address: int,
    profile: str,
    section_runtime_addresses: dict[str, int] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    data, sections = parse_elf32(object_path)
    symbols = parse_elf32_symbols(data, sections)
    text = _section_by_name(sections, ".text")
    rodata = _section_by_name(sections, ".rodata")
    constants = _section_by_name(sections, ".rodata.cst32")
    exidx = _section_by_name(sections, ".ARM.exidx")

    admitted_indexes = {
        int(text["index"]), int(rodata["index"]), int(constants["index"])
    }
    unexpected = [
        str(section["name"])
        for section in sections
        if int(section["flags"]) & SHF_ALLOC
        and int(section["size"])
        and int(section["index"]) not in admitted_indexes
        and int(section["index"]) != int(exidx["index"])
    ]
    if unexpected:
        raise BuildError(f"unexpected allocated sections: {unexpected}")
    if (
        int(text["type"]) != SHT_PROGBITS
        or int(text["flags"]) != (SHF_ALLOC | SHF_EXECINSTR)
        or int(rodata["type"]) != SHT_PROGBITS
        or int(rodata["flags"]) != SHF_ALLOC
        or int(constants["type"]) != SHT_PROGBITS
        or not int(constants["flags"]) & SHF_ALLOC
        or int(constants["flags"]) & (SHF_WRITE | SHF_EXECINSTR)
        or int(exidx["type"]) != SHT_ARM_EXIDX
    ):
        raise BuildError("admitted section types or flags changed")

    text_start = int(text["offset"])
    payload = bytearray(data[text_start:text_start + int(text["size"])])
    section_offsets = {int(text["index"]): 0}
    rodata_report = []
    for section in (rodata, constants):
        alignment = int(section["alignment"])
        if alignment < 1 or alignment & (alignment - 1):
            raise BuildError(f"invalid alignment for {section['name']}")
        payload.extend(b"\0" * (align_up(len(payload), alignment) - len(payload)))
        section_offsets[int(section["index"])] = len(payload)
        start = int(section["offset"])
        payload.extend(data[start:start + int(section["size"])])
        rodata_report.append(
            {
                "section": section["name"],
                "offset": section_offsets[int(section["index"])],
                "size": int(section["size"]),
                "sha256": sha256(data[start:start + int(section["size"])]),
            }
        )

    section_runtime_addresses = section_runtime_addresses or {}
    text_runtime = section_runtime_addresses.get(".text", runtime_address)
    rodata_runtime = section_runtime_addresses.get(
        ".rodata", runtime_address + section_offsets[int(rodata["index"])]
    )
    constants_runtime = section_runtime_addresses.get(
        ".rodata.cst32",
        rodata_runtime
        + section_offsets[int(constants["index"])]
        - section_offsets[int(rodata["index"])],
    )
    section_runtimes = {
        int(text["index"]): text_runtime,
        int(rodata["index"]): rodata_runtime,
        int(constants["index"]): constants_runtime,
    }

    symbol_by_index = {index: symbol for index, symbol in enumerate(symbols)}
    undefined = sorted(
        str(symbol["name"])
        for symbol in symbols
        if int(symbol["section_index"]) == 0 and str(symbol["name"])
    )
    if undefined:
        raise BuildError(f"overlay retains undefined symbols: {undefined}")

    global_functions = {
        str(symbol["name"]): {
            "offset": section_offsets[int(symbol["section_index"])]
            + (int(symbol["value"]) & ~1),
            "size": int(symbol["size"]),
        }
        for symbol in symbols
        if int(symbol["binding"]) == STB_GLOBAL
        and int(symbol["type"]) == STT_FUNC
        and int(symbol["section_index"]) in section_offsets
    }
    if set(global_functions) != EXPECTED_GLOBAL_FUNCTIONS:
        raise BuildError(
            f"global function ABI changed: {sorted(global_functions)}"
        )
    if global_functions["lc3_ltpf_analyse"]["offset"] != 0:
        raise BuildError("lc3_ltpf_analyse is no longer the payload entry")

    text_relocations = _relocations(data, sections, int(text["index"]))
    observed_text = tuple(
        (offset, kind, str(symbol_by_index[index]["name"]))
        for offset, kind, index in text_relocations
    )
    expected_text = EXPECTED_TEXT_RELOCATIONS
    if profile == "linux-clang":
        # Linux Clang has independent code scheduling; its exact closure is
        # pinned in overlay.json and checked below by name/type/count.
        if len(observed_text) != 16 or tuple(item[1:] for item in observed_text) != tuple(
            item[1:] for item in expected_text
        ):
            raise BuildError(f"Linux text relocation closure changed: {observed_text}")
    elif observed_text != expected_text:
        raise BuildError(f"Apple text relocation closure changed: {observed_text}")

    resolved_text = []
    if len(text_relocations) % 2:
        raise BuildError("text MOVW/MOVT closure has an odd relocation count")
    for index in range(0, len(text_relocations), 2):
        low = text_relocations[index]
        high = text_relocations[index + 1]
        if (
            low[1] != R_ARM_THM_MOVW_ABS_NC
            or high[1] != R_ARM_THM_MOVT_ABS
            or low[2] != high[2]
            or ((struct.unpack_from("<H", payload, low[0] + 2)[0] >> 8) & 0xF)
            != ((struct.unpack_from("<H", payload, high[0] + 2)[0] >> 8) & 0xF)
        ):
            raise BuildError("text MOVW/MOVT pair contract changed")
    for offset, kind, index in text_relocations:
        symbol = symbol_by_index[index]
        section_index = int(symbol["section_index"])
        if section_index not in section_offsets:
            raise BuildError(f"text relocation leaves payload: {symbol['name']}")
        target = section_runtimes[section_index] + (int(symbol["value"]) & ~1)
        _resolve_movwt_half(payload, offset, target, high=kind == R_ARM_THM_MOVT_ABS)
        resolved_text.append(
            {"offset": offset, "type": kind, "symbol": symbol["name"], "target": target}
        )

    dispatch_relocations = _relocations(data, sections, int(rodata["index"]))
    if len(dispatch_relocations) != 7:
        raise BuildError("resample dispatch relocation count changed")
    observed_dispatch = tuple(
        str(symbol_by_index[index]["name"])
        for _offset, kind, index in dispatch_relocations
        if kind == R_ARM_ABS32
    )
    if observed_dispatch != EXPECTED_DISPATCH_SYMBOLS:
        raise BuildError(f"resample dispatch targets changed: {observed_dispatch}")
    dispatch_entries = []
    rodata_offset = section_offsets[int(rodata["index"])]
    for offset, kind, index in dispatch_relocations:
        if kind != R_ARM_ABS32 or offset + 4 > int(rodata["size"]):
            raise BuildError("unsupported resample dispatch relocation")
        symbol = symbol_by_index[index]
        if int(symbol["type"]) != STT_FUNC or int(symbol["section_index"]) != int(text["index"]):
            raise BuildError("dispatch target is not a local text function")
        place = rodata_offset + offset
        addend = struct.unpack_from("<I", payload, place)[0]
        target = text_runtime + (int(symbol["value"]) & ~1) + addend | 1
        struct.pack_into("<I", payload, place, target)
        dispatch_entries.append(
            {"offset": place, "symbol": symbol["name"], "target": target}
        )

    exidx_relocations = _relocations(data, sections, int(exidx["index"]))
    if len(exidx_relocations) != 11 or int(exidx["size"]) != 88:
        raise BuildError("discarded CANTUNWIND closure changed")
    exidx_bytes = data[int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])]
    exidx_addends = []
    for row, (offset, kind, index) in enumerate(exidx_relocations):
        symbol = symbol_by_index[index]
        addend, marker = struct.unpack_from("<II", exidx_bytes, offset)
        if (
            offset != row * 8
            or kind != R_ARM_PREL31
            or int(symbol["binding"]) != STB_LOCAL
            or int(symbol["type"]) != STT_SECTION
            or int(symbol["section_index"]) != int(text["index"])
            or marker != 1
        ):
            raise BuildError("discarded CANTUNWIND row changed")
        exidx_addends.append(addend)
    if exidx_addends[0] != 0 or exidx_addends != sorted(set(exidx_addends)):
        raise BuildError("discarded CANTUNWIND function ordering changed")

    if _relocations(data, sections, int(constants["index"])):
        raise BuildError("constant table gained relocations")

    return bytes(payload), {
        "functions": global_functions,
        "text_size": int(text["size"]),
        "rodata": rodata_report,
        "text_relocations": resolved_text,
        "dispatch_entries": dispatch_entries,
        "discarded_cantunwind_rows": 11,
        "runtime_dependencies": [],
        "section_runtime_addresses": {
            ".text": text_runtime,
            ".rodata": rodata_runtime,
            ".rodata.cst32": constants_runtime,
        },
    }


def _verify_expected(label: str, observed: dict[str, Any], expected: dict[str, Any], record: bool) -> None:
    if record:
        return
    for key in ("size", "sha256"):
        if observed[key] != expected.get(key):
            raise BuildError(
                f"{label} {key} differs: expected {expected.get(key)!r}, observed {observed[key]!r}"
            )


def build(
    *,
    config_path: Path,
    output_dir: Path,
    clang: str,
    profile: str,
    record: bool,
    base_path_override: Path | None = None,
    base_expected_override: dict[str, Any] | None = None,
    expected_override: dict[str, Any] | None = None,
    placement_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise BuildError("unsupported liblc3 overlay schema")
    profiles = config.get("profiles", {})
    if profile not in profiles:
        raise BuildError(f"unknown toolchain profile {profile!r}")
    active = profiles[profile]
    toolchain = {"reviewed_version_prefix": active["reviewed_version_prefix"]}
    version = compiler_version(clang)
    validate_compiler_version(toolchain, version)

    base_path = (
        base_path_override.resolve()
        if base_path_override is not None
        else G2_ROOT / config["base"]["path"]
    )
    base = base_path.read_bytes()
    base_expected = base_expected_override or config["base"]
    if len(base) != base_expected["size"] or sha256(base) != base_expected["sha256"]:
        raise BuildError("official Apollo base differs from pins")
    source_records = []
    for source in config["sources"]:
        path = G2_ROOT / source["path"]
        payload = path.read_bytes()
        if len(payload) != source["size"] or sha256(payload) != source["sha256"]:
            raise BuildError(f"source differs from pins: {source['path']}")
        source_records.append({**source})

    overlay_start = align_up(len(base), config["alignment"])
    runtime_address = config["run_base"] + overlay_start - config["preamble_bytes"]
    section_runtime_addresses = None
    if placement_override is not None:
        text_placement = placement_override["text"]
        rodata_placement = placement_override["rodata"]
        runtime_address = int(text_placement["runtime_address"])
        section_runtime_addresses = {
            ".text": runtime_address,
            ".rodata": int(rodata_placement["runtime_address"]),
            ".rodata.cst32": int(rodata_placement["runtime_address"])
            + int(rodata_placement["constants_offset"]),
        }
    flags = config["toolchain_flags"]
    include_dirs = [G2_ROOT / item for item in config["include_dirs"]]
    with tempfile.TemporaryDirectory(prefix="open-cfw-liblc3-ltpf-") as temporary:
        object_path = Path(temporary) / "liblc3_ltpf.o"
        command = [clang, "--target=arm-none-eabi", *flags]
        for include_dir in include_dirs:
            command.extend(("-I", str(include_dir)))
        command.extend(("-c", str(G2_ROOT / config["compile_source"]), "-o", str(object_path)))
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode:
            raise BuildError(completed.stderr.strip() or completed.stdout.strip())
        overlay, link_report = _extract_overlay(
            object_path,
            runtime_address,
            profile,
            section_runtime_addresses,
        )

    overlay_record = {"size": len(overlay), "sha256": sha256(overlay)}
    expected = expected_override or active
    _verify_expected("overlay", overlay_record, expected["overlay"], record)

    component = bytearray(base)
    placement_sections = None
    if placement_override is None:
        component.extend(b"\0" * (overlay_start - len(component)))
        component.extend(overlay)
    else:
        rodata_offset = int(link_report["rodata"][0]["offset"])
        segments = {
            "text": overlay[:rodata_offset],
            "rodata": overlay[rodata_offset:],
        }
        placement_sections = {}
        for name, segment in segments.items():
            placement = placement_override[name]
            file_offset = int(placement["file_offset"])
            capacity = int(placement["capacity"])
            if len(segment) > capacity:
                raise BuildError(
                    f"liblc3 {name} segment exceeds reviewed cave capacity"
                )
            existing = bytes(component[file_offset:file_offset + len(segment)])
            if sha256(existing) != placement["expected_sha256"]:
                raise BuildError(f"liblc3 {name} cave bytes differ from pins")
            component[file_offset:file_offset + len(segment)] = segment
            placement_sections[name] = {
                "file_offset": file_offset,
                "runtime_address": int(placement["runtime_address"]),
                "capacity": capacity,
                "size": len(segment),
                "sha256": sha256(segment),
            }
    patch = config["patch_site"]
    patch_offset = patch["runtime_address"] - config["run_base"] + config["preamble_bytes"]
    observed_patch = bytes(component[patch_offset:patch_offset + 4])
    expected_hex = patch.get("expected_hex")
    expected_size = patch.get("expected_size")
    expected_sha256 = patch.get("expected_sha256")
    if expected_hex is not None:
        if (
            not isinstance(expected_hex, str)
            or re.fullmatch(r"[0-9a-fA-F]{8}", expected_hex) is None
            or expected_size is not None
            or expected_sha256 is not None
        ):
            raise BuildError("lc3_encode callsite guard is invalid")
        if observed_patch != bytes.fromhex(expected_hex):
            raise BuildError("authenticated lc3_encode callsite differs")
    elif (
        expected_size != 4
        or not isinstance(expected_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
    ):
        raise BuildError("lc3_encode callsite requires an exact or hashed guard")
    elif sha256(observed_patch) != expected_sha256:
        raise BuildError("authenticated lc3_encode callsite hash differs")
    target = runtime_address + link_report["functions"][patch["target_function"]]["offset"]
    replacement = encode_thumb_branch(patch["runtime_address"], target, link=True)
    component[patch_offset:patch_offset + 4] = replacement
    if decode_thumb_bl(patch["runtime_address"], replacement) != target:
        raise BuildError("patched BL does not decode to admitted entry")

    # The component is itself an Apollo OTA payload.  Appending source bytes
    # changes both the nested payload length and its CRC-32; leaving the
    # inherited base header intact would produce an invalid, unflashable
    # provider even though the code and relocation closure were correct.
    flags = struct.unpack_from("<I", component, 0)[0] >> 24
    if flags != 0x04 or len(component) > 0x00FFFFFF:
        raise BuildError("Apollo OTA preamble flags or final size changed")
    struct.pack_into("<I", component, 0, flags << 24 | len(component))
    struct.pack_into("<I", component, 4, zlib.crc32(component[8:]) & 0xFFFFFFFF)

    component_bytes = bytes(component)
    component_record = {"size": len(component_bytes), "sha256": sha256(component_bytes)}
    _verify_expected("component", component_record, expected["component"], record)
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(output_dir / "liblc3_ltpf.text.bin", overlay)
    atomic_write(output_dir / "ota_s200_firmware_ota.bin", component_bytes)
    report = {
        "schema_version": 1,
        "name": config["name"],
        "profile": profile,
        "toolchain": {"executable": clang, "version": version, "flags": flags},
        "sources": source_records,
        "base": {"path": str(base_path), "size": len(base), "sha256": sha256(base)},
        "placement": {
            "file_offset": (
                overlay_start
                if placement_override is None
                else int(placement_override["text"]["file_offset"])
            ),
            "runtime_address": runtime_address,
            "runtime_address_hex": f"0x{runtime_address:08X}",
            "entry": target,
            "entry_hex": f"0x{target:08X}",
            **({"sections": placement_sections} if placement_sections else {}),
        },
        "overlay": {**overlay_record, **link_report},
        "patch_site": {
            **patch,
            "file_offset": patch_offset,
            "replacement_hex": replacement.hex(),
            "decoded_target": target,
        },
        "component": {
            **component_record,
            "source_owned_bytes": len(overlay),
            "source_owned_patch_bytes": 4,
            "opaque_base_bytes": len(base) - config["preamble_bytes"] - 4,
        },
        "historical_non_corpus_routing": {
            "0x00438400": False,
            "0x00438604": False,
        },
    }
    atomic_write(
        output_dir / "build-report.json",
        (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=COMPONENT_ROOT / "overlay.json")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--profile", default="apple-clang")
    parser.add_argument("--clang")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    clang = args.clang or (
        "/opt/homebrew/opt/llvm@22/bin/clang" if args.profile == "linux-clang" else "/usr/bin/clang"
    )
    output_dir = args.output_dir or COMPONENT_ROOT / "build" / args.profile
    try:
        report = build(
            config_path=args.config,
            output_dir=output_dir,
            clang=clang,
            profile=args.profile,
            record=args.record,
        )
    except (BuildError, OSError, KeyError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
