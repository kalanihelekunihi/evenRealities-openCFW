#!/usr/bin/env python3
"""Controlled stock/C oracle for notification whitelist-check response encoding."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_tx_whitelist_check_4d76cc.c"
COMMON = G2 / "components/audio/uart_thread_source_candidate/message_notify_tx_common_4d7038.c"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-check"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
const uint8_t audio_ble_ancc_not_whitelisted_pb_descriptor[24]={0};
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_ring_pb_assert_509b48(const void*a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(image, segments, symbols, compiled, ident, has_response, response,
        encode_ok, written, flags, cache_mode):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, image)
    cpu.mem_map(0x100000, 0x100000)
    for address, content in segments:
        cpu.mem_write(address, content)
    cpu.mem_map(0x20000000, 0x200000)
    cpu.mem_map(0x20300000, 0x100000)
    payload = 0x20010000
    cpu.mem_write(payload, bytes(response))
    valid_cell = (symbols["audio_message_notify_crc_valid_2007501b"] if compiled else 0x2007501b)
    cached_cell = (symbols["audio_message_notify_cached_crc_200749a4"] if compiled else 0x200749a4)
    app_crc = int.from_bytes(bytes(response[:4]), "little")
    cached_crc = app_crc if cache_mode == 1 else (app_crc ^ 0x89abcdef)
    cpu.mem_write(valid_cell, bytes((int(cache_mode != 0),)))
    cpu.mem_write(cached_cell, cached_crc.to_bytes(4, "little"))
    tx = (symbols["audio_message_notify_tx_packet_2037c7a0"]
          if compiled else 0x2037c7a0)
    state = (symbols["audio_message_notify_tx_state_200f60e0"]
             if compiled else 0x200f60e0)
    descriptor = (symbols["audio_ble_ancc_not_whitelisted_pb_descriptor"]
                  if compiled else 0x7799f4)
    cpu.mem_write(tx, bytes([0xa5]) * 0x100)
    cpu.mem_write(state, bytes([0x5a]) * 0x4c)
    labels = {"ostream": (0x4905f4, "audio_pb_ostream_from_buffer"),
              "copy": (0x439c04, "audio_uart_checksum_copy"),
              "zero": (0x43c0e4, "audio_uart_buffer_zero"),
              "encode": (0x490c32, "audio_pb_encode"),
              "send": (0x475b14, "audio_ring_pb_tx_ble_475b14"),
              "fault": (0x509b48, "audio_ring_pb_assert_509b48"),
              "flags": (0x43d0ce, "audio_log_flags"),
              "extended": (0x43d574, "audio_log_extended"),
              "compact": (0x43ce9e, "compressed_log_output")}
    cuts = {(symbols[name] & ~1) if compiled else native: kind
            for kind, (native, name) in labels.items()}
    effects = []

    def cstr(address):
        return bytes(cpu.mem_read(address, 160)).split(b"\0")[0].decode("latin1")

    def hook(machine, pc, width, unused):
        kind = cuts.get(pc)
        if kind is None:
            return
        a, b, c, d = (machine.reg_read(reg) for reg in
                      (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                       A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
        result = 0
        if kind == "ostream":
            effects.append((kind, b == tx, c))
            machine.mem_write(a, (0x12345679).to_bytes(4, "little") +
                              b.to_bytes(4, "little") + c.to_bytes(4, "little") + bytes(8))
        elif kind == "copy":
            effects.append((kind, c))
            machine.mem_write(a, bytes(machine.mem_read(b, c)))
        elif kind == "zero":
            effects.append((kind, a == state, b, c))
            machine.mem_write(a, bytes([c & 255]) * b)
        elif kind == "encode":
            effects.append((kind, b == descriptor, c == state))
            machine.mem_write(a + 12, written.to_bytes(4, "little"))
            result = int(encode_ok)
        elif kind == "send":
            effects.append((kind, a, b, c == tx, d))
        elif kind == "fault":
            raw = bytes(machine.mem_read(a, 20))
            words = [int.from_bytes(raw[i:i+4], "little") for i in range(0, 20, 4)]
            effects.append((kind, words[0], words[1], cstr(words[2]),
                            cstr(words[3]), words[4]))
        elif kind == "flags":
            effects.append((kind,))
            result = flags
        elif kind == "extended":
            effects.append((kind, a, cstr(b), cstr(c), cstr(d)))
        elif kind == "compact":
            effects.append((kind, a, cstr(b)))
        machine.reg_write(A.UC_ARM_REG_R0, result)
        machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(A.UC_ARM_REG_R0, ident)
    cpu.reg_write(A.UC_ARM_REG_R1, payload if has_response else 0)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    entry = symbols["audio_message_notify_tx_whitelist_check_4d76cc"] if compiled else 0x4d76cc
    cpu.emu_start(entry | 1, 0x600000, count=40000)
    return (cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(state, 0x4c)),
            bytes(cpu.mem_read(tx, 0x100)), effects,
            bytes(cpu.mem_read(valid_cell, 1)), bytes(cpu.mem_read(cached_cell, 4)))


def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "tx-whitelist-check-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "tx-whitelist-check-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_message_notify_tx_whitelist_check_4d76cc",
                    str(SOURCE), str(COMMON), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for ident, response, encode_ok, written, flags, cache_mode in itertools.product(
            (0, 1, 255, 0x100), (None, (0, 1, 2, 3, 4, 5), (1, 4, 7, 9, 11, 13), (255, 0, 127, 63, 2, 88)),
            (0, 1), (0, 0x12345), (0, 1, 2, 4, 7), (0, 1, 2)):
        args = (ident, response is not None, response or (0, 0, 0, 0, 0, 0),
                encode_ok, written, flags, cache_mode)
        stock = run(image, segments, symbols, False, *args)
        actual = run(image, segments, symbols, True, *args)
        if stock != actual:
            raise RuntimeError(f"common response mismatch {args}: stock={stock[0],stock[1][:8],stock[3]} C={actual[0],actual[1][:8],actual[3]}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_TX_WHITELIST_CHECK_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "shared_source": str(COMMON.relative_to(ROOT)), "shared_source_sha256": sha(COMMON),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf_path),
               "cases": cases,
               "scope": "null, CRC cache invalid/equal/different, 76-byte state, 256-byte packet, encode results, send ABI and log metadata",
               "limits": ["Real nanopb and BLE side effects, later variadic log values, final placement and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()
