#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the production-routed EM9305 reconstructible-tail overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = Path(__file__).resolve().parent
STOCK = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
RECORD_MODULE_DIR = ROOT / "components/em9305/source_image"
import sys
sys.path.insert(0, str(RECORD_MODULE_DIR))
from record_package import Record, build_package, parse_package  # noqa: E402

STOCK_IDENTITY = (
    211_948,
    "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9",
)
APP_ADDRESS = 0x00302400
APP_STOCK_END = 0x00335BC8
APP_SECTOR_END = 0x00336000
ARC_NOP = bytes.fromhex("e078")
FLAGS = (
    "-mcpu=em", "-Os", "-std=c99", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
)

# Section, entry address, complete entry allocation.  The emitted C wrapper is
# four bytes; the remaining allocation is deterministic ARCv2-EM NOP fill.
ENTRY_PATCHES = (
    (".tail_303e50", 0x00303E50, 12),
    (".tail_303e5c", 0x00303E5C, 10),
    (".tail_303f50", 0x00303F50, 10),
    (".tail_303f68", 0x00303F68, 10),
    (".tail_3047b0", 0x003047B0, 14),
    (".tail_3069b8", 0x003069B8, 10),
    (".tail_307c08", 0x00307C08, 14),
    (".tail_307dd8", 0x00307DD8, 14),
    (".tail_30f368", 0x0030F368, 10),
    (".tail_30f710", 0x0030F710, 16),
    (".tail_30f720", 0x0030F720, 14),
    (".tail_310480", 0x00310480, 12),
    (".tail_31048c", 0x0031048C, 10),
    (".tail_3108f4", 0x003108F4, 10),
    (".tail_311f84", 0x00311F84, 10),
    (".tail_3122f0", 0x003122F0, 10),
    (".tail_31369c", 0x0031369C, 14),
    (".tail_313760", 0x00313760, 10),
    (".tail_31b2f8", 0x0031B2F8, 4),
    (".tail_32cac4", 0x0032CAC4, 8),
    (".tail_32cacc", 0x0032CACC, 8),
    (".tail_32cad4", 0x0032CAD4, 8),
    (".tail_32cadc", 0x0032CADC, 6),
)
DIRECT_NOOPS = (
    (".noop_302d80", 0x00302D80, 2, 2),
    (".noop_304eb4", 0x00304EB4, 6, 6),
    (".noop_313778", 0x00313778, 2, 2),
    (".noop_3137f4", 0x003137F4, 6, 4),
)
META_ISLANDS = (
    (0x00302664, 822),
    (0x00332FC4, 158),
)
META_ENTRY_PATCHES = (
    (".meta_302664", 0x00302664, "open_cfw_em9305_metaware_memmove"),
    (".meta_302748", 0x00302748, "open_cfw_em9305_metaware_udiv64"),
    (".meta_302760", 0x00302760, "open_cfw_em9305_metaware_sdiv64"),
    (".meta_3027c8", 0x003027C8, "open_cfw_em9305_metaware_shift_left64"),
    (".meta_3027f4", 0x003027F4, "open_cfw_em9305_metaware_shift_right64"),
    (".meta_302820", 0x00302820, "open_cfw_em9305_metaware_stack_guard"),
    (".meta_332fc4", 0x00332FC4, "open_cfw_em9305_metaware_memcpy"),
    (".meta_33301c", 0x0033301C, "open_cfw_em9305_metaware_memset"),
)


class BuildError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: list[str], *, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        command, cwd=cwd, text=True, capture_output=True, check=False,
    )
    if result.returncode != 0:
        raise BuildError(
            f"command failed ({result.returncode}): {' '.join(command)}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result.stdout


def extract_section(objcopy: str, elf: Path, section: str, output: Path) -> bytes:
    run([objcopy, "-O", "binary", f"--only-section={section}", str(elf), str(output)])
    if not output.is_file():
        raise BuildError(f"section extraction produced no output: {section}")
    return output.read_bytes()


def build(
    *, gcc: str, nm: str, objcopy: str, objdump: str, readelf: str,
    output_dir: Path,
) -> dict:
    stock = STOCK.read_bytes()
    if (len(stock), digest(stock)) != STOCK_IDENTITY:
        raise BuildError("authenticated EM9305 stock package identity drift")
    parsed = parse_package(stock)
    if len(parsed.records) != 4:
        raise BuildError("EM9305 record count drift")
    application = parsed.records[3]
    if (
        application.address != APP_ADDRESS
        or application.address + len(application.payload) != APP_STOCK_END
    ):
        raise BuildError("EM9305 application record boundary drift")

    output_dir.mkdir(parents=True, exist_ok=True)
    source = SOURCE_DIR / "runtime_reconstructible_tail.c"
    entries = SOURCE_DIR / "runtime_reconstructible_tail_entries.c"
    meta_source = SOURCE_DIR / "runtime_metaware.c"
    meta_entries = SOURCE_DIR / "runtime_metaware_entries.c"
    linker = SOURCE_DIR / "reconstructible_tail.ld"
    object_path = output_dir / "runtime_reconstructible_tail.o"
    entries_path = output_dir / "runtime_reconstructible_tail_entries.o"
    meta_object_path = output_dir / "runtime_metaware.o"
    meta_entries_path = output_dir / "runtime_metaware_entries.o"
    elf = output_dir / "reconstructible_tail.elf"
    run([gcc, *FLAGS, "-c", str(source), "-o", str(object_path)])
    run([gcc, *FLAGS, "-c", str(entries), "-o", str(entries_path)])
    run([gcc, *FLAGS, "-c", str(meta_source), "-o", str(meta_object_path)])
    run([gcc, *FLAGS, "-c", str(meta_entries), "-o", str(meta_entries_path)])
    run([
        gcc, "-mcpu=em", "-nostdlib", "-Wl,--gc-sections",
        f"-Wl,-T,{linker}", str(object_path), str(entries_path),
        str(meta_object_path), str(meta_entries_path), "-o", str(elf),
    ])
    undefined = [line.split()[-1] for line in run([nm, "-u", str(elf)]).splitlines()
                 if line.split()]
    if undefined:
        raise BuildError(f"linked EM9305 tail has undefined symbols: {undefined}")
    section_text = run([readelf, "-SW", str(elf)])
    executable_sections = {
        match.group(1)
        for line in section_text.splitlines()
        if (match := re.match(
            r"^\s*\[\s*\d+\]\s+(\S+)\s+PROGBITS\b.*\bAX\b", line
        ))
    }
    expected_sections = {
        *(section for section, _address, _allocation in ENTRY_PATCHES),
        *(section for section, _address, _allocation, _source in DIRECT_NOOPS),
        *(section for section, _address, _target in META_ENTRY_PATCHES),
        ".tail_impl", ".meta_impl",
    }
    if executable_sections != expected_sections:
        raise BuildError(
            "unexpected allocatable executable sections: "
            f"{sorted(executable_sections ^ expected_sections)}"
        )
    disassembly = run([objdump, "-d", str(elf)])
    for section, _address, _allocation in ENTRY_PATCHES:
        suffix = section.removeprefix(".tail_")
        marker = f"Disassembly of section {section}:"
        block = disassembly.split(marker, 1)[-1].split(
            "Disassembly of section", 1
        )[0]
        if marker not in disassembly or f"_{suffix}_impl>" not in block:
            raise BuildError(f"{section}: branch target is not its C implementation")
    for section, _address, target in META_ENTRY_PATCHES:
        marker = f"Disassembly of section {section}:"
        block = disassembly.split(marker, 1)[-1].split(
            "Disassembly of section", 1
        )[0]
        if marker not in disassembly or f"<{target}>" not in block:
            raise BuildError(f"{section}: branch target is not {target}")

    payload = bytearray(application.payload)
    section_rows = []
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-tail-sections-") as raw:
        temporary = Path(raw)
        for index, (section, address, allocation) in enumerate(ENTRY_PATCHES):
            body = extract_section(objcopy, elf, section, temporary / f"entry-{index}.bin")
            if len(body) != 4:
                raise BuildError(f"{section}: expected four-byte C tail branch, got {len(body)}")
            replacement = body + ARC_NOP * ((allocation - len(body)) // 2)
            if len(replacement) != allocation:
                raise BuildError(f"{section}: invalid NOP-fill allocation")
            offset = address - APP_ADDRESS
            payload[offset:offset + allocation] = replacement
            section_rows.append({
                "section": section,
                "address": address,
                "allocation_bytes": allocation,
                "source_bytes": len(body),
                "generated_padding_bytes": allocation - len(body),
                "sha256": digest(replacement),
            })
        noop_rows = []
        for index, (section, address, allocation, source_size) in enumerate(DIRECT_NOOPS):
            raw_body = extract_section(
                objcopy, elf, section, temporary / f"noop-{index}.bin"
            )
            if len(raw_body) != ((allocation + 3) // 4) * 4:
                raise BuildError(
                    f"{section}: unexpected ARC section size {len(raw_body)}"
                )
            body = raw_body[:allocation]
            offset = address - APP_ADDRESS
            payload[offset:offset + len(body)] = body
            noop_rows.append({
                "section": section,
                "address": address,
                "allocation_bytes": allocation,
                "source_bytes": source_size,
                "generated_padding_bytes": allocation - source_size,
                "sha256": digest(body),
            })
        implementation = extract_section(
            objcopy, elf, ".tail_impl", temporary / "implementation.bin"
        )
        meta_replacements = {
            address: bytearray(ARC_NOP * (size // 2))
            for address, size in META_ISLANDS
        }
        meta_rows = []
        for index, (section, address, target) in enumerate(META_ENTRY_PATCHES):
            body = extract_section(
                objcopy, elf, section, temporary / f"meta-entry-{index}.bin"
            )
            if len(body) != 4:
                raise BuildError(f"{section}: expected four-byte C branch")
            for island_address, replacement in meta_replacements.items():
                relative = address - island_address
                if 0 <= relative <= len(replacement) - len(body):
                    replacement[relative:relative + len(body)] = body
                    break
            else:
                raise BuildError(f"{section}: entry is outside MetaWare islands")
            meta_rows.append({
                "section": section,
                "address": address,
                "target": target,
                "source_bytes": len(body),
                "sha256": digest(body),
            })
        for island_address, replacement in meta_replacements.items():
            offset = island_address - APP_ADDRESS
            payload[offset:offset + len(replacement)] = replacement
        meta_implementation = extract_section(
            objcopy, elf, ".meta_impl", temporary / "meta-implementation.bin"
        )

    if not implementation or not meta_implementation:
        raise BuildError("EM9305 source implementation section is empty")
    if len(implementation) + len(meta_implementation) > APP_SECTOR_END - APP_STOCK_END:
        raise BuildError("EM9305 implementation cave exceeds authenticated sector tail")
    if len(payload) != APP_STOCK_END - APP_ADDRESS:
        raise BuildError("entry patching changed the stock application length")
    payload.extend(implementation)
    payload.extend(meta_implementation)
    if APP_ADDRESS + len(payload) > APP_SECTOR_END:
        raise BuildError("EM9305 source extension crosses the current flash sector")

    records = list(parsed.records)
    records[3] = Record(application.address, bytes(payload))
    provider = build_package(records, parsed.erase_sectors)
    reparsed = parse_package(provider)
    if reparsed.records[:3] != parsed.records[:3]:
        raise BuildError("EM9305 non-application records changed")
    provider_path = output_dir / "firmware_ble_em9305.bin"
    provider_path.write_bytes(provider)
    source_bytes = (
        sum(row["source_bytes"] for row in section_rows)
        + sum(row["source_bytes"] for row in noop_rows)
        + len(implementation)
        + sum(row["source_bytes"] for row in meta_rows)
        + len(meta_implementation)
    )
    generated_bytes = (
        sum(row["generated_padding_bytes"] for row in section_rows)
        + sum(row["generated_padding_bytes"] for row in noop_rows)
        + sum(size for _address, size in META_ISLANDS)
        - sum(row["source_bytes"] for row in meta_rows)
        + reparsed.metadata_size
    )
    candidate_bytes = 0
    retained_bytes = len(provider) - source_bytes - generated_bytes - candidate_bytes
    report = {
        "schema_version": 1,
        "status": "em9305-runtime-production-routed",
        "target": "ARCv2 EM",
        "compiler": run([gcc, "--version"]).splitlines()[0],
        "flags": list(FLAGS),
        "provider": {
            "path": str(provider_path.relative_to(ROOT)),
            "size": len(provider),
            "sha256": digest(provider),
        },
        "application": {
            "target_address": APP_ADDRESS,
            "stock_end_exclusive": APP_STOCK_END,
            "source_end_exclusive": APP_ADDRESS + len(payload),
            "sector_end_exclusive": APP_SECTOR_END,
            "implementation_address": APP_STOCK_END,
            "implementation_bytes": len(implementation),
            "implementation_sha256": digest(implementation),
            "metaware_implementation_address": APP_STOCK_END + len(implementation),
            "metaware_implementation_bytes": len(meta_implementation),
            "metaware_implementation_sha256": digest(meta_implementation),
        },
        "accounting": {
            "production_source_bytes": source_bytes,
            "generated_or_reconstructible_bytes": generated_bytes,
            "typed_retained_or_external_bytes": retained_bytes,
            "candidate_source_not_routed_bytes": candidate_bytes,
            "unclassified_bytes": 0,
        },
        "entry_patches": section_rows,
        "direct_c_noops": noop_rows,
        "metaware_entry_patches": meta_rows,
        "metaware_interior_entries_replaced_with_generated_nops": [
            0x003026A8, 0x00302844,
        ],
        "undefined_symbols": [],
        "production_routed": True,
        "hardware_operations": [],
        "hardware_validation": "blocked by unavailable physical evidence",
    }
    report_path = output_dir / "build-report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcc", default=os.environ.get("OPENCFW_ARC_GCC", "arc-linux-gnu-gcc"))
    parser.add_argument("--nm", default=os.environ.get("OPENCFW_ARC_NM", "arc-linux-gnu-nm"))
    parser.add_argument("--objcopy", default=os.environ.get("OPENCFW_ARC_OBJCOPY", "arc-linux-gnu-objcopy"))
    parser.add_argument("--objdump", default=os.environ.get("OPENCFW_ARC_OBJDUMP", "arc-linux-gnu-objdump"))
    parser.add_argument("--readelf", default=os.environ.get("OPENCFW_ARC_READELF", "arc-linux-gnu-readelf"))
    parser.add_argument("--output-dir", type=Path, default=SOURCE_DIR / "build")
    args = parser.parse_args()
    report = build(
        gcc=args.gcc, nm=args.nm, objcopy=args.objcopy,
        objdump=args.objdump, readelf=args.readelf,
        output_dir=args.output_dir.resolve(),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, OSError, ValueError) as error:
        raise SystemExit(f"EM9305 reconstructible-tail build failed: {error}") from error
