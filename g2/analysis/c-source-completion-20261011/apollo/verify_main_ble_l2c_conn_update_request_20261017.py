#!/usr/bin/env python3
"""Stock/C L2CAP connection-update request state and packet contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_l2c_conn_update_request_536ea4_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-l2c-conn-update-request"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "request.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    definitions = {"audio_ble_l2c_slave_state": 0x20073bd8,
                   "audio_ble_l2c_state": 0x200737d8,
                   "DmConnIdByHandle": 0x4b6e97,
                   "WsfTimerStartSec": 0x52a4b9,
                   "audio_ble_l2c_msg_alloc_530b28": 0x530b29,
                   "L2cDataReq": 0x530bbd}
    command = ["arm-none-eabi-ld", "-Ttext=0x100000"]
    command += [f"--defsym={name}={address}" for name, address in definitions.items()]
    subprocess.run(command + [str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, handle, conn, identifier, seed, alloc_ok):
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
        spec, packet = 0x20011000, 0x20012000
        cpu.mem_write(spec, bytes((seed + i * 29) & 255 for i in range(12)))
        cpu.mem_write(packet, bytes([0xa5] * 32))
        cpu.mem_write(0x20073bd8, bytes([0x5a] * 32))
        cpu.mem_write(0x200737d8, bytes([0x33] * 48))
        cpu.mem_write(0x200737d8 + 0x24, bytes([identifier]))
        cpu.reg_write(A.UC_ARM_REG_R0, handle)
        cpu.reg_write(A.UC_ARM_REG_R1, spec)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x4b6e96:
                calls.append(("id", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, conn)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x52a4b8:
                calls.append(("timer", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x530b28:
                calls.append(("alloc", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, packet if alloc_ok else 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x530bbc:
                calls.append(("send", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1),
                              machine.reg_read(A.UC_ARM_REG_R2),
                              machine.reg_read(A.UC_ARM_REG_R3)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x536ea4 if stock else symbols["audio_ble_l2c_conn_update_request_536ea4"]
        cpu.emu_start(entry | 1, 0, count=400)
        assert done[0], (stock, handle, conn, identifier, seed, alloc_ok, calls)
        return (calls, bytes(cpu.mem_read(packet, 32)),
                bytes(cpu.mem_read(0x20073bd8, 32)),
                bytes(cpu.mem_read(0x200737d8, 48)))

    cases = list(itertools.product((0, 1, 0x1234, 0xffff), (0, 1, 2, 3),
                                   (0, 1, 254, 255), (0, 17), (False, True)))
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"L2CAP request mismatch {case}: "
                               f"{native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_L2C_CONN_UPDATE_REQUEST_C",
              "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Connection lookup, timer, allocator, and L2CAP sender are controlled at call boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
