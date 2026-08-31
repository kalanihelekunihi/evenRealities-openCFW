#!/usr/bin/env python3
"""Immutable-table admission and finalization for specialized liblc3.

The functions in this module are used by the component builder.  They are
deliberately independent of any stock placement: finalization accepts an
explicit section layout and an exact runtime-symbol map, then emits XIP bytes
only after the final ELF has no unresolved symbols or retained relocations.

SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


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
RELOCATION_NAMES = {
    2: "R_ARM_ABS32",
    10: "R_ARM_THM_CALL",
    30: "R_ARM_THM_JUMP24",
    47: "R_ARM_THM_MOVW_ABS_NC",
    48: "R_ARM_THM_MOVT_ABS",
}
SHT_PROGBITS = 1
SHT_REL = 9
SHF_WRITE = 1
SHF_ALLOC = 2
SHF_EXECINSTR = 4
SHF_MERGE = 0x10
STB_GLOBAL = 1
STT_OBJECT = 1
STT_FUNC = 2
UINT32_LIMIT = 1 << 32


class SpecializedXipError(RuntimeError):
    """Raised when immutable-table admission or finalization fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SpecializedXipError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def artifact_record(payload: bytes) -> dict[str, Any]:
    return {"size": len(payload), "sha256": sha256_bytes(payload)}


def align_up(value: int, alignment: int) -> int:
    require(isinstance(value, int) and 0 <= value < UINT32_LIMIT,
            "address escapes uint32")
    require(alignment > 0 and alignment & (alignment - 1) == 0,
            "alignment must be a nonzero power of two")
    result = (value + alignment - 1) & -alignment
    require(result < UINT32_LIMIT, "aligned address overflows uint32")
    return result


def _section(sections: list[dict[str, Any]], name: str,
             *, required: bool = True) -> dict[str, Any] | None:
    matches = [section for section in sections if section["name"] == name]
    require(len(matches) <= 1, f"duplicate section: {name}")
    if required:
        require(len(matches) == 1, f"missing section: {name}")
    return matches[0] if matches else None


def _section_bytes(payload: bytes, section: dict[str, Any]) -> bytes:
    start = int(section["offset"])
    end = start + int(section["size"])
    require(0 <= start <= end <= len(payload), "section payload escapes ELF")
    return payload[start:end]


def _symbol_section(symbol: dict[str, Any],
                    sections: list[dict[str, Any]]) -> str:
    index = int(symbol["section_index"])
    if index == 0:
        return "UND"
    if index >= len(sections):
        return "ABS" if index == 0xFFF1 else f"SPECIAL:{index}"
    return str(sections[index]["name"])


def relocation_records(payload: bytes, sections: list[dict[str, Any]],
                       symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for section in sections:
        if int(section["type"]) != SHT_REL or not int(section["size"]):
            continue
        require(int(section["entry_size"]) == 8 and
                int(section["size"]) % 8 == 0,
                f"malformed relocation section {section['name']}")
        target_index = int(section["info"])
        require(target_index < len(sections), "invalid relocation target")
        target = str(sections[target_index]["name"])
        for cursor in range(0, int(section["size"]), 8):
            offset, information = struct.unpack_from(
                "<II", payload, int(section["offset"]) + cursor)
            kind = information & 0xFF
            symbol_index = information >> 8
            require(kind in RELOCATION_NAMES and symbol_index < len(symbols),
                    "unadmitted relocation encoding")
            symbol = symbols[symbol_index]
            records.append({
                "section": target,
                "offset": offset,
                "type": RELOCATION_NAMES[kind],
                "symbol": str(symbol["name"]),
                "symbol_section": _symbol_section(symbol, sections),
                "symbol_value": int(symbol["value"]),
                "external": int(symbol["section_index"]) == 0,
            })
    return records


DEFAULT_TABLE_REFERENCE_CONTRACT = {
    "by_type": {
        "R_ARM_THM_MOVW_ABS_NC": 6,
        "R_ARM_THM_MOVT_ABS": 6,
    },
    "by_symbol": {
        "lc3_band_lim": 4,
        "lc3_fft_twiddles_bf2": 2,
        "lc3_fft_twiddles_bf3": 2,
        "lc3_mdct_rot": 2,
        "lc3_mdct_win": 2,
    },
}


def validate_relocation_closure(
        records: list[dict[str, Any]], allowed_imports: set[str],
        table_reference_contract: dict[str, dict[str, int]] | None = None
        ) -> dict[str, Any]:
    allowed_sections = {".text", ".rodata", TABLE_SECTION}
    require(records and all(row["section"] in allowed_sections
                            for row in records),
            "relocation targets an unadmitted output section")
    table_initializers = [row for row in records
                          if row["section"] == TABLE_SECTION]
    require(len(table_initializers) == 78 and all(
        row["type"] == "R_ARM_ABS32" and
        row["symbol_section"] == ".rodata" and
        row["symbol"] == "" and not row["external"]
        for row in table_initializers),
        "immutable table initializer closure drift")
    offsets = [int(row["offset"]) for row in table_initializers]
    require(len(set(offsets)) == 78 and all(
        offset % 4 == 0 and 0 <= offset <= TABLE_BYTES - 4
        for offset in offsets), "immutable table relocation offsets drift")

    text_references = [row for row in records
                       if row["section"] == ".text" and
                       row["symbol_section"] == TABLE_SECTION]
    contract = (DEFAULT_TABLE_REFERENCE_CONTRACT if
                table_reference_contract is None else
                table_reference_contract)
    require(set(contract) == {"by_type", "by_symbol"} and
            all(isinstance(key, str) and isinstance(value, int) and value > 0
                for counts in contract.values()
                for key, value in counts.items()) and
            sum(contract["by_type"].values()) ==
            sum(contract["by_symbol"].values()),
            "invalid immutable table reference contract")
    require(Counter(row["type"] for row in text_references) ==
            Counter(contract["by_type"]),
            "immutable table code-reference closure drift")
    require(Counter(row["symbol"] for row in text_references) ==
            Counter(contract["by_symbol"]),
            "immutable table code-reference symbols drift")

    external = Counter(row["symbol"] for row in records if row["external"])
    require(set(external) == allowed_imports and
            all(count > 0 for count in external.values()),
            "retained runtime relocation closure drift")
    encoded = lambda rows: sha256_bytes(json.dumps(
        rows, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {
        "total": len(records),
        "by_type": dict(sorted(Counter(
            row["type"] for row in records).items())),
        "by_section": dict(sorted(Counter(
            row["section"] for row in records).items())),
        "external_by_symbol": dict(sorted(external.items())),
        "records_sha256": encoded(records),
        "table_initializers": {
            "count": 78,
            "type": "R_ARM_ABS32",
            "target_section": ".rodata",
            "offsets": sorted(offsets),
            "records_sha256": encoded(table_initializers),
        },
        "table_code_references": {
            "count": len(text_references),
            "by_type": dict(sorted(Counter(
                row["type"] for row in text_references).items())),
            "records_sha256": encoded(text_references),
        },
    }


def validate_policy_object(path: Path, *, builder: Any,
                           roots: list[str], allowed_imports: set[str],
                           table_readonly: bool,
                           table_reference_contract:
                           dict[str, dict[str, int]] | None = None) -> tuple[
                               dict[str, bytes], dict[str, Any]]:
    payload, sections = builder.parse_elf32(path)
    symbols = builder.parse_elf32_symbols(payload, sections)
    expected = {
        ".text": (SHT_PROGBITS, SHF_ALLOC | SHF_EXECINSTR, 16),
        ".rodata": (SHT_PROGBITS, SHF_ALLOC | SHF_MERGE, 16),
        TABLE_SECTION: (
            SHT_PROGBITS,
            SHF_ALLOC if table_readonly else SHF_ALLOC | SHF_WRITE,
            TABLE_ALIGNMENT,
        ),
    }
    artifacts: dict[str, bytes] = {}
    for name, (kind, flags, alignment) in expected.items():
        section = _section(sections, name)
        assert section is not None
        require(int(section["type"]) == kind and
                int(section["flags"]) == flags and
                int(section["alignment"]) == alignment and
                int(section["size"]) > 0,
                f"linked section contract changed: {name}")
        artifacts[name] = _section_bytes(payload, section)
    require(len(artifacts[TABLE_SECTION]) == TABLE_BYTES,
            "immutable table size drift")
    unexpected_allocated = [
        str(section["name"]) for section in sections
        if int(section["size"]) and int(section["flags"]) & SHF_ALLOC and
        str(section["name"]) not in expected
    ]
    require(not unexpected_allocated,
            f"unexpected allocated sections: {unexpected_allocated}")
    allocated_writable = [
        str(section["name"]) for section in sections
        if int(section["size"]) and int(section["flags"]) & SHF_ALLOC and
        int(section["flags"]) & SHF_WRITE
    ]
    require(allocated_writable == ([] if table_readonly else [TABLE_SECTION]),
            "allocated writable-section closure drift")

    undefined = sorted(
        str(symbol["name"]) for symbol in symbols
        if int(symbol["section_index"]) == 0 and str(symbol["name"])
    )
    require(set(undefined) == allowed_imports and
            len(undefined) == len(allowed_imports),
            "retained runtime imports drift")

    text = _section(sections, ".text")
    table = _section(sections, TABLE_SECTION)
    assert text is not None and table is not None
    text_index = int(text["index"])
    table_index = int(table["index"])
    root_records: dict[str, dict[str, int]] = {}
    for root in roots:
        matches = [symbol for symbol in symbols
                   if symbol["name"] == root and
                   int(symbol["binding"]) == STB_GLOBAL and
                   int(symbol["type"]) == STT_FUNC and
                   int(symbol["section_index"]) == text_index]
        require(len(matches) == 1, f"provider root ABI changed: {root}")
        root_records[root] = {
            "offset": int(matches[0]["value"]) & ~1,
            "size": int(matches[0]["size"]),
        }
    table_records: dict[str, dict[str, int]] = {}
    for name, (offset, size) in TABLE_SYMBOLS.items():
        matches = [symbol for symbol in symbols
                   if symbol["name"] == name and
                   int(symbol["binding"]) == STB_GLOBAL and
                   int(symbol["type"]) == STT_OBJECT and
                   int(symbol["section_index"]) == table_index]
        require(len(matches) == 1 and
                int(matches[0]["value"]) == offset and
                int(matches[0]["size"]) == size,
                f"immutable table symbol geometry drift: {name}")
        table_records[name] = {"offset": offset, "size": size}

    records = relocation_records(payload, sections, symbols)
    relocation_report = validate_relocation_closure(
        records, allowed_imports, table_reference_contract)
    global_functions = sorted(
        str(symbol["name"]) for symbol in symbols
        if int(symbol["binding"]) == STB_GLOBAL and
        int(symbol["type"]) == STT_FUNC and
        int(symbol["section_index"]) == text_index
    )
    return artifacts, {
        "roots": root_records,
        "retained_imports": undefined,
        "global_functions": global_functions,
        "global_function_count": len(global_functions),
        "table_symbols": table_records,
        "relocations": relocation_report,
        "allocated_writable_sections": allocated_writable,
    }


def apply_readonly_policy(pre_policy: Path, post_policy: Path, *,
                          builder: Any, roots: list[str],
                          allowed_imports: set[str], objcopy: str,
                          table_reference_contract:
                          dict[str, dict[str, int]] | None = None
                          ) -> tuple[dict[str, bytes], dict[str, Any]]:
    pre_artifacts, pre_report = validate_policy_object(
        pre_policy, builder=builder, roots=roots,
        allowed_imports=allowed_imports, table_readonly=False,
        table_reference_contract=table_reference_contract)
    builder._run([
        objcopy, "--set-section-flags",
        f"{TABLE_SECTION}=alloc,load,readonly,data,contents",
        str(pre_policy), str(post_policy),
    ])
    post_artifacts, post_report = validate_policy_object(
        post_policy, builder=builder, roots=roots,
        allowed_imports=allowed_imports, table_readonly=True,
        table_reference_contract=table_reference_contract)
    require(pre_artifacts == post_artifacts,
            "read-only conversion changed allocated payload bytes")
    for key in ("roots", "retained_imports", "global_functions",
                "global_function_count", "table_symbols", "relocations"):
        require(pre_report[key] == post_report[key],
                f"read-only conversion changed {key}")
    return post_artifacts, {
        "classification": "logically-immutable-relocated-pointer-tables",
        "conversion": "authenticated-post-link-SHF_WRITE-clear",
        "pre_policy_object": artifact_record(pre_policy.read_bytes()),
        "post_policy_object": artifact_record(post_policy.read_bytes()),
        "pre_policy_allocated_writable_sections": [TABLE_SECTION],
        "post_policy_allocated_writable_sections": [],
        "runtime_copy_bytes": 0,
        "runtime_writable_bytes": 0,
        "table_symbols": post_report["table_symbols"],
        "relocations": post_report["relocations"],
        "link": post_report,
    }


def qualification_layout(section_sizes: dict[str, int],
                         text_start: int) -> dict[str, Any]:
    require(set(section_sizes) == {"text", "rodata", "table_rodata"},
            "finalizer section-size set drift")
    text_start = align_up(text_start, 16)
    text_end = text_start + section_sizes["text"]
    rodata_start = align_up(text_end, 16)
    rodata_end = rodata_start + section_sizes["rodata"]
    table_start = align_up(rodata_end, TABLE_ALIGNMENT)
    table_end = table_start + section_sizes["table_rodata"]
    require(table_end <= UINT32_LIMIT and
            section_sizes["table_rodata"] == TABLE_BYTES,
            "qualification layout overflows or table size drifted")
    return {
        "text": {"start": text_start, "end_exclusive": text_end,
                 "size": section_sizes["text"], "alignment": 16},
        "rodata": {"start": rodata_start, "end_exclusive": rodata_end,
                   "size": section_sizes["rodata"], "alignment": 16},
        "table_rodata": {
            "start": table_start, "end_exclusive": table_end,
            "size": section_sizes["table_rodata"],
            "alignment": TABLE_ALIGNMENT,
        },
        "span": table_end - text_start,
        "synthetic": True,
        "production_placement": False,
    }


def validate_runtime_bindings(bindings: dict[str, int], *,
                              allowed_imports: set[str],
                              layout: dict[str, Any]) -> None:
    require(set(bindings) == allowed_imports,
            "finalizer runtime-symbol set drift")
    placed = [(int(row["start"]), int(row["end_exclusive"]))
              for name, row in layout.items()
              if name in {"text", "rodata", "table_rodata"}]
    text_start = int(layout["text"]["start"])
    for name, address in bindings.items():
        require(isinstance(address, int) and 1 <= address < UINT32_LIMIT and
                address & 1, f"{name}: runtime function must be a Thumb address")
        canonical = address & ~1
        require(all(not (start <= canonical < end) for start, end in placed),
                f"{name}: runtime binding overlaps specialized sections")
        require(abs(canonical - text_start) < (1 << 24),
                f"{name}: runtime binding exceeds Thumb branch reach")
    require(len(set(bindings.values())) == len(bindings),
            "runtime bindings must have unique qualification addresses")


def _final_linker_script(layout: dict[str, Any], roots: list[str]) -> str:
    return f"""/* Generated qualification layout; never a stock map. */
ENTRY({roots[2]})
SECTIONS
{{
  .text 0x{layout['text']['start']:08X} : {{ *(.text) }}
  .rodata 0x{layout['rodata']['start']:08X} : {{ *(.rodata) }}
  {TABLE_SECTION} 0x{layout['table_rodata']['start']:08X} :
      {{ *({TABLE_SECTION}) }}
  /DISCARD/ : {{ *(.comment) *(.note*) }}
}}
ASSERT(SIZEOF(.text) == {layout['text']['size']}, "text size drift")
ASSERT(SIZEOF(.rodata) == {layout['rodata']['size']}, "rodata size drift")
ASSERT(SIZEOF({TABLE_SECTION}) == {TABLE_BYTES}, "table size drift")
"""


def _validate_final_table(*, template: bytes, final_table: bytes,
                          table_relocations: list[dict[str, Any]],
                          rodata_start: int, rodata_size: int) -> None:
    require(len(template) == len(final_table) == TABLE_BYTES,
            "final table payload size drift")
    relocation_offsets = {int(row["offset"]) for row in table_relocations}
    require(len(relocation_offsets) == 78,
            "final table relocation offset set drift")
    for offset in range(0, TABLE_BYTES, 4):
        before = struct.unpack_from("<I", template, offset)[0]
        after = struct.unpack_from("<I", final_table, offset)[0]
        if offset in relocation_offsets:
            require(before % 4 == 0 and before < rodata_size,
                    "table relocation addend escapes rodata")
            require(after == rodata_start + before,
                    "final placer did not apply a table initializer relocation")
        else:
            require(before == after == 0,
                    "unrelocated table word changed or gained a pointer")


def finalize_xip(relocatable: Path, output_dir: Path, *, builder: Any,
                 roots: list[str], allowed_imports: set[str], lld: str,
                 layout: dict[str, Any], runtime_bindings: dict[str, int],
                 table_reference_contract:
                 dict[str, dict[str, int]] | None = None
                 ) -> dict[str, Any]:
    artifacts, source_report = validate_policy_object(
        relocatable, builder=builder, roots=roots,
        allowed_imports=allowed_imports, table_readonly=True,
        table_reference_contract=table_reference_contract)
    section_sizes = {
        "text": len(artifacts[".text"]),
        "rodata": len(artifacts[".rodata"]),
        "table_rodata": len(artifacts[TABLE_SECTION]),
    }
    expected_layout = qualification_layout(
        section_sizes, int(layout["text"]["start"]))
    require(layout == expected_layout,
            "finalizer layout is not exact, contiguous, and aligned")
    validate_runtime_bindings(runtime_bindings,
                              allowed_imports=allowed_imports, layout=layout)

    output_dir.mkdir(parents=True, exist_ok=True)
    final_elf = output_dir / "liblc3_encoder.qualification-final.elf"
    with tempfile.TemporaryDirectory(
            prefix="open-cfw-liblc3-finalizer-") as temporary:
        linker_script = Path(temporary) / "qualification-final.ld"
        linker_script.write_text(_final_linker_script(layout, roots),
                                 encoding="utf-8")
        builder._run([
            lld, "-m", "armelf", "--build-id=none", "--no-undefined",
            "-T", str(linker_script), "-o", str(final_elf), str(relocatable),
            *(f"--defsym={name}=0x{address:08x}"
              for name, address in sorted(runtime_bindings.items())),
        ])

    payload, sections = builder.parse_elf32(final_elf)
    symbols = builder.parse_elf32_symbols(payload, sections)
    final_artifacts: dict[str, bytes] = {}
    expected_sections = {
        ".text": ("text", SHF_ALLOC | SHF_EXECINSTR),
        ".rodata": ("rodata", SHF_ALLOC | SHF_MERGE),
        TABLE_SECTION: ("table_rodata", SHF_ALLOC),
    }
    for name, (layout_name, flags) in expected_sections.items():
        section = _section(sections, name)
        assert section is not None
        require(int(section["type"]) == SHT_PROGBITS and
                int(section["flags"]) == flags and
                int(section["address"]) == layout[layout_name]["start"] and
                int(section["size"]) == layout[layout_name]["size"],
                f"final section geometry drift: {name}")
        final_artifacts[name] = _section_bytes(payload, section)
    unexpected_allocated = [
        str(section["name"]) for section in sections
        if int(section["size"]) and int(section["flags"]) & SHF_ALLOC and
        str(section["name"]) not in expected_sections
    ]
    require(not unexpected_allocated,
            f"final ELF gained allocated sections: {unexpected_allocated}")
    require(not any(int(section["type"]) == SHT_REL and int(section["size"])
                    for section in sections),
            "final ELF retained unapplied relocations")
    require(not any(int(symbol["section_index"]) == 0 and
                    str(symbol["name"]) for symbol in symbols),
            "final ELF retained unresolved symbols")

    for name, address in runtime_bindings.items():
        matches = [symbol for symbol in symbols if symbol["name"] == name]
        require(len(matches) == 1 and
                int(matches[0]["section_index"]) == 0xFFF1 and
                int(matches[0]["value"]) == address,
                f"final runtime binding drift: {name}")
    table_start = int(layout["table_rodata"]["start"])
    for name, (offset, size) in TABLE_SYMBOLS.items():
        matches = [symbol for symbol in symbols if symbol["name"] == name]
        require(len(matches) == 1 and
                int(matches[0]["value"]) == table_start + offset and
                int(matches[0]["size"]) == size,
                f"final table symbol drift: {name}")

    # Parse the input again so symbol association stays visible and the
    # finalizer does not merely trust the earlier aggregate link report.
    source_payload, source_sections = builder.parse_elf32(relocatable)
    source_symbols = builder.parse_elf32_symbols(source_payload, source_sections)
    input_records = relocation_records(
        source_payload, source_sections, source_symbols)
    table_relocations = [row for row in input_records
                         if row["section"] == TABLE_SECTION]
    _validate_final_table(
        template=artifacts[TABLE_SECTION],
        final_table=final_artifacts[TABLE_SECTION],
        table_relocations=table_relocations,
        rodata_start=int(layout["rodata"]["start"]),
        rodata_size=int(layout["rodata"]["size"]),
    )

    # Only now may raw XIP section bytes be emitted.
    emitted: dict[str, dict[str, Any]] = {}
    for name, payload_bytes in (
            ("text", final_artifacts[".text"]),
            ("rodata", final_artifacts[".rodata"]),
            ("table_rodata", final_artifacts[TABLE_SECTION])):
        path = output_dir / f"liblc3_encoder.{name}.qualification-xip.bin"
        builder.atomic_write(path, payload_bytes)
        emitted[name] = artifact_record(payload_bytes)
    return {
        "mode": "synthetic-address-finalizer-qualification",
        "layout": layout,
        "runtime_bindings": dict(sorted(runtime_bindings.items())),
        "runtime_bindings_authenticated_for_stock": False,
        "production_placement": False,
        "service_audio_routed": False,
        "firmware_image_emitted": False,
        "final_elf": artifact_record(final_elf.read_bytes()),
        "xip_artifacts": emitted,
        "relocation_application": {
            "input_relocations": source_report["relocations"]["total"],
            "input_table_initializers": source_report["relocations"]
                ["table_initializers"]["count"],
            "input_table_code_references": source_report["relocations"]
                ["table_code_references"]["count"],
            "output_relocations": 0,
            "all_input_relocations_applied": True,
            "table_initializers_verified_word_for_word": True,
            "xip_emission_after_validation": True,
        },
    }
