#!/usr/bin/env python3
"""Compare Terminal ring pointer and item lookup with pinned stock."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_resource_items_597324.c"
WRAP = G2 / "components/audio/uart_thread_source_candidate/td_session_find_by_id.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-resource-items-597324"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = "#include <stdint.h>\nuint8_t audio_td_state[0xa1dc];\n"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x597be0-0x438000:0x597be4-0x438000], "little") != 0x20110d74:
        raise RuntimeError("Apollo stock payload or ring pointer changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "resource-items-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "resource-items-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_resource_597324",
                    str(SOURCE), str(WRAP), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, function, count, start, index):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        ring = symbols["audio_td_state"] + 0x1054 if compiled else 0x20110d74
        u.mem_write(ring + 0x8500, struct.pack("<HH", count, start))
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, index)
        if function == "resource":
            entry = symbols["audio_terminal_resource_597324"] if compiled else 0x597324
        else:
            entry = symbols["audio_terminal_item_59737c"] if compiled else 0x59737c
        u.emu_start(entry | 1, 0x600000, count=10000)
        result = u.reg_read(A.UC_ARM_REG_R0)
        return (None if result == 0 else result-ring,
                bytes(u.mem_read(ring + 0x8500, 4)))

    cases = 0
    for function in ("resource", "item"):
        for count in (0, 1, 2, 64):
            for start in (0, 1, 63):
                for index in (0, 1, 63, 64, 0x10000):
                    stock = run(False, function, count, start, index)
                    selected = run(True, function, count, start, index)
                    if stock != selected:
                        raise RuntimeError(f"resource/item mismatch {function=} {count=} "
                                           f"{start=} {index=}: {stock} vs {selected}")
                    cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_RESOURCE_ITEMS_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "wrap_source_sha256": sha(WRAP), "payload_sha256": PIN,
              "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "ring pointer relative to source-owned state, count guards and 64-slot wrap",
              "limits": ["Final RAM placement of source-owned 0xa1dc-byte Terminal-data state remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
