#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Link the generated transparent codebase into an Apollo main firmware image.

Every byte of the output comes from a compiled translation unit in the
generated tree: recovered code where a unit compiled, declared data arrays
where the region is not code, and an explicit trap where neither holds.  No
span is copied forward from the vendor payload without a source unit behind it.

The stock address map is preserved.  Recovered code is full of absolute
references -- `DAT_004452c8` *is* the address 0x004452C8 -- so relocating
functions would silently invalidate every one of them.  A function whose
compiled form fits its stock envelope is placed there; one that does not fit
gets a trap, and the overflow is reported rather than papered over.

Usage:
    tools/build_transparent_image.py --source build/transparent/source \\
        --database build/transparent --output build/transparent/image
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import struct
import subprocess
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

#: Relocations clang emits for this codebase.  Anything else is refused rather
#: than guessed at.
R_ARM_ABS32 = 2
R_ARM_THM_CALL = 10
R_ARM_THM_JUMP24 = 30
R_ARM_PREL31 = 42
R_ARM_THM_MOVW_ABS_NC = 47
R_ARM_THM_MOVT_ABS = 48
SUPPORTED_RELOCATIONS = {
    R_ARM_ABS32,
    R_ARM_THM_CALL,
    R_ARM_THM_JUMP24,
    R_ARM_THM_MOVW_ABS_NC,
    R_ARM_THM_MOVT_ABS,
}

#: `BKPT #0`.  A trap must not fall through into whatever follows it.
THUMB_BREAKPOINT = b"\x00\xbe"

SHF_ALLOC = 0x2
SHT_RELA = 4
SHT_REL = 9
SHT_SYMTAB = 2
STT_SECTION = 3


class ImageError(RuntimeError):
    pass


class Elf32:
    """Just enough ELF32 little-endian to place sections and fix references."""

    def __init__(self, data: bytes, origin: str) -> None:
        if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
            raise ImageError(f"{origin} is not a little-endian ELF32 object")
        self.data = data
        self.origin = origin
        section_offset, = struct.unpack_from("<I", data, 0x20)
        entry_size, count, string_index = struct.unpack_from("<HHH", data, 0x2E)
        self.sections: list[dict[str, Any]] = []
        for index in range(count):
            base = section_offset + index * entry_size
            fields = struct.unpack_from("<10I", data, base)
            self.sections.append({
                "index": index,
                "name_offset": fields[0],
                "type": fields[1],
                "flags": fields[2],
                "address": fields[3],
                "offset": fields[4],
                "size": fields[5],
                "link": fields[6],
                "info": fields[7],
                "align": fields[8] or 1,
                "entsize": fields[9],
            })
        strings = self.sections[string_index]
        for section in self.sections:
            section["name"] = self._string(strings["offset"], section["name_offset"])

    def _string(self, table_offset: int, offset: int) -> str:
        start = table_offset + offset
        end = self.data.index(b"\0", start)
        return self.data[start:end].decode("utf-8", "replace")

    def contents(self, section: dict[str, Any]) -> bytes:
        if section["type"] == 8:  # SHT_NOBITS
            return b"\0" * section["size"]
        return self.data[section["offset"]:section["offset"] + section["size"]]

    def symbols(self) -> list[dict[str, Any]]:
        table = next(
            (s for s in self.sections if s["type"] == SHT_SYMTAB), None
        )
        if table is None:
            return []
        strings = self.sections[table["link"]]
        result = []
        for position in range(0, table["size"], 16):
            base = table["offset"] + position
            name_offset, value, size, info, other, shndx = struct.unpack_from(
                "<IIIBBH", self.data, base
            )
            result.append({
                "name": self._string(strings["offset"], name_offset),
                "value": value,
                "size": size,
                "type": info & 0xF,
                "section": shndx,
            })
        return result

    def relocations(self, target_index: int) -> list[dict[str, int]]:
        result = []
        for section in self.sections:
            if section["type"] not in (SHT_REL, SHT_RELA):
                continue
            if section["info"] != target_index:
                continue
            stride = 12 if section["type"] == SHT_RELA else 8
            for position in range(0, section["size"], stride):
                base = section["offset"] + position
                offset, info = struct.unpack_from("<II", self.data, base)
                addend = 0
                if section["type"] == SHT_RELA:
                    addend, = struct.unpack_from("<i", self.data, base + 8)
                result.append({
                    "offset": offset,
                    "symbol": info >> 8,
                    "type": info & 0xFF,
                    "addend": addend,
                })
        return result


def encode_thumb_branch(site: int, target: int, link: bool) -> bytes:
    """Encode a Thumb-2 BL/B.W from `site` to `target`."""
    delta = target - (site + 4)
    if delta % 2:
        raise ImageError(f"unaligned branch displacement {delta:#x}")
    if not -(1 << 24) <= delta < (1 << 24):
        raise ImageError(f"branch displacement {delta:#x} out of Thumb range")
    value = delta >> 1
    sign = (value >> 23) & 1
    imm10 = (value >> 11) & 0x3FF
    imm11 = value & 0x7FF
    j1 = ((value >> 22) & 1) ^ sign ^ 1
    j2 = ((value >> 21) & 1) ^ sign ^ 1
    first = 0xF000 | (sign << 10) | imm10
    second = (0xD000 if link else 0x9000) | (j1 << 13) | (j2 << 11) | imm11
    return struct.pack("<HH", first, second)


def decode_thumb_branch_addend(instruction: bytes) -> int:
    first, second = struct.unpack("<HH", instruction)
    sign = (first >> 10) & 1
    imm10 = first & 0x3FF
    imm11 = second & 0x7FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    upper = ((j1 ^ sign ^ 1) << 22) | ((j2 ^ sign ^ 1) << 21)
    value = (sign << 23) | upper | (imm10 << 11) | imm11
    if sign:
        value -= 1 << 24
    return value << 1


def encode_thumb_movw_movt(instruction: bytes, value: int) -> bytes:
    """Patch a 16-bit immediate into a Thumb-2 MOVW/MOVT, keeping the opcode."""
    first, second = struct.unpack("<HH", instruction)
    immediate = value & 0xFFFF
    imm4 = (immediate >> 12) & 0xF
    i = (immediate >> 11) & 1
    imm3 = (immediate >> 8) & 0x7
    imm8 = immediate & 0xFF
    first = (first & 0xFBF0) | (i << 10) | imm4
    second = (second & 0x8F00) | (imm3 << 12) | imm8
    return struct.pack("<HH", first, second)


def decode_thumb_movw_movt_addend(instruction: bytes) -> int:
    first, second = struct.unpack("<HH", instruction)
    imm4 = first & 0xF
    i = (first >> 10) & 1
    imm3 = (second >> 12) & 0x7
    imm8 = second & 0xFF
    return (imm4 << 12) | (i << 11) | (imm3 << 8) | imm8


#: The stock image was built by IAR at high size optimization.  Recompiled
#: decompiler output is routinely a few bytes larger, which is the difference
#: between fitting a function's stock envelope and not.  When the default does
#: not fit, the unit is rebuilt under these alternatives and the smallest
#: result that fits wins.  Every variant is recorded, so a placed function
#: always states which one produced it.
SIZE_VARIANTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Oz", ()),
    ("Os", ("-Os",)),
    ("O1", ("-O1",)),
    ("Oz-no-jump-tables", ("-fno-jump-tables",)),
    ("Oz-no-outline", ("-mno-outline",)),
    ("O2", ("-O2",)),
)


def compile_source(
    clang: str,
    source: Path,
    object_path: Path,
    include: Path,
    extra: tuple[str, ...] = (),
) -> str:
    from generate_transparent_source import COMPILE_FLAGS  # noqa: PLC0415

    completed = subprocess.run(
        [
            clang,
            *COMPILE_FLAGS,
            *extra,
            "-I",
            str(include),
            "-c",
            str(source),
            "-o",
            str(object_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return "" if completed.returncode == 0 else completed.stderr


def placeable_sections(elf: Elf32) -> list[dict[str, Any]]:
    """Alloc sections that belong in the image, in a stable order.

    Unwind tables are dropped: the stock image carries none for these
    functions, and they are not reachable code.
    """
    keep = []
    for section in elf.sections:
        if not section["flags"] & SHF_ALLOC:
            continue
        if section["name"].startswith(".ARM.exidx") or section["name"].startswith(
            ".ARM.extab"
        ):
            continue
        if section["size"] == 0:
            continue
        keep.append(section)
    keep.sort(key=lambda section: (not section["name"].startswith(".text"), section["name"]))
    return keep


def place_unit(
    elf: Elf32,
    envelope_start: int,
    envelope_size: int,
    symbol_addresses: dict[str, int],
) -> tuple[bytes, dict[str, Any]]:
    """Lay a unit's sections into its envelope and fix every reference."""
    sections = placeable_sections(elf)
    if not sections:
        raise ImageError("unit has no allocatable content")

    placement: dict[int, int] = {}
    cursor = envelope_start
    for position, section in enumerate(sections):
        # The function must begin exactly at its stock entry point.  Thumb code
        # is 2-byte aligned and stock functions routinely start two bytes off a
        # word boundary, so honouring the object's 4-byte .text alignment here
        # would both waste the gap and move the entry.  Only trailing sections
        # get aligned.
        if position:
            align = max(section["align"], 1)
            cursor = (cursor + align - 1) // align * align
        placement[section["index"]] = cursor
        cursor += section["size"]
    total = cursor - envelope_start
    if total > envelope_size:
        raise ImageError(f"compiled size {total} exceeds envelope {envelope_size}")

    buffer = bytearray(b"\0" * total)
    for section in sections:
        start = placement[section["index"]] - envelope_start
        buffer[start:start + section["size"]] = elf.contents(section)

    symbols = elf.symbols()
    applied = 0
    for section in sections:
        for relocation in elf.relocations(section["index"]):
            kind = relocation["type"]
            if kind == R_ARM_PREL31:
                continue
            if kind not in SUPPORTED_RELOCATIONS:
                raise ImageError(f"unsupported relocation type {kind}")
            symbol = symbols[relocation["symbol"]]
            if symbol["type"] == STT_SECTION:
                if symbol["section"] not in placement:
                    raise ImageError("reference to a discarded section")
                target = placement[symbol["section"]] + symbol["value"]
            elif symbol["section"] == 0:
                address = symbol_addresses.get(symbol["name"])
                if address is None:
                    raise ImageError(f"undefined symbol {symbol['name']}")
                target = address
            else:
                if symbol["section"] not in placement:
                    raise ImageError("reference into a discarded section")
                target = placement[symbol["section"]] + symbol["value"]

            site = placement[section["index"]] + relocation["offset"]
            local = site - envelope_start
            if kind == R_ARM_ABS32:
                addend = int.from_bytes(buffer[local:local + 4], "little")
                buffer[local:local + 4] = ((target + addend) & 0xFFFFFFFF).to_bytes(
                    4, "little"
                )
            elif kind in (R_ARM_THM_MOVW_ABS_NC, R_ARM_THM_MOVT_ABS):
                instruction = bytes(buffer[local:local + 4])
                addend = decode_thumb_movw_movt_addend(instruction)
                # MOVW carries the low half of the address and MOVT the high
                # half; the addend a REL relocation leaves behind is already
                # the half-word the compiler put there.
                full = target + (addend if kind == R_ARM_THM_MOVW_ABS_NC else addend << 16)
                half = full & 0xFFFF if kind == R_ARM_THM_MOVW_ABS_NC else (full >> 16) & 0xFFFF
                buffer[local:local + 4] = encode_thumb_movw_movt(instruction, half)
            else:
                addend = decode_thumb_branch_addend(bytes(buffer[local:local + 4]))
                # Symbols carry the Thumb bit because that is what a function
                # pointer must hold, but a BL/B.W displacement is computed
                # against the even instruction address -- the bit is implied by
                # the instruction, not encoded in the offset.
                buffer[local:local + 4] = encode_thumb_branch(
                    site, (target & ~1) + addend, link=(kind == R_ARM_THM_CALL)
                )
            applied += 1

    report = {
        "placed_bytes": total,
        "sections": [section["name"] for section in sections],
        "relocations": applied,
    }
    return bytes(buffer), report


def bucket_overflow(overflow: int) -> str:
    """Group an envelope overshoot into a band worth reasoning about."""
    for limit in (2, 4, 8, 16, 32, 64, 128, 256):
        if overflow <= limit:
            return f"<= {limit} bytes over"
    return "> 256 bytes over"


def trap_bytes(size: int) -> bytes:
    """A stub that halts instead of running unrecovered behavior."""
    if size < 2:
        return b"\0" * size
    return THUMB_BREAKPOINT + b"\0" * (size - 2)


def build(
    source_dir: Path,
    database_dir: Path,
    output_dir: Path,
    clang: str,
    jobs: int,
    reuse_objects: bool = False,
) -> dict[str, Any]:
    manifest = json.loads((source_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    regions = json.loads((database_dir / "region-map.json").read_text(encoding="utf-8"))
    database = json.loads((database_dir / "function-db.json").read_text(encoding="utf-8"))
    image_meta = manifest["image"]
    load_base = image_meta["load_base"]
    image_size = image_meta["size"]

    output_dir.mkdir(parents=True, exist_ok=True)

    # Every FUN_/thunk_/SUB_ symbol resolves to its stock entry point, with the
    # Thumb bit set: the address map is preserved, so no symbol needs inventing.
    symbol_addresses: dict[str, int] = {}
    for record in database["functions"]:
        for key in ("ghidra_name", "name"):
            name = record.get(key)
            if name:
                symbol_addresses[name] = record["entry"] | 1

    data_index_path = source_dir / "data" / "data-index.json"
    data_index = json.loads(data_index_path.read_text(encoding="utf-8"))["regions"]

    # --- compile the data shards -------------------------------------------
    object_root = output_dir / "objects"
    object_root.mkdir(parents=True, exist_ok=True)
    data_sources = sorted((source_dir / "data").glob("data-shard-*.c"))
    data_objects: dict[str, Path] = {}
    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {}
        for source in data_sources:
            object_path = object_root / f"{source.stem}.o"
            futures[pool.submit(compile_source, clang, source, object_path, source_dir)] = (
                source, object_path
            )
        for future in concurrent.futures.as_completed(futures):
            source, object_path = futures[future]
            error = future.result()
            if error:
                failures.append(f"{source.name}: {error.splitlines()[0] if error else ''}")
            else:
                data_objects[source.stem] = object_path
    if failures:
        raise ImageError("data shards failed to compile:\n  " + "\n  ".join(failures))

    # Pull each declared array back out of its object by symbol.
    data_bytes: dict[str, bytes] = {}
    for stem, object_path in data_objects.items():
        elf = Elf32(object_path.read_bytes(), object_path.name)
        for symbol in elf.symbols():
            if not symbol["name"].startswith("openg2_data_"):
                continue
            if symbol["section"] == 0 or symbol["section"] >= len(elf.sections):
                continue
            section = elf.sections[symbol["section"]]
            content = elf.contents(section)
            data_bytes[symbol["name"]] = content[
                symbol["value"]:symbol["value"] + symbol["size"]
            ]

    # --- assemble ----------------------------------------------------------
    image = bytearray(b"\0" * image_size)
    covered = bytearray(image_size)

    def write(address: int, payload: bytes, what: str) -> None:
        offset = address - load_base
        if offset < 0 or offset + len(payload) > image_size:
            raise ImageError(f"{what} at {address:#x} falls outside the image")
        if any(covered[offset:offset + len(payload)]):
            raise ImageError(f"{what} at {address:#x} overlaps an earlier region")
        image[offset:offset + len(payload)] = payload
        for index in range(offset, offset + len(payload)):
            covered[index] = 1

    accounting = Counter()
    byte_accounting = Counter()

    data_by_start = {entry["start"]: entry for entry in data_index}
    for region in regions["regions"]:
        if region["kind"] == "function":
            continue
        entry = data_by_start.get(region["start"])
        if entry is None:
            raise ImageError(f"no data unit for region at {region['start']:#x}")
        payload = data_bytes.get(entry["symbol"])
        if payload is None or len(payload) != region["size"]:
            raise ImageError(
                f"data unit {entry['symbol']} did not yield {region['size']} bytes"
            )
        digest = hashlib.sha256(payload).hexdigest()
        if digest != region["sha256"]:
            raise ImageError(
                f"data unit {entry['symbol']} does not reproduce its recorded hash"
            )
        write(region["start"], payload, "data region")
        accounting[f"data:{region['classification']}"] += 1
        byte_accounting["data"] += region["size"]

    units_by_entry = {unit["entry"]: unit for unit in manifest["units"]}
    placement_failures: Counter[str] = Counter()
    variant_counts: Counter[str] = Counter()
    overflow_histogram: Counter[str] = Counter()
    overflow_total = [0]
    unit_reports: list[dict[str, Any]] = []

    for record in database["functions"]:
        entry = record["entry"]
        unit = units_by_entry.get(entry)
        if unit is None:
            continue
        for low, high in record["ranges"]:
            envelope = high - low
            if envelope <= 0:
                continue
            is_entry_range = low <= entry < high
            object_name = unit.get("object")
            if not is_entry_range or not object_name or not unit.get("compiled"):
                reason = (
                    "split-range-tail" if not is_entry_range
                    else "did-not-compile"
                )
                write(low, trap_bytes(envelope), "trap")
                accounting[f"trap:{reason}"] += 1
                byte_accounting["trap"] += envelope
                placement_failures[reason] += 1
                continue
            payload = None
            report: dict[str, Any] = {}
            last_failure = "unknown"
            best_overflow: int | None = None
            for variant_name, extra in SIZE_VARIANTS:
                if variant_name == "Oz":
                    candidate_object = source_dir / object_name
                else:
                    candidate_object = object_root / (
                        f"{Path(object_name).stem}.{variant_name}.o"
                    )
                    source_path = source_dir / unit["source"]
                    fresh = (
                        reuse_objects
                        and candidate_object.is_file()
                        and candidate_object.stat().st_mtime
                        >= source_path.stat().st_mtime
                    )
                    if not fresh:
                        error = compile_source(
                            clang, source_path, candidate_object, source_dir, extra
                        )
                        if error:
                            last_failure = "variant-did-not-compile"
                            continue
                try:
                    elf = Elf32(candidate_object.read_bytes(), candidate_object.name)
                    payload, report = place_unit(elf, low, envelope, symbol_addresses)
                    report["variant"] = variant_name
                    break
                except ImageError as failure:
                    message = str(failure)
                    match = re.match(
                        r"compiled size (\d+) exceeds envelope (\d+)", message
                    )
                    if match:
                        # The long tail of distinct size pairs says nothing on
                        # its own.  What matters is by how much recovered code
                        # overshoots the stock envelope -- measured once per
                        # function, at its best variant, not once per attempt.
                        last_failure = "compiled-size-exceeds-envelope"
                        overflow = int(match.group(1)) - int(match.group(2))
                        best_overflow = (
                            overflow
                            if best_overflow is None
                            else min(best_overflow, overflow)
                        )
                    else:
                        last_failure = message.split(":", 1)[0][:60]
                    payload = None
            if payload is None:
                if best_overflow is not None:
                    # Some variants can fail for an unrelated reason after one
                    # has already overshot.  Overflow is the finding that
                    # matters, so it wins the label and the two tables agree.
                    last_failure = "compiled-size-exceeds-envelope"
                    overflow_total[0] += best_overflow
                    overflow_histogram[bucket_overflow(best_overflow)] += 1
                write(low, trap_bytes(envelope), "trap")
                accounting["trap:placement"] += 1
                byte_accounting["trap"] += envelope
                placement_failures[last_failure] += 1
                continue
            write(low, payload + b"\0" * (envelope - len(payload)), "code")
            accounting["code"] += 1
            byte_accounting["code"] += len(payload)
            byte_accounting["code-padding"] += envelope - len(payload)
            variant_counts[report.get("variant", "Oz")] += 1
            unit_reports.append({
                "entry": entry,
                "name": unit.get("name"),
                "envelope": envelope,
                **report,
            })

    if not all(covered):
        missing = covered.index(0)
        raise ImageError(
            f"image byte at {load_base + missing:#x} has no source unit behind it"
        )

    # The 32-byte staging header is generated, not copied: size and CRC-32 of
    # the assembled image, keeping the stock flag byte.
    flags = image[3] & 0xFF
    struct.pack_into("<I", image, 0, (flags << 24) | image_size)
    struct.pack_into("<I", image, 4, zlib.crc32(bytes(image[8:])) & 0xFFFFFFFF)

    image_path = output_dir / "ota_s200_firmware_ota.bin"
    image_path.write_bytes(bytes(image))

    stock = (REPO_ROOT / image_meta["path"]).read_bytes()
    identical = sum(1 for a, b in zip(image, stock) if a == b)

    report = {
        "schema_version": 1,
        "generator": "tools/build_transparent_image.py",
        "image": {
            "artifact": str(image_path.relative_to(output_dir)),
            "size": image_size,
            "sha256": hashlib.sha256(bytes(image)).hexdigest(),
            "load_base": load_base,
        },
        "stock_reference": {
            "path": image_meta["path"],
            "sha256": image_meta["sha256"],
            "bytes_identical_to_stock": identical,
        },
        "regions": dict(sorted(accounting.items())),
        "bytes": dict(sorted(byte_accounting.items())),
        "placement_failures": dict(placement_failures.most_common(20)),
        "size_variants_used": dict(sorted(variant_counts.items())),
        "envelope_overflow": {
            "total_bytes": overflow_total[0],
            "histogram": dict(sorted(overflow_histogram.items())),
        },
        "opaque_bytes": 0,
        "units_placed": len(unit_reports),
    }
    (output_dir / "IMAGE-REPORT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=REPO_ROOT / "build/transparent/source")
    parser.add_argument("--database", type=Path, default=REPO_ROOT / "build/transparent")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "build/transparent/image")
    parser.add_argument("--clang", default="/usr/bin/clang")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--reuse-objects",
        action="store_true",
        help="reuse variant objects that are newer than their source",
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        report = build(
            args.source.resolve(),
            args.database.resolve(),
            args.output.resolve(),
            args.clang,
            args.jobs,
            args.reuse_objects,
        )
    except ImageError as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
