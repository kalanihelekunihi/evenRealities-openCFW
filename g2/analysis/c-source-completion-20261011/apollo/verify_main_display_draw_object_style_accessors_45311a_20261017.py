#!/usr/bin/env python3
"""Compare stock/C draw-object property wrappers and color byte width."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_draw_object_style_accessors_45311a.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-draw-object-style-accessors-45311a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ADDRESSES = [0x45311a, 0x453124, 0x45312e, 0x453138, 0x453142,
             0x45314c, 0x453156, 0x453160, 0x45316a, 0x453180,
             0x45318c, 0x453198, 0x4531a4, 0x441004]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "style-accessors.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_lv_draw_style_metric_45311a",
                    "--defsym=audio_uart_lv_style_property_44bdea=0x44bdea",
                    "--defsym=audio_uart_lv_color_bpp_440f44=0x440f44",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, address, lower_return, selector, format_value):
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
        cpu.reg_write(A.UC_ARM_REG_R0, format_value if address == 0x441004 else 0x20010000)
        cpu.reg_write(A.UC_ARM_REG_R1, selector)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc in (0x44bdea, 0x440f44):
                events.append((pc, machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1),
                               machine.reg_read(A.UC_ARM_REG_R2)))
                machine.reg_write(A.UC_ARM_REG_R0, lower_return)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        name = ("audio_uart_lv_color_format_bytes_441004" if address == 0x441004
                else f"audio_uart_lv_draw_style_metric_{address:x}")
        entry = address if native else symbols[name]
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (native, address, events)
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    values = (0, 1, 0xfc, 0xfd, 0xff, 0x100, 0x12345678, 0xffffffff)
    cases = [(address, value, selector, format_value)
             for address in ADDRESSES for value in values
             for selector, format_value in ((0, 7), (0x1234, 0x107))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"style accessor mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_DRAW_OBJECT_STYLE_ACCESSORS_45311A_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "provider_count": len(ADDRESSES),
              "native_body": "0x45311a..0x4531ae property wrappers plus 0x441004..0x441016",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Style property and color-bpp providers are controlled lower calls.",
                         "Draw-object task assembly is a separate gate."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(path.read_bytes()))


if __name__ == "__main__":
    main()
