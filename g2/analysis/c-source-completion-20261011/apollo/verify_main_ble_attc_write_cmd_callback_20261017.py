#!/usr/bin/env python3
"""Compare stock/C ATT client pending write callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_write_cmd_callback_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-write-cmd-callback"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "write-cmd.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_attc_write_cmd_callback_530de6",
                    "--defsym=audio_ble_attc_exec_callback_531ad6=0x531ad7",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, connection, status, pending):
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
        ccb = 0x20011000
        cpu.mem_write(ccb, bytes(0x60))
        for index, value in enumerate(pending):
            cpu.mem_write(ccb + 0x2a + index * 2, struct.pack("<H", value))
        cpu.reg_write(A.UC_ARM_REG_R0, connection)
        cpu.reg_write(A.UC_ARM_REG_R1, ccb)
        cpu.reg_write(A.UC_ARM_REG_R2, status)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x531ad6:
                r0, r1, r2, r3 = (machine.reg_read(x) for x in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                events.append((r0, r1, r2, r3))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x530de6 if native else symbols["audio_ble_attc_write_cmd_callback_530de6"]
        cpu.emu_start(entry | 1, 0, count=200)
        assert done[0], (native, events)
        return events, bytes(cpu.mem_read(ccb + 0x2a, 20)).hex()

    patterns = [(0,) * 10, (0x1234,) + (0,) * 9,
                (0, 0x1001) + (0,) * 8, (0x4567,) * 10]
    cases = list(itertools.product((0, 1, 127, 255), (0, 1, 255), patterns))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATT client write callback mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_WRITE_CMD_CALLBACK_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["ATT event execution is a controlled lower call."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
