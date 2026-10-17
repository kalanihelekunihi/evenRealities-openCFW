#!/usr/bin/env python3
"""Controlled stock/C comparison for LVGL object redraw at 0x4531ae."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_obj_redraw_4531ae.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-obj-redraw-4531ae"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_display_area_copy_439c04": 0x439c04,
    "audio_uart_lv_obj_coords_43fc2a": 0x43fc2a,
    "audio_uart_lv_obj_ext_draw_size_452dc8": 0x452dc8,
    "audio_uart_lv_area_expand_450b98": 0x450b98,
    "audio_uart_lv_area_intersect_450bcc": 0x450bcc,
    "audio_uart_lv_obj_event_451670": 0x451670,
    "audio_uart_lv_obj_has_flag_43e0e0": 0x43e0e0,
    "audio_uart_lv_child_count_44ddea": 0x44ddea,
    "audio_uart_lv_draw_style_metric_453160": 0x453160,
    "audio_uart_lv_draw_style_metric_45316a": 0x45316a,
    "audio_uart_lv_draw_object_4541b6": 0x4541b6,
    "audio_uart_lv_mask_rect_dsc_init_48a984": 0x48a984,
    "audio_uart_ambiq_image_options_init_488918": 0x488918,
    "audio_uart_lv_area_width_451598": 0x451598,
    "audio_uart_lv_area_height_4515a4": 0x4515a4,
    "audio_uart_lv_draw_layer_create_48475e": 0x48475e,
    "audio_uart_lv_draw_mask_rect_48a98e": 0x48a98e,
    "audio_uart_lv_draw_layer_48895e": 0x48895e,
}
LAYER, OBJECT, SPEC, TABLE = 0x20010000, 0x20011000, 0x20012000, 0x20013000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "obj-redraw.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_obj_redraw_4531ae",
                    *(f"--defsym={name}=0x{address|1:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, coords, clip, extra, count, overflow, corner, radius):
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
        def put(address, value):
            cpu.mem_write(address, struct.pack("<I", value & 0xffffffff))
        def area(address):
            return struct.unpack("<4i", cpu.mem_read(address, 16))
        def write_area(address, values):
            cpu.mem_write(address, struct.pack("<4i", *values))
        write_area(LAYER + 0x18, clip)
        write_area(OBJECT + 0x14, coords)
        put(OBJECT + 8, SPEC)
        put(SPEC, TABLE)
        put(TABLE, 0x20014000)
        put(TABLE + 4, 0x20014100)
        cpu.reg_write(A.UC_ARM_REG_R0, LAYER)
        cpu.reg_write(A.UC_ARM_REG_R1, OBJECT)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done, child_index = [], [False], [0]

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
            value = 0
            if pc == 0x439c04:
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
                events.append(("copy", r2, bytes(machine.mem_read(r0, r2)).hex()))
                value = r0
            elif pc == 0x43fc2a:
                events.append(("coords", r0))
                write_area(r1, coords)
            elif pc == 0x452dc8:
                events.append(("extra", r0))
                value = extra
            elif pc == 0x450b98:
                events.append(("expand", area(r0), r1, r2))
                x1, y1, x2, y2 = area(r0)
                write_area(r0, (x1 - r1, y1 - r2, x2 + r1, y2 + r2))
            elif pc == 0x450bcc:
                left, right = area(r1), area(r2)
                result = (max(left[0], right[0]), max(left[1], right[1]),
                          min(left[2], right[2]), min(left[3], right[3]))
                value = int(result[0] <= result[2] and result[1] <= result[3])
                write_area(r0, result)
                events.append(("intersect", left, right, value))
            elif pc == 0x451670:
                events.append(("event", r1, r2))
                value = 1
            elif pc == 0x43e0e0:
                events.append(("flag", r1))
                value = int(overflow)
            elif pc == 0x44ddea:
                events.append(("count",))
                value = count
            elif pc in (0x453160, 0x45316a):
                events.append(("radius" if pc == 0x453160 else "corner",))
                value = radius if pc == 0x453160 else corner
            elif pc == 0x4541b6:
                events.append(("child", r0, r1))
            elif pc == 0x48a984:
                events.append(("mask_init",))
                machine.mem_write(r0, bytes(0x34))
            elif pc == 0x488918:
                events.append(("image_init",))
                machine.mem_write(r0, bytes(0x6c))
                put(r0 + 0x34, 256)
                put(r0 + 0x38, 256)
                put(r0 + 0x60, 0xe0000001)
            elif pc in (0x451598, 0x4515a4):
                events.append(("width" if pc == 0x451598 else "height", area(r0)))
                x1, y1, x2, y2 = area(r0)
                value = x2 - x1 + 1 if pc == 0x451598 else y2 - y1 + 1
            elif pc == 0x48475e:
                events.append(("create", r1, area(r2)))
                value = 0x20015000 + child_index[0] * 0x100
                child_index[0] += 1
            elif pc == 0x48a98e:
                events.append(("mask_draw", r0,
                               bytes(machine.mem_read(r1, 0x34)).hex()))
            elif pc == 0x48895e:
                events.append(("layer_draw", r0,
                               bytes(machine.mem_read(r1, 0x6c)).hex(),
                               area(r2)))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4531ae if native else symbols["audio_uart_lv_obj_redraw_4531ae"]
        cpu.emu_start(entry | 1, 0, count=3000)
        assert done[0], (native, events)
        return events, area(LAYER + 0x18)

    cases = [(coords, clip, extra, count, overflow, corner, radius)
             for coords, clip, extra, count, overflow, corner, radius in
             (( (10, 10, 50, 50), (0, 0, 100, 100), 2, 0, 0, 0, 0),
              ( (200, 200, 240, 240), (0, 0, 100, 100), 2, 0, 0, 0, 0),
              ( (102, 10, 110, 30), (0, 0, 100, 100), 4, 1, 0, 0, 0),
              ( (10, 10, 50, 50), (0, 0, 100, 100), 2, 2, 0, 0, 0),
              ( (10, 10, 50, 50), (0, 0, 100, 100), 2, 2, 1, 1, 0),
              ( (10, 10, 50, 50), (0, 0, 100, 100), 2, 2, 0, 1, 5),
              ( (10, 10, 50, 50), (0, 0, 100, 100), 2, 1, 0, 1, 40),
              ( (10, 10, 50, 50), (0, 25, 100, 35), 2, 1, 0, 1, 5))]
    cases += [(coords, clip, 2, count, overflow, 1, radius)
              for coords, clip, count, overflow, radius in itertools.product(
                  ((10, 10, 30, 60), (10, 10, 60, 30)),
                  ((0, 0, 100, 100), (0, 20, 100, 40)),
                  (0, 2), (0, 1), (0, 5, 40))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"object-redraw mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_DISPLAY_OBJ_REDRAW_4531AE_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Events, area operations, child draw, mask and layer drawing are controlled lower calls."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
