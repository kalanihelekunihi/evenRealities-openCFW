#!/usr/bin/env python3
"""Stock/C lower-call replay for the main-page unselect route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_main_unselected_5b2c68.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-main-unselected-5b2c68"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_lv_child_44dce2": (0x101010, 0x44dce2, "child"),
    "audio_terminal_ui_scroll_to_view_44ea2e": (0x101020, 0x44ea2e, "scroll"),
    "audio_terminal_list_anim_old_start_58c6c4": (0x101030, 0x58c6c4, "fade"),
    "audio_conversate_ui_list_view_mode_set_5b0edc": (0x101040, 0x5b0edc, "mode"),
    "audio_conversate_tag_unselect_5969a4": (0x101050, 0x5969a4, "tag"),
    "audio_conversate_ui_main_page_refresh_5b13fe": (0x101060, 0x5b13fe, "refresh"),
    "audio_log_flags": (0x101070, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101080, 0x43d574, "extended"),
    "compressed_log_output": (0x101090, 0x43ce9e, "compact"),
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
                    "audio_conversate_ui_route_5b2c68",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, list_object, first, selected, previous, flags):
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
        cpu.mem_write(base, bytes([0x5a]) * 0xb0)
        for offset, value in ((0x64, list_object), (0x7c, selected),
                              (0x80, previous), (0x84, 3)):
            cpu.mem_write(base + offset, struct.pack("<I", value))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 256)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2,
                  A.UC_ARM_REG_R3)]
            value = 0
            if kind == "child":
                events.append((kind, r[0], r[1]))
                value = first
            elif kind == "mode":
                events.append((kind, r[0], r[1], cstr(machine, r[2])))
            elif kind in ("tag", "refresh", "flags"):
                events.append((kind,))
                if kind == "flags":
                    value = flags
            elif kind == "extended":
                line, message = struct.unpack("<II", machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 8))
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, message)))
            elif kind == "compact":
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2])))
            elif kind == "scroll":
                events.append((kind, r[0], r[1]))
            else:
                events.append((kind, r[0], r[1], r[2]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b2c68 if native else symbols["audio_conversate_ui_route_5b2c68"]
        cpu.emu_start(entry | 1, 0, count=700)
        if not done[0]:
            raise RuntimeError("main-page unselect did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(base, 0xb0))

    cases = [(list_object, first, selected, previous, flags)
             for list_object in (0, 0x20003000)
             for first in (0, 0x20004000)
             for selected in (0, 0x20005000)
             for previous in (0, 0x20006000)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"main-page unselect mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_MAIN_UNSELECTED_5B2C68_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b2c68..0x5b2d17",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL child and scroll, fade, list mode, tag, refresh and logging remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
