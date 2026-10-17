#!/usr/bin/env python3
"""Stock/C comparison for Cordio indication/notification message setup."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_setup_msg_5339ac_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-setup-msg"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "setup.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {"attL2cDataReq": 0x4b50bb,
            "WsfTimerStartSec": 0x52a4b9,
            "audio_ble_att_exec_callback_4b5074": 0x4b5075,
            "audio_ble_atts_exec_callback_533934": 0x533935,
            "audio_ble_att_cfg_ptr_200004b4": 0x200004b4}
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_atts_setup_msg_5339ac",
                    *(f"--defsym={name}={hex(value)}" for name, value in defs.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, opcode, flow, slot, connection, full):
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
        ccb, main_ccb, packet, config = 0x20011000, 0x20012000, 0x20013000, 0x20014000
        cpu.mem_write(ccb, bytes(0x80))
        cpu.mem_write(main_ccb, bytes(32))
        cpu.mem_write(packet, bytes(32))
        cpu.mem_write(config, bytes(16))
        cpu.mem_write(ccb + 0x10, struct.pack("<I", main_ccb))
        cpu.mem_write(ccb + 0x24, bytes([connection, slot]))
        if full:
            for index in range(10):
                cpu.mem_write(ccb + 0x2a + 2 * index, struct.pack("<H", index + 1))
        cpu.mem_write(main_ccb + slot * 4 + 2, bytes([2 if flow else 0]))
        cpu.mem_write(packet, struct.pack("<HH", 0x19, 0x1234))
        cpu.mem_write(packet + 8, bytes([opcode]))
        cpu.mem_write(0x200004b4, struct.pack("<I", config))
        cpu.mem_write(config + 6, bytes([29]))
        for reg, value in ((A.UC_ARM_REG_R0, ccb), (A.UC_ARM_REG_R1, connection),
                           (A.UC_ARM_REG_R2, slot), (A.UC_ARM_REG_R3, packet),
                           (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        calls, done = [], [False]
        targets = {0x4b50ba: "send", 0x52a4b8: "timer",
                   0x4b5074: "att_event", 0x533934: "atts_event"}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in targets:
                label = targets[pc]
                args = tuple(machine.reg_read(x) for x in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if label == "send":
                    calls.append((label, args[0] == main_ccb, args[1], args[2],
                                  args[3] == packet))
                    machine.mem_write(packet + 2, struct.pack("<H", 0xabcd))
                elif label == "timer":
                    calls.append((label, args[0] == ccb, args[1]))
                elif label == "att_event":
                    extra = struct.unpack("<I", machine.mem_read(
                        machine.reg_read(A.UC_ARM_REG_SP), 4))[0]
                    calls.append((label, args, extra))
                else:
                    calls.append((label, args[:3]))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5339ac if native else symbols["audio_ble_atts_setup_msg_5339ac"]
        cpu.emu_start(entry | 1, 0, count=400)
        assert done[0], (native, opcode, calls)
        return calls, bytes(cpu.mem_read(ccb, 0x40)).hex()

    cases = list(itertools.product((0x1b, 0x1d, 0x23), (False, True),
                                   (0, 1), (1, 255), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATTS setup mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_SETUP_MSG_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Transport, timer and event callbacks are controlled; config-pointer RAM placement remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
