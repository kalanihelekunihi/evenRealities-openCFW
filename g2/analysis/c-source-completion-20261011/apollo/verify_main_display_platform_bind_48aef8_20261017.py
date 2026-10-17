#!/usr/bin/env python3
"""Compare stock/C LVGL draw-buffer descriptor initialization."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_platform_bind_48aef8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-platform-bind-48aef8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_draw_memzero_48aa54": (0x48aa54, "zero"),
    "audio_uart_font_bitmap_stride": (0x48aad8, "stride"),
    "audio_uart_lv_draw_align_48ab04": (0x48ab04, "align"),
    "audio_uart_lvgl_log": (0x44d25c, "log"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "platform-bind.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_platform_bind",
                    "--defsym=audio_uart_display_lv_state=0x2006f548",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, width, height, format_value, provided_stride,
            capacity, aligned):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        output, data, sp = 0x20010000, 0x20020000, 0x200ff000
        cpu.mem_write(output, bytes([0xa5]) * 28)
        cpu.mem_write(sp, struct.pack("<3I", provided_stride, data, capacity))
        for reg, value in ((A.UC_ARM_REG_R0, output),
                           (A.UC_ARM_REG_R1, width),
                           (A.UC_ARM_REG_R2, height),
                           (A.UC_ARM_REG_R3, format_value),
                           (A.UC_ARM_REG_SP, sp),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def cstr(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0", 1)[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = kinds.get(pc)
            if kind is None:
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            call_sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "zero":
                machine.mem_write(r0, bytes(r1))
                events.append((kind, r0, r1))
            elif kind == "stride":
                events.append((kind, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, (r0 * 2) & 0xffffffff)
            elif kind == "align":
                events.append((kind, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, r0 if aligned else r0 + 4)
            else:
                line, fmt = r2, cstr(word(call_sp))
                item = (kind, r0, cstr(r1), line, cstr(r3), fmt)
                if line == 0x125:
                    item += (word(call_sp + 4), word(call_sp + 8))
                events.append(item)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x48aef8 if native else symbols["audio_uart_display_platform_bind"]
        cpu.emu_start(entry | 1, 0, count=700)
        if not done[0]:
            raise RuntimeError(f"platform bind did not return: {native} {width} {height}")
        return cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(output, 28)), events

    cases = [(width, height, fmt, stride, capacity, aligned)
             for width in (1, 0x240, 0x10000)
             for height in (1, 0x120, 0xffff)
             for fmt in (0, 0x0d, 0x10d)
             for stride in (0, 7)
             for capacity in (0, 100, 0x14400, 0xffffffff)
             for aligned in (False, True)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"platform bind mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_PLATFORM_BIND_48AEF8_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x48aef8..0x48aff9",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Non-null draw-buffer fixtures only; memzero, stride, alignment and LVGL logging are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
