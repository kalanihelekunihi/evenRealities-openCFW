#!/usr/bin/env python3
"""Native/C page class context-bit traversal comparison."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_needs_context_44d1cc.c"
OUT = G2 / "build/c-firmware/20261015/main-page-needs-context-44d1cc"


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_needs_context_44d1cc",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, first, second, third):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, nodes = 0x20010000, (0x20010100, 0x20010200, 0x20010300)
            u.mem_write(page, nodes[0].to_bytes(4, "little"))
            for index, kind in enumerate((first, second, third)):
                next_node = nodes[index+1] if index < 2 else 0
                data = bytearray(40)
                data[0:4] = next_node.to_bytes(4, "little")
                data[32:36] = (0xa0 | (kind << 2)).to_bytes(4, "little")
                u.mem_write(nodes[index], bytes(data))
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_needs_context_44d1cc"] if compiled else 0x44d1cc
            u.emu_start(entry | 1, 0x600000, count=10000)
            return u.reg_read(A.UC_ARM_REG_R0)

        count = 0
        for kinds in itertools.product(range(4), repeat=3):
            native, source = run(False, *kinds), run(True, *kinds)
            if native != source:
                raise AssertionError((kinds, native, source))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_NEEDS_CONTEXT_44D1CC_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x44d1cc..0x44d1fb",
               "cases": count,
               "limits": ["Three-class chains cover all 4-bit context kind combinations 0..3.",
                          "Malformed cycles and hardware behavior remain outside this comparison."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
