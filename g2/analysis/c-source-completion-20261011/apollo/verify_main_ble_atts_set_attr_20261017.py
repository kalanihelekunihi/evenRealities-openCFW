#!/usr/bin/env python3
"""Stock/C comparison for Cordio AttsSetAttr with controlled lower calls."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_set_attr_5353e8_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-set-attr"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "set-attr.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e", "AttsSetAttr",
                    "--defsym=WsfTaskLock=0x52b8c9",
                    "--defsym=attsFindByHandle=0x56c5d5",
                    "--defsym=memcpy=0x439be5",
                    "--defsym=WsfTaskUnlock=0x52b8d1",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, handle, length, found, variable):
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
        attr, dest, src, len_ptr = 0x20011000, 0x20012000, 0x20013000, 0x20014000
        cpu.mem_write(attr, bytes(32))
        cpu.mem_write(attr + 4, struct.pack("<IIH", dest, len_ptr, 8))
        cpu.mem_write(attr + 0xe, bytes([8 if variable else 0]))
        cpu.mem_write(dest, bytes([0xaa]) * 16)
        cpu.mem_write(src, bytes(range(16)))
        cpu.mem_write(len_ptr, struct.pack("<H", 0x7777))
        cpu.reg_write(A.UC_ARM_REG_R0, handle)
        cpu.reg_write(A.UC_ARM_REG_R1, length)
        cpu.reg_write(A.UC_ARM_REG_R2, src)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]
        targets = {0x52b8c8: "lock", 0x56c5d4: "find",
                   0x439be4: "copy", 0x52b8d0: "unlock"}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in targets:
                label = targets[pc]
                r0, r1, r2 = (machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if label == "find":
                    calls.append((label, r0, r1 != 0))
                    machine.reg_write(A.UC_ARM_REG_R0, attr if found else 0)
                elif label == "copy":
                    calls.append((label, r0 == dest, r1 == src, r2))
                    machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
                else:
                    calls.append((label,))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5353e8 if native else symbols["AttsSetAttr"]
        cpu.emu_start(entry | 1, 0, count=200)
        assert done[0], (native, calls)
        return (calls, cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(dest, 16)).hex(),
                bytes(cpu.mem_read(len_ptr, 2)).hex())

    cases = list(itertools.product((1, 0x1234, 0xffff), (0, 4, 8, 9),
                                   (False, True), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATTS set attr mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_SET_ATTR_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Task lock, attribute lookup, copy and unlock are controlled lower calls."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
