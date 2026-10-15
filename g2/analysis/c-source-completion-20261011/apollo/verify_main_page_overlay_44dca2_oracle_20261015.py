#!/usr/bin/env python3
"""Native/C page overlay pointer comparison, including null input."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_overlay_44dca2.c"
OUT = G2 / "build/c-firmware/20261015/main-page-overlay-44dca2"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_overlay_44dca2",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, present, value):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            object_address = 0x20010000
            u.mem_write(object_address, b"\xa5" * 4 + value.to_bytes(4, "little") + b"\x33" * 56)
            u.reg_write(A.UC_ARM_REG_R0, object_address if present else 0)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_overlay_44dca2"] if compiled else 0x44dca2
            u.emu_start(entry | 1, 0x600000, count=1000)
            return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(object_address, 64))

        values = (0, 1, 0x20020000, 0xffffffff)
        count = 0
        for present in (0, 1):
            for value in values:
                native, source = run(False, present, value), run(True, present, value)
                if native != source:
                    raise AssertionError((present, value, native, source))
                count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_OVERLAY_44DCA2_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44dca2..0x44dce1",
               "cases": count,
               "limits": ["Null and non-null pointer effects are compared.",
                          "Final page-object layout and hardware behavior remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
