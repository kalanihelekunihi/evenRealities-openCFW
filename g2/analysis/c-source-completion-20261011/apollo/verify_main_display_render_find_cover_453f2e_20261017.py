#!/usr/bin/env python3
"""Compare stock/C LVGL cover-finder exits and reverse child recursion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_find_cover_453f2e.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-find-cover-453f2e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
AREA, ROOT_OBJ, CHILD1, CHILD2 = 0x20008000, 0x20010000, 0x20011000, 0x20012000
VECTOR, TABLE = 0x20020000, 0x20021000
LOWERS = {"audio_uart_lv_area_contains_450f28": 0x450f28,
          "audio_uart_lv_obj_has_flag_43e0e0": 0x43e0e0,
          "audio_uart_lv_scrollbar_mode_452dd8": 0x452dd8,
          "audio_uart_lv_style_property_44bdea": 0x44bdea,
          "audio_uart_lv_obj_event_451670": 0x451670,
          "audio_uart_lv_child_count_44ddea": 0x44ddea}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "find-cover.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_render_find_cover_453f2e",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, contains, hidden, scroll, opacity, result, count,
            child_cover):
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
        cpu.mem_write(AREA, struct.pack("<4i", 1, 2, 7, 8))
        cpu.mem_write(ROOT_OBJ + 8, struct.pack("<I", VECTOR))
        cpu.mem_write(VECTOR, struct.pack("<I", TABLE))
        cpu.mem_write(TABLE, struct.pack("<II", CHILD1, CHILD2))
        cpu.reg_write(A.UC_ARM_REG_R0, AREA)
        cpu.reg_write(A.UC_ARM_REG_R1, ROOT_OBJ)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def object_tag(pointer):
            return {ROOT_OBJ: "root", CHILD1: "first", CHILD2: "second"}.get(pointer, pointer)

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x450f28:
                tag = object_tag(r1 - 0x14)
                events.append(("contains", tag, r2))
                machine.reg_write(A.UC_ARM_REG_R0, int(contains) if tag == "root" else 1)
            elif pc == 0x43e0e0:
                tag = object_tag(r0)
                events.append(("flag", tag, r1))
                machine.reg_write(A.UC_ARM_REG_R0, int(hidden) if tag == "root" else 0)
            elif pc == 0x452dd8:
                tag = object_tag(r0)
                events.append(("scroll", tag))
                machine.reg_write(A.UC_ARM_REG_R0, int(scroll) if tag == "root" else 0)
            elif pc == 0x44bdea:
                tag = object_tag(r0)
                events.append(("opacity", tag, r1, r2))
                machine.reg_write(A.UC_ARM_REG_R0, opacity if tag == "root" else 255)
            elif pc == 0x451670:
                tag = object_tag(r0)
                payload_area = struct.unpack("<I", machine.mem_read(r2 + 4, 4))[0]
                events.append(("event", tag, r1, payload_area))
                value = result if tag == "root" else (
                    0 if (tag == "second" and child_cover) else 1)
                machine.mem_write(r2, bytes((value,)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == 0x44ddea:
                tag = object_tag(r0)
                events.append(("count", tag))
                machine.reg_write(A.UC_ARM_REG_R0, count if tag == "root" else 0)
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x453f2e if native else symbols["audio_uart_lv_render_find_cover_453f2e"]
        cpu.emu_start(entry | 1, 0, count=5000)
        assert done[0], (native, events)
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = list(itertools.product((False, True), (False, True),
                                   (False, True), (252, 253, 255),
                                   (0, 1, 2), (0, 1, 2), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"cover finder mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_FIND_COVER_453F2E_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x453f2e..0x453fce, including bounded recursion",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Containment, flags, scrollbar mode, style property, event and child count are controlled lower calls.",
                         "Fixture has at most two direct children and no grandchildren."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()
