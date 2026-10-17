#!/usr/bin/env python3
"""Check sourced 24-hour calendar wrapper against both stock entrypoints."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/time_epoch_to_calendar_449ed4_44a100.c"
BASE_SOURCE = G2 / "components/audio/uart_thread_source_candidate/time_epoch_to_calendar_449fda.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-time-epoch-calendar-44a100"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    objects = []
    for index, path in enumerate((SOURCE, BASE_SOURCE)):
        obj = OUT / f"calendar-{index}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                        "-mthumb", "-std=c11", "-O2", "-Wall", "-Wextra",
                        "-Werror", "-ffreestanding", "-fno-builtin", "-c",
                        str(path), "-o", str(obj)], check=True)
        objects.append(obj)
    elf_path = OUT / "oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_time_epoch_to_calendar_44a100",
                    "--defsym=audio_uart_hand_record=0x200736d4",
                    *map(str, objects), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, entry_name, seconds, mode):
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
        cpu.mem_write(0x200736d4 + 24, struct.pack("<I", mode))
        record = 0x20080000
        cpu.mem_write(record, bytes([0xa5]) * 40)
        cpu.reg_write(A.UC_ARM_REG_R0, seconds)
        cpu.reg_write(A.UC_ARM_REG_R1, record)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ({"base": 0x449ed4, "wrapper": 0x44a100,
                  "mode": 0x46650c}[entry_name] if native
                 else symbols[{"base": "audio_time_epoch_to_calendar_449ed4",
                               "wrapper": "audio_time_epoch_to_calendar_44a100",
                               "mode": "audio_time_format_mode_46650c"}[entry_name]])
        cpu.emu_start(entry | 1, 0, count=15000)
        if not done[0]:
            raise RuntimeError(f"calendar did not return: {native} {entry_name} {seconds}")
        if entry_name == "mode":
            return cpu.reg_read(A.UC_ARM_REG_R0)
        return tuple(struct.unpack("<I", cpu.mem_read(record + offset, 4))[0]
                     for offset in (4, 12, 16, 20, 24, 28, 32))

    times = (0, 1, 946684799, 946684800, 946684801, 951782399,
             951782400, 1700000000, 1735689599, 1735689600,
             2147483647, 4294967295)
    cases = [(entry, seconds, mode) for entry in ("base", "wrapper")
             for seconds in times for mode in (0, 1)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"calendar mismatch {case}: {stock} != {compiled}")
    for mode in (0, 1, 2, 0x87654321):
        case = ("mode", 0, mode)
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"format mode mismatch {case}: {stock} != {compiled}")
        cases.append(case)
    record = {"status": "PASS_DIRECT_MAIN_TIME_EPOCH_CALENDAR_44A100_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_bodies": ["0x449ed4..0x449fd9", "0x44a100..0x44a107",
                                "0x46650c..0x466511"],
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "base_source": str(BASE_SOURCE.relative_to(ROOT)),
              "base_source_sha256": sha(BASE_SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Seven initialized calendar fields were compared; native stack-copy fields at offsets 0, 8 and 36 are not claimed."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
