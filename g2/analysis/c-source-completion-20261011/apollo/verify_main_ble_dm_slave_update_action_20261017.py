#!/usr/bin/env python3
"""Controlled stock/C branches for Cordio slave connection update."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_slave_update_action_56e526_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-dm-slave-update-action"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CASES = (("audio_ble_dm_action_56e526", 0x56e526),)
LOWER = {0x530d3c: ("features", 0), 0x52af40: ("hci", 2),
         0x536ea4: ("l2c", 2), 0x56e4f8: ("response", 2)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "actions.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    definitions = {"audio_ble_hci_get_le_supported_features_530d3c": 0x530d3d,
                   "audio_ble_hci_conn_update_52af40": 0x52af41,
                   "audio_ble_l2c_conn_update_request_536ea4": 0x536ea5,
                   "audio_ble_dm_slave_update_response_56e4f8": 0x56e4f9}
    command = ["arm-none-eabi-ld", "-Ttext=0x100000"]
    command += [f"--defsym={name}={address}" for name, address in definitions.items()]
    subprocess.run(command + [str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD" and segment["p_vaddr"] < 0x20000000]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, entry, variant):
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
        ccb, msg = 0x20010000, 0x20011000
        ccb_flag, global_flag, updating = variant
        ccb_bytes = bytearray(((i * 17 + updating * 31) & 255) for i in range(64))
        ccb_bytes[40] = ccb_flag
        ccb_bytes[17] = updating
        msg_bytes = bytes(((i * 43 + global_flag * 19) & 255) for i in range(64))
        cpu.mem_write(ccb, bytes(ccb_bytes))
        cpu.mem_write(msg, msg_bytes)
        cpu.reg_write(A.UC_ARM_REG_R0, ccb)
        cpu.reg_write(A.UC_ARM_REG_R1, msg)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in LOWER:
                regs = tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                kind, width = LOWER[pc]
                calls.append((kind, regs[:width]))
                if kind == "features":
                    machine.reg_write(A.UC_ARM_REG_R0, global_flag)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        start = entry if stock else symbols[next(name for name, addr in CASES if addr == entry)]
        cpu.emu_start(start | 1, 0, count=100)
        assert done[0], (stock, hex(entry), variant, calls)
        return calls, bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(msg, 64))

    for name, address in CASES:
        for variant in itertools.product((0, 2, 255), (0, 2, 255), (0, 1, 7)):
            native, compiled = run(True, address, variant), run(False, address, variant)
            if native != compiled:
                raise RuntimeError(f"DM action mismatch {name} variant {variant}: "
                                   f"{native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_DM_SLAVE_UPDATE_ACTION_C",
              "cases": len(CASES) * 27, "actions": [name for name, _ in CASES],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Lower calls are controlled and their bodies remain independently gated.",
                         "Only stock-observed call arguments are compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
