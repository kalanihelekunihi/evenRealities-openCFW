#!/usr/bin/env python3
"""Native/C comparison for the completed-UID nanopb send path."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_send_completed_5591b0.c"
TX = G2 / "components/audio/uart_thread_source_candidate/quicklist_tx_encoders_558d9e.c"
SCHEMA = G2 / "components/audio/uart_thread_source_candidate/quicklist_pb_descriptor.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-send-completed"
NATIVE = {"ostream": 0x4905f4, "copy": 0x439c04, "rowcopy": 0x439be4,
          "zero": 0x43c0e4, "encode": 0x490c32, "send": 0x475c1a,
          "assert": 0x509b48, "flags": 0x43d0ce}
SYMBOL = {"ostream": "audio_pb_ostream_from_buffer", "copy": "audio_uart_checksum_copy",
          "rowcopy": "audio_queue_copy_bytes", "zero": "audio_uart_buffer_zero",
          "encode": "audio_pb_encode", "send": "audio_ring_pb_tx_ble_475c1a",
          "assert": "audio_ring_pb_assert_509b48", "flags": "audio_log_flags"}
SHIM = '''#include <stdint.h>
void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){return a;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){return 0;}
void audio_ring_pb_tx_ble_475c1a(uint32_t a,uint32_t b,const void*c,uint32_t d){}
void audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d){}
void audio_ring_pb_assert_509b48(void*a){}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){return 0;}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "test.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_send_completed_5591b0",
                        str(SOURCE), str(TX), str(SCHEMA), str(shim), "-o", str(elf)],
                       check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, count, encode_ok, sequence):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            payload = 0x20010000
            u.mem_write(payload, bytes((index * 13 + 9) & 255 for index in range(0x1230)))
            if count is not None:
                u.mem_write(payload+2, count.to_bytes(2, "little"))
            tx = syms["audio_quicklist_tx_packet"] if compiled else 0x2037a5a0
            state = syms["audio_quicklist_tx_state"] if compiled else 0x200f7484
            descriptor = syms["audio_quicklist_pb_descriptor"] if compiled else 0x77b02c
            u.mem_write(tx, b"\xa5" * 0x400)
            u.mem_write(state, b"\x5a" * 0x1238)
            u.mem_write(0x20074ffd, bytes([sequence]))
            cuts = {(syms[SYMBOL[op]] & ~1) if compiled else addr: op
                    for op, addr in NATIVE.items()}
            effects = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if op == "ostream":
                    effects.append((op, r1 == tx, r2))
                    cpu.mem_write(r0, (0x12345679).to_bytes(4, "little") +
                                  r1.to_bytes(4, "little") + r2.to_bytes(4, "little") + bytes(8))
                elif op in ("copy", "rowcopy"):
                    effects.append((op, r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
                    cpu.reg_write(A.UC_ARM_REG_R0, r0)
                elif op == "zero":
                    effects.append((op, r0 == state, r1, r2))
                    cpu.mem_write(r0, bytes([r2 & 255]) * r1)
                elif op == "encode":
                    effects.append((op, r1 == descriptor, r2 == state))
                    cpu.mem_write(r0+12, (0x12345).to_bytes(4, "little"))
                    cpu.reg_write(A.UC_ARM_REG_R0, int(encode_ok))
                elif op == "send":
                    effects.append((op, r0, r1, r2 == tx, r3))
                elif op == "assert":
                    raw = bytes(cpu.mem_read(r0, 20))
                    effects.append((op, raw[:8], raw[16:20]))
                else:
                    cpu.reg_write(A.UC_ARM_REG_R0, 0)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, 0)
            u.reg_write(A.UC_ARM_REG_R1, 0 if count is None else payload)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_send_completed_5591b0"] if compiled else 0x5591b0
            u.emu_start(entry | 1, 0x600000, count=1000000)
            return (u.reg_read(A.UC_ARM_REG_R0), bytes(u.mem_read(state, 0x1238)),
                    bytes(u.mem_read(0x20074ffd, 1)), effects)

        cases = 0
        for count, ok, sequence in itertools.product((None, 0, 1, 2, 20),
                                                     (False, True), (0, 255)):
            native, source = run(False, count, ok, sequence), run(True, count, ok, sequence)
            if native != source:
                first = next((i for i, (a, b) in enumerate(zip(native[1], source[1])) if a != b), None)
                raise AssertionError((count, ok, sequence, native[0], source[0], first,
                                      native[2], source[2], native[3], source[3]))
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SEND_COMPLETED_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "native_span": "0x5591b0..0x559369", "cases": cases,
               "limits": ["Nanopb encode, BLE send, assertion, and logging are controlled lower calls.",
                          "Return, complete TX state, sequence, and lower effects are compared.",
                          "RAM placement and hardware behavior remain unproved."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)


if __name__ == "__main__":
    main()
