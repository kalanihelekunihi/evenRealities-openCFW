#!/usr/bin/env python3
"""Compare QuickList PB conversion return and all 232 output bytes."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_convert_58da28.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-convert"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY = IMAGE[0x58da28-0x438000:0x58daca-0x438000]
assert BODY[:2] == bytes.fromhex("7cb5") and BODY[-2:] == bytes.fromhex("76bd")

with tempfile.TemporaryDirectory() as tmp:
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_convert_pb",
                    str(SRC), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]

    def run(compiled, input_bytes, source_valid=True, target_valid=True):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        source, target = 0x20010000, 0x20011000
        uc.mem_write(source, bytes(input_bytes))
        uc.mem_write(target, bytes([0xa5]) * 0xe8)

        def hook(cpu, address, _size, _user):
            if compiled:
                return
            if address == 0x43d0ce:  # logging disabled
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif address == 0x43c0e4:  # memclr
                p, size = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                cpu.mem_write(p, bytes(size))
            elif address == 0x439be4:  # memcpy
                p, src, size = (cpu.reg_read(reg) for reg in
                                (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                cpu.mem_write(p, bytes(cpu.mem_read(src, size)))
            else:
                return
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_R0, source if source_valid else 0)
        uc.reg_write(A.UC_ARM_REG_R1, target if target_valid else 0)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = names["audio_quicklist_convert_pb"] if compiled else 0x58da28
        uc.emu_start(entry | 1, 0x600000, count=30000)
        return uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(target, 0xe8))

    cases = []
    for length in (0, 1, 20, 199, 200, 201, 255, 65535):
        sample = bytearray(((i * 37 + 11) & 255) for i in range(0xe8))
        sample[24:26] = length.to_bytes(2, "little")
        native, compiled = run(False, sample), run(True, sample)
        if native != compiled:
            raise AssertionError((length, native[0], compiled[0],
                                  next((i for i in range(0xe8) if native[1][i] != compiled[1][i]), None)))
        cases.append({"length": length, "return": native[0],
                      "output_sha256": hashlib.sha256(native[1]).hexdigest()})
    sample = bytes(0xe8)
    for source_valid, target_valid in ((False, True), (True, False), (False, False)):
        native, compiled = run(False, sample, source_valid, target_valid), run(True, sample, source_valid, target_valid)
        if native != compiled:
            raise AssertionError((source_valid, target_valid, native[0], compiled[0]))
        cases.append({"source_valid": source_valid, "target_valid": target_valid,
                      "return": native[0], "output_sha256": hashlib.sha256(native[1]).hexdigest()})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_CONVERT_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entry": "0x58da28", "native_body_sha256": hashlib.sha256(BODY).hexdigest(),
           "cases": cases, "coverage": "return and complete 232-byte output across title-length boundaries and null inputs",
           "limits": ["Native memory helpers were intercepted; final placement and device behavior remain open."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
