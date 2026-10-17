#!/usr/bin/env python3
"""Bounded stock/C oracle for the direct and early-return refr_obj paths."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_draw_object_4541b6.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-draw-object-4541b6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_obj_has_flag_43e0e0": 0x43e0e0,
    "audio_uart_lv_scrollbar_mode_452dd8": 0x452dd8,
    "audio_uart_lv_draw_color_composite_44c54a": 0x44c54a,
    "audio_uart_lv_obj_redraw_4531ae": 0x4531ae,
    "audio_uart_lv_render_area_select_454074": 0x454074,
    "audio_uart_lv_render_cover_event_45417c": 0x45417c,
    "audio_uart_lv_area_height_4515a4": 0x4515a4,
    "audio_uart_lv_area_width_451598": 0x451598,
    "audio_uart_lv_color_format_bytes_441004": 0x441004,
    "audio_uart_lv_draw_layer_create_48475e": 0x48475e,
    "audio_uart_ambiq_image_options_init_488918": 0x488918,
    "audio_uart_lv_draw_layer_48895e": 0x48895e,
    "audio_uart_display_area_copy_439c04": 0x439c04,
    **{f"audio_uart_lv_draw_style_metric_{address:x}": address for address in
       (0x45311a, 0x453124, 0x45312e, 0x453138, 0x453142,
        0x45314c, 0x453156, 0x453180, 0x45318c, 0x453198, 0x4531a4)},
    "audio_uart_display_lv_root": 0x20020000,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "draw-object.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_draw_object_4541b6",
                    *(f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, hidden, layered, opa, kind, select, tiled=False,
            mask=0, alpha=0, pivot_x=2, pivot_y=3, right=19, bottom=22,
            rotation=0):
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
        layer, object_addr = 0x20010000, 0x20011000
        for root in (0x20020000, 0x2006f548):
            cpu.mem_write(root + 0x10, struct.pack("<I", 0x20030000))
        cpu.mem_write(0x20030000 + 0x3c, bytes((6,)))
        cpu.mem_write(0x20030000 + 0x38, struct.pack("<I", 0x10000))
        cpu.mem_write(object_addr + 0x14, struct.pack("<4i", 10, 20, right, bottom))
        cpu.mem_write(0x20012000 + 4, struct.pack("<2i", 10, 20))
        cpu.mem_write(layer + 0x38, bytes((199,)))
        cpu.mem_write(layer + 0x39, struct.pack("<I", 0x12345678))
        cpu.reg_write(A.UC_ARM_REG_R0, layer)
        cpu.reg_write(A.UC_ARM_REG_R1, object_addr)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc not in LOWERS.values():
                return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            r1 = machine.reg_read(A.UC_ARM_REG_R1)
            r2 = machine.reg_read(A.UC_ARM_REG_R2)
            if pc == 0x43e0e0:
                events.append(("hidden", r0, r1))
                result = hidden
            elif pc in (0x45318c, 0x453180):
                events.append(("layered" if pc == 0x45318c else "opa", r0, r1))
                result = layered if pc == 0x45318c else opa
            elif pc == 0x44c54a:
                events.append(("recolor", r0, r1, r2))
                result = 0x87654321
            elif pc == 0x452dd8:
                events.append(("type", r0))
                result = kind
            elif pc == 0x4531ae:
                events.append(("redraw", r0, r1,
                               bytes(machine.mem_read(layer + 0x38, 5)).hex()))
                result = 0
            elif pc == 0x454074:
                events.append(("select", r0, r1, r2))
                result = select
                if tiled:
                    r3 = machine.reg_read(A.UC_ARM_REG_R3)
                    sp = machine.reg_read(A.UC_ARM_REG_SP)
                    area_out = struct.unpack("<I", machine.mem_read(sp, 4))[0]
                    machine.mem_write(r3, struct.pack("<4i", 10, 20, right, bottom))
                    machine.mem_write(area_out, struct.pack("<4i", 10, 20, right, bottom))
            elif pc in (0x4515a4, 0x451598):
                x1, y1, x2, y2 = struct.unpack("<4i", machine.mem_read(r0, 16))
                events.append(("height" if pc == 0x4515a4 else "width",))
                result = y2 - y1 + 1 if pc == 0x4515a4 else x2 - x1 + 1
            elif pc == 0x4531a4:
                events.append(("mask",))
                result = mask
            elif pc == 0x45417c:
                events.append(("alpha",))
                result = alpha
            elif pc == 0x441004:
                events.append(("pixel_bytes", r0))
                result = 4
            elif pc == 0x48475e:
                events.append(("create", r1, tuple(struct.unpack("<4i", machine.mem_read(r2, 16)))))
                result = 0x20012000
            elif pc in (0x453138, 0x453142, 0x45312e, 0x45311a,
                        0x453124, 0x45314c, 0x453156, 0x453198):
                events.append((f"style_{pc:x}",))
                result = {0x453138: pivot_x, 0x453142: pivot_y,
                          0x45312e: rotation,
                          0x45311a: 256, 0x453124: 256, 0x45314c: 0,
                          0x453156: 0, 0x453198: 0}[pc]
            elif pc == 0x488918:
                events.append(("init",))
                machine.mem_write(r0, bytes(0x6c))
                result = 0
            elif pc == 0x439c04:
                machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
                result = r0
            elif pc == 0x48895e:
                events.append(("draw", bytes(machine.mem_read(r1, 0x6c)).hex(),
                               tuple(struct.unpack("<4i", machine.mem_read(r2, 16)))))
                result = 0
            else:
                raise RuntimeError(f"unexpected lower 0x{pc:x}")
            machine.reg_write(A.UC_ARM_REG_R0, result)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4541b6 if native else symbols["audio_uart_lv_draw_object_4541b6"]
        cpu.emu_start(entry | 1, 0, count=3000)
        assert done[0], (native, events)
        return events, bytes(cpu.mem_read(layer + 0x38, 5)).hex()

    cases = [(hidden, layered, opa, kind, select)
             for hidden, layered, opa, kind, select in
             ((1, 255, 255, 0, 1), (0, 0, 255, 0, 1),
              (0, 1, 100, 0, 1), (0, 2, 255, 0, 1),
              (0, 255, 100, 0, 1), (0, 200, 252, 2, 0),
              (0, 100, 253, 1, 0))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"draw object mismatch {case}: {stock} != {compiled}")
    tile_cases = [
        ((0, 255, 255, 2, 1, True), {}),
        ((0, 255, 255, 2, 1, True), {"alpha": 1}),
        ((0, 255, 255, 2, 1, True), {"mask": 0x20035000}),
        ((0, 255, 255, 1, 1, True), {"right": 32777, "bottom": 23}),
        ((0, 255, 255, 1, 1, True), {"right": 32777, "bottom": 23,
                                      "pivot_x": 0x20000032, "pivot_y": 0x2fffffcd}),
        ((0, 100, 127, 1, 1, True), {"right": 32777, "bottom": 24,
                                     "mask": 0x20035000, "rotation": 3601}),
        ((0, 2, 2, 2, 1, True), {"pivot_x": 0x3fffffff,
                                "pivot_y": 0x20000000, "rotation": -1}),
        ((0, 254, 254, 2, 1, True), {"pivot_x": 0x3ffffffe,
                                    "pivot_y": 0x20000032, "rotation": -3601}),
    ]
    for tile_case, options in tile_cases:
        stock, compiled = run(True, *tile_case, **options), run(False, *tile_case, **options)
        if stock != compiled:
            raise RuntimeError(f"draw object tiled mismatch {tile_case} {options}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_DISPLAY_DRAW_OBJECT_4541B6_C",
              "cases": len(cases) + len(tile_cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["The tiled task path has eight controlled cases; broader property variants remain open.",
                         "Three lower layer and redraw providers remain unresolved."]}
    receipt = OUT / "oracle-direct-receipt.json"
    receipt.write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
    print(record["status"], len(cases) + len(tile_cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
