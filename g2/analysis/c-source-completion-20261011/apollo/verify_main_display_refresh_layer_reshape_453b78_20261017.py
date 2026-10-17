#!/usr/bin/env python3
"""Compare Apollo stock and C refresh-layer reshape call frames."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_layer_reshape_453b78.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-layer-reshape-453b78"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_lv_area_height_4515a4": 0x4515a4,
          "audio_uart_lv_area_width_451598": 0x451598,
          "audio_uart_lv_draw_buf_reshape_48b196": 0x48b196,
          "audio_uart_lvgl_log": 0x44d25c}
LAYER, DRAW = 0x20010000, 0x20012000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "layer-reshape.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_layer_reshape_draw_buf_453b78",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, width, height, fmt, stride, allocation_ok=True):
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
        cpu.mem_write(LAYER, struct.pack("<I4i", DRAW, 2, 3, 9, 10))
        cpu.mem_write(LAYER + 0x14, bytes((fmt,)))
        cpu.reg_write(A.UC_ARM_REG_R0, LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, stride)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == 0x4515a4:
                events.append(("height", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, height)
            elif pc == 0x451598:
                events.append(("width", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, width)
            elif pc == 0x48b196:
                args = tuple(machine.reg_read(x) for x in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                fifth = struct.unpack("<I", machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 4))[0]
                events.append(("reshape", *args, fifth))
                machine.reg_write(A.UC_ARM_REG_R0, DRAW if allocation_ok else 0)
            elif pc == 0x44d25c:
                def cstr(address):
                    return bytes(machine.mem_read(address, 128)).split(b"\0")[0].decode()
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                words = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append(("assert", machine.reg_read(A.UC_ARM_REG_R0),
                               cstr(machine.reg_read(A.UC_ARM_REG_R1)),
                               machine.reg_read(A.UC_ARM_REG_R2),
                               cstr(machine.reg_read(A.UC_ARM_REG_R3)),
                               *(cstr(address) for address in words)))
                done[0] = True
                machine.emu_stop()
                return
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x453b78 if native else symbols["audio_uart_lv_layer_reshape_draw_buf_453b78"]
        cpu.emu_start(entry | 1, 0, count=1000)
        assert done[0], (native, events)
        return events

    cases = list(itertools.product((1, 7, 128, 1024), (1, 13, 240, 65535),
                                   (0, 7, 10, 31), (0, 1, 240, 0xffff)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"reshape mismatch {case}: {stock} != {compiled}")
    failure_cases = list(itertools.product((1, 128), (1, 240),
                                           (0, 7), (0, 240)))
    for case in failure_cases:
        stock, compiled = run(True, *case, False), run(False, *case, False)
        if stock != compiled:
            raise RuntimeError(f"reshape failure mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_LAYER_RESHAPE_453B78_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "cases": len(cases) + len(failure_cases),
              "success_cases": len(cases), "failure_cases": len(failure_cases),
              "native_body": "0x453b78..0x453bce through success return or failure log",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Area width, height and draw-buffer reshape are controlled lower calls.",
                         "Failure cases stop at the stock/C assertion log; the deliberate fault loop is not executed."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(path.read_bytes()))


if __name__ == "__main__":
    main()
