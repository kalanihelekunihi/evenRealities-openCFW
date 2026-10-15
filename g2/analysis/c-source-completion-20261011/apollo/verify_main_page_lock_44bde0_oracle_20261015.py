#!/usr/bin/env python3
"""Native/C LVGL page lock-byte comparison."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_lock_44bde0.c"
OUT = G2 / "build/c-firmware/20261015/main-page-lock-44bde0"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x44c154-0x438000:0x44c158-0x438000], "little") != 0x2006f548:
        raise RuntimeError("LV state RAM literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text("unsigned char audio_uart_display_lv_state[0x200];\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_lock_44bde0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, value):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            state = syms["audio_uart_display_lv_state"] if compiled else 0x2006f548
            u.mem_write(state, b"\xa7" * 0x200)
            u.reg_write(A.UC_ARM_REG_R0, value)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_lock_44bde0"] if compiled else 0x44bde0
            u.emu_start(entry | 1, 0x600000, count=1000)
            return bytes(u.mem_read(state, 0x200))

        values = (0, 1, 2, 0x7f, 0xff, 0x100, 0x12345678)
        for value in values:
            if run(False, value) != run(True, value):
                raise AssertionError(value)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_LOCK_44BDE0_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44bde0..0x44bde9",
               "native_state_address": "0x2006f548", "cases": len(values),
               "limits": ["A 512-byte controlled LVGL state range is compared.",
                          "Final state layout and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(values))


if __name__ == "__main__":
    main()
