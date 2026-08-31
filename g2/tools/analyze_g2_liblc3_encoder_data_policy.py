#!/usr/bin/env python3
"""Qualify the specialized LC3 pointer tables for immutable XIP placement.

SPDX-License-Identifier: MIT
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
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(G2 / "tools"))

from apollo_overlay import (  # noqa: E402
    SHF_ALLOC,
    SHF_EXECINSTR,
    SHF_WRITE,
    SHT_PROGBITS,
    SHT_REL,
    STB_GLOBAL,
    STT_OBJECT,
    parse_elf32,
    parse_elf32_symbols,
)


COMPONENT = G2 / "components/apollo_main/liblc3_encoder"
MANIFEST = COMPONENT / "data_policy_admission.json"
LINKER = COMPONENT / "data_policy_linker.ld"
SPECIALIZATION = COMPONENT / "specialization_experiment.json"
SHARED = G2 / "components/shared/liblc3"
PROVIDER = SHARED / "runtime_liblc3_encoder_provider.c"
TARGET_COMPAT = SHARED / "target_compat"
UPSTREAM = G2 / "third_party/liblc3"
UPSTREAM_INCLUDE = UPSTREAM / "include"
UPSTREAM_SRC = UPSTREAM / "src"
TABLES = UPSTREAM_SRC / "tables.c"
TABLES_H = UPSTREAM_SRC / "tables.h"
ENCODER_SOURCES = tuple(
    UPSTREAM_SRC / f"{name}.c"
    for name in (
        "attdet", "bits", "bwdet", "energy", "lc3", "ltpf", "mdct",
        "sns", "spec", "tables", "tns",
    )
)
LLVM_ROOT = Path("/opt/homebrew/opt/llvm@22/bin")
LLVM_NM = LLVM_ROOT / "llvm-nm"
LLVM_OBJCOPY = LLVM_ROOT / "llvm-objcopy"
LLD = Path("/opt/homebrew/bin/ld.lld")
PROFILES = {
    "apple-clang": Path("/usr/bin/clang"),
    "linux-clang": LLVM_ROOT / "clang",
}
TARGET_FLAGS = (
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
    "-mfloat-abi=hard", "-std=c11", "-O2", "-ffast-math",
    "-fshort-enums", "-ffreestanding", "-fno-builtin",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
    "-Werror", "-DLC3_PLUS_HR=0",
)
ROOTS = (
    "open_cfw_liblc3_encoder_provider_plan",
    "open_cfw_liblc3_encoder_provider_setup",
    "open_cfw_liblc3_encoder_provider_encode",
    "open_cfw_liblc3_encoder_provider_close",
)
RUNTIME_IMPORTS = {
    "__aeabi_memclr", "__aeabi_memclr4", "fabsf", "floorf", "fmaxf",
    "fminf", "memcpy", "memmove", "memset", "sqrtf", "truncf",
}
TABLE_SECTION = ".lc3_table_rodata"
TABLE_BYTES = 404
TABLE_ALIGNMENT = 8
TABLE_SYMBOLS = {
    "lc3_band_lim": (0, 112),
    "lc3_fft_twiddles_bf2": (112, 60),
    "lc3_fft_twiddles_bf3": (172, 8),
    "lc3_mdct_rot": (180, 112),
    "lc3_mdct_win": (292, 112),
}
UINT32_LIMIT = 1 << 32


class DataPolicyError(RuntimeError):
    """Raised when the table closure or immutable-XIP contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataPolicyError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(command: list[str]) -> str:
    return subprocess.run(command, check=True, capture_output=True,
                          text=True).stdout


def align_up(value: int, alignment: int) -> int:
    require(alignment > 0 and alignment & (alignment - 1) == 0,
            "alignment must be a nonzero power of two")
    require(0 <= value < UINT32_LIMIT, "address escapes uint32")
    result = (value + alignment - 1) & -alignment
    require(result < UINT32_LIMIT, "aligned address overflows uint32")
    return result


def checked_interval(name: str, start: int, size: int,
                     alignment: int) -> tuple[int, int]:
    require(isinstance(start, int) and isinstance(size, int),
            f"{name}: interval must use integers")
    require(start >= 0 and size > 0 and start % alignment == 0,
            f"{name}: invalid start, size, or alignment")
    end = start + size
    require(end <= UINT32_LIMIT and end > start,
            f"{name}: interval overflow")
    return start, end


def overlaps(first: tuple[int, int], second: tuple[int, int]) -> bool:
    return first[0] < second[1] and second[0] < first[1]


def validate_xip_layout(*, flash_start: int, flash_end: int,
                        rodata_start: int, rodata_size: int,
                        table_start: int, table_size: int,
                        forbidden: tuple[tuple[int, int], ...] = ()) -> dict[str, int]:
    flash = checked_interval("flash", flash_start, flash_end - flash_start, 1)
    rodata = checked_interval("rodata", rodata_start, rodata_size, 16)
    table = checked_interval("table", table_start, table_size, TABLE_ALIGNMENT)
    require(table_size == TABLE_BYTES, "table size differs from admission")
    require(table_start == align_up(rodata[1], TABLE_ALIGNMENT),
            "table must immediately follow aligned rodata")
    require(flash[0] <= rodata[0] and table[1] <= flash[1],
            "XIP sections escape admitted flash")
    require(not overlaps(rodata, table), "rodata and table overlap")
    for index, interval in enumerate(forbidden):
        blocked = checked_interval(f"forbidden[{index}]", interval[0],
                                   interval[1] - interval[0], 1)
        require(not overlaps(rodata, blocked) and not overlaps(table, blocked),
                "XIP layout overlaps a protected interval")
    return {
        "rodata_start": rodata[0], "rodata_end_exclusive": rodata[1],
        "table_start": table[0], "table_end_exclusive": table[1],
        "runtime_copy_bytes": 0, "runtime_writable_bytes": 0,
    }


def validate_adapter_state_layout(*, ram_start: int, ram_end: int,
                                  state_start: int, state_count: int = 4,
                                  occupied: tuple[tuple[int, int], ...] = ()) -> dict[str, int]:
    ram = checked_interval("ram", ram_start, ram_end - ram_start, 1)
    require(state_count == 4, "authenticated service context count changed")
    total = state_count * 2628
    states = checked_interval("adapter states", state_start, total, 8)
    require(ram[0] <= states[0] and states[1] <= ram[1],
            "adapter states escape admitted RAM")
    for index, interval in enumerate(occupied):
        used = checked_interval(f"occupied[{index}]", interval[0],
                                interval[1] - interval[0], 1)
        require(not overlaps(states, used),
                "adapter states overlap an occupied interval")
    return {
        "state_start": states[0], "state_end_exclusive": states[1],
        "state_count": state_count, "state_bytes_each": 2628,
        "runtime_writable_bytes": total,
    }


def relocate_table(template: bytes, relocation_offsets: list[int],
                   rodata_base: int, rodata_size: int) -> bytes:
    require(len(template) == TABLE_BYTES, "table template size drift")
    require(rodata_base % 16 == 0 and 0 <= rodata_base < UINT32_LIMIT,
            "rodata base is not an aligned uint32 address")
    require(rodata_size > 0 and rodata_base + rodata_size <= UINT32_LIMIT,
            "rodata interval overflows uint32")
    offsets = sorted(relocation_offsets)
    require(len(offsets) == 78 and len(set(offsets)) == len(offsets),
            "table relocation count or uniqueness drift")
    require(all(offset % 4 == 0 and 0 <= offset <= TABLE_BYTES - 4
                for offset in offsets), "table relocation offset is invalid")
    nonzero = {
        offset for offset in range(0, TABLE_BYTES, 4)
        if struct.unpack_from("<I", template, offset)[0] != 0
    }
    require(set(offsets) == nonzero,
            "relocations do not cover exactly every initialized pointer")
    output = bytearray(template)
    for offset in offsets:
        addend = struct.unpack_from("<I", template, offset)[0]
        require(addend % 4 == 0 and addend < rodata_size,
                "table pointer addend escapes aligned rodata")
        struct.pack_into("<I", output, offset, rodata_base + addend)
    return bytes(output)


def section_by_name(sections: list[dict[str, Any]], name: str,
                    *, required: bool = True) -> dict[str, Any] | None:
    matches = [section for section in sections if section["name"] == name]
    require(len(matches) <= 1, f"duplicate section: {name}")
    if required:
        require(len(matches) == 1, f"missing section: {name}")
    return matches[0] if matches else None


def section_bytes(payload: bytes, section: dict[str, Any]) -> bytes:
    start = int(section["offset"])
    return payload[start:start + int(section["size"])]


def relocation_records(payload: bytes, sections: list[dict[str, Any]],
                       symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names = {
        2: "R_ARM_ABS32", 10: "R_ARM_THM_CALL", 30: "R_ARM_THM_JUMP24",
        47: "R_ARM_THM_MOVW_ABS_NC", 48: "R_ARM_THM_MOVT_ABS",
    }
    records: list[dict[str, Any]] = []
    for section in sections:
        if int(section["type"]) != SHT_REL or not int(section["size"]):
            continue
        require(int(section["entry_size"]) == 8 and
                int(section["size"]) % 8 == 0,
                "malformed relocation section")
        target = sections[int(section["info"])]
        for cursor in range(0, int(section["size"]), 8):
            offset, information = struct.unpack_from(
                "<II", payload, int(section["offset"]) + cursor)
            kind = information & 0xFF
            symbol_index = information >> 8
            require(kind in names and symbol_index < len(symbols),
                    "unadmitted relocation encoding")
            symbol = symbols[symbol_index]
            symbol_section = (sections[int(symbol["section_index"])]["name"]
                              if int(symbol["section_index"]) else "UND")
            records.append({
                "section": str(target["name"]), "offset": offset,
                "type": names[kind], "symbol": str(symbol["name"]),
                "symbol_section": str(symbol_section),
                "symbol_value": int(symbol["value"]),
            })
    return records


def compile_one(compiler: Path, source: Path, output: Path) -> None:
    run([
        str(compiler), *TARGET_FLAGS,
        "-I", str(TARGET_COMPAT), "-I", str(UPSTREAM_INCLUDE),
        "-I", str(UPSTREAM_SRC), "-I", str(SHARED),
        "-c", str(source), "-o", str(output),
    ])


def source_mutability_audit() -> dict[str, Any]:
    sources = {
        "energy.c": (UPSTREAM_SRC / "energy.c").read_text(encoding="utf-8"),
        "mdct.c": (UPSTREAM_SRC / "mdct.c").read_text(encoding="utf-8"),
        "sns.c": (UPSTREAM_SRC / "sns.c").read_text(encoding="utf-8"),
        "tables.c": TABLES.read_text(encoding="utf-8"),
    }
    expected_counts = {
        "lc3_band_lim": 3,
        "lc3_fft_twiddles_bf2": 2,
        "lc3_fft_twiddles_bf3": 2,
        "lc3_mdct_rot": 3,
        "lc3_mdct_win": 3,
    }
    joined = "\n".join(sources.values())
    for symbol, count in expected_counts.items():
        require(len(re.findall(rf"\b{re.escape(symbol)}\b", joined)) == count,
                f"{symbol}: source reference count drift")
    required_reads = {
        "energy.c": ["const int *lim = lc3_band_lim[dt][sr];"],
        "sns.c": ["const int *lim = lc3_band_lim[dt][sr];"],
        "mdct.c": [
            "fft_bf3(lc3_fft_twiddles_bf3[i3]",
            "fft_bf2(lc3_fft_twiddles_bf2[i2][i3]",
            "const float *win = lc3_mdct_win[dt][sr];",
            "const struct lc3_mdct_rot_def *rot = lc3_mdct_rot[dt][sr];",
        ],
    }
    for name, tokens in required_reads.items():
        require(all(token in sources[name] for token in tokens),
                f"{name}: read-only table use drift")
    for symbol in TABLE_SYMBOLS:
        require(re.search(rf"\b{symbol}\s*\[[^;]*\]\s*=", sources["tables.c"],
                          re.S) is not None,
                f"{symbol}: initializer definition drift")
        for name in ("energy.c", "mdct.c", "sns.c"):
            require(re.search(rf"\b{symbol}\b\s*(?:\[[^]]+\])+\s*=",
                              sources[name]) is None,
                    f"{name}: write to {symbol} detected")
    return {
        "source_sha256": {name: sha256(UPSTREAM_SRC / name)
                          for name in sources},
        "reference_counts": expected_counts,
        "retained_behavior": "read-only-indexed-pointer-loads",
        "runtime_initializer_present": False,
    }


def build_once(profile: str, compiler: Path, output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True)
    objects: list[Path] = []
    for index, source in enumerate((*ENCODER_SOURCES, PROVIDER)):
        output = output_dir / f"{index:02d}-{source.stem}.o"
        compile_one(compiler, source, output)
        objects.append(output)
    writable = output_dir / "liblc3-data-policy-write.o"
    run([
        str(LLD), "-m", "armelf", "-r", "--gc-sections",
        "--build-id=none", f"--entry={ROOTS[2]}",
        *(f"--undefined={root}" for root in ROOTS),
        "-T", str(LINKER), "-o", str(writable),
        *(str(path) for path in objects),
    ])
    pre_payload, pre_sections = parse_elf32(writable)
    pre_table = section_by_name(pre_sections, TABLE_SECTION)
    assert pre_table is not None
    require(int(pre_table["flags"]) == SHF_ALLOC | SHF_WRITE,
            "pre-policy table section does not carry exact input flags")
    require(int(pre_table["size"]) == TABLE_BYTES and
            int(pre_table["alignment"]) == TABLE_ALIGNMENT,
            "pre-policy table geometry drift")
    unexpected = section_by_name(pre_sections, ".unexpected_writable",
                                 required=False)
    require(unexpected is None or int(unexpected["size"]) == 0,
            "retained unexpected writable data")

    admitted = output_dir / "liblc3-data-policy-readonly.o"
    run([
        str(LLVM_OBJCOPY), "--set-section-flags",
        f"{TABLE_SECTION}=alloc,load,readonly,data,contents",
        str(writable), str(admitted),
    ])
    payload, sections = parse_elf32(admitted)
    symbols = parse_elf32_symbols(payload, sections)
    text = section_by_name(sections, ".text")
    rodata = section_by_name(sections, ".rodata")
    table = section_by_name(sections, TABLE_SECTION)
    assert text is not None and rodata is not None and table is not None
    require(int(text["flags"]) == SHF_ALLOC | SHF_EXECINSTR and
            int(text["alignment"]) == 16, "text section contract drift")
    require(int(rodata["flags"]) == SHF_ALLOC | 0x10 and
            int(rodata["alignment"]) == 16, "rodata section contract drift")
    require(int(table["flags"]) == SHF_ALLOC and
            int(table["type"]) == SHT_PROGBITS and
            int(table["size"]) == TABLE_BYTES and
            int(table["alignment"]) == TABLE_ALIGNMENT,
            "post-policy immutable table flags or geometry drift")
    allocated_writable = [
        str(section["name"]) for section in sections
        if int(section["size"]) and int(section["flags"]) & SHF_ALLOC
        and int(section["flags"]) & SHF_WRITE
    ]
    require(not allocated_writable, "post-policy object retains writable data")

    table_index = int(table["index"])
    table_symbol_records: dict[str, dict[str, int]] = {}
    for name, (offset, size) in TABLE_SYMBOLS.items():
        matches = [symbol for symbol in symbols
                   if symbol["name"] == name and
                   int(symbol["section_index"]) == table_index and
                   int(symbol["binding"]) == STB_GLOBAL and
                   int(symbol["type"]) == STT_OBJECT]
        require(len(matches) == 1 and int(matches[0]["value"]) == offset and
                int(matches[0]["size"]) == size,
                f"{name}: table symbol geometry drift")
        table_symbol_records[name] = {"offset": offset, "size": size}

    records = relocation_records(payload, sections, symbols)
    table_relocations = [row for row in records
                         if row["section"] == TABLE_SECTION]
    require(len(table_relocations) == 78 and all(
        row["type"] == "R_ARM_ABS32" and
        row["symbol_section"] == ".rodata" and row["symbol"] == ""
        for row in table_relocations),
        "table initialization relocations escaped internal rodata")
    text_references = [row for row in records
                       if row["section"] == ".text" and
                       row["symbol_section"] == TABLE_SECTION]
    require(len(text_references) == 12 and Counter(
        row["type"] for row in text_references) == {
            "R_ARM_THM_MOVW_ABS_NC": 6, "R_ARM_THM_MOVT_ABS": 6,
        }, "table text-reference closure drift")
    require(Counter(row["symbol"] for row in text_references) == {
        "lc3_band_lim": 4, "lc3_fft_twiddles_bf2": 2,
        "lc3_fft_twiddles_bf3": 2, "lc3_mdct_rot": 2,
        "lc3_mdct_win": 2,
    }, "table text-reference symbol set drift")

    template = section_bytes(payload, table)
    rodata_payload = section_bytes(payload, rodata)
    offsets = [row["offset"] for row in table_relocations]
    relocated = relocate_table(template, offsets, 0x00600000,
                               len(rodata_payload))
    undefined_output = run([str(LLVM_NM), "-u", str(admitted)])
    undefined = set(re.findall(r"\bU\s+(\S+)$", undefined_output, re.M))
    require(undefined == RUNTIME_IMPORTS,
            "post-policy retained runtime imports drift")
    relocation_digest = sha256_bytes(json.dumps(
        records, sort_keys=True, separators=(",", ":")).encode())
    table_relocation_digest = sha256_bytes(json.dumps(
        table_relocations, sort_keys=True, separators=(",", ":")).encode())
    text_reference_digest = sha256_bytes(json.dumps(
        text_references, sort_keys=True, separators=(",", ":")).encode())
    return {
        "compiler_version": run([str(compiler), "--version"]).splitlines()[0],
        "pre_policy_object": {
            "size": writable.stat().st_size, "sha256": sha256(writable),
            "table_flags": ["SHF_ALLOC", "SHF_WRITE"],
        },
        "post_policy_object": {
            "size": admitted.stat().st_size, "sha256": sha256(admitted),
            "allocated_writable_sections": [],
            "retained_imports": sorted(undefined),
        },
        "sections": {
            "text": {"size": int(text["size"]),
                     "sha256": sha256_bytes(section_bytes(payload, text))},
            "rodata": {"size": len(rodata_payload),
                       "sha256": sha256_bytes(rodata_payload)},
            "table_rodata": {"size": len(template),
                             "alignment": int(table["alignment"]),
                             "flags": ["SHF_ALLOC"],
                             "sha256": sha256_bytes(template)},
        },
        "table_symbols": table_symbol_records,
        "initialization": {
            "runtime_copy_bytes": 0,
            "runtime_writable_bytes": 0,
            "relocation_count": len(table_relocations),
            "relocation_type": "R_ARM_ABS32",
            "relocation_target": ".rodata",
            "relocation_offsets": sorted(offsets),
            "relocation_records_sha256": table_relocation_digest,
            "synthetic_rodata_base": 0x00600000,
            "synthetic_relocated_sha256": sha256_bytes(relocated),
            "final_relocation_required": True,
        },
        "text_references": {
            "count": len(text_references),
            "by_symbol": dict(sorted(Counter(
                row["symbol"] for row in text_references).items())),
            "records_sha256": text_reference_digest,
        },
        "all_relocations_sha256": relocation_digest,
    }


def reproducible_profile(profile: str, compiler: Path,
                         output_dir: Path) -> dict[str, Any]:
    first = build_once(profile, compiler, output_dir / "first")
    second = build_once(profile, compiler, output_dir / "second")
    require(first == second, f"{profile}: policy build report is nondeterministic")
    for name in ("liblc3-data-policy-write.o",
                 "liblc3-data-policy-readonly.o"):
        require((output_dir / "first" / name).read_bytes() ==
                (output_dir / "second" / name).read_bytes(),
                f"{profile}:{name}: bytes are nondeterministic")
    return first


def build_profiles() -> dict[str, Any]:
    for tool in (LLVM_NM, LLVM_OBJCOPY, LLD, *PROFILES.values()):
        require(tool.is_file(), f"reviewed tool unavailable: {tool}")
    with tempfile.TemporaryDirectory(prefix="opencfw-lc3-data-policy-") as tmp:
        directory = Path(tmp)
        return {name: reproducible_profile(name, compiler, directory / name)
                for name, compiler in PROFILES.items()}


def validate_admission(path: Path, report: dict[str, Any]) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1 and
            manifest["name"] == "liblc3_encoder_data_policy_admission",
            "data-policy manifest schema drift")
    profiles = report["profiles"]
    common_initialization = profiles["apple-clang"]["initialization"]
    require(profiles["linux-clang"]["initialization"] == common_initialization,
            "profile table-initialization geometry differs")
    compact_profiles = {
        name: {key: value for key, value in profile.items()
               if key != "initialization"}
        for name, profile in profiles.items()
    }
    observed = {
        key: value for key, value in report.items() if key != "profiles"
    }
    observed["common_initialization"] = common_initialization
    observed["profiles"] = compact_profiles
    require(manifest["expected"] == observed,
            "data-policy evidence or deterministic receipt drift")


def run_audit(path: Path = MANIFEST, *, discover: bool = False
              ) -> dict[str, Any]:
    specialization = json.loads(SPECIALIZATION.read_text(encoding="utf-8"))
    variant = specialization["variants"]["non_hr_only"]["expected"]
    report = {
        "status": "liblc3-encoder-immutable-xip-data-policy",
        "source": {
            "linker_path": str(LINKER.relative_to(G2)),
            "linker_sha256": sha256(LINKER),
            "tables_source_sha256": sha256(TABLES),
            "tables_header_sha256": sha256(TABLES_H),
            "provider_sha256": sha256(PROVIDER),
            "specialization_manifest_sha256": sha256(SPECIALIZATION),
            "license": "MIT-policy-Apache-2.0-upstream",
        },
        "baseline": {
            "specialized_data_size":
                variant["artifacts"]["table_rodata"]["size"],
            "specialized_data_sha256":
                variant["artifacts"]["table_rodata"]["sha256"],
            "specialized_data_relocations":
                variant["relocations"]["by_section"][TABLE_SECTION],
        },
        "mutability": source_mutability_audit(),
        "profiles": build_profiles(),
        "policy": {
            "classification": "logically-immutable-relocated-pointer-tables",
            "output_section": TABLE_SECTION,
            "output_flags": ["SHF_ALLOC"],
            "load_run_policy": "same-address-read-only-XIP",
            "runtime_copy_bytes": 0,
            "runtime_initialization": False,
            "final_build_time_relocation_required": True,
            "final_table_address_required": True,
            "final_rodata_address_required": True,
            "new_relocation_or_symbol_ingress_forbidden": True,
            "production_routed": False,
            "firmware_image_emitted": False,
        },
        "composition": {
            "table_flash_bytes": TABLE_BYTES,
            "table_runtime_writable_bytes": 0,
            "adapter_state_count": 4,
            "adapter_state_bytes_each": 2628,
            "adapter_state_runtime_writable_bytes": 10512,
            "combined_runtime_writable_bytes": 10512,
            "additional_runtime_writable_bytes": 0,
            "stock_context_total_bytes": 10512,
            "adapter_state_deficit_over_stock_bytes": 0,
            "writable_placement_assigned": True,
            "writable_placement_scope": "authenticated-stock-context-slots",
        },
        "routing": {
            "placement_assigned": False,
            "service_audio_routed": False,
            "firmware_image_emitted": False,
            "hardware_operations": False,
            "remaining_prerequisites": [
                "The final placer must assign text, rodata, and aligned table XIP addresses and apply every internal and runtime relocation.",
                "The final closure must reject any new write reference or external symbol ingress to the five table objects.",
                "The four compact service adapter states fit the authenticated stock slots; call-site routing must initialize them before use.",
            ],
        },
    }
    require(report["baseline"] == {
        "specialized_data_size": 404,
        "specialized_data_sha256":
            "c4c45a0ea2a6895b34d21adc0a20928de754948d66e8270883ddb3a9a5e8372a",
        "specialized_data_relocations": 78,
    }, "specialized data baseline drift")
    if not discover:
        validate_admission(path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--admission", type=Path, default=MANIFEST)
    parser.add_argument("--discover", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_audit(args.admission, discover=args.discover),
                     sort_keys=True, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
