#!/usr/bin/env python3
"""Native/C QuickList frame dispatch with nanopb and validator cuts."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_frame_process_55894c.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-frame-process"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODY = IMAGE[0x55894c-0x438000:0x558b3c-0x438000]
assert BODY[:2] == bytes.fromhex("f0b5")

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("""#include <stdint.h>
uint8_t audio_quicklist_rx_state[0x1238];
const uint8_t audio_quicklist_pb_descriptor[4]={0};
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_pb_stream_init(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_pb_decode(void*a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_quicklist_one_validate(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_one_dispatch(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_many_validate(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_many_dispatch(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_event_validate(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_quicklist_event_dispatch(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
""")
    elf_path = Path(tmp) / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_frame_process_55894c",
                    str(SRC), str(shim), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
    labels = {
        "zero": (0x43c0e4, "audio_uart_buffer_zero"),
        "init": (0x48f49c, "audio_uart_pb_stream_init"),
        "copy": (0x439c04, "audio_uart_checksum_copy"),
        "decode": (0x490120, "audio_uart_pb_decode"),
        "one_valid": (0x558cb0, "audio_quicklist_one_validate"),
        "one_send": (0x558d9e, "audio_quicklist_one_dispatch"),
        "many_valid": (0x558f34, "audio_quicklist_many_validate"),
        "many_send": (0x558ffe, "audio_quicklist_many_dispatch"),
        "event_valid": (0x559378, "audio_quicklist_event_validate"),
        "event_send": (0x559470, "audio_quicklist_event_dispatch"),
        "flags": (0x43d0ce, "audio_log_flags"),
    }

    def run(compiled, command, ident, decode_ok, validate_ok, data_valid):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        data = 0x20010000
        uc.mem_write(data, bytes(range(32)))
        state = names["audio_quicklist_rx_state"] if compiled else 0x200f624c
        uc.mem_write(state, bytes([0x5a]) * 0x1238)
        cuts = {(names[name] & ~1) if compiled else stock: key
                for key, (stock, name) in labels.items()}
        effects = []

        def hook(cpu, address, _size, _user):
            kind = cuts.get(address)
            if kind is None:
                return
            r0, r1, r2 = (cpu.reg_read(reg) for reg in
                          (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if kind == "flags":
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "zero":
                effects.append((kind, r0-state, r1, r2))
                cpu.mem_write(r0, bytes(r1))
            elif kind == "init":
                effects.append((kind, r1-data, r2))
                cpu.mem_write(r0, bytes.fromhex("0000000000000000") + r2.to_bytes(4, "little") + bytes(4))
            elif kind == "copy":
                effects.append((kind, r2))
                cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
            elif kind == "decode":
                effects.append((kind, r2-state))
                if decode_ok:
                    cpu.mem_write(r2, bytes([command, ident]))
                cpu.reg_write(A.UC_ARM_REG_R0, int(decode_ok))
            else:
                effects.append((kind, r0, r1-state))
                cpu.reg_write(A.UC_ARM_REG_R0, 0 if (kind.endswith("valid") and validate_ok)
                              else 5 if kind.endswith("valid") else 0x30 + command)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_R0, data if data_valid else 0)
        uc.reg_write(A.UC_ARM_REG_R1, 32)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = names["audio_quicklist_frame_process_55894c"] if compiled else 0x55894c
        uc.emu_start(entry | 1, 0x600000, count=30000)
        return uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(state, 0x1238)), effects

    cases = []
    for command, ident, decode_ok, validate_ok, data_valid in (
        (0, 0, True, True, False), (0, 0, False, True, True),
        (0, 0, True, True, True), (1, 7, True, True, True),
        (1, 7, True, False, True), (2, 8, True, True, True),
        (2, 8, True, False, True), (3, 9, True, True, True),
        (3, 9, True, False, True), (4, 2, True, True, True)):
        native = run(False, command, ident, decode_ok, validate_ok, data_valid)
        compiled = run(True, command, ident, decode_ok, validate_ok, data_valid)
        if native != compiled:
            index = next((i for i in range(0x1238) if native[1][i] != compiled[1][i]), None)
            raise AssertionError((command, ident, decode_ok, validate_ok, data_valid,
                                  native[0], compiled[0], index, native[2], compiled[2]))
        cases.append({"command": command, "id": ident, "decode_ok": decode_ok,
                      "validate_ok": validate_ok, "data_valid": data_valid,
                      "return": native[0], "effects": native[2],
                      "state_sha256": hashlib.sha256(native[1]).hexdigest()})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_FRAME_PROCESS_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entry": "0x55894c", "native_body_sha256": hashlib.sha256(BODY).hexdigest(),
           "cases": cases, "coverage": "decode and command routing with intercepted nanopb, validation and logging-disabled effects",
           "limits": ["Validators, dispatchers, schema descriptor, real nanopb decode and logging-enabled paths remain open."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
