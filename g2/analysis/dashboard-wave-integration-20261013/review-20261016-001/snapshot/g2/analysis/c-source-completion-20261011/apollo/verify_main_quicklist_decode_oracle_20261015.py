#!/usr/bin/env python3
"""Bounded native/C Quicklist command dispatch comparison with storage cuts."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_decode_558b3c.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-decode"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
NATIVE = IMAGE[0x558b3c - 0x438000:0x558cb0 - 0x438000]
assert NATIVE[:2] == bytes.fromhex("38b5") and NATIVE[-2:] == bytes.fromhex("30bd")

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("""#include <stdint.h>
uint32_t audio_quicklist_store_one(const void *p) { (void)p; return 0; }
uint32_t audio_quicklist_store_many(const void *p) { (void)p; return 0; }
""")
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_decode_558b3c",
                    str(SRC), str(shim), "-o", str(elf_path)], check=True)
    symbols = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(segment["p_vaddr"], segment.data()) for segment in
                    ELFFile(stream).iter_segments() if segment["p_type"] == "PT_LOAD"]

    def run(compiled, command, event, storage_result):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        state = symbols["audio_quicklist_rx_state"] if compiled else 0x200f624c
        uc.mem_write(state, bytes([command, 0, 0, 0, 0, 0, 0, 0, event]))
        native_cuts = {0x58d51c: "one", 0x58d668: "many", 0x43d0ce: "flags",
                       0x43d574: "extended", 0x43ce9e: "compact"}
        compiled_cuts = {symbols["audio_quicklist_store_one"] & ~1: "one",
                         symbols["audio_quicklist_store_many"] & ~1: "many"}
        cuts = compiled_cuts if compiled else native_cuts
        effects = []

        def hook(cpu, address, _size, _user):
            kind = cuts.get(address)
            if kind is None:
                return
            if kind in ("one", "many"):
                effects.append((kind, cpu.reg_read(A.UC_ARM_REG_R0) - state))
                cpu.reg_write(A.UC_ARM_REG_R0, storage_result)
            elif kind == "flags":
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_quicklist_decode_558b3c"] if compiled else 0x558b3c
        uc.emu_start(entry | 1, 0x600000, count=10000)
        return uc.reg_read(A.UC_ARM_REG_R0), effects

    cases = []
    for command, event, storage_result in ((0, 0, 0), (1, 0, 0), (1, 0, 7),
                                           (2, 0, 0), (2, 0, 9), (3, 1, 0),
                                           (3, 2, 0), (3, 9, 0), (4, 0, 0),
                                           (255, 0, 0)):
        native = run(False, command, event, storage_result)
        compiled = run(True, command, event, storage_result)
        if native != compiled:
            raise AssertionError((command, event, storage_result, native, compiled))
        cases.append({"command": command, "event": event, "storage_result": storage_result,
                      "return": native[0], "storage_effects": native[1]})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_DECODE_ORACLE",
           "source": str(SRC.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entry": "0x558b3c", "native_body_sha256": hashlib.sha256(NATIVE).hexdigest(),
           "cases": cases, "coverage": "command dispatch and storage-call arguments with logging flags zero",
           "limits": ["Storage children and frame parser remain separate unresolved contracts.",
                      "Logging branches and final RAM placement are not covered."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
