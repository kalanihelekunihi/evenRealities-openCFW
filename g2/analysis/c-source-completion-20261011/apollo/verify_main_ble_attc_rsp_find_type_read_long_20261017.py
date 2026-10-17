#!/usr/bin/env python3
"""Stock/C contracts for Cordio find-by-type and read-long responses."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_rsp_find_type_read_long_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-rsp-find-type-read-long"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = {"find": (0x56c3b0, "audio_attc_rsp_find_type_56c3b0"),
           "long": (0x56c454, "audio_attc_rsp_read_long_56c454")}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "read-rsp.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", str(obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, kind, length, start, maximum, handle, continuing,
            status, value_length, mtu, slot, pairs):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not stock:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        ccb, main_ccb, packet, event = (0x20011000, 0x20012000,
                                        0x20013000, 0x20014000)
        cpu.mem_write(ccb, bytes([0xa5] * 64))
        cpu.mem_write(ccb, main_ccb.to_bytes(4, "little"))
        cpu.mem_write(ccb + 7, bytes([continuing]))
        cpu.mem_write(ccb + 0x0c, handle.to_bytes(2, "little"))
        cpu.mem_write(ccb + 0x12, start.to_bytes(2, "little"))
        cpu.mem_write(ccb + 0x14, maximum.to_bytes(2, "little"))
        cpu.mem_write(ccb + 0x28, bytes([slot]))
        cpu.mem_write(main_ccb, bytes(64))
        cpu.mem_write(main_ccb + slot * 4, mtu.to_bytes(2, "little"))
        data = bytearray([0xa5] * 64)
        for index, (first, last) in enumerate(pairs):
            offset = 9 + index * 4
            data[offset:offset + 2] = first.to_bytes(2, "little")
            data[offset + 2:offset + 4] = last.to_bytes(2, "little")
        cpu.mem_write(packet, bytes(data))
        event_data = bytearray([0x5a] * 16)
        event_data[3] = status
        event_data[8:10] = value_length.to_bytes(2, "little")
        cpu.mem_write(event, bytes(event_data))
        for register, value in ((A.UC_ARM_REG_R0, ccb), (A.UC_ARM_REG_R1, length),
                                (A.UC_ARM_REG_R2, packet), (A.UC_ARM_REG_R3, event),
                                (A.UC_ARM_REG_SP, 0x200ff000),
                                (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(register, value)
        entry = ENTRIES[kind][0] if stock else symbols[ENTRIES[kind][1]]
        cpu.emu_start(entry | 1, 0x101f00, count=300)
        return bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(event, 16)), bytes(cpu.mem_read(packet, 64))

    pair_sets = ((), ((1, 1),), ((5, 8),), ((1, 0xffff),),
                 ((10, 9),), ((0, 0),), ((1, 2), (3, 4)),
                 ((5, 8), (9, 10)), ((0xffff, 0xffff),))
    find_cases = [("find", length, start, maximum, 0x1234, continuing,
                   status, 8, 247, 0, pairs)
                  for length, start, maximum, continuing, status, pairs in
                  itertools.product((0, 1, 2, 4, 5, 8, 9),
                                    (0, 1, 5, 0xffff), (0, 4, 10, 0xffff),
                                    (0, 1, 2), (0, 0x73), pair_sets)]
    find_cases = [case for index, case in enumerate(find_cases) if index % 97 == 0]
    find_cases += [("find", length, 1, 10, 0x1234, 1, 0, 8, 247, 0, pairs)
                   for length, pairs in itertools.product((1, 4, 5, 8, 9), pair_sets)]
    long_cases = [("long", length, 0x1234, 0xffff, 0x4567, continuing,
                   status, value_length, mtu, slot, ())
                  for length, continuing, status, value_length, mtu, slot in
                  itertools.product((0, 1, 23, 247, 0xffff), (0, 1, 2),
                                    (0, 0x73), (0, 1, 0xffff),
                                    (0, 23, 247, 0xffff), (0, 1, 2))]
    long_cases = [case for index, case in enumerate(long_cases) if index % 13 == 0]
    cases = find_cases + long_cases
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT response mismatch {case}: {native[:2]} != {compiled[:2]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_RSP_FIND_TYPE_READ_LONG_C",
              "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["CCB, packet, and response event buffers are controlled; parent response dispatcher is separate."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
