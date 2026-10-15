#!/usr/bin/env python3
"""Native/C call-boundary comparison for the 0x498668 page factory."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_factory_498668.c"
OUT = G2 / "build/c-firmware/20261015/main-page-factory-498668"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x498c48-0x438000:0x498c4c-0x438000], "little") != 0x756108:
        raise RuntimeError("page descriptor literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text("""#include <stdint.h>
void *audio_uart_page_create_44cf98(const void*a,void*b){return 0;}
void audio_uart_page_initialize_44d0f0(void*a){}
""")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_498668",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, parent, created):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            targets = {(syms["audio_uart_page_create_44cf98"] & ~1) if compiled else 0x44cf98: "create",
                       (syms["audio_uart_page_initialize_44d0f0"] & ~1) if compiled else 0x44d0f0: "init"}
            calls = []

            def hook(cpu, address, size, unused):
                op = targets.get(address)
                if op is None:
                    return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                calls.append((op, r0, r1 if op == "create" else None))
                if op == "create":
                    cpu.reg_write(A.UC_ARM_REG_R0, created)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, parent)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_498668"] if compiled else 0x498668
            u.emu_start(entry | 1, 0x600000, count=10000)
            return u.reg_read(A.UC_ARM_REG_R0), calls

        count = 0
        for parent, created in itertools.product((0, 0x20010000, 0x12345678),
                                                 (0, 0x20020000, 0x87654321)):
            native, source = run(False, parent, created), run(True, parent, created)
            if native != source:
                raise AssertionError((parent, created, native, source))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_498668_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x498668..0x49867f",
               "descriptor_literal_slot": "0x498c48", "descriptor_address": "0x756108",
               "cases": count,
               "limits": ["Page allocator and initializer are controlled lower interfaces.",
                          "The stock ROM descriptor address is not a final linker placement."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
