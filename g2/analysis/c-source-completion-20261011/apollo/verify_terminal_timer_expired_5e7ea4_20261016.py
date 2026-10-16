#!/usr/bin/env python3
"""Compare terminal timer expiry over boundary and wraparound cases."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_timer_expired_5e7ea4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-timer-expired-5e7ea4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            blob[0x5e7ea4-0x438000:0x5e7ec4-0x438000].hex() != \
            "002802d00278002a01d1002007e04068091a002901d4012000e00020c0b27047":
        raise RuntimeError("Terminal timer stock slice changed")
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "timer-expired-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_timer_expired_5e7ea4",
                    str(SOURCE), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, present, active, tick, deadline):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        timer = 0x20001000
        u.mem_write(timer, bytes((active, 0xa5, 0x5a, 0xff)) + struct.pack("<I", deadline))
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, timer if present else 0)
        u.reg_write(A.UC_ARM_REG_R1, tick)
        entry = symbols["audio_terminal_timer_expired_5e7ea4"] if compiled else 0x5e7ea4
        u.emu_start(entry|1, 0x600000, count=1000)
        return u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(timer, 8)).hex()

    cases = 0
    for present in (False, True):
        for active in (0, 1, 0xff):
            for deadline in (0, 1, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff):
                for delta in (-2, -1, 0, 1, 2, 0x7fffffff, 0x80000000):
                    tick = (deadline + delta) & 0xffffffff
                    stock = run(False, present, active, tick, deadline)
                    selected = run(True, present, active, tick, deadline)
                    if stock != selected:
                        raise RuntimeError(f"timer expiry mismatch {present=} {active=} "
                                           f"{tick=} {deadline=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_TIMER_EXPIRED_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "null, inactive, deadline and modular signed-difference boundaries",
              "limits": ["Caller timer initialization, tick source and concurrent mutation remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
