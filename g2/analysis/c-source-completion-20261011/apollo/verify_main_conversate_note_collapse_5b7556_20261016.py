#!/usr/bin/env python3
"""Stock/C replay for Conversate note collapse transition 0x5b7556."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_note_collapse_5b7556.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-note-collapse-5b7556"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
    "audio_terminal_fade_out_58c426": (0x101020, 0x58c426, "fadeout"),
    "audio_uart_lv_obj_has_flag_43e0e0": (0x101030, 0x43e0e0, "flag"),
    "audio_uart_page_58c238": (0x101040, 0x58c238, "fadein"),
    "audio_uart_page_43dfa4": (0x101050, 0x43dfa4, "addflag"),
    "audio_uart_lv_obj_width_43fd9e": (0x101060, 0x43fd9e, "width"),
    "audio_uart_lv_obj_height_43fdda": (0x101070, 0x43fdda, "height"),
    "audio_conversate_expand_animation_5b7704": (0x101080, 0x5b7704, "expand"),
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
                    "audio_conversate_ui_route_5b7556",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    "--defsym=audio_conversate_note_collapse_complete_5b7518=0x5b7519",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, root, note, expanded, has_flag, marker):
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
        base = 0x20071368
        for off, value in ((0x1c, root), (0x24, note), (0x2c, expanded),
                           (8, 0x20003000), (0x20, 0x20004000), (0x7c, 0x20005000)):
            cpu.mem_write(base + off, struct.pack("<I", value))
        cpu.mem_write(base + 0x8d, bytes([marker]))
        cpu.mem_write(base + 0x98, b"\x5a")
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
        cpu.reg_write(A.UC_ARM_REG_R1, 0x5678)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in (A.UC_ARM_REG_R0,
                 A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
            value = 0
            if kind == "zero":
                events.append((kind, r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2] & 0xff]) * r[1])
            elif kind == "expand":
                config = bytes(machine.mem_read(r[1], 36))
                events.append((kind, r[0], config, r[2]))
            else:
                args = r[:2] if kind in ("flag", "addflag", "width", "height") else r
                events.append((kind, *args))
                if kind == "flag":
                    value = has_flag
                elif kind == "width":
                    value = 278
                elif kind == "height":
                    value = 127
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b7556 if native else symbols["audio_conversate_ui_route_5b7556"]
        cpu.emu_start(entry | 1, 0, count=260)
        if not done[0]:
            raise RuntimeError("note collapse route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(base + 0x98, 1))

    cases = [(root, note, expanded, has_flag, marker)
             for root in (0, 0x20001000)
             for note in (0, 0x20002000)
             for expanded in (0, 0x20006000)
             for has_flag in (0, 1)
             for marker in (0, 1)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"note collapse mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_NOTE_COLLAPSE_5B7556_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b7556..0x5b7603",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Fade, LVGL and animation scheduler calls remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
