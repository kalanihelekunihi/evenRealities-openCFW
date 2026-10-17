#!/usr/bin/env python3
"""Compare stock/C LVGL layer creation under controlled allocator and initializer."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_draw_layer_create_48475e.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-draw-layer-create-48475e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_lv_heap_alloc": 0x44f730,
          "audio_uart_lv_render_layer_init_4847c4": 0x4847c4,
          "audio_uart_lvgl_log": 0x44d25c}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "layer-create.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_draw_layer_create_48475e",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, parent, color_format, seed, alloc_ok=True):
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
        parent_addr, area, child = 0x20010000, 0x20011000, 0x20012000
        cpu.mem_write(parent_addr + 0x38, bytes((seed,)))
        cpu.mem_write(parent_addr + 0x39, struct.pack("<I", 0x12345678 ^ seed))
        cpu.mem_write(area, struct.pack("<4i", -2, 3, 9, 14))
        cpu.reg_write(A.UC_ARM_REG_R0, parent_addr if parent else 0)
        cpu.reg_write(A.UC_ARM_REG_R1, color_format)
        cpu.reg_write(A.UC_ARM_REG_R2, area)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == 0x44f730:
                r0 = machine.reg_read(A.UC_ARM_REG_R0)
                events.append(("alloc", r0))
                machine.mem_write(child, bytes(0x58))
                result = child if alloc_ok else 0
            elif pc == 0x4847c4:
                r0, r1, r2, r3 = (machine.reg_read(x) for x in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                events.append(("init", r0, r1, r2,
                               tuple(struct.unpack("<4i", machine.mem_read(r3, 16)))))
                machine.mem_write(child + 0x38, bytes((77,)))
                machine.mem_write(child + 0x39, struct.pack("<I", 0xaabbccdd))
                result = 0
            elif pc == 0x44d25c:
                r0, r1, r2, r3 = (machine.reg_read(x) for x in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                args = struct.unpack("<3I", machine.mem_read(sp, 12))
                def string(address):
                    return bytes(machine.mem_read(address, 160)).split(b"\0")[0].decode()
                events.append(("log", r0, string(r1), r2, string(r3),
                               *(string(a) for a in args)))
                result = 0
            else:
                return
            machine.reg_write(A.UC_ARM_REG_R0, result)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        def write_hook(machine, _access, address, size, value, _user):
            if address == 0xffffffff:
                events.append(("fault_write", address, size, value))
                done[0] = True
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED, write_hook)
        entry = 0x48475e if native else symbols["audio_uart_lv_draw_layer_create_48475e"]
        try:
            cpu.emu_start(entry | 1, 0, count=300)
        except UcError:
            if not done[0] or alloc_ok:
                raise
        assert done[0], (native, events)
        return events, (cpu.reg_read(A.UC_ARM_REG_R0) if alloc_ok else None), bytes(cpu.mem_read(child, 0x58)).hex()

    cases = [(parent, fmt, seed, alloc_ok) for parent in (False, True)
             for fmt in (0, 6, 16, 255, 0x10006) for seed in (0, 199)
             for alloc_ok in (False, True)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"layer-create mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_DISPLAY_DRAW_LAYER_CREATE_48475E_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Allocator and initializer are controlled lower calls; real heap behavior remains outside this oracle."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
