#!/usr/bin/env python3
"""Stock/C comparison for the Conversate heartbeat stop/check leaf."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_stop_5b03d8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-stop-5b03d8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_device_role_get": (0x101010, 0x45a568, "role"),
    "g2_flashdb_candidate_tick": (0x101020, 0x4490cc, "tick"),
    "audio_log_flags": (0x101030, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101040, 0x43d574, "extended"),
    "audio_log_simple": (0x101050, 0x43ce9e, "simple"),
    "audio_conversate_success_5b03c2": (0x101060, 0x5b03c2, "success"),
    "audio_uart_ring_wear_persist_48eb32": (0x101070, 0x48eb32, "persist"),
    "audio_conversate_report_5b02e4": (0x101080, 0x5b02e4, "report"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-stop.o", OUT / "oracle-stop.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_stop_5b03d8",
                    "--defsym=audio_conversate_last_success_tick_20074394=0x20074394",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, role, elapsed, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20074394, struct.pack("<I", 0x12345678))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "tick":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, (0x12345678 + elapsed)&0xffffffff)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4)), word(sp+8), word(sp+12)))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2]), r[3], word(sp)))
            elif kind == "persist":
                events.append((kind, r[0], r[1], bytes(machine.mem_read(r[2], 8)).hex()))
            elif kind == "report":
                events.append((kind, r[0], r[1]))
            else:
                events.append((kind,))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b03d8 if native else symbols["audio_conversate_ui_stop_5b03d8"])|1,
                      0, count=500)
        if not done[0]: raise RuntimeError(f"heartbeat stop did not return: {native, role, elapsed, flags}")
        return events

    cases = [(role, elapsed, flags) for role in (0, 1, 2)
             for elapsed in (0, 1, 60000, 60001, 60002, 0xffffffff)
             for flags in (0, 1, 2, 4, 7)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"heartbeat stop mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_STOP_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Child providers and logger are controlled lower contracts.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
