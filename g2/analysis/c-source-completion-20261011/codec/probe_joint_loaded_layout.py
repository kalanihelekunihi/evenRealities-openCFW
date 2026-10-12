#!/usr/bin/env python3
"""Place all selected source-root loaded sections in native A XIP/SRAM spans.

This is a relocatable capacity probe. Its explicit discard list applies only
under the source-root GC assumption and is not a production linker script.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"


def section_body(source):
    text = source.read_text()
    return text.split("SECTIONS {", 1)[1].rsplit("}\n", 1)[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--gc-receipt", type=Path, required=True)
    parser.add_argument("--xip-layout", type=Path, required=True)
    parser.add_argument("--resident-layout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = json.loads(args.closure.read_text())
    gc = json.loads(args.gc_receipt.read_text())
    candidate_sha = hashlib.sha256(args.candidate.read_bytes()).hexdigest()
    assert source["candidate_sha256"] == gc["candidate_sha256"] == candidate_sha
    selected = {s["section"] for s in source["all_source_roots_closure"]["sections"]}
    all_alloc = {s["section"] for s in source["all_alloc_progbits"]["sections"]}
    assert all_alloc - selected == set(gc["discarded_sections"])
    xip = section_body(args.xip_layout)
    resident = section_body(args.resident_layout)
    scripted = set(re.findall(r"\*\((\.[^)]+)\)", xip + resident))
    supplemental = sorted(selected - scripted)
    assert all(name.startswith(('.rodata.', '.text.')) for name in supplemental), supplemental
    last_close = xip.rfind(' }')
    assert last_close >= 0
    xip = xip[:last_close] + ''.join(f'  *({name})\n' for name in supplemental) + xip[last_close:]
    discard = "\n /DISCARD/ : {\n" + "".join(f"  *({name})\n" for name in gc["discarded_sections"]) + " }\n"
    known_bss = ("\n .gx8002_flash_protection_maps 0x20026ff8 (NOLOAD) : "
                 "{ *(.bss.gx8002.flash_protection_maps.26ff8) }\n"
                 " .gx8002_console_port 0x2002731c (NOLOAD) : "
                 "{ *(.bss.gx8002.console_port.2731c) }\n")
    script = args.output / "joint-loaded-probe.ld"
    script.write_text("SECTIONS {" + resident + xip + known_bss + discard + "}\n"
                      'ASSERT(ADDR(.gx8002_xip_closure) + SIZEOF(.gx8002_xip_closure) <= 0x1020be88, "XIP overflow")\n'
                      'ASSERT(ADDR(.gx8002_resident_body_pre) + SIZEOF(.gx8002_resident_body_pre) <= 0x10025cd0, "clock overlap")\n'
                      'ASSERT(ADDR(.gx8002_resident_body_post) + SIZEOF(.gx8002_resident_body_post) <= 0x100264e4, "tail overlap")\n'
                      'ASSERT(ADDR(.gx8002_request_initial) + SIZEOF(.gx8002_request_initial) == 0x10026d7c, "SRAM end mismatch")\n')
    with script.open("a") as file:
        file.write('ASSERT(SIZEOF(.gx8002_flash_protection_maps) == 0x18, "flash map BSS extent mismatch")\n'
                   'ASSERT(SIZEOF(.gx8002_console_port) == 0x4, "console port BSS extent mismatch")\n')
    placed = args.output / "joint-loaded-probe.o"
    command = ["docker", "run", "--rm", "--network=none", "--read-only", "--platform", "linux/amd64",
               "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
               "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
               "--mount", f"type=bind,src={args.output.resolve()},dst=/out", "--tmpfs", "/tmp:rw",
               "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-gcc",
               "-mcpu=ck804ef", "-mhard-float", "-nostdlib", "-nostartfiles",
               "-Wl,-r", "-Wl,-A,ck803", "-Wl,-T,/out/joint-loaded-probe.ld",
               f"/repo/{args.candidate.resolve().relative_to(ROOT)}", "-o", "/out/joint-loaded-probe.o"]
    run = subprocess.run(command, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr[-2000:]
    listing = subprocess.check_output([str(READELF), "-SW", str(placed)], text=True)
    sections = {}
    allocated_progbits = []
    placed_nobits = []
    for line in listing.splitlines():
        match = re.search(r"\]\s+(\.gx8002_\S+)\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)", line)
        if match:
            sections[match[1]] = {"address": int(match[2], 16), "bytes": int(match[3], 16)}
        alloc = re.search(r"\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+\d+\s+(\S+)", line)
        if alloc and "A" in alloc[4] and int(alloc[3], 16):
            allocated_progbits.append({"section": alloc[1], "address": int(alloc[2], 16),
                                       "bytes": int(alloc[3], 16)})
        bss = re.search(r"\]\s+(\S+)\s+NOBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+\d+\s+(\S+)", line)
        if bss and "A" in bss[4] and int(bss[3], 16):
            placed_nobits.append({"section": bss[1], "address": int(bss[2], 16),
                                     "bytes": int(bss[3], 16)})
    assert all((0x10023400 <= row["address"] and row["address"] + row["bytes"] <= 0x10026d7c) or
               (0x10203004 <= row["address"] and row["address"] + row["bytes"] <= 0x1020be88)
               for row in allocated_progbits)
    assert sorted(placed_nobits, key=lambda row: row["address"]) == [
        {"section": ".gx8002_flash_protection_maps", "address": 0x20026ff8, "bytes": 24},
        {"section": ".gx8002_console_port", "address": 0x2002731c, "bytes": 4},
    ]
    xip_result = sections[".gx8002_xip_closure"]
    assert xip_result["address"] == 0x10203004
    assert xip_result["address"] + xip_result["bytes"] <= 0x1020be88
    output = {
        "candidate_sha256": candidate_sha,
        "linker_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "placed_sha256": hashlib.sha256(placed.read_bytes()).hexdigest(),
        "selected_loaded_sections": len(selected),
        "supplemental_source_root_sections": supplemental,
        "conditional_gc_excluded_sections": len(gc["discarded_sections"]),
        "xip": {"start": hex(xip_result["address"]),
                 "end_exclusive": hex(xip_result["address"] + xip_result["bytes"]),
                 "margin_bytes": 0x1020be88 - xip_result["address"] - xip_result["bytes"]},
        "resident_pre": sections[".gx8002_resident_body_pre"],
        "resident_post": sections[".gx8002_resident_body_post"],
        "fixed_tail_end": hex(sections[".gx8002_request_initial"]["address"] + sections[".gx8002_request_initial"]["bytes"]),
        "nonzero_allocated_progbits_outputs": allocated_progbits,
        "placed_nobits_outputs": placed_nobits,
        "relocatable_target_link_passed": True,
        "executable_firmware_complete": False,
        "limits": [
            "The 25 excluded sections are dropped under selected source roots; absent stock indirect/external roots remain unproven.",
            "Relocatable placement does not resolve C-SKY branch reach, veneers, final relocation values or the ambient KWS import.",
            "BSS, runtime aliasing, package headers, flash behavior and hardware execution remain outside this loaded-section probe.",
        ],
    }
    (args.output / "receipt.json").write_text(json.dumps(output, indent=2) + "\n")
    print({"selected_loaded_sections": len(selected), "xip_margin": output["xip"]["margin_bytes"],
           "tail_end": output["fixed_tail_end"]})


if __name__ == "__main__":
    main()
