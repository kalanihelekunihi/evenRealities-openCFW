#!/usr/bin/env python3
"""Native/C QuickList single-item cache comparison with clock and logging cuts."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_store_one_58d51c.c"
CONVERT = G2 / "components/audio/uart_thread_source_candidate/quicklist_convert_58da28.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-store-one"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY = IMAGE[0x58d51c-0x438000:0x58d668-0x438000]
assert BODY[:2] == bytes.fromhex("f0b5") and BODY[-2:] == bytes.fromhex("f0bd")

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint32_t audio_quicklist_tick_now(void){return 0;}\n")
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_store_one",
                    str(SRC), str(CONVERT), str(shim), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]

    def run(compiled, source_valid, title_length, tick):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x200000)
        source = 0x20010000
        item = bytearray(((i * 19 + 5) & 255) for i in range(0xe8))
        item[24:26] = title_length.to_bytes(2, "little")
        uc.mem_write(source, bytes(item))
        state = names["audio_quicklist_item_cache"] if compiled else 0x20101a1c
        uc.mem_write(state, bytes([0x5a]) * 0x1238)
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
        entry = names["audio_quicklist_store_one"] if compiled else 0x58d51c
        uc.emu_start(entry | 1, 0x600000, count=60000)
        return uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(state, 0x1238)), calls

    cases = []
    for source_valid, length, tick in ((False, 0, 0), (True, 0, 0),
                                      (True, 20, 0x12345678), (True, 200, 0xffffffff),
                                      (True, 201, 0xdeadbeef), (True, 65535, 17)):
        native, compiled = run(False, source_valid, length, tick), run(True, source_valid, length, tick)
        if native != compiled:
            index = next((i for i in range(0x1238) if native[1][i] != compiled[1][i]), None)
            raise AssertionError((source_valid, length, tick, native[0], compiled[0], index,
                                  native[1][index] if index is not None else None,
                                  compiled[1][index] if index is not None else None,
                                  native[2], compiled[2]))
        cases.append({"source_valid": source_valid, "title_length": length, "tick": tick,
                      "return": native[0], "state_sha256": hashlib.sha256(native[1]).hexdigest()})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_STORE_ONE_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "convert_source": str(CONVERT.relative_to(ROOT)), "convert_sha256": hashlib.sha256(CONVERT.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entry": "0x58d51c", "native_body_sha256": hashlib.sha256(BODY).hexdigest(),
           "cases": cases, "coverage": "return, clock effects and full 0x1238-byte item cache with logging disabled",
           "limits": ["Native clock and memory helpers were intercepted; actual time source, startup and placement remain open."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
