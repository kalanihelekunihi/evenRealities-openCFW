#!/usr/bin/env python3
"""Direct stock/C replay of Conversate close timer label route."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_auto_duration_label_5b68d6.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-auto-duration-label-5b68d6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_lv_child_44dce2": (0x101010, 0x44dce2, "child"),
    "audio_terminal_ui_object_valid_43e2ea": (0x101020, 0x43e2ea, "valid"),
    "audio_uart_page_460084": (0x101030, 0x460084, "key"),
    "audio_uart_page_45fffe": (0x101040, 0x45fffe, "lookup"),
    "audio_lv_label_set_text_fmt_49954c": (0x101050, 0x49954c, "label"),
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
                    "audio_conversate_ui_route_5b68d6",
                    "--defsym=audio_conversate_ui_state_20071368=0x20071368",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, root, hidden, first_valid, label_valid, seconds):
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
        cpu.mem_write(0x20071368 + 0x1c, struct.pack("<I", root))
        cpu.mem_write(0x20071368 + 0x96, bytes([hidden]))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
        cpu.reg_write(A.UC_ARM_REG_R1, seconds)
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
            if kind == "child":
                events.append((kind, r[0], r[1]))
                value = 0x20002000 if r[1] == 0 else 0x20003000
            elif kind == "valid":
                events.append((kind, r[0]))
                value = first_valid if r[0] == 0x20002000 else label_valid
            elif kind == "key":
                value = 17
                events.append((kind, bytes(machine.mem_read(r[0], 32)).split(b"\0", 1)[0]))
            elif kind == "lookup":
                value = 0x20004000
                events.append((kind, bytes(machine.mem_read(r[0], 32)).split(b"\0", 1)[0], r[1]))
            else:
                value = 0
                events.append((kind, r[0], r[1], r[2]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b68d6 if native else symbols["audio_conversate_ui_route_5b68d6"]
        cpu.emu_start(entry | 1, 0, count=150)
        if not done[0]:
            raise RuntimeError("duration label route did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = [(root, hidden, first, label, seconds)
             for root in (0, 0x20001000)
             for hidden in (0, 1)
             for first in (0, 1)
             for label in (0, 1)
             for seconds in (0, 1, 42, 0xffffffff)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"duration label mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_AUTO_DURATION_LABEL_5B68D6_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b68d6..0x5b6941",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL object validity and localization remain controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
