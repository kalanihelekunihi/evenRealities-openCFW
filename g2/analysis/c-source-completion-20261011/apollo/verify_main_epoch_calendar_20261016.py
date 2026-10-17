#!/usr/bin/env python3
"""Compare defined calendar fields in native and compiled Main 0x449fda."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/time_epoch_to_calendar_449fda.c"
BASE = G2 / "build/c-firmware/20261016/main-log-datetime-now/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-epoch-calendar"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
FIELDS = {"weekday": 4, "year_since_2000": 12, "month": 16, "day": 20,
          "hour": 24, "minute": 28, "second": 32}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(entry, segments, mode_cell, seconds, mode):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in ((0x100000, 0x100000), (0x300000, 0x1000),
                          (0x400000, 0x400000), (0x20000000, 0x80000)):
        uc.mem_map(address, size)
    for address, data in segments:
        if data:
            uc.mem_write(address, data)
    uc.mem_write(mode_cell, mode.to_bytes(4, "little"))
    uc.mem_write(0x20005000, b"\xa5" * 40)
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, 0x300001)
    uc.reg_write(UC_ARM_REG_R0, seconds)
    uc.reg_write(UC_ARM_REG_R1, 0x20005000)
    uc.emu_start(entry | 1, 0x300000, count=30000)
    data = bytes(uc.mem_read(0x20005000, 40))
    return {name: int.from_bytes(data[offset:offset+4], "little")
            for name, offset in FIELDS.items()}, data


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main stock payload changed")
    elf_path = OUT / "epoch-calendar-oracle.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-ffreestanding", "-fno-builtin",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_time_epoch_to_calendar_449fda",
                    str(SOURCE), str(OUT / "epoch-calendar-oracle-storage.c"), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
        symbols = {sym.name: sym["st_value"] for sym in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = (0, 946684799, 946684800, 946771199, 946771200,
             951782400, 978307200, 1072915200, 1078012800,
             2147483647, 4102444800, 4107542400, 0xffffffff)
    rows = []
    for seconds in cases:
        for mode in (0, 1, 2):
            stock, stock_data = run(0x449fda, [(0x438000, payload)],
                                    0x200736d4 + 24, seconds, mode)
            candidate, candidate_data = run(symbols["audio_time_epoch_to_calendar_449fda"],
                                             segments, symbols["audio_uart_hand_record"] + 24,
                                             seconds, mode)
            if stock != candidate:
                raise RuntimeError(f"calendar mismatch {seconds} {mode}: {stock} vs {candidate}")
            rows.append({"seconds": seconds, "clock_mode": mode, "defined_fields": stock,
                         "native_other_words": [stock_data[i:i+4].hex() for i in (0, 8, 36)],
                         "candidate_other_words": [candidate_data[i:i+4].hex() for i in (0, 8, 36)]})
    candidate = OUT / "candidate.o"
    before = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(BASE)], text=True).splitlines() if line.strip()}
    after = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(candidate)], text=True).splitlines() if line.strip()}
    if len(before) != 132 or len(after) != 131 or \
            before - after != {"audio_time_epoch_to_calendar_449fda"} or after - before:
        raise RuntimeError("Main calendar import frontier changed")
    result = {"status": "PASS_BOUNDED_MAIN_EPOCH_CALENDAR_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
              "candidate_object": str(candidate.relative_to(ROOT)), "candidate_object_sha256": sha(candidate),
              "oracle_elf": str(elf_path.relative_to(ROOT)), "oracle_elf_sha256": sha(elf_path),
              "cases": rows, "case_count": len(rows), "unresolved_before": 132,
              "unresolved_after": 131, "source_complete": False, "flashable": False,
              "hardware_proof": False,
              "limits": ["Only seven assigned output fields are compared; native copies three uninitialized stack words.",
                         "Clock mode is a source-owned record, but final RAM placement and runtime writes remain open.",
                         "This bounded source does not establish whole Main image equivalence."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(rows), sha(path))


if __name__ == "__main__":
    main()
