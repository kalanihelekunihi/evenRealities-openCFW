#!/usr/bin/env python3
"""Native/C page class parent and callback traversal comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_descriptor_init_44d1fc.c"
OUT = G2 / "build/c-firmware/20261015/main-page-descriptor-init-44d1fc"


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_descriptor_init_44d1fc",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, depth, mask):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, nodes, callback = 0x20010000, [0x20010200+i*0x100 for i in range(depth)], 0x500001
            u.mem_write(page, nodes[0].to_bytes(4, "little") + b"\x33" * 60)
            for index, node in enumerate(nodes):
                parent = nodes[index+1] if index+1 < depth else 0
                cb = callback if mask & (1 << index) else 0
                u.mem_write(node, parent.to_bytes(4, "little") + cb.to_bytes(4, "little") + b"\x55" * 32)
            calls = []

            def hook(cpu, address, size, unused):
                if address != callback-1:
                    return
                calls.append((cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1),
                              int.from_bytes(cpu.mem_read(page, 4), "little")))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, nodes[0])
            u.reg_write(A.UC_ARM_REG_R1, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_descriptor_init_44d1fc"] if compiled else 0x44d1fc
            u.emu_start(entry | 1, 0x600000, count=100000)
            return calls, bytes(u.mem_read(page, 64))

        count = 0
        for depth in (1, 2, 3, 4):
            for mask in range(1 << depth):
                native, source = run(False, depth, mask), run(True, depth, mask)
                if native != source:
                    raise AssertionError((depth, mask, native, source))
                count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_DESCRIPTOR_INIT_44D1FC_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44d1fc..0x44d22f",
               "cases": count,
               "limits": ["One to four page-class levels and every callback mask are compared.",
                          "Callback bodies are controlled; final descriptor layout remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
