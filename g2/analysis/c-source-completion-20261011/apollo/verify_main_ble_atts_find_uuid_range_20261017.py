#!/usr/bin/env python3
"""Stock/C comparison for Cordio UUID range search with controlled comparison."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_find_uuid_range_56d93c_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-find-uuid-range"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "find-uuid.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "attsFindUuidInRange",
                    "--defsym=audio_ble_atts_state=0x2006e5f0",
                    "--defsym=attsUuidCmp=0x56c551",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, start, end, target, empty):
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
        g1, g2 = 0x20020000, 0x20020100
        a1, a2 = 0x20021000, 0x20022000
        uuid, attr_out, group_out = 0x20023000, 0x20024000, 0x20024004
        for address in (g1, g2):
            cpu.mem_write(address, bytes(0x40))
        cpu.mem_write(g1, struct.pack("<II", g2, a1))
        cpu.mem_write(g1 + 0x10, struct.pack("<HH", 1, 3))
        cpu.mem_write(g2, struct.pack("<II", 0, a2))
        cpu.mem_write(g2 + 0x10, struct.pack("<HH", 6, 7))
        for base, handles in ((a1, (1, 2, 3)), (a2, (6, 7))):
            cpu.mem_write(base, bytes(0x50))
            for index, handle in enumerate(handles):
                cpu.mem_write(base + 16 * index, bytes([handle]))
        cpu.mem_write(0x2006e5f0 + 0x258, struct.pack("<I", 0 if empty else g1))
        cpu.mem_write(uuid, bytes([target, 0]))
        cpu.mem_write(attr_out, struct.pack("<II", 0xaaaa5555, 0xbbbb6666))
        sp = 0x200ff000
        cpu.mem_write(sp, struct.pack("<II", attr_out, group_out))
        for reg, value in ((A.UC_ARM_REG_R0, start), (A.UC_ARM_REG_R1, end),
                           (A.UC_ARM_REG_R2, 2), (A.UC_ARM_REG_R3, uuid),
                           (A.UC_ARM_REG_SP, sp), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x56c550:
                attr, length, uuid_ptr = (machine.reg_read(x) for x in
                                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                            A.UC_ARM_REG_R2))
                attr_handle = machine.mem_read(attr, 1)[0]
                calls.append((attr, length, uuid_ptr == uuid, attr_handle))
                machine.reg_write(A.UC_ARM_REG_R0, int(attr_handle == target))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x56d93c if native else symbols["attsFindUuidInRange"]
        cpu.emu_start(entry | 1, 0, count=1000)
        assert done[0], (native, start, end, calls)
        return (cpu.reg_read(A.UC_ARM_REG_R0), calls,
                struct.unpack("<II", cpu.mem_read(attr_out, 8)))

    cases = list(itertools.product((0, 1, 2, 3, 4, 5, 6, 7, 8, 0xffff),
                                   (0, 2, 3, 6, 7, 0xffff),
                                   (2, 7, 99), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATT UUID range mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_FIND_UUID_RANGE_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["UUID comparison is a controlled lower call; test groups cover two ranges."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
