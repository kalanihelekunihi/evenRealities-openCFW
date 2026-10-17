#!/usr/bin/env python3
"""Stock/C comparison for the Cordio database-hash update callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_database_hash_update_534d46_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-database-hash-update"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "hash-update.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_atts_database_hash_update_534d46",
                    "--defsym=WsfBufFree=0x5304d5",
                    "--defsym=WStrReverse=0x56d8f1",
                    "--defsym=attsFindUuidInRange=0x56d93d",
                    "--defsym=AttsSetAttr=0x5353e9",
                    "--defsym=attsCsfSetHashUpdateStatus=0x52c6c1",
                    "--defsym=audio_ble_att_common_state=0x200610ac",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, plain, found, seed):
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
        msg, cipher_ptr, plain_ptr = 0x20011000, 0x20012000, 0x20013000
        original = bytes((seed + 7 * i) & 0xff for i in range(16))
        cpu.mem_write(msg, bytes(32))
        cpu.mem_write(msg + 4, struct.pack("<I", cipher_ptr))
        cpu.mem_write(cipher_ptr, original)
        cpu.mem_write(msg + 8, struct.pack("<I", plain_ptr if plain else 0))
        cpu.mem_write(0x200610ac + 0x58, struct.pack("<I", 0x101d01))
        cpu.reg_write(A.UC_ARM_REG_R0, msg)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]
        targets = {0x5304d4: "free", 0x56d8f0: "reverse", 0x56d93c: "find",
                   0x5353e8: "set", 0x52c6c0: "status", 0x101d00: "app"}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in targets:
                label = targets[pc]
                r0, r1, r2, r3 = (machine.reg_read(x) for x in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if label == "free":
                    calls.append((label, r0 == plain_ptr))
                elif label == "reverse":
                    calls.append((label, r0 == cipher_ptr, r1))
                    machine.mem_write(r0, bytes(machine.mem_read(r0, r1))[::-1])
                elif label == "find":
                    sp = machine.reg_read(A.UC_ARM_REG_SP)
                    group, attribute = struct.unpack("<II", machine.mem_read(sp, 8))
                    calls.append((label, r0, r1, r2, bytes(machine.mem_read(r3, 2)).hex(),
                                  group != 0, attribute != 0))
                    machine.reg_write(A.UC_ARM_REG_R0, 0x1234 if found else 0)
                elif label == "set":
                    calls.append((label, r0, r1, r2 == cipher_ptr,
                                  bytes(machine.mem_read(r2, 16)).hex()))
                elif label == "status":
                    calls.append((label, r0))
                elif label == "app":
                    raw = bytearray(machine.mem_read(r0, 16))
                    value = struct.unpack_from("<I", raw, 4)[0]
                    struct.pack_into("<I", raw, 4, int(value == cipher_ptr))
                    calls.append((label, bytes(raw).hex()))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x534d46 if native else symbols["audio_ble_atts_database_hash_update_534d46"]
        cpu.emu_start(entry | 1, 0, count=300)
        assert done[0], (native, calls)
        return calls, bytes(cpu.mem_read(msg, 12)).hex(), bytes(cpu.mem_read(cipher_ptr, 16)).hex()

    cases = list(itertools.product((False, True), (False, True), (0, 0x55, 0xf0)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATTS hash update mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_DATABASE_HASH_UPDATE_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Six downstream calls are controlled; final RAM placement is open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
