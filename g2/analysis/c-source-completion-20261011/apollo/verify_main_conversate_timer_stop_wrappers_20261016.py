#!/usr/bin/env python3
"""Direct stock/C comparison of loading and selection timer stop wrappers."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_stop_wrappers_5b37c8_5b383c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-timer-stop-wrappers"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = [(0x5b37c8, "audio_conversate_timer_1_stop_5b37c8", 0x20073a3c, "Loading timeout"),
           (0x5b383c, "audio_conversate_timer_2_stop_5b383c", 0x20073a44, "Select timeout")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-stops.o", OUT / "oracle-stops.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_timer_1_stop_5b37c8",
                    "--defsym=audio_conversate_timer_mgr_ram_20073a3c=0x20073a3c",
                    "--defsym=audio_conversate_timer_stop_5b35d0=0x101010",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, row, fill):
        address, symbol, _, _ = row
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x20073a3c, bytes([fill])*0x1c)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def string(addr):
            return bytes(cpu.mem_read(addr, 80)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == (0x5b35d0 if native else 0x101010):
                calls.append((machine.reg_read(A.UC_ARM_REG_R0),
                              string(machine.reg_read(A.UC_ARM_REG_R1))))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((address if native else symbols[symbol])|1, 0, count=100)
        if not done[0]: raise RuntimeError(f"timer stop did not return: {native, row, fill}")
        return {"calls": calls, "ram": bytes(cpu.mem_read(0x20073a3c, 0x1c)).hex()}

    cases = [(row, fill) for row in ENTRIES for fill in (0, 0x5a, 0xff)]
    for row, fill in cases:
        a, b = run(True, row, fill), run(False, row, fill)
        if a != b or a["calls"] != [(row[2], row[3])]:
            raise RuntimeError(f"timer stop mismatch {(row[0], fill)}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TIMER_STOP_WRAPPERS_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Shared timer stop lower is a controlled contract.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
