#!/usr/bin/env python3
"""Direct stock/C comparison of Conversate list-button style setter."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_slot_fade_5b1072.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-ui-slot-fade-5b1072"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_terminal_ui_object_valid_43e2ea": (0x101010, 0x43e2ea, "valid"),
    "audio_terminal_session_row_show_5897ee": (0x101020, 0x5897ee, "show"),
    "audio_terminal_session_row_hide_589892": (0x101030, 0x589892, "hide"),
    "audio_uart_page_44130c": (0x101040, 0x44130c, "opacity"),
    "audio_log_flags": (0x101050, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101060, 0x43d574, "extended"),
    "compressed_log_output": (0x101070, 0x43ce9e, "compressed"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("authenticated Main payload changed")
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_slot_fade_5b1072",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, object_value, valid, mode, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        cpu.reg_write(A.UC_ARM_REG_R0, object_value)
        cpu.reg_write(A.UC_ARM_REG_R1, mode)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(address):
            result = bytearray()
            for i in range(160):
                value = cpu.mem_read(address+i, 1)[0]
                if value == 0:
                    return result.decode("utf-8", "replace")
                result.append(value)
            raise RuntimeError("unterminated log string")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            r1 = machine.reg_read(A.UC_ARM_REG_R1)
            r2 = machine.reg_read(A.UC_ARM_REG_R2)
            r3 = machine.reg_read(A.UC_ARM_REG_R3)
            if kind == "valid":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, valid)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind in ("show", "hide"):
                events.append((kind, r0))
            elif kind == "opacity":
                events.append((kind, r0, r1, r2))
            elif kind == "extended":
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                events.append((kind, r0, cstr(r1), cstr(r2), cstr(r3), line, cstr(fmt)))
            else:
                events.append((kind, r0, cstr(r1), cstr(r2), r3 if r0 == 0x08400000 else None))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b1072 if native else symbols["audio_conversate_ui_slot_fade_5b1072"]
        cpu.emu_start(entry | 1, 0, count=300)
        if not done[0]:
            raise RuntimeError("slot fade did not return")
        return events

    cases = [(object_value, valid, mode, flags)
             for object_value in (0, 0x20008000)
             for valid in (0, 1)
             for mode in (0, 1, 2, 255)
             for flags in (0, 1, 2, 4)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"slot fade mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_SLOT_FADE_5B1072_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b1072..0x5b114f",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Object-valid, row show/hide, style setter and logging sinks are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
