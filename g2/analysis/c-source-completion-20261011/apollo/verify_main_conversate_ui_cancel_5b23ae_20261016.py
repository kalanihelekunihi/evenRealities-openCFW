#!/usr/bin/env python3
"""Direct stock/C replay of Conversate UI minute update."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_cancel_5b23ae.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-cancel-5b23ae"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_device_role_get": (0x101010, 0x45a568, "role"),
          "audio_quicklist_tick_now": (0x101020, 0x44a1c6, "seconds"),
          "audio_conversate_report_5b02e4": (0x101030, 0x5b02e4, "report")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b2d38-0x438000:0x5b2d3c-0x438000] == (0x20071368).to_bytes(4, "little")
    obj, elf_path = OUT / "oracle-cancel.o", OUT / "oracle-cancel.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_cancel_5b23ae",
                    "--defsym=audio_conversate_ui_deinit_tail_200713fd=0x200713fd",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, role, stored, seconds):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x200713f8, b"\x5a"*0x20)
        cpu.mem_write(0x20071404, struct.pack("<I", stored))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            if kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "seconds":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, seconds)
            else:
                events.append((kind, machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1)))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b23ae if native else symbols["audio_conversate_ui_cancel_5b23ae"])|1,
                      0, count=100)
        if not done[0]: raise RuntimeError(f"minute update did not return: {native, role, stored, seconds}")
        return {"events": events, "ram": bytes(cpu.mem_read(0x200713f8, 0x20)).hex()}

    cases = [(role, stored, seconds) for role in (0, 1, 2)
             for stored in (0, 1, 2, 60, 0xffffffff)
             for seconds in (0, 59, 60, 61, 120, 3600, 0xffffffff)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"minute update mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_CANCEL_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Role, seconds and report are controlled lower contracts.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
