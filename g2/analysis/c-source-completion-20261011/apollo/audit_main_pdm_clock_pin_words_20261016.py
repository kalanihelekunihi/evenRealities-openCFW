#!/usr/bin/env python3
"""Verify source ownership and bounded PDM pin-word reads."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/pdm_clock_pin_words_2007421c.c"
CLOCK = G2 / "components/audio/codec_pdm_clock_source_candidate/clock.c"
LAYOUT = G2 / "components/audio/uart_thread_source_candidate/pdm_clock_pin_words_2007421c.ld"
BASE = G2 / "build/c-firmware/20261016/main-epoch-calendar/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-pdm-clock-pin-words"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        return {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}


def run(entry, segments, stub, group, pin50, pin51):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in ((0x100000, 0x100000), (0x300000, 0x1000),
                          (0x400000, 0x400000), (0x20000000, 0x80000)):
        uc.mem_map(address, size)
    for address, data in segments:
        if data:
            uc.mem_write(address, data)
    uc.mem_write(0x2007421c, pin50.to_bytes(4, "little"))
    uc.mem_write(0x20074220, pin51.to_bytes(4, "little"))
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, 0x300001)
    uc.reg_write(UC_ARM_REG_R0, group)
    calls = []

    def hook(engine, address, size, _):
        if address == stub:
            calls.append((engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1)))
            engine.reg_write(UC_ARM_REG_R0, 0)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, 0x300000, count=1000)
    return calls


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main stock payload changed")
    for literal, value in ((0x4c36cc, 0x2007421c), (0x4c36d0, 0x20074220)):
        if int.from_bytes(payload[literal-0x438000:literal-0x438000+4], "little") != value:
            raise RuntimeError("PDM pin literal changed")
    placement = OUT / "placement-probe.elf"
    pins = symbols(placement)
    with placement.open("rb") as stream:
        section = ELFFile(stream).get_section_by_name(".g2_pdm_clock_pin_words")
        if section["sh_size"] != 8 or section["sh_type"] != "SHT_NOBITS":
            raise RuntimeError("PDM pin placement section changed")
    if pins["g2_pdm_clock_pin_50"] != 0x2007421c or pins["g2_pdm_clock_pin_51"] != 0x20074220:
        raise RuntimeError("PDM pin placement changed")
    stub_source = OUT / "clock-oracle-stub.c"
    stub_source.write_text("""#include <stdint.h>
__attribute__((noinline)) uint32_t g2_codec_pin_function(uint32_t p,uint32_t c)
{ return p+c; }
""")
    clock_obj, stub_obj = OUT / "clock-oracle.o", OUT / "clock-oracle-stub.o"
    for source, output in ((CLOCK, clock_obj), (stub_source, stub_obj)):
        subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-O2", "-Wall", "-Wextra", "-Werror", "-c",
                        str(source), "-o", str(output)], check=True)
    oracle = OUT / "clock-oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-T", str(LAYOUT),
                    "-e", "g2_pdm_clock_enable", str(clock_obj), str(stub_obj),
                    str(OUT / "pin-words.o"), "-o", str(oracle)], check=True)
    with oracle.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    rows = []
    for group in (0, 1, 2, 3, 4):
        for pin50, pin51 in ((0, 0), (0x1234, 0x5678), (0xffffffff, 0xabcdef)):
            old = run(0x4c31d8, [(0x438000, payload)], 0x480f0c, group, pin50, pin51)
            new = run(syms["g2_pdm_clock_enable"], segments,
                      syms["g2_codec_pin_function"] & ~1, group, pin50, pin51)
            if old != new:
                raise RuntimeError(f"PDM pin clock mismatch {group} {pin50:#x} {pin51:#x}")
            rows.append({"group": group, "pin50": pin50, "pin51": pin51,
                         "pin_function_calls": old})
    candidate = OUT / "candidate.o"
    before = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(BASE)], text=True).splitlines() if line.strip()}
    after = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(candidate)], text=True).splitlines() if line.strip()}
    if (len(before) != 131 or len(after) != 129 or
            before - after != {"g2_pdm_clock_pin_50", "g2_pdm_clock_pin_51"} or after - before):
        raise RuntimeError("Main PDM pin-word import frontier changed")
    result = {"status": "PASS_BOUNDED_MAIN_PDM_CLOCK_PIN_WORDS_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "clock_source": str(CLOCK.relative_to(ROOT)), "clock_source_sha256": sha(CLOCK),
              "linker_script": str(LAYOUT.relative_to(ROOT)), "linker_script_sha256": sha(LAYOUT),
              "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
              "candidate_object": str(candidate.relative_to(ROOT)), "candidate_object_sha256": sha(candidate),
              "placement_elf": str(placement.relative_to(ROOT)), "placement_elf_sha256": sha(placement),
              "oracle_elf": str(oracle.relative_to(ROOT)), "oracle_elf_sha256": sha(oracle),
              "cases": rows, "case_count": len(rows), "unresolved_before": 131,
              "unresolved_after": 129, "source_complete": False, "flashable": False,
              "hardware_proof": False,
              "limits": ["The two native pointer literals and 8-byte NOLOAD placement are qualified.",
                         "The runtime writer and values of these mutable cells remain unauthenticated.",
                         "Final whole-Main RAM collision, startup and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(rows), sha(path))


if __name__ == "__main__":
    main()
