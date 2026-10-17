#!/usr/bin/env python3
"""Stock/C event mutation contract for Cordio prepare-write response."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_rsp_prepare_write_539dcc_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-rsp-prepare-write"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LEAVES = {"audio_attc_rsp_prepare_write_539dcc": 0x539dcc}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "prepare-write.o", OUT / "oracle.elf"
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

    def run(stock, name, length, continuing, pending_length, value_length):
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
        ccb, packet, event = 0x20011000, 0x20012000, 0x20013000
        cpu.mem_write(ccb, bytes(64))
        cpu.mem_write(ccb + 7, bytes([continuing]))
        cpu.mem_write(ccb + 0x10, pending_length.to_bytes(2, "little"))
        cpu.mem_write(packet, bytes([0x5a] * 64))
        event_bytes = bytearray([0xa5] * 16)
        event_bytes[4:8] = (packet + 9).to_bytes(4, "little")
        event_bytes[8:10] = value_length.to_bytes(2, "little")
        cpu.mem_write(event, bytes(event_bytes))
        for register, value in ((A.UC_ARM_REG_R0, ccb), (A.UC_ARM_REG_R1, length),
                                (A.UC_ARM_REG_R2, packet), (A.UC_ARM_REG_R3, event),
                                (A.UC_ARM_REG_SP, 0x200ff000),
                                (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(register, value)
        entry = LEAVES[name] if stock else symbols[name]
        cpu.emu_start(entry | 1, 0x101f00, count=30)
        return (bytes(cpu.mem_read(event, 16)),
                bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(packet, 64)))

    cases = list(itertools.product(LEAVES, (0, 1, 5, 0xffff),
                                   (0, 1, 2, 255), (0, 1, 0xffff),
                                   (0, 1, 4, 5, 0xffff)))
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT prepare-write mismatch {case[:2]}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_RSP_PREPARE_WRITE_C", "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Prepare-write response event mutation only; dispatcher and other handlers are separate."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
