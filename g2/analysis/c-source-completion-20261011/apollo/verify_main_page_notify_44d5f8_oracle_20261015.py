#!/usr/bin/env python3
"""Compare bounded Apollo page notification dispatch with compiled C."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_notify_44d5f8.c"
OUT = G2 / "build/c-firmware/20261015/main-page-notify-44d5f8"
SHIM = '''void audio_uart_page_update_unbound_44d45c(void *p) {}
void audio_uart_page_update_bound_44d4b6(void *p) {}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_notify_44d5f8",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, flags, mutation):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page = 0x20010000
            initial = bytearray(range(64))
            initial[0x1c] = flags
            u.mem_write(page, bytes(initial))
            cuts = {(syms[name] & ~1) if compiled else addr: label for addr, name, label in
                    [(0x44d45c, "audio_uart_page_update_unbound_44d45c", "unbound"),
                     (0x44d4b6, "audio_uart_page_update_bound_44d4b6", "bound")]}
            trace = []

            def hook(cpu, address, size, unused):
                label = cuts.get(address)
                if label is None:
                    return
                value = cpu.mem_read(page+0x1c, 1)[0]
                trace.append((label, cpu.reg_read(A.UC_ARM_REG_R0), value))
                cpu.mem_write(page+0x1c, bytes([(value ^ mutation) & 0xff]))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_page_notify_44d5f8"] if compiled else 0x44d5f8
            u.emu_start(entry | 1, 0x600000, count=100000)
            return trace, bytes(u.mem_read(page, 64))

        count = 0
        for flags in (0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 0xff):
            for mutation in (0, 0x10, 0x0f):
                native, source = run(False, flags, mutation), run(True, flags, mutation)
                if native != source:
                    raise AssertionError((flags, mutation, native[0], source[0], native[1] == source[1]))
                count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_NOTIFY_44D5F8_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d5f8..0x44d639",
               "cases": count,
               "limits": ["The two lower update calls are controlled, not implemented here.",
                          "Dispatch trace and 64-byte page state are compared; native return and hardware are not."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
