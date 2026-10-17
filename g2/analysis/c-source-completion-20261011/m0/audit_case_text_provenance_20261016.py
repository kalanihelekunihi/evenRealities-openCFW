#!/usr/bin/env python3
"""Attribute the mixed-Oz CASE .text tail to linker inputs."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261015/case-gc-size-frontier/mixed-oz-receipt.json"
NAMED = G2 / "build/c-firmware/20261016/case-named-function-size/receipt.json"
OUT = G2 / "build/c-firmware/20261016/case-text-provenance"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base, named = json.loads(BASE.read_text()), json.loads(NAMED.read_text())
    elf = ROOT / base["elf"]
    reloc = ROOT / base["relocatable"]
    layout = ROOT / base["linker_script"]
    if (base["status"] != "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER"
            or named["baseline_receipt_sha256"] != sha(BASE)
            or named["experimental_elf_sha256"] != sha(elf)
            or sha(elf) != base["elf_sha256"]
            or sha(reloc) != base["relocatable_sha256"]
            or sha(layout) != base["linker_script_sha256"]):
        raise RuntimeError("CASE baseline changed")
    OUT.mkdir(parents=True, exist_ok=True)
    map_path, replay = OUT / "mixed-oz.map", OUT / "mixed-oz-mapcheck.elf"
    subprocess.run(["arm-none-eabi-ld", "--gc-sections", "--sort-section=alignment",
                    "-Map=" + str(map_path), "-T", str(layout), str(reloc), "-o", str(replay)],
                   check=True)
    if sha(replay) != sha(elf):
        raise RuntimeError("map link did not reproduce pinned ELF")
    with elf.open("rb") as stream:
        image = ELFFile(stream)
        section = image.get_section_by_name(".text")
        start, end = section["sh_addr"], section["sh_addr"] + section["sh_size"]
        funcs = [(s["st_value"], s["st_value"] + s["st_size"])
                 for s in image.get_section_by_name(".symtab").iter_symbols()
                 if s["st_info"]["type"] == "STT_FUNC" and s["st_size"]
                 and start <= s["st_value"] < end]
    tail_start = max(b for _, b in funcs)
    map_text = map_path.read_text()
    region = map_text[map_text.index(f".text           {start:#010x}"):]
    region = region[:region.index("\n.glue_7")]
    rows = []
    pattern = re.compile(r"^ (\.[^\s]+)\s*\n?\s*(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+" +
                         re.escape(str(reloc)), re.M)
    for match in pattern.finditer(region):
        rows.append((match[1], int(match[2], 16), int(match[3], 16)))
    rodata = [row for row in rows if row[0].startswith(".rodata")]
    if (section["sh_size"] != named["candidate_text_bytes"] or
            tail_start != 0x0800d627 or end - tail_start != 8780 or
            sum(row[2] for row in rodata) != 8778 or
            min(row[1] for row in rodata) != 0x0800d628 or
            max(row[1] + row[2] for row in rodata) != end or
            named["candidate_text_bytes_outside_function_symbols"] != 8951):
        raise RuntimeError("CASE .text provenance frontier changed")
    result = {
        "status": "PASS_EXPERIMENTAL_CASE_TEXT_PROVENANCE",
        "baseline_receipt": str(BASE.relative_to(ROOT)), "baseline_receipt_sha256": sha(BASE),
        "named_receipt": str(NAMED.relative_to(ROOT)), "named_receipt_sha256": sha(NAMED),
        "experimental_elf": base["elf"], "experimental_elf_sha256": sha(elf),
        "map": str(map_path.relative_to(ROOT)), "map_sha256": sha(map_path),
        "replayed_elf": str(replay.relative_to(ROOT)), "replayed_elf_sha256": sha(replay),
        "text_start": hex(start), "text_end": hex(end), "text_bytes": section["sh_size"],
        "last_function_end": hex(tail_start), "tail_bytes": end - tail_start,
        "tail_alignment_bytes": min(row[1] for row in rodata) - tail_start,
        "tail_internal_alignment_bytes": (end - tail_start) - sum(row[2] for row in rodata) -
        (min(row[1] for row in rodata) - tail_start),
        "retained_rodata_sections": len(rodata),
        "retained_rodata_bytes": sum(row[2] for row in rodata),
        "text_bytes_outside_function_symbols": named["candidate_text_bytes_outside_function_symbols"],
        "other_outside_function_bytes": named["candidate_text_bytes_outside_function_symbols"] - (end - tail_start),
        "payload_overflow_bytes": base["overflow_bytes"],
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The map proves output placement and input section sizes, not native byte equivalence.",
                   "Moving read-only data to a different section alone does not reduce load bytes.",
                   "The remaining small symbol gaps and the total payload overflow require separate analysis."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], result["retained_rodata_bytes"], sha(path))


if __name__ == "__main__":
    main()
