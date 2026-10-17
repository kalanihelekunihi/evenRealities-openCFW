#!/usr/bin/env python3
"""Direct stock/C replay of the Conversate display report boundary."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_report_5b02e4.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-report-5b02e4"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_device_role_get": (0x101010, 0x45a568, "role"),
    "audio_quicklist_refresh_enabled_4434d0": (0x101020, 0x4434d0, "enabled"),
    "audio_conversate_ui_event_name_5b16fc": (0x101030, 0x5b16fc, "name"),
    "audio_log_flags": (0x101040, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101050, 0x43d574, "extended"),
    "audio_log_simple": (0x101060, 0x43ce9e, "simple"),
    "audio_uart_master_display_refresh": (0x101070, 0x464bb2, "send"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_report_5b02e4",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, value, role, enabled, flags, send_result):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x101e00, b"TEST_EVENT_NAME\0")
        cpu.reg_write(A.UC_ARM_REG_R0, event)
        cpu.reg_write(A.UC_ARM_REG_R1, value)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def string(ptr):
            if not ptr: return ""
            return bytes(cpu.mem_read(ptr, 256)).split(b"\0", 1)[0].decode("latin1")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r0, r1, r2, r3 = [machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "enabled":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, enabled)
            elif kind == "name":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x101e00)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, fmt = struct.unpack("<II", bytes(machine.mem_read(sp, 8)))
                args = struct.unpack("<III", bytes(machine.mem_read(sp + 8, 12))) if line == 126 else ()
                norm = (args[0], string(args[1]), args[2]) if args else ()
                events.append((kind, r0, string(r1), string(r2), string(r3),
                               line, string(fmt), norm))
            elif kind == "simple":
                args = struct.unpack("<II", bytes(machine.mem_read(sp, 8))) if r0 == 0x0cc00000 else ()
                norm = (r3, string(args[0]), args[1]) if args else ()
                events.append((kind, r0, string(r1), string(r2), norm))
            elif kind == "send":
                packet = bytes(machine.mem_read(r1, 8))
                events.append((kind, r0, packet[0], int.from_bytes(packet[4:8], "little"), r2, r3))
                machine.reg_write(A.UC_ARM_REG_R0, send_result)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b02e4 if native else symbols["audio_conversate_report_5b02e4"])|1,
                      0, count=700)
        if not done[0]: raise RuntimeError("Conversate report did not return")
        return events

    cases = [(event, value, role, enabled, flags, send_result)
             for event in (0, 4, 17, 255, 0x101)
             for value in (0, 0x12345678)
             for role in (0, 1, 2)
             for enabled in (0, 1, 2)
             for flags in (0, 1, 2, 4, 7)
             for send_result in (0, 0x55aa55aa)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"Conversate report mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_REPORT_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b02e4..0x5b03c1",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "UI event-name provider at 0x5b16fc remains unresolved.",
              "limits": ["Packet padding bytes are unspecified in stock stack storage and excluded from comparison.",
                         "Incidental return register is excluded because the linked display-refresh provider has a void C contract."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
