#!/usr/bin/env python3
"""Compare Terminal elapsed-record lookup with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/td_record_elapsed_get_59769c.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-td-record-elapsed-get-59769c"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
uint8_t *audio_td_current_record(uint32_t session){(void)session;return 0;}
uint32_t audio_uart_ring_rtc_refresh(void){return 0;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "elapsed-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "elapsed-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_td_record_elapsed_get_59769c",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, output_present, record_present, start, now, session):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        out = 0x20002000
        record = 0x20003000
        u.mem_write(out, struct.pack("<I", 0xa5a5a5a5))
        u.mem_write(record+0x88, struct.pack("<I", start))
        current = (symbols["audio_td_current_record"] if compiled else 0x597188)&~1
        rtc = (symbols["audio_uart_ring_rtc_refresh"] if compiled else 0x44a1ea)&~1
        trace = []
        def hook(cpu, pc, size, _):
            if pc == current:
                trace.append(("record", cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_R0, record if record_present else 0)
            elif pc == rtc:
                trace.append(("rtc",))
                cpu.reg_write(A.UC_ARM_REG_R0, now)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, session)
        u.reg_write(A.UC_ARM_REG_R1, out if output_present else 0)
        entry = symbols["audio_td_record_elapsed_get_59769c"] if compiled else 0x59769c
        u.emu_start(entry|1, 0x600000, count=10000)
        return u.reg_read(A.UC_ARM_REG_R0), \
               int.from_bytes(u.mem_read(out, 4), "little"), trace

    cases = 0
    for output_present in (False, True):
        for record_present in (False, True):
            for start in (0, 1, 100, 0xffffffff):
                for now in (0, 99, 100, 101, 0xffffffff):
                    for session in (0, 0x1234):
                        stock = run(False, output_present, record_present, start, now, session)
                        selected = run(True, output_present, record_present, start, now, session)
                        if stock != selected:
                            raise RuntimeError(f"elapsed mismatch {output_present=} {record_present=} "
                                               f"{start=} {now=} {session=}: {stock} vs {selected}")
                        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TD_RECORD_ELAPSED_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "null pointers, record start and RTC ordering with output and call trace",
              "limits": ["Current-record and RTC lower-call effects, clock validity and concurrency remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
