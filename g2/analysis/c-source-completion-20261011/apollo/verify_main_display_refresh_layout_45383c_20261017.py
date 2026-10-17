#!/usr/bin/env python3
"""Compare stock/C LVGL refresh layout with controlled draw and allocation calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_refresh_layout_45383c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-refresh-layout-45383c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, NODE = 0x2006f548, 0x20010000, 0x20012000
INSERTED = (0x20013000, 0x20013100)
DEFINITIONS = {
    "audio_uart_lv_display_pre_refresh_454692": 0x454692,
    "audio_uart_lv_display_width_44fa7e": 0x44fa7e,
    "audio_uart_lv_display_height_44faa8": 0x44faa8,
    "audio_uart_lv_list_first": 0x482cd8,
    "audio_uart_lv_list_next": 0x482cf0,
    "audio_uart_lv_list_insert_before_482b56": 0x482b56,
    "audio_uart_lv_list_remove_482c0e": 0x482c0e,
    "audio_uart_lv_heap_free": 0x44f758,
    "audio_uart_lv_area_subtract_450c2a": 0x450c2a,
    "audio_uart_display_area_copy_439c04": 0x439c04,
    "audio_uart_lv_area_intersect_450bcc": 0x450bcc,
    "audio_uart_lv_draw_buf_copy_48ad42": 0x48ad42,
    "audio_uart_lv_list_clear_custom_482c9a": 0x482c9a,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "refresh-layout.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_refresh_layout_45383c",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in DEFINITIONS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, mode, flush, populated, invalid_count, invalid_flag,
            subtract_result, same_buffer):
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

        write(ROOT_RAM + 0x10, DISPLAY)
        write(DISPLAY, 16)
        write(DISPLAY + 4, 8)
        cpu.mem_write(DISPLAY + 0x39, bytes((mode,)))
        write(DISPLAY + 0x1c, 0x20030000)
        write(DISPLAY + 0x20, 0x20031000 if flush else 0)
        write(DISPLAY + 0x24, 0x20030000 if same_buffer else 0x20032000)
        write(DISPLAY + 0x260, invalid_count)
        write(DISPLAY + 0x268, 16)
        write(DISPLAY + 0x26c, NODE if populated else 0)
        write(DISPLAY + 0x270, NODE if populated else 0)
        cpu.mem_write(DISPLAY + 0x40, struct.pack("<4i", 2, 2, 7, 6))
        cpu.mem_write(DISPLAY + 0x240, bytes((invalid_flag,)))
        cpu.mem_write(NODE, struct.pack("<4iII", 0, 0, 15, 7, 0, 0))
        for address in INSERTED:
            cpu.mem_write(address, bytes([0xa5]) * 24)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done, allocations = [], [False], [0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == 0x44fdbe:
                events.append(("event", machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == 0x48ad42:
                events.append(("copy", tuple(machine.reg_read(reg) for reg in
                                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))))
            elif pc == 0x450c2a:
                events.append(("subtract",))
                if subtract_result > 0:
                    output = machine.reg_read(A.UC_ARM_REG_R0)
                    for index in range(subtract_result):
                        machine.mem_write(output + index * 16,
                                          struct.pack("<4i", index, index, index + 2, index + 2))
                machine.reg_write(A.UC_ARM_REG_R0, subtract_result & 0xffffffff)
            elif pc == 0x44f718:
                address = INSERTED[allocations[0]]
                allocations[0] += 1
                events.append(("malloc", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, address)
            elif pc == 0x44f758:
                events.append(("free", machine.reg_read(A.UC_ARM_REG_R0)))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x45383c if native else symbols["audio_uart_lv_refresh_layout_45383c"]
        cpu.emu_start(entry | 1, 0, count=8000)
        if not done[0]:
            raise RuntimeError(f"refresh layout did not return: {native} {(mode,flush,populated,invalid_count,invalid_flag,subtract_result,same_buffer)}")
        return (bytes(cpu.mem_read(DISPLAY + 0x260, 12)),
                bytes(cpu.mem_read(NODE, 24)),
                tuple(bytes(cpu.mem_read(address, 24)) for address in INSERTED), events)

    cases = [(mode, flush, populated, count, flag, subtract, same)
             for mode in (0, 1) for flush in (0, 1)
             for populated in (0, 1) for count in (0, 1)
             for flag in (0, 1) for subtract in (-1, 0, 1, 2)
             for same in (0, 1)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"refresh layout mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_REFRESH_LAYOUT_45383C_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x45383c..0x4539b2", "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()), "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Area subtraction returns -1, 0, 1 or 2 under a controlled lower call; draw-buffer copy, event dispatch, heap alloc and free are controlled.",
                         "Multi-node initial lists and the render pass remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()
