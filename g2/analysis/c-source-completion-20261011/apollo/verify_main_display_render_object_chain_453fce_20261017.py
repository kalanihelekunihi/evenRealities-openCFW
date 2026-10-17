#!/usr/bin/env python3
"""Compare stock/C selected-object render and ancestor sibling order."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_object_chain_453fce.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-object-chain-453fce"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ROOT_RAM, DISPLAY, LAYER = 0x2006f548, 0x20008000, 0x20009000
LEAF, PARENT, GRAND = 0x20010000, 0x20011000, 0x20012000
BEFORE, AFTER, UNCLE = 0x20013000, 0x20014000, 0x20015000
PVECTOR, PTABLE, GVECTOR, GTABLE = 0x20020000, 0x20021000, 0x20022000, 0x20023000
LOWERS = {"audio_uart_display_active_screen_get": 0x44fc62,
          "audio_uart_lv_obj_parent_44dca2": 0x44dca2,
          "audio_uart_lv_draw_color_chain_44c582": 0x44c582,
          "audio_uart_lv_draw_object_4541b6": 0x4541b6,
          "audio_uart_lv_child_count_44ddea": 0x44ddea,
          "audio_uart_lv_obj_event_451670": 0x451670}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "object-chain.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_render_object_chain_453fce",
                    "--defsym=audio_uart_display_lv_root=0x2006f548",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, levels, leaf_position, parent_position,
            null_input, active_available, missing_leaf):
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

        write(ROOT_RAM + 0x10, DISPLAY)
        write(PARENT + 8, PVECTOR)
        write(PVECTOR, PTABLE)
        children = [BEFORE, LEAF, AFTER]
        if missing_leaf:
            children[1] = UNCLE
        elif leaf_position != 1:
            children[1], children[leaf_position] = children[leaf_position], children[1]
        cpu.mem_write(PTABLE, struct.pack("<3I", *children))
        write(GRAND + 8, GVECTOR)
        write(GVECTOR, GTABLE)
        upper = [PARENT, UNCLE]
        if parent_position == 1:
            upper.reverse()
        cpu.mem_write(GTABLE, struct.pack("<2I", *upper))
        write(LAYER + 0x39, 0xaabbccdd)
        cpu.reg_write(A.UC_ARM_REG_R0, LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, 0 if null_input else LEAF)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def tag(pointer):
            return {LEAF: "leaf", PARENT: "parent", GRAND: "grand",
                    BEFORE: "before", AFTER: "after", UNCLE: "uncle"}.get(pointer, pointer)

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x44fc62:
                events.append(("active", r0))
                machine.reg_write(A.UC_ARM_REG_R0, LEAF if active_available else 0)
            elif pc == 0x44dca2:
                events.append(("parent", tag(r0)))
                parent = PARENT if r0 == LEAF and levels >= 1 else (
                    GRAND if r0 == PARENT and levels >= 2 else 0)
                machine.reg_write(A.UC_ARM_REG_R0, parent)
            elif pc == 0x44c582:
                events.append(("color", tag(r0), r1))
                machine.reg_write(A.UC_ARM_REG_R0, 0x11223344)
            elif pc == 0x4541b6:
                events.append(("draw", r0, tag(r1), word(LAYER + 0x39)))
            elif pc == 0x44ddea:
                events.append(("count", tag(r0)))
                machine.reg_write(A.UC_ARM_REG_R0, 3 if r0 == PARENT else 2)
            elif pc == 0x451670:
                events.append(("event", tag(r0), r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x453fce if native else symbols["audio_uart_lv_render_object_chain_453fce"]
        cpu.emu_start(entry | 1, 0, count=5000)
        assert done[0], (native, events)
        return events, word(LAYER + 0x39)

    cases = list(itertools.product((0, 1, 2), (0, 1, 2), (0, 1),
                                   (False, True), (False, True), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"object-chain mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_OBJECT_CHAIN_453FCE_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x453fce..0x454074, including two ancestor levels",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Active screen, parent, color, draw object, child count and event are controlled lower calls.",
                         "Fixture reaches at most two ancestor levels."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()
