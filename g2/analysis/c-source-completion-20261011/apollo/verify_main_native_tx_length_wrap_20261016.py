#!/usr/bin/env python3
"""Observe native GX8002 packet-copy lengths at the 16-bit wrap boundary."""
import hashlib
import json
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-tx-packet/native-length-wrap-receipt.json"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def run(payload, length):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
    cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
    cpu.mem_write(0x438000, payload)
    cpu.mem_map(0x20000000, 0x100000)
    cpu.mem_map(0x101000, 0x1000)
    stack, wire, total, data = 0x200ef000, 0x2007399c, 0x20071000, 0x20010000
    for offset, value in ((0, 1), (4, wire), (8, total)):
        cpu.mem_write(stack + offset, value.to_bytes(4, "little"))
    for register, value in ((A.UC_ARM_REG_R0, 0x1234), (A.UC_ARM_REG_R1, 0x5678),
                            (A.UC_ARM_REG_R2, data), (A.UC_ARM_REG_R3, length),
                            (A.UC_ARM_REG_SP, stack), (A.UC_ARM_REG_LR, 0x101181)):
        cpu.reg_write(register, value)
    copies = []
    done = [False]

    def hook(machine, address, _size, _user):
        if address == 0x101180:
            done[0] = True
            machine.emu_stop()
            return
        if address in (0x439be4, 0x58faac, 0x43d0ce):
            if address == 0x439be4:
                copies.append([machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1),
                               machine.reg_read(A.UC_ARM_REG_R2)])
            machine.reg_write(A.UC_ARM_REG_R0, 0x12345678 if address == 0x58faac else 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(0x57bb0b, 0, count=3000)
    if not done[0]:
        raise RuntimeError(f"native constructor did not return: {length}")
    return {"input_length": length, "status": cpu.reg_read(A.UC_ARM_REG_R0),
            "reported_total": int.from_bytes(cpu.mem_read(total, 2), "little"),
            "copy_calls": copies}


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    cases = [run(payload, length) for length in (12, 65531, 65532, 65534, 65535)]
    normal, rejected, *wrapped = cases
    if (normal["status"] != 0 or normal["reported_total"] != 30 or
            normal["copy_calls"][1][2] != 12 or
            rejected["status"] != 0xfffffffe or rejected["copy_calls"] or
            [(item["status"], item["reported_total"], item["copy_calls"][1][2])
             for item in wrapped] != [(0, 14, 65532), (0, 16, 65534), (0, 17, 65535)]):
        raise RuntimeError("native packet wrap observations changed")
    record = {
        "status": "PASS_NATIVE_MAIN_GX8002_TX_LENGTH_WRAP_GATE",
        "stock_payload_sha256": PAYLOAD_SHA,
        "native_entry": "0x57bb0a", "native_memcpy": "0x439be4",
        "cases": cases,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["The native memcpy and CRC lower calls were recorded and skipped, so no huge copy was executed.",
                   "This proves the native length-wrap path can request an over-30-byte copy; it does not make the C allocation safe for such input.",
                   "No runtime input bound or whole-image memory safety is established."]}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
