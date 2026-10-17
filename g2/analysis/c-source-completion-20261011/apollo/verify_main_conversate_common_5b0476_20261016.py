#!/usr/bin/env python3
"""Bounded native/C Conversate common-data callback comparison."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_common_data_handler_5b0476.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-common-5b0476"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_reply_status_200d6b84": 0x200d6b84,
    "audio_conversate_context_200d5bd8": 0x200d5bd8,
    "audio_conversate_enter_5b01ca": 0x101010,
    "audio_conversate_receive_5b1b4c": 0x101020,
    "audio_conversate_data_handler_5b08a2": 0x101030,
    "audio_conversate_respond_5b200e": 0x101040,
    "audio_conversate_success_5b03c2": 0x101050,
    "audio_conversate_leave_5b0284": 0x101060,
    "audio_log_flags": 0x101070,
    "audio_log_extended": 0x101080,
    "audio_log_simple": 0x101090,
}
NATIVE = {0x5b01ca: "enter", 0x5b1b4c: "receive", 0x5b08a2: "handler",
          0x5b200e: "respond", 0x5b03c2: "success", 0x5b0284: "leave",
          0x43d0ce: "flags", 0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {LOWERS[name]: kind for name, kind in (
    ("audio_conversate_enter_5b01ca", "enter"),
    ("audio_conversate_receive_5b1b4c", "receive"),
    ("audio_conversate_data_handler_5b08a2", "handler"),
    ("audio_conversate_respond_5b200e", "respond"),
    ("audio_conversate_success_5b03c2", "success"),
    ("audio_conversate_leave_5b0284", "leave"),
    ("audio_log_flags", "flags"), ("audio_log_extended", "extended"),
    ("audio_log_simple", "simple"))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    obj, elf_path = OUT / "oracle-common.o", OUT / "oracle-common.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_registry_callback_5b0476",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, status, handler_result, flags, length):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x200d6b84, b"\xaa")
        cpu.mem_write(0x200d5bd8, b"\x00\x42")
        for reg, value in ((A.UC_ARM_REG_R0, event), (A.UC_ARM_REG_R1, 0x20022000),
                           (A.UC_ARM_REG_R2, length), (A.UC_ARM_REG_R3, 0x1234),
                           (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind in ("enter", "leave", "success"):
                events.append((kind,))
            elif kind == "receive":
                events.append((kind, r[0], r[1], r[2]))
                machine.reg_write(A.UC_ARM_REG_R0, status)
            elif kind == "handler":
                events.append((kind, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0, handler_result)
            elif kind == "respond":
                events.append((kind, r[0], machine.mem_read(r[0], 1)[0], r[1]))
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                fmt = string(word(sp+4))
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, word(sp+8) if "%d" in fmt else None))
            elif kind == "simple":
                fmt = string(r[1])
                events.append((kind, r[0], fmt, string(r[2]),
                               r[3] if "%d" in fmt else None))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b0476 if native else symbols["audio_uart_registry_callback_5b0476"]
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]: raise RuntimeError("Conversate callback did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0),
                "reply": cpu.mem_read(0x200d6b84, 1)[0], "events": events}

    cases = []
    for event in (0, 1):
        for status, handler_result in ((13, 0), (7, 0), (0, 0), (0, 9)):
            for flags in (0, 1, 2, 4, 7):
                for length in (5, 0x10005):
                    fixture = [event, status, handler_result, flags, length]
                    native_result = run(True, *fixture)
                    compiled_result = run(False, *fixture)
                    if native_result != compiled_result:
                        raise RuntimeError(f"Conversate mismatch {fixture}: {native_result} != {compiled_result}")
                    cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_COMMON_5B0476_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Conversate RAM and deeper receive/response children are controlled contracts.",
                         "Selected event, status and log paths only; arbitrary packet behavior remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
