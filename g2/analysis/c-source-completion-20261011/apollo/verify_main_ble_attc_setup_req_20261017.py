#!/usr/bin/env python3
"""Stock/C Cordio ATT request setup copy and send contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_setup_req_531160_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-setup-req"
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
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_ble_attc_send_req_531144=0x531145",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, event, pattern, status):
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
        ccb, message, packet, write_params = (0x20011000, 0x20012000,
                                               0x20013000, 0x20014000)
        cpu.mem_write(ccb, bytes([0x5a] * 64))
        data = bytearray([pattern] * 12)
        data[2] = event
        data[3] = status
        data[4:8] = packet.to_bytes(4, "little")
        cpu.mem_write(message, bytes(data))
        cpu.mem_write(packet, bytes([pattern ^ 0xff] * 16))
        cpu.mem_write(packet, write_params.to_bytes(4, "little"))
        cpu.mem_write(write_params, bytes((index + pattern) & 0xff for index in range(16)))
        cpu.reg_write(A.UC_ARM_REG_R0, ccb)
        cpu.reg_write(A.UC_ARM_REG_R1, message)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x531144:
                calls.append(("send", machine.reg_read(A.UC_ARM_REG_R0),
                              bytes(machine.mem_read(ccb, 64))))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x531160 if stock else symbols["audio_ble_attc_setup_req_531160"]
        cpu.emu_start(entry | 1, 0, count=300)
        assert done[0], (stock, event, pattern, status, calls)
        return calls, bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(message, 12))

    cases = list(itertools.product((0, 1, 5, 10, 11, 12, 16, 255),
                                   (0, 0x5a, 0xa5, 0xff), (0, 1, 255)))
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT setup request mismatch {case}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_SETUP_REQ_C", "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["ATT request sender is controlled at its call boundary."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
