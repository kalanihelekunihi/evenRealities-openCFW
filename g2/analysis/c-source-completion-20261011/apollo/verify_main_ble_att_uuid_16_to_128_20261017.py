#!/usr/bin/env python3
"""Stock/C comparison for Cordio mutable ATT UUID base conversion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_att_uuid_16_to_128_4b5014_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-att-uuid-16-to-128"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BASE = bytes.fromhex("fb349b5f800000800010000000000000")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "uuid-16-to-128.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "attUuidCmp16to128",
                    "--defsym=audio_ble_att_uuid_base_2000044c=0x2000044c",
                    "--defsym=memcmp=0x4751c9",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, a, match, mutation):
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
        uuid16, uuid128, base_addr = 0x20011000, 0x20012000, 0x2000044c
        initial = bytearray(BASE)
        initial[12:14] = mutation.to_bytes(2, "little")
        cpu.mem_write(base_addr, bytes(initial))
        cpu.mem_write(uuid16, struct.pack("<H", a))
        expected = bytearray(BASE)
        expected[12:14] = a.to_bytes(2, "little")
        if not match:
            expected[3] ^= 1
        cpu.mem_write(uuid128, bytes(expected))
        for reg, value in ((A.UC_ARM_REG_R0, uuid16), (A.UC_ARM_REG_R1, uuid128),
                           (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x4751c8:
                r0, r1, r2 = (machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                calls.append((r0 == base_addr, r1 == uuid128, r2))
                result = int(bytes(machine.mem_read(r0, r2)) != bytes(machine.mem_read(r1, r2)))
                machine.reg_write(A.UC_ARM_REG_R0, result)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b5014 if native else symbols["attUuidCmp16to128"]
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (native, calls)
        return calls, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(base_addr, 16)).hex()

    cases = list(itertools.product((0, 0x1234, 0xffff), (False, True),
                                   (0, 0x55aa, 0xffff)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATT UUID conversion mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATT_UUID_16_TO_128_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["memcmp is controlled; UUID template initialization is separately sourced."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
