#!/usr/bin/env python3
"""Stock/C contracts for Cordio ATT error response and queued-packet free."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_error_and_free_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-error-free"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "error-free.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=WsfMsgFree=0x4bf9b1", str(obj), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run_error(stock, request, code, lo, hi, baseline):
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
        cpu.mem_write(ccb + 6, bytes([request]))
        data = bytearray([0xa5] * 32)
        data[10:13] = bytes([lo, hi, code])
        cpu.mem_write(packet, bytes(data))
        cpu.mem_write(event, baseline)
        for register, value in ((A.UC_ARM_REG_R0, ccb), (A.UC_ARM_REG_R1, 5),
                                (A.UC_ARM_REG_R2, packet), (A.UC_ARM_REG_R3, event),
                                (A.UC_ARM_REG_SP, 0x200ff000),
                                (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(register, value)
        entry = 0x4b5230 if stock else symbols["audio_attc_rsp_error_4b5230"]
        cpu.emu_start(entry | 1, 0x101f00, count=100)
        return bytes(cpu.mem_read(event, 16)), bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(packet, 32))

    def run_free(stock, packet_present):
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
        msg, packet = 0x20011000, 0x20012000
        cpu.mem_write(msg, bytes([0xa5] * 32))
        cpu.mem_write(msg + 4, (packet if packet_present else 0).to_bytes(4, "little"))
        cpu.reg_write(A.UC_ARM_REG_R0, msg)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x4bf9b0:
                calls.append(("WsfMsgFree", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x531ac0 if stock else symbols["audio_ble_attc_free_pkt_531ac0"]
        cpu.emu_start(entry | 1, 0, count=100)
        assert done[0], (stock, packet_present, calls)
        return calls, bytes(cpu.mem_read(msg, 32))

    error_cases = list(itertools.product((0, 1, 5, 6, 9, 11, 16, 255),
                                         (0, 1, 0x75, 255), (0, 0x34), (0, 0x12),
                                         (bytes(16), bytes(range(16)))))
    for case in error_cases:
        native, compiled = run_error(True, *case), run_error(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT error response mismatch {case[:4]}: {native[0]} != {compiled[0]}")
    for present in (False, True):
        native, compiled = run_free(True, present), run_free(False, present)
        if native != compiled:
            raise RuntimeError(f"ATT packet-free mismatch {present}: {native} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_ERROR_FREE_C",
              "cases": len(error_cases) + 2,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["WSF message free is controlled at its call boundary."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
