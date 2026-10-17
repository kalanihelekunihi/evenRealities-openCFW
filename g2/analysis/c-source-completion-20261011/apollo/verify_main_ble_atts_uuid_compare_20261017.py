#!/usr/bin/env python3
"""Stock/C comparison of Cordio attribute UUID matching."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_uuid_compare_56c550_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-uuid-compare"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "uuid-compare.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "attsUuidCmp",
                    "--defsym=memcmp=0x4751c9",
                    "--defsym=attUuidCmp16to128=0x4b5015",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, is_128, length, same):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        attr, a_uuid, b_uuid = 0x20011000, 0x20012000, 0x20013000
        cpu.mem_write(attr, bytes(32))
        cpu.mem_write(attr, struct.pack("<I", a_uuid))
        cpu.mem_write(attr + 0xe, bytes([1 if is_128 else 0]))
        cpu.mem_write(a_uuid, bytes(range(16)))
        cpu.mem_write(b_uuid, bytes(range(16)) if same else bytes([99]) + bytes(range(1, 16)))
        for reg, value in ((A.UC_ARM_REG_R0, attr), (A.UC_ARM_REG_R1, length),
                           (A.UC_ARM_REG_R2, b_uuid), (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in (0x4751c8, 0x4b5014):
                r0, r1, r2 = (machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if pc == 0x4751c8:
                    calls.append(("memcmp", r0, r1, r2))
                    result = 0 if bytes(machine.mem_read(r0, r2)) == bytes(machine.mem_read(r1, r2)) else 1
                else:
                    calls.append(("convert", r0, r1))
                    result = int(machine.mem_read(r0, 1) == machine.mem_read(r1, 1))
                machine.reg_write(A.UC_ARM_REG_R0, result)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x56c550 if native else symbols["attsUuidCmp"]
        cpu.emu_start(entry | 1, 0, count=150)
        assert done[0], (native, calls)
        return calls, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = list(itertools.product((False, True), (2, 4, 16), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATT UUID compare mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_UUID_COMPARE_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["memcmp and 16-to-128 conversion are controlled lower calls."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
