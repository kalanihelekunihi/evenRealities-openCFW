#!/usr/bin/env python3
"""Stock/C lower-call replay for the Conversate transcribe-label update."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_transcribe_label_update_5b32b4.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-transcribe-label-update-5b32b4"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_lv_child_44dce2": (0x101010, 0x44dce2, "child"),
    "audio_conversate_transcribe_get_5b4364": (0x101020, 0x5b4364, "get"),
    "audio_uart_page_49942e": (0x101030, 0x49942e, "text"),
    "audio_uart_lv_obj_height_43fdda": (0x101040, 0x43fdda, "height"),
    "audio_terminal_display_status_44ea04": (0x101050, 0x44ea04, "scroll"),
    "audio_log_flags": (0x101060, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101070, 0x43d574, "extended"),
    "compressed_log_output": (0x101080, 0x43ce9e, "compact"),
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
                    "audio_conversate_ui_route_5b32b4",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, parent, label, text, parent_height, label_height, flags):
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
        cpu.mem_write(base, bytes(0xb0))
        cpu.mem_write(base + 0x20, struct.pack("<I", parent))
        cpu.mem_write(0x200e2ae4, b"hello transcript\0")
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
                value = label
            elif kind == "get":
                events.append((kind,))
                value = text
            elif kind == "text":
                events.append((kind, r[0], r[1]))
            elif kind == "height":
                events.append((kind, r[0]))
                value = parent_height if r[0] == parent else label_height
            elif kind == "scroll":
                events.append((kind, r[0], r[1], r[2]))
            elif kind == "flags":
                events.append((kind,))
                value = flags
            elif kind == "extended":
                line, message = struct.unpack("<II", machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 8))
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, message)))
            else:
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2])))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b32b4 if native else symbols["audio_conversate_ui_route_5b32b4"]
        cpu.emu_start(entry | 1, 0, count=700)
        if not done[0]:
            raise RuntimeError("transcribe-label update did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(base, 0xb0))

    cases = [(parent, label, text, ph, lh, flags)
             for parent in (0, 0x20003000)
             for label in (0, 0x20004000)
             for text in (0, 0x200e2ae4)
             for ph, lh in ((120, 40), (40, 120), (120, 120))
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"transcribe-label update mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TRANSCRIBE_LABEL_UPDATE_5B32B4_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b32b4..0x5b332d",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Child lookup, transcribe getter, LVGL height, scroll and log transport remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
