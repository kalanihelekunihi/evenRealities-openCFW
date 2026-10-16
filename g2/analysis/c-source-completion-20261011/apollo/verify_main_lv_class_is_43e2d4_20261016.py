#!/usr/bin/env python3
"""Compare the LVGL class ancestry walker with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_class_is_43e2d4.c"
OUT = G2 / "build/c-firmware/20261016/main-lv-class-is-43e2d4"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OBJECT = 0x20001000
CLASSES = [0x20002000, 0x20002100, 0x20002200, 0x20002300]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    assert hashlib.sha256(blob).hexdigest() == PIN
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "lv-class-is-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_class_is_43e2d4",
                    str(SOURCE), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as stream:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, chain, requested):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(OBJECT, struct.pack("<I", CLASSES[0] if chain else 0))
        for i, address in enumerate(CLASSES):
            next_class = CLASSES[i + 1] if i + 1 < chain else 0
            u.mem_write(address, struct.pack("<I", next_class))
        u.reg_write(A.UC_ARM_REG_R0, OBJECT)
        u.reg_write(A.UC_ARM_REG_R1, requested)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_uart_lv_class_is_43e2d4"] if compiled else 0x43e2d4
        u.emu_start(entry | 1, 0x600000, count=1000)
        return u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for chain in range(5):
        for requested in (0, *CLASSES, 0x20002400):
            stock, selected = run(False, chain, requested), run(True, chain, requested)
            if stock != selected:
                raise RuntimeError(f"class ancestry mismatch {(chain, requested)}: {stock} != {selected}")
            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_MAIN_LV_CLASS_IS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "Zero through four class-chain links and each match position",
              "limits": ["Null object and cyclic class chain outside bounded oracle; class records require source ownership."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(path))


if __name__ == "__main__":
    main()
