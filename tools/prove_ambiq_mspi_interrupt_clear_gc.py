#!/usr/bin/env python3
"""Compile and section-GC the authenticated AmbiqSuite MSPI translation unit.

This proof is deliberately isolated: it writes only to a temporary directory,
does not touch a device, and does not alter the supplied SDK tree.  The full
unmodified am_hal_mspi.c is compiled, while only
am_hal_mspi_interrupt_clear is retained by the final link.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from typing import Any


EXPECTED_SOURCE_SHA256 = (
    "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"
)
LEAF = "am_hal_mspi_interrupt_clear"
LEAF_SECTION = f".text.{LEAF}"
MAGIC_WORD = 0x01BEBEBE
MSPI_BASE = 0x40060000


class ProofError(RuntimeError):
    """Raised when a compile/link invariant is not satisfied."""


def run(command: list[str], *, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if completed.returncode:
        rendered = " ".join(command)
        raise ProofError(
            f"command failed ({completed.returncode}): {rendered}\n"
            f"{completed.stdout}{completed.stderr}"
        )
    return completed.stdout + completed.stderr


def c_string(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def c_string_at(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("utf-8", errors="replace")


def read_elf32(path: Path) -> dict[str, Any]:
    """Read the ELF32 section and symbol facts needed by this proof."""

    data = path.read_bytes()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise ProofError(f"{path}: expected a little-endian ELF32 file")
    (
        _e_type,
        machine,
        _e_version,
        entry,
        _e_phoff,
        section_offset,
        _e_flags,
        _e_ehsize,
        _e_phentsize,
        _e_phnum,
        section_entry_size,
        section_count,
        section_names_index,
    ) = struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
    if machine != 40:
        raise ProofError(f"{path}: expected EM_ARM (40), got {machine}")
    if section_entry_size != 40:
        raise ProofError(
            f"{path}: expected 40-byte ELF32 section headers, "
            f"got {section_entry_size}"
        )

    sections: list[dict[str, Any]] = []
    for index in range(section_count):
        values = struct.unpack_from(
            "<IIIIIIIIII",
            data,
            section_offset + index * section_entry_size,
        )
        sections.append(
            {
                "index": index,
                "name_offset": values[0],
                "type": values[1],
                "flags": values[2],
                "address": values[3],
                "offset": values[4],
                "size": values[5],
                "link": values[6],
                "info": values[7],
                "alignment": values[8],
                "entry_size": values[9],
            }
        )
    section_names = sections[section_names_index]
    names = data[
        section_names["offset"] : section_names["offset"] + section_names["size"]
    ]
    for section in sections:
        section["name"] = c_string_at(names, section["name_offset"])

    symbols: list[dict[str, Any]] = []
    for section in sections:
        if section["type"] != 2:  # SHT_SYMTAB
            continue
        if section["entry_size"] != 16:
            raise ProofError(f"{path}: unexpected ELF32 symbol entry size")
        string_section = sections[section["link"]]
        strings = data[
            string_section["offset"] : string_section["offset"]
            + string_section["size"]
        ]
        for offset in range(
            section["offset"],
            section["offset"] + section["size"],
            section["entry_size"],
        ):
            name_offset, value, size, info, other, section_index = struct.unpack_from(
                "<IIIBBH",
                data,
                offset,
            )
            symbols.append(
                {
                    "name": c_string_at(strings, name_offset),
                    "value": value,
                    "size": size,
                    "binding": info >> 4,
                    "type": info & 0x0F,
                    "visibility": other & 0x03,
                    "section_index": section_index,
                }
            )

    return {
        "entry": entry,
        "sections": sections,
        "symbols": symbols,
        "data": data,
    }


def section(elf: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [item for item in elf["sections"] if item["name"] == name]
    if len(matches) != 1:
        raise ProofError(f"expected exactly one {name!r} section")
    return matches[0]


def section_data(elf: dict[str, Any], item: dict[str, Any]) -> bytes:
    start = item["offset"]
    return elf["data"][start : start + item["size"]]


def find_tool(explicit: str | None, candidates: tuple[str, ...]) -> str:
    if explicit:
        return explicit
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise ProofError(f"could not find any of: {', '.join(candidates)}")


def compiler_flags(sdk_root: Path, cmsis_core: Path) -> list[str]:
    return [
        "--target=arm-none-eabi",
        "-mcpu=cortex-m55",
        "-mthumb",
        "-Oz",
        "-ffreestanding",
        "-fno-builtin",
        "-ffunction-sections",
        "-fdata-sections",
        "-Wno-unused-function",
        "-I",
        str(sdk_root / "mcu" / "apollo510"),
        "-I",
        str(sdk_root / "mcu" / "apollo510" / "hal"),
        "-I",
        str(sdk_root / "CMSIS" / "AmbiqMicro" / "Include"),
        "-I",
        str(cmsis_core),
    ]


def run_proof(
    *,
    sdk_root: Path,
    cmsis_core: Path,
    clang: str,
    lld: str,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    source = sdk_root / "mcu" / "apollo510" / "hal" / "mcu" / "am_hal_mspi.c"
    source_data = source.read_bytes()
    source_sha256 = hashlib.sha256(source_data).hexdigest()
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise ProofError(
            f"am_hal_mspi.c SHA-256 drift: {source_sha256} != "
            f"{EXPECTED_SOURCE_SHA256}"
        )

    flags = compiler_flags(sdk_root, cmsis_core)
    with tempfile.TemporaryDirectory(prefix="openCFW-mspi-gc-") as directory:
        temporary = Path(directory)
        obj = temporary / "am_hal_mspi.o"
        probe_source = temporary / "abi_probe.c"
        probe_obj = temporary / "abi_probe.o"
        linked = temporary / "interrupt_clear.elf"

        run([clang, *flags, "-c", str(source), "-o", str(obj)], env=env)

        object_elf = read_elf32(obj)
        leaf_section = section(object_elf, LEAF_SECTION)
        leaf_bytes = section_data(object_elf, leaf_section)
        if struct.pack("<I", MAGIC_WORD) not in leaf_bytes:
            raise ProofError("compiled leaf omitted initialized-handle validation")
        if struct.pack("<I", MSPI_BASE) not in leaf_bytes:
            raise ProofError("compiled leaf omitted the Apollo510 MSPI base")
        relocation_names = {
            item["name"]
            for item in object_elf["sections"]
            if item["name"].startswith((".rel", ".rela"))
        }
        if f".rel{LEAF_SECTION}" in relocation_names:
            raise ProofError("compiled leaf has an unexpected text relocation")
        if f".rela{LEAF_SECTION}" in relocation_names:
            raise ProofError("compiled leaf has an unexpected text relocation")

        probe_source.write_text(
            '#include <stddef.h>\n'
            f'#include "{c_string(source)}"\n'
            '_Static_assert(sizeof(am_hal_handle_prefix_t) == 4, '
            '"handle prefix size");\n'
            '_Static_assert(offsetof(am_hal_mspi_state_t, prefix) == 0, '
            '"handle prefix offset");\n'
            '_Static_assert(offsetof(am_hal_mspi_state_t, ui32Module) == 4, '
            '"MSPI module offset");\n'
            '_Static_assert(offsetof(MSPI0_Type, INTSTAT) == 0x204, '
            '"INTSTAT offset");\n'
            '_Static_assert(offsetof(MSPI0_Type, INTCLR) == 0x208, '
            '"INTCLR offset");\n'
            '_Static_assert(MSPI0_BASE == 0x40060000UL, "MSPI0 base");\n'
            '_Static_assert(MSPI1_BASE - MSPI0_BASE == 0x1000UL, '
            '"MSPI stride");\n',
            encoding="utf-8",
        )
        run([clang, *flags, "-c", str(probe_source), "-o", str(probe_obj)], env=env)

        linker_command = [lld]
        if Path(lld).name == "lld":
            linker_command.extend(["-flavor", "gnu"])
        linker_command.extend(
            [
                "--gc-sections",
                "--entry",
                LEAF,
                "-Ttext=0x10000",
                str(obj),
                "-o",
                str(linked),
            ]
        )
        run(linker_command, env=env)

        linked_elf = read_elf32(linked)
        text_section = section(linked_elf, ".text")
        undefined = sorted(
            {
                item["name"]
                for item in linked_elf["symbols"]
                if item["name"] and item["section_index"] == 0
            }
        )
        if undefined:
            raise ProofError(f"linked leaf retains undefined symbols: {undefined}")
        leaf_symbols = [
            item for item in linked_elf["symbols"] if item["name"] == LEAF
        ]
        if len(leaf_symbols) != 1:
            raise ProofError("linked ELF does not contain exactly one leaf symbol")
        linked_leaf = leaf_symbols[0]
        if linked_leaf["size"] != leaf_section["size"]:
            raise ProofError("linked .text contains more than the retained leaf")
        if text_section["size"] != leaf_section["size"]:
            raise ProofError("linked .text contains more than the retained leaf")
        linked_section_names = {item["name"] for item in linked_elf["sections"]}
        linked_symbol_names = {
            item["name"] for item in linked_elf["symbols"] if item["name"]
        }
        linked_global_symbols = sorted(
            {
                item["name"]
                for item in linked_elf["symbols"]
                if item["name"]
                and item["binding"] != 0
                and item["section_index"] != 0
            }
        )
        if linked_global_symbols != [LEAF]:
            raise ProofError(
                "linked ELF retained unexpected global symbols: "
                f"{linked_global_symbols}"
            )
        if ".bss.g_MSPIState" in linked_section_names:
            raise ProofError("private MSPI state survived section GC")
        if "g_MSPIState" in linked_symbol_names:
            raise ProofError("private MSPI state symbol survived section GC")

        object_undefined = sorted(
            {
                item["name"]
                for item in object_elf["symbols"]
                if item["name"] and item["section_index"] == 0
            }
        )
        compiler_version = run([clang, "--version"], env=env).splitlines()[0]
        linker_version = run(
            [lld, *(["-flavor", "gnu"] if Path(lld).name == "lld" else []), "--version"],
            env=env,
        ).splitlines()[0]
        return {
            "status": "ok",
            "read_only": True,
            "source": {
                "path": str(source),
                "sha256": source_sha256,
            },
            "toolchain": {
                "compiler": compiler_version,
                "linker": linker_version,
                "target": "arm-none-eabi",
                "cpu": "cortex-m55",
                "optimization": "-Oz",
            },
            "abi_probe": {
                "handle_prefix_size": 4,
                "handle_prefix_offset": 0,
                "module_offset": 4,
                "mspi0_base": MSPI_BASE,
                "module_stride": 0x1000,
                "intstat_offset": 0x204,
                "intclr_offset": 0x208,
            },
            "object": {
                "leaf_section": LEAF_SECTION,
                "leaf_size": leaf_section["size"],
                "leaf_text_relocations": 0,
                "undefined_symbols_in_full_translation_unit": object_undefined,
                "undefined_symbol_count": len(object_undefined),
                "private_state_size": section(
                    object_elf,
                    ".bss.g_MSPIState",
                )["size"],
            },
            "linked": {
                "entry": linked_elf["entry"],
                "text_size": text_section["size"],
                "leaf_symbol_size": linked_leaf["size"],
                "undefined_symbols": undefined,
                "private_state_retained": False,
                "global_defined_symbols": linked_global_symbols,
            },
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sdk-root",
        type=Path,
        required=True,
        help="AmbiqSuite root containing mcu/apollo510 and CMSIS/AmbiqMicro",
    )
    parser.add_argument(
        "--cmsis-core",
        type=Path,
        required=True,
        help="CMSIS/ARM/Include directory containing core_cm55.h",
    )
    parser.add_argument("--clang", help="Clang executable (default: PATH)")
    parser.add_argument("--lld", help="ld.lld or lld executable (default: PATH)")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run_proof(
            sdk_root=args.sdk_root.resolve(),
            cmsis_core=args.cmsis_core.resolve(),
            clang=find_tool(args.clang, ("clang",)),
            lld=find_tool(args.lld, ("ld.lld", "lld")),
        )
    except (OSError, ProofError) as error:
        raise SystemExit(f"error: {error}") from error

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "authenticated full-TU section-GC proof: "
            f"{result['linked']['text_size']} bytes, "
            f"{len(result['linked']['undefined_symbols'])} unresolved, "
            "private state discarded"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
