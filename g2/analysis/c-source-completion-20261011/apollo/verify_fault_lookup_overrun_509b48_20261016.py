#!/usr/bin/env python3
"""Compare every matchable code with the pinned stock wrapping-row lookup."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/fault_lookup_overrun_509b48.c"
TABLE_SOURCE = G2 / "components/audio/uart_thread_source_candidate/fault_code_table_6c8e60.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/fault-lookup-overrun-509b48"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    rows = [struct.unpack_from("<HHI", blob, 0x6c8e60-0x438000+8*i)
            for i in range(256)]
    first = {}
    for index, (code, _, pointer) in enumerate(rows):
        first.setdefault(code, (index, pointer))
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "fault-lookup-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_fault_unmapped_code_message_509b48",
                    str(SOURCE), str(TABLE_SOURCE), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]
    entry = symbols["audio_fault_unmapped_code_message_509b48"]
    def run(code, limit):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x10000)
        u.mem_map(0x600000, 0x1000)
        u.reg_write(A.UC_ARM_REG_R0, code)
        u.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.emu_start(entry | 1, 0x600000, count=limit)
        return u, u.reg_read(A.UC_ARM_REG_PC) == 0x600000
    for code, (index, pointer) in first.items():
        u, returned = run(code, 20000)
        if not returned:
            raise RuntimeError(f"matching code never returned: {code}")
        got = u.reg_read(A.UC_ARM_REG_R0)
        if index < 43:
            expected = blob[pointer-0x438000:].split(b"\0", 1)[0]
            actual = bytes(u.mem_read(got, len(expected)+1)).split(b"\0", 1)[0]
            if actual != expected:
                raise RuntimeError(f"defined code mismatch: {code}")
        elif got != pointer:
            raise RuntimeError(f"overrun pointer mismatch: {code} {got:08x} {pointer:08x}")
    for code in (43, 0xffff, 0xace1):
        if code not in first:
            _, returned = run(code, 20000)
            if returned:
                raise RuntimeError(f"nonmatching code returned: {code}")
    result = {"status": "PASS_EXPERIMENTAL_FAULT_LOOKUP_OVERRUN_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "table_source_sha256": sha(TABLE_SOURCE), "payload_sha256": PIN,
              "oracle_elf_sha256": sha(elf), "matchable_codes": len(first),
              "defined_message_codes": sum(index < 43 for index, _ in first.values()),
              "overrun_pointer_codes": sum(index >= 43 for index, _ in first.values()),
              "nonmatching_loop_samples": [c for c in (43, 0xffff, 0xace1) if c not in first],
              "limits": ["Overrun pointers are absolute stock values and may not denote strings.",
                         "Only three nonmatching codes sampled; the pinned index instruction proves eight-bit wrap.",
                         "Final relocation and whole-image placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(first), sha(receipt))


if __name__ == "__main__":
    main()
