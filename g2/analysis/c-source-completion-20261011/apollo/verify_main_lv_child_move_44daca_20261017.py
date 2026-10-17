#!/usr/bin/env python3
"""Compare stock and C LVGL child ordering for valid parent/index fixtures."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_child_move_44daca.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-lv-child-move-44daca"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_page_overlay_44dca2": (0x44dca2, "parent"),
    "audio_uart_lv_child_count_44ddea": (0x44ddea, "count"),
    "audio_uart_lv_child_index_44de92": (0x44de92, "index"),
    "audio_uart_lv_obj_event_451670": (0x451670, "event"),
    "audio_uart_display_size_changed": (0x440656, "invalidate"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "display_lv_child_move_44daca.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_page_44daca",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, current, target):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x10000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        parent, spec, array = 0x20002000, 0x20003000, 0x20004000
        children = [0x20001000 + i * 0x100 for i in range(4)]
        child = children[current]
        cpu.mem_write(parent + 8, struct.pack("<I", spec))
        cpu.mem_write(spec, struct.pack("<I", array))
        cpu.mem_write(array, struct.pack("<4I", *children))
        cpu.reg_write(A.UC_ARM_REG_R0, child)
        cpu.reg_write(A.UC_ARM_REG_R1, target & 0xffffffff)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            name = kinds.get(pc)
            if name is None:
                return
            r0, r1, r2 = (machine.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if name == "parent":
                assert r0 == child
                machine.reg_write(A.UC_ARM_REG_R0, parent)
            elif name == "count":
                assert r0 == parent
                machine.reg_write(A.UC_ARM_REG_R0, 4)
            elif name == "index":
                assert r0 == child
                machine.reg_write(A.UC_ARM_REG_R0, current)
            elif name == "event":
                events.append((name, r0, r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            else:
                events.append((name, r0))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x44daca if native else symbols["audio_uart_page_44daca"]
        cpu.emu_start(entry | 1, 0, count=500)
        if not done[0]:
            raise RuntimeError(f"child move did not return: {native} {current} {target}")
        return struct.unpack("<4I", cpu.mem_read(array, 16)), events

    cases = [(current, target) for current in range(4)
             for target in (-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"child move mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_LV_CHILD_MOVE_44DACA_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x44daca..0x44dbc3",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Valid four-child fixtures and controlled LVGL lower calls only; null, absent-parent, and fatal assertions are not replayed."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
