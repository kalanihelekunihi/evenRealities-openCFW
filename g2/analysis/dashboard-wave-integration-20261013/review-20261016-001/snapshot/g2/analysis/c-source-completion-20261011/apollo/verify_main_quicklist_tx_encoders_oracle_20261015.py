#!/usr/bin/env python3
"""Native/C QuickList item, multi-item and event transmit path comparison."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_tx_encoders_558d9e.c"
SCHEMA = G2 / "components/audio/uart_thread_source_candidate/quicklist_pb_descriptor.c"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-tx-encoders"
OUT.mkdir(parents=True, exist_ok=True)
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = {"one": (0x558d9e, "audio_quicklist_one_dispatch"),
           "many": (0x558ffe, "audio_quicklist_many_dispatch"),
           "event": (0x559470, "audio_quicklist_event_dispatch")}

with tempfile.TemporaryDirectory() as tmp:
    shim = Path(tmp) / "shim.c"
    shim.write_text("""#include <stdint.h>
void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
void audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d)
{(void)a;(void)b;(void)c;(void)d;}
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
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_one_dispatch",
                    str(SRC), str(SCHEMA), str(shim), "-o", str(elf_path)], check=True)
    names = {parts[2]: int(parts[0], 16) for row in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf_path)], text=True).splitlines()
        if len(parts := row.split()) == 3}
    with elf_path.open("rb") as stream:
        segments = [(seg["p_vaddr"], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
    hooks = {"ostream": (0x4905f4, "audio_pb_ostream_from_buffer"),
             "copy": (0x439c04, "audio_uart_checksum_copy"),
             "zero": (0x43c0e4, "audio_uart_buffer_zero"),
             "encode": (0x490c32, "audio_pb_encode"),
             "send": (0x475b14, "audio_ring_pb_tx_ble_475b14"),
             "assert": (0x509b48, "audio_ring_pb_assert_509b48"),
             "flags": (0x43d0ce, "audio_log_flags")}

    def run(compiled, kind, has_payload, encode_ok, ident):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x200000)
        uc.mem_map(0x20300000, 0x100000)
        payload = 0x20010000
        uc.mem_write(payload, bytes((i * 13 + 9) & 255 for i in range(0xe8)))
        tx = names["audio_quicklist_tx_packet"] if compiled else 0x2037a5a0
        state = names["audio_quicklist_tx_state"] if compiled else 0x200f7484
        descriptor = names["audio_quicklist_pb_descriptor"] if compiled else 0x77b02c
        uc.mem_write(tx, bytes([0xa5]) * 0x400)
        uc.mem_write(state, bytes([0x5a]) * 0x1238)
        cuts = {(names[name] & ~1) if compiled else address: op
                for op, (address, name) in hooks.items()}
        effects = []

        def string(pointer):
            return bytes(uc.mem_read(pointer, 160)).split(b"\0")[0].decode("ascii")

        def hook(cpu, address, _size, _user):
            op = cuts.get(address)
            if op is None:
                return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if op == "ostream":
                effects.append((op, r1 == tx, r2))
                cpu.mem_write(r0, (0x12345679).to_bytes(4, "little") + r1.to_bytes(4, "little") +
                              r2.to_bytes(4, "little") + bytes(8))
            elif op == "copy":
                effects.append((op, r2))
                cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
            elif op == "zero":
                effects.append((op, r0 == state, r1, r2))
                cpu.mem_write(r0, bytes([r2 & 255]) * r1)
            elif op == "encode":
                effects.append((op, r1 == descriptor, r2 == state))
                cpu.mem_write(r0 + 12, (0x12345).to_bytes(4, "little"))
                cpu.reg_write(A.UC_ARM_REG_R0, int(encode_ok))
            elif op == "send":
                effects.append((op, r0, r1, r2 == tx, r3))
            elif op == "assert":
                raw = bytes(cpu.mem_read(r0, 20))
                effects.append((op, int.from_bytes(raw[4:8], "little"),
                                string(int.from_bytes(raw[8:12], "little")),
                                string(int.from_bytes(raw[12:16], "little")),
                                int.from_bytes(raw[16:20], "little")))
            else:
                cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, hook)
        uc.reg_write(A.UC_ARM_REG_R0, ident)
        uc.reg_write(A.UC_ARM_REG_R1, payload if has_payload else 0)
        uc.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        native, symbol = ENTRIES[kind]
        uc.emu_start((names[symbol] if compiled else native) | 1, 0x600000, count=40000)
        return uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(state, 0x1238)), effects

    cases = []
    for kind in ENTRIES:
        for has_payload, encode_ok in ((False, False), (True, False), (True, True)):
            native = run(False, kind, has_payload, encode_ok, 0x12a)
            compiled = run(True, kind, has_payload, encode_ok, 0x12a)
            if native != compiled:
                index = next((i for i in range(0x1238) if native[1][i] != compiled[1][i]), None)
                raise AssertionError((kind, has_payload, encode_ok, native[0], compiled[0],
                                      index, native[1][index] if index is not None else None,
                                      compiled[1][index] if index is not None else None,
                                      native[2], compiled[2]))
            cases.append({"kind": kind, "payload": has_payload, "encode_ok": encode_ok,
                          "return": native[0], "effects": native[2],
                          "state_sha256": hashlib.sha256(native[1]).hexdigest()})

receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_TX_ENCODERS_ORACLE",
           "source": str(SRC.relative_to(ROOT)), "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
           "schema_source": str(SCHEMA.relative_to(ROOT)), "schema_source_sha256": hashlib.sha256(SCHEMA.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_entries": {key: hex(value[0]) for key, value in ENTRIES.items()},
           "cases": cases, "coverage": "return, complete TX message state and lower encode/BLE effects with logging disabled",
           "limits": ["Nanopb encode, BLE send and assertion were intercepted; logging-enabled paths and hardware remain open."]}
(OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], len(cases))
