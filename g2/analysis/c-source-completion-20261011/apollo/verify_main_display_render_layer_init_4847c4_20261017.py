#!/usr/bin/env python3
"""Compare stock/C LVGL layer initialization and display-list insertion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_layer_init_4847c4.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-layer-init-4847c4"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, LAYER = 0x2006f548, 0x20010000, 0x20011000
AREA, HEAD, SECOND, CALLBACK = 0x20013000, 0x20014000, 0x20015000, 0x101800
LOWERS = {"audio_uart_lv_refreshing_display_453604": 0x453604,
          "audio_uart_display_area_copy_439c04": 0x439c04,
          "audio_uart_lvgl_log": 0x44d25c}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "layer-init.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_render_layer_init_4847c4",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, parent, fmt, callback, links, null_layer=False):
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

        def write(address, value):
            cpu.mem_write(address, struct.pack("<I", value))

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def area(address):
            return struct.unpack("<4i", cpu.mem_read(address, 16))

        def tag(address):
            if LAYER <= address < LAYER + 0x100:
                return ("layer", address - LAYER)
            if address == AREA:
                return ("area",)
            if address == DISPLAY:
                return ("display",)
            return ("address", address)

        cpu.mem_write(LAYER, bytes((0xa5,)) * 0x58)
        cpu.mem_write(AREA, struct.pack("<4i", -3, 4, 23, 41))
        write(ROOT_RAM + 0x10, DISPLAY)
        write(DISPLAY + 0x2b0, CALLBACK | 1 if callback else 0)
        write(DISPLAY + 0x2ac, HEAD if links else 0)
        write(HEAD + 0x4c, SECOND if links == 2 else 0)
        write(SECOND + 0x4c, 0)
        cpu.reg_write(A.UC_ARM_REG_R0, 0 if null_layer else LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, parent)
        cpu.reg_write(A.UC_ARM_REG_R2, fmt)
        cpu.reg_write(A.UC_ARM_REG_R3, AREA)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x484380:
                machine.mem_write(r0, bytes(r1))
            elif pc == 0x453604:
                events.append(("refresh_display",))
                machine.reg_write(A.UC_ARM_REG_R0, DISPLAY)
            elif pc == 0x439c04:
                events.append(("copy", tag(r0), tag(r1), r2, area(r1)))
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
            elif pc == CALLBACK:
                events.append(("callback", tag(r0), tag(r1),
                               bytes(machine.mem_read(LAYER, 0x58)).hex()))
            elif pc == 0x44d25c:
                def cstr(address):
                    return bytes(machine.mem_read(address, 128)).split(b"\0")[0].decode()
                r3 = machine.reg_read(A.UC_ARM_REG_R3)
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                words = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append(("assert", r0, cstr(r1), r2, cstr(r3),
                               *(cstr(address) for address in words)))
                done[0] = True
                machine.emu_stop()
                return
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = (0x4846de if native else
                 symbols["audio_uart_lv_render_layer_base_init_4846de"]) if null_layer else (
                 0x4847c4 if native else symbols["audio_uart_lv_render_layer_init_4847c4"])
        cpu.emu_start(entry | 1, 0, count=3000)
        assert done[0], (native, events)
        return (events, bytes(cpu.mem_read(LAYER, 0x58)).hex(),
                word(DISPLAY + 0x2ac), word(HEAD + 0x4c), word(SECOND + 0x4c))

    cases = list(itertools.product((0, HEAD), (0, 7, 31),
                                   (False, True), (0, 1, 2)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"layer init mismatch {case}: {stock} != {compiled}")
    stock, compiled = run(True, 0, 0, False, 0, True), run(False, 0, 0, False, 0, True)
    if stock != compiled:
        raise RuntimeError(f"layer base null mismatch: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_LAYER_INIT_4847C4_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + 1,
              "native_body": "0x4846de..0x48475e plus 0x4847c4..0x484836 through return or null assertion log",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Memzero, refreshing display, area copy and callback are controlled lower calls.",
                         "Null-layer case stops at the assertion log; deliberate fault loop is not executed."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(path.read_bytes()))


if __name__ == "__main__":
    main()
