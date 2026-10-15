#!/usr/bin/env python3
"""Compare decoded startup ITCM delay with its selected C loop."""
import hashlib
import importlib.util
import json
import random
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/platform_callbacks_offline/itcm.c"
DECODER = G2 / "analysis/audio-platform-callbacks-closure-2026-10-08/itcm_record.py"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
OBJECT = OUT / "itcm-delay-verifier-source.o"
ELF = OUT / "itcm-delay-verifier-source.elf"
LINK = OUT / "itcm-delay-verifier.ld"
RECEIPT = OUT / "itcm-delay-native-comparison.json"
STOP = 0x20001000


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(entry, source_segments, itcm, count):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.mem_map(0, 0x1000)
    u.mem_write(0x40, itcm)
    u.mem_map(0x100000, 0x10000)
    for address, data in source_segments:
        u.mem_write(address, data)
    u.mem_map(0x20000000, 0x10000)
    u.reg_write(UC_ARM_REG_SP, 0x2000f000)
    u.reg_write(UC_ARM_REG_LR, STOP | 1)
    u.reg_write(UC_ARM_REG_R0, count)
    u.emu_start(entry | 1, STOP, count=1000000)
    assert u.reg_read(UC_ARM_REG_PC) == STOP
    return u.reg_read(UC_ARM_REG_R0)


def main():
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    spec = importlib.util.spec_from_file_location("itcm_record", DECODER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    itcm = module.decode_itcm(payload)
    assert len(itcm) == 24 and itcm[:6].hex() == "0138fdd17047"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    LINK.write_text("SECTIONS { . = 0x100000; .text : { *(.text*) *(.rodata*) } "
                    "/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }\n")
    subprocess.run(["arm-none-eabi-ld", "-T", str(LINK), str(OBJECT),
                    "--defsym=actual_itcm_delay=audio_itcm_delay_iterations",
                    "--unresolved-symbols=ignore-all", "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    assert "audio_itcm_delay_iterations" in syms
    counts = [1, 2, 3, 4, 7, 15, 31, 63, 127, 255, 1024]
    rng = random.Random(0x40)
    counts += [rng.randrange(1, 2049) for _ in range(128)]
    for count in counts:
        original = run(0x40, segments, itcm, count)
        compiled = run(syms["audio_itcm_delay_iterations"], segments, itcm, count)
        assert original == compiled == 0, count
    receipt = {"status": "PASS_BOUNDED_NATIVE_ITCM_DELAY_C",
               "stock_payload_sha256": hashlib.sha256(payload).hexdigest(),
               "decoder": str(DECODER.relative_to(ROOT)), "decoder_sha256": sha(DECODER),
               "decoded_itcm_sha256": hashlib.sha256(itcm).hexdigest(), "delay_entry": "0x40",
               "delay_entry_bytes": itcm[:6].hex(), "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "cases": len(counts), "positive_input_min": min(counts),
               "positive_input_max": max(counts), "source_elf_sha256": sha(ELF),
               "whole_image_complete": False, "hardware_proof": False,
               "limits": ["Positive counts and final R0 are compared; cycle timing, interrupts and zero-input 2^32-iteration behavior are not verified.",
                          "The ITCM block is decoded from the stock startup record; final source placement is not established."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(counts), sha(RECEIPT))


if __name__ == "__main__":
    main()
