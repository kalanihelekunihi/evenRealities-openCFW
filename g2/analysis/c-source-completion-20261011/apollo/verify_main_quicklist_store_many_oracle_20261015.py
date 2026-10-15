#!/usr/bin/env python3
"""Native/C QuickList multi-item cache and return comparison."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
DIR = G2 / "components/audio/uart_thread_source_candidate"
SRC = DIR / "quicklist_store_many_58d668.c"
ONE = DIR / "quicklist_store_one_58d51c.c"
CONVERT = DIR / "quicklist_convert_58da28.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-store-many"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY = IMAGE[0x58d668-0x438000:0x58d9c0-0x438000]
assert BODY[:4] == bytes.fromhex("2de9f847") and BODY[-4:] == bytes.fromhex("bde8f087")

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint32_t audio_quicklist_tick_now(void){return 0;}\n")
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_store_many",
                    str(SRC), str(ONE), str(CONVERT), str(shim), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]

    def run(compiled, total, count, first_index, old_valid, tick, source_valid=True):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x200000)
        source = 0x20010000
        data = bytearray((i * 17 + 3) & 255 for i in range(8 + 20 * 0xe8))
        data[0], data[1] = 2, total
        data[2:4] = count.to_bytes(2, "little")
        for i in range(20):
            item = 8 + i * 0xe8
            data[item + 4:item + 8] = (first_index + i).to_bytes(4, "little")
            data[item + 24:item + 26] = (3 + i).to_bytes(2, "little")
        uc.mem_write(source, bytes(data))
        state = names["audio_quicklist_item_cache"] if compiled else 0x20101a1c
        initial = bytearray([0x5a] * 0x1238)
        initial[0x1221] = old_valid
        uc.mem_write(state, bytes(initial))
        calls = []

        def hook(cpu, address, _size, _user):
            if compiled:
                if address != (names["audio_quicklist_tick_now"] & ~1):
                    return
                calls.append("tick")
                cpu.reg_write(A.UC_ARM_REG_R0, tick)
            elif address == 0x43d0ce:
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif address == 0x43c0e4:
                p, size = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                cpu.mem_write(p, bytes(size))
            elif address == 0x439be4:
                p, src, size = (cpu.reg_read(reg) for reg in
                                (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                cpu.mem_write(p, bytes(cpu.mem_read(src, size)))
            elif address == 0x44a1c6:
                calls.append("tick")
                cpu.reg_write(A.UC_ARM_REG_R0, tick)
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_R0, source if source_valid else 0)
        uc.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = names["audio_quicklist_store_many"] if compiled else 0x58d668
        uc.emu_start(entry | 1, 0x600000, count=100000)
        return uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(state, 0x1238)), calls

    cases = []
    inputs = ((0, 0, 0, 0), (5, 0, 0, 0), (0, 2, 0, 4),
              (5, 2, 0, 0), (5, 2, 3, 1), (5, 2, 19, 0),
              (5, 3, 0, 19), (5, 21, 0, 0), (5, 2, 0, 19),
              (5, 2, 0, 1), (1, 2, 0, 0))
    for total, count, first_index, old_valid in inputs:
        tick = 0x12345678
        native = run(False, total, count, first_index, old_valid, tick)
        compiled = run(True, total, count, first_index, old_valid, tick)
        if native != compiled:
            index = next((i for i in range(0x1238) if native[1][i] != compiled[1][i]), None)
            raise AssertionError((total, count, first_index, old_valid,
                                  native[0], compiled[0], index,
                                  native[1][index] if index is not None else None,
                                  compiled[1][index] if index is not None else None,
                                  native[2], compiled[2]))
        cases.append({"total": total, "count": count, "first_index": first_index,
                      "old_valid": old_valid, "return": native[0],
                      "state_sha256": hashlib.sha256(native[1]).hexdigest()})
    native, compiled = run(False, 0, 0, 0, 0, 0, False), run(True, 0, 0, 0, 0, 0, False)
    if native != compiled:
        raise AssertionError(("null", native[0], compiled[0]))
    cases.append({"source_valid": False, "return": native[0]})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_STORE_MANY_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entry": "0x58d668", "native_body_sha256": hashlib.sha256(BODY).hexdigest(),
           "cases": cases, "coverage": "return, clock effects and full 0x1238-byte cache over selected counts and indexes",
           "limits": ["Native clock and memory helpers were intercepted; logging enabled paths and device behavior remain open."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
