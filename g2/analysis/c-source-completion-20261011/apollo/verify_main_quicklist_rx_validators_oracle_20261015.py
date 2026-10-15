#!/usr/bin/env python3
"""Compare QuickList receive validator null and ordinary effects."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_rx_validators_558cb0.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-rx-validators"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = {"one": (0x558cb0, 0x558d9e, "audio_quicklist_one_validate"),
           "many": (0x558f34, 0x558ffe, "audio_quicklist_many_validate"),
           "event": (0x559378, 0x559470, "audio_quicklist_event_validate")}

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("""#include <stdint.h>
void audio_uart_checksum_copy(void*a,const void*b,uint32_t n){(void)a;(void)b;(void)n;}
void audio_ring_pb_assert_509b48(void*a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
""")
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_one_validate",
                    str(SRC), str(shim), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]

    def run(compiled, kind, valid):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        pointer = 0x20010000
        uc.mem_write(pointer, bytes((i * 3 + 7) & 255 for i in range(0xe8)))
        cuts = {(names["audio_uart_checksum_copy"] & ~1) if compiled else 0x439c04: "copy",
                (names["audio_ring_pb_assert_509b48"] & ~1) if compiled else 0x509b48: "assert",
                (names["audio_log_flags"] & ~1) if compiled else 0x43d0ce: "flags"}
        effects = []

        def hook(cpu, address, _size, _user):
            op = cuts.get(address)
            if op is None:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if op == "copy":
                data = bytes(cpu.mem_read(r1, r2))
                effects.append(("copy", r2, data.hex()))
                cpu.mem_write(r0, data)
            elif op == "assert":
                effects.append(("assert", bytes(cpu.mem_read(r0, 20)).hex()))
            else:
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_R0, 17)
        uc.reg_write(A.UC_ARM_REG_R1, pointer if valid else 0)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        native, _end, name = ENTRIES[kind]
        uc.emu_start((names[name] if compiled else native) | 1, 0x600000, count=20000)
        return uc.reg_read(A.UC_ARM_REG_R0), effects

    cases = []
    for kind in ENTRIES:
        for valid in (False, True):
            native, compiled = run(False, kind, valid), run(True, kind, valid)
            if native != compiled:
                raise AssertionError((kind, valid, native, compiled))
            cases.append({"kind": kind, "payload_valid": valid,
                          "return": native[0], "effects": native[1]})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_RX_VALIDATORS_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entries": {key: hex(value[0]) for key, value in ENTRIES.items()},
           "native_body_sha256": {key: hashlib.sha256(IMAGE[value[0]-0x438000:value[1]-0x438000]).hexdigest()
                                  for key, value in ENTRIES.items()},
           "cases": cases, "coverage": "return, copied assertion literal and 20-byte assert record with logging disabled",
           "limits": ["Logging-enabled argument effects and native assertion side effects were intercepted."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
