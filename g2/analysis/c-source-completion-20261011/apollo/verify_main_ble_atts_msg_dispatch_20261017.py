#!/usr/bin/env python3
"""Compare Cordio server message dispatcher under controlled callbacks."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_msg_dispatch_534c42_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-msg-dispatch"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "atts-msg.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_atts_msg_534c42",
                    "--defsym=audio_ble_atts_state=0x2006e5f0",
                    "--defsym=audio_ble_dm_conn_set_idle=0x4b71dd",
                    "--defsym=audio_ble_atts_database_hash_update_534d46=0x534d47",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, param):
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
        msg, cb = 0x20011000, 0x20020000
        cpu.mem_write(msg, bytes(32))
        cpu.mem_write(msg, struct.pack("<H", param))
        cpu.mem_write(msg + 2, bytes([event]))
        cpu.mem_write(0x2006e5f0 + 0x260, struct.pack("<II", cb, 0x101d01))
        cpu.mem_write(cb + 8, struct.pack("<I", 0x101c01))
        cpu.reg_write(A.UC_ARM_REG_R0, msg)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        targets = {0x4b71dc: "idle", 0x534d46: "hash",
                   0x101c00: "ind", 0x101d00: "sign"}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in targets:
                events.append((targets[pc], tuple(machine.reg_read(x) for x in
                                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                   A.UC_ARM_REG_R2))))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x534c42 if native else symbols["audio_ble_atts_msg_534c42"]
        cpu.emu_start(entry | 1, 0, count=200)
        assert done[0], (native, event, events)
        return events, bytes(cpu.mem_read(msg, 12)).hex()

    cases = list(itertools.product((0x00, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25),
                                   (0, 0x12, 0x1234)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATTS message mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_MSG_DISPATCH_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Four downstream calls are controlled; ATT control-block RAM ownership remains open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
