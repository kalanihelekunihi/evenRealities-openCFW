#!/usr/bin/env python3
"""Compare stock/C LVGL mask task construction under controlled lowers."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import (Uc, UcError, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB,
                     UC_HOOK_CODE, UC_HOOK_MEM_WRITE_UNMAPPED)
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_draw_mask_rect_48a98e.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-draw-mask-rect-48a98e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_color_has_alpha_440fc4": 0x440fc4,
    "audio_uart_lvgl_log": 0x44d25c,
    "audio_uart_lv_render_task_alloc_4843ee": 0x4843ee,
    "audio_uart_lv_malloc": 0x44f718,
    "audio_uart_lv_grid_copy_454738": 0x454738,
    "audio_uart_lv_obj_has_flag_43e0e0": 0x43e0e0,
    "audio_lv_object_clear_flag_43dfa4": 0x43dfa4,
    "audio_lv_object_flag_43ded4": 0x43ded4,
    "audio_uart_lv_obj_event_451670": 0x451670,
    "audio_uart_lv_render_task_queue_484476": 0x484476,
}
LAYER, DSC, TASK, HEAP, OBJECT = (0x20010000, 0x20011000,
                                  0x20012000, 0x20013000, 0x20014000)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "mask-draw.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_draw_mask_rect_48a98e",
                    *(f"--defsym={name}=0x{address|1:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, alpha, alloc_ok, object_present, flag, seed):
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
        cpu.mem_write(LAYER, bytes(0x58))
        cpu.mem_write(LAYER + 4, struct.pack("<4i", 1, 2, 11, 22))
        cpu.mem_write(LAYER + 0x14, bytes((16 if alpha else 6,)))
        cpu.mem_write(DSC, bytes(((seed + i * 11) & 255) for i in range(0x34)))
        cpu.mem_write(DSC, struct.pack("<I", OBJECT if object_present else 0))
        cpu.mem_write(TASK, bytes((0xa5,)) * 0x58)
        cpu.mem_write(HEAP, bytes((0x5a,)) * 0x34)
        cpu.reg_write(A.UC_ARM_REG_R0, LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, DSC)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def get(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def cstr(address):
            return bytes(cpu.mem_read(address, 180)).split(b"\0")[0].decode()

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc not in LOWERS.values():
                return
            r0, r1, r2, r3 = (machine.reg_read(x) for x in
                               (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            value = 0
            if pc == 0x440fc4:
                events.append(("alpha", r0))
                value = int(alpha)
            elif pc == 0x44d25c:
                argc = 1 if r0 == 2 else 3
                args = [get(sp + i * 4) for i in range(argc)]
                events.append(("log", r0, cstr(r1), r2, cstr(r3),
                               *(cstr(a) for a in args)))
            elif pc == 0x4843ee:
                events.append(("task", r0,
                               struct.unpack("<4i", machine.mem_read(r1, 16))))
                value = TASK
            elif pc == 0x44f718:
                events.append(("alloc", r0))
                value = HEAP if alloc_ok else 0
            elif pc == 0x454738:
                events.append(("copy", r2, bytes(machine.mem_read(r1, r2)).hex()))
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
                value = r0
            elif pc == 0x43e0e0:
                events.append(("has_flag", r0, r1))
                value = int(flag)
            elif pc in (0x43dfa4, 0x43ded4):
                events.append(("clear" if pc == 0x43dfa4 else "add", r0, r1))
            elif pc == 0x451670:
                events.append(("event", r0, r1, r2))
                value = 1
            elif pc == 0x484476:
                events.append(("queue", r0, r1,
                               bytes(machine.mem_read(TASK, 0x58)).hex(),
                               bytes(machine.mem_read(HEAP, 0x34)).hex()))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        def fault(machine, _access, address, size, value, _user):
            if address == 0xffffffff:
                events.append(("fault_write", address, size, value))
                done[0] = True
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED, fault)
        entry = 0x48a98e if native else symbols["audio_uart_lv_draw_mask_rect_48a98e"]
        try:
            cpu.emu_start(entry | 1, 0, count=400)
        except UcError:
            if not done[0] or alloc_ok or not alpha:
                raise
        assert done[0], (native, events)
        return events, bytes(cpu.mem_read(TASK, 0x58)).hex(), bytes(cpu.mem_read(HEAP, 0x34)).hex()

    cases = list(itertools.product((False, True), repeat=4))
    cases = [(*case, seed) for case in cases for seed in (0, 17)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"mask-draw mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_DISPLAY_DRAW_MASK_RECT_48A98E_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Alpha predicate, allocation, task creation, event and queue are controlled lower calls."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
