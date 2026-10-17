#!/usr/bin/env python3
"""Compare stock/C LVGL render-area selection and cover-event gate."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_render_area_helpers_454074.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-render-area-helpers-454074"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LAYER, OBJECT, OUTPUT, OBJECT_AREA = 0x20010000, 0x20011000, 0x20012000, 0x20013000
LOWERS = {"audio_uart_lv_obj_ext_draw_size_452dc8": 0x452dc8,
          "audio_uart_lv_obj_coords_43fc2a": 0x43fc2a,
          "audio_uart_lv_area_expand_450b98": 0x450b98,
          "audio_uart_display_area_copy_439c04": 0x439c04,
          "audio_uart_lv_obj_adjust_area_440494": 0x440494,
          "audio_uart_lv_area_intersect_450bcc": 0x450bcc,
          "audio_uart_lv_area_overlap_450f00": 0x450f00,
          "audio_uart_lv_obj_event_451670": 0x451670,
          "audio_uart_lvgl_log": 0x44d25c}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "area-helpers.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_render_area_select_454074",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, kind, extra, first_ok, second_ok, cover_ok, event_result):
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

        def area(address):
            return struct.unpack("<4i", cpu.mem_read(address, 16))

        def write_area(address, values):
            cpu.mem_write(address, struct.pack("<4i", *values))

        def signed(value):
            return struct.unpack("<i", struct.pack("<I", value))[0]

        write_area(LAYER + 0x18, (0, 0, 8, 8))
        write_area(OBJECT + 0x14, (2, 3, 12, 13))
        write_area(OUTPUT, (-20, -20, -10, -10))
        write_area(OBJECT_AREA, (-30, -30, -15, -15))
        cpu.reg_write(A.UC_ARM_REG_R0, OBJECT if kind == 9 else LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, OUTPUT if kind == 9 else OBJECT)
        cpu.reg_write(A.UC_ARM_REG_R2, kind)
        cpu.reg_write(A.UC_ARM_REG_R3, OUTPUT)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.mem_write(0x200ff000, struct.pack("<I", OBJECT_AREA))
        events, done, intersects = [], [False], [0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc == 0x452dc8:
                events.append(("extra", r0))
                machine.reg_write(A.UC_ARM_REG_R0, extra)
            elif pc == 0x43fc2a:
                events.append(("coords", r0))
                write_area(r1, (2, 3, 12, 13))
            elif pc == 0x450b98:
                events.append(("expand", area(r0), signed(r1), signed(r2)))
                a = area(r0)
                write_area(r0, (a[0] - signed(r1), a[1] - signed(r2),
                                a[2] + signed(r1), a[3] + signed(r2)))
            elif pc == 0x439c04:
                events.append(("copy", area(r1), r2))
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
            elif pc == 0x440494:
                events.append(("adjust", r0, area(r1), r2))
                a = area(r1)
                write_area(r1, (a[0] + 1, a[1] + 1, a[2] + 1, a[3] + 1))
            elif pc == 0x450bcc:
                intersects[0] += 1
                ok = first_ok if intersects[0] == 1 else second_ok
                events.append(("intersect", area(r1), area(r2), ok))
                a, b = area(r1), area(r2)
                write_area(r0, (max(a[0], b[0]), max(a[1], b[1]),
                                min(a[2], b[2]), min(a[3], b[3])))
                machine.reg_write(A.UC_ARM_REG_R0, int(ok))
            elif pc == 0x450f00:
                events.append(("overlap", area(r0), area(r1), cover_ok))
                machine.reg_write(A.UC_ARM_REG_R0, int(cover_ok))
            elif pc == 0x451670:
                event_area = struct.unpack("<I", machine.mem_read(r2 + 4, 4))[0]
                events.append(("event", r0, r1, event_area))
                machine.mem_write(r2, bytes((event_result,)))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
            elif pc == 0x44d25c:
                def cstr(address):
                    return bytes(machine.mem_read(address, 128)).split(b"\0")[0].decode()
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                events.append(("log", r0, cstr(r1), r2,
                               cstr(machine.reg_read(A.UC_ARM_REG_R3)),
                               cstr(struct.unpack("<I", machine.mem_read(sp, 4))[0])))
            else:
                return
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = (0x45417c if native else symbols["audio_uart_lv_render_cover_event_45417c"]) if kind == 9 else (
                 0x454074 if native else symbols["audio_uart_lv_render_area_select_454074"])
        cpu.emu_start(entry | 1, 0, count=5000)
        assert done[0], (native, events)
        return events, cpu.reg_read(A.UC_ARM_REG_R0), area(OUTPUT), area(OBJECT_AREA)

    area_cases = list(itertools.product((0, 1, 2, 3), (0, 3),
                                        (False, True), (False, True)))
    cover_cases = [(9, 0, True, True, cover_ok, event_result)
                   for cover_ok in (False, True) for event_result in (0, 1, 2)]
    for case in area_cases:
        full = (*case, True, 0)
        stock, compiled = run(True, *full), run(False, *full)
        if stock != compiled:
            raise RuntimeError(f"render area mismatch {full}: {stock} != {compiled}")
    for case in cover_cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"cover event mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_RENDER_AREA_HELPERS_454074_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "cases": len(area_cases) + len(cover_cases),
              "native_body": "0x454074..0x454152 plus 0x45417c..0x4541b6",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Geometry, area operations, object events and logging are controlled lower calls.",
                         "Layer draw-task behavior remains with draw object 0x4541b6."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(path.read_bytes()))


if __name__ == "__main__":
    main()
