#!/usr/bin/env python3
"""Direct stock/C replay of prep-note line count, scroll extent, and clamp."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_prep_scroll_bounds_5b6a06.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-prep-scroll-bounds-5b6a06"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = {
    "audio_conversate_prep_note_line_count_5b4770": 0x5b4770,
    "audio_conversate_prep_scroll_max_5b6a06": 0x5b6a06,
    "audio_conversate_prep_scroll_clamp_5b6a3a": 0x5b6a3a,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_prep_scroll_clamp_5b6a3a",
                    "--defsym=audio_conversate_prep_note_ram_200d7630=0x200d7630",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    "--defsym=audio_uart_lv_obj_height_43fdda=0x101011",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, name, note, height, count, requested):
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
        cpu.mem_write(0x20071368 + 0x24, struct.pack("<I", note))
        cpu.mem_write(0x200d7630 + 0x109a, struct.pack("<H", count))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, requested & 0xffffffff)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc != (0x43fdda if native else 0x101010):
                return
            arg = machine.reg_read(A.UC_ARM_REG_R0)
            events.append(("height", arg))
            machine.reg_write(A.UC_ARM_REG_R0, height & 0xffffffff)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ENTRIES[name] if native else symbols[name]
        cpu.emu_start(entry | 1, 0, count=130)
        if not done[0]:
            raise RuntimeError("prep scroll bounds did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = [(note, height, count, requested)
             for note in (0, 0x20001000)
             for height in (-1, 0, 27, 28, 100)
             for count in (0, 1, 10, 65535)
             for requested in (-1, 0, 1, 28, 10000)]
    for case in cases:
        for name in ENTRIES:
            stock, selected = run(True, name, *case), run(False, name, *case)
            if stock != selected:
                raise RuntimeError(f"prep scroll bounds mismatch {name} {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_PREP_SCROLL_BOUNDS_5B6A06_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) * len(ENTRIES),
              "native_bodies": ["0x5b4770..0x5b4775", "0x5b6a06..0x5b6a39", "0x5b6a3a..0x5b6a51"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL height remains a controlled lower boundary.",
                         "This source owns scroll bounds, not the full prep-note route."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
