#!/usr/bin/env python3
"""Controlled stock/C comparison of MessageNotify frame and child dispatch."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_frame_4d6ba8.c"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-frame"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
const uint8_t audio_ble_ancc_not_whitelisted_pb_descriptor[24]={0};
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_pb_stream_init(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_pb_decode(void*a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_message_notify_rx_ctrl_4d6db0(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_tx_ctrl_4d6ea2(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_rx_whitelist_ctrl_4d73d6(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_tx_whitelist_ctrl_4d749a(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_rx_whitelist_check_4d7624(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_tx_whitelist_check_4d76cc(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_message_notify_tx_common_response_4d7038(uint32_t a,const void*b){(void)a;(void)b;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(image, segments, symbols, compiled, command, ident, decode_ok,
        validate_ok, data_valid, length):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, image)
    cpu.mem_map(0x100000, 0x100000)
    for address, content in segments:
        cpu.mem_write(address, content)
    cpu.mem_map(0x20000000, 0x100000)
    data = 0x20010000
    cpu.mem_write(data, bytes(range(32)))
    labels = {
        "zero": (0x48949c, "audio_uart_buffer_zero"),
        "init": (0x48f49c, "audio_uart_pb_stream_init"),
        "copy": (0x439c04, "audio_uart_checksum_copy"),
        "decode": (0x490120, "audio_uart_pb_decode"),
        "ctrl_valid": (0x4d6db0, "audio_message_notify_rx_ctrl_4d6db0"),
        "ctrl_send": (0x4d6ea2, "audio_message_notify_tx_ctrl_4d6ea2"),
        "white_valid": (0x4d73d6, "audio_message_notify_rx_whitelist_ctrl_4d73d6"),
        "white_send": (0x4d749a, "audio_message_notify_tx_whitelist_ctrl_4d749a"),
        "check_valid": (0x4d7624, "audio_message_notify_rx_whitelist_check_4d7624"),
        "check_send": (0x4d76cc, "audio_message_notify_tx_whitelist_check_4d76cc"),
        "common_send": (0x4d7038, "audio_message_notify_tx_common_response_4d7038"),
        "flags": (0x43d0ce, "audio_log_flags"),
    }
    cuts = {(symbols[name] & ~1) if compiled else native: kind
            for kind, (native, name) in labels.items()}
    effects = []
    decoded = None

    def hook(machine, address, size, unused):
        nonlocal decoded
        kind = cuts.get(address)
        if kind is None:
            return
        r0, r1, r2 = (machine.reg_read(reg) for reg in
                      (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
        result = 0
        if kind == "flags":
            effects.append((kind,))
        elif kind == "zero":
            decoded = r0
            effects.append((kind, r1))
            machine.mem_write(r0, bytes(r1))
        elif kind == "init":
            effects.append((kind, r1-data, r2))
            machine.mem_write(r0, bytes(8) + r2.to_bytes(4, "little") + bytes(4))
        elif kind == "copy":
            effects.append((kind, r2))
            machine.mem_write(r0, bytes(machine.mem_read(r1, r2)))
        elif kind == "decode":
            effects.append((kind, r2-decoded))
            if decode_ok:
                machine.mem_write(r2, bytes((command, ident)) + bytes(2) +
                                  bytes((i & 255 for i in range(72))))
            result = int(decode_ok)
        elif kind == "common_send":
            effects.append((kind, r0, bytes(machine.mem_read(r1, 2))))
            result = 0x55
        else:
            effects.append((kind, r0, r1-decoded))
            result = (0 if validate_ok else 5) if kind.endswith("valid") else 0x30 + command
        machine.reg_write(A.UC_ARM_REG_R0, result)
        machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(A.UC_ARM_REG_R0, data if data_valid else 0)
    cpu.reg_write(A.UC_ARM_REG_R1, length)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    entry = symbols["audio_message_notify_frame_process_4d6ba8"] if compiled else 0x4d6ba8
    cpu.emu_start(entry | 1, 0x600000, count=30000)
    return cpu.reg_read(A.UC_ARM_REG_R0), effects


def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "message-notify-frame-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "message-notify-frame-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_message_notify_frame_process_4d6ba8",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for command, ident, decode_ok, validate_ok, data_valid, length in itertools.product(
            (0, 1, 2, 3, 4, 5), (0, 7, 255), (0, 1), (0, 1), (0, 1),
            (0, 32, 65537)):
        args = (command, ident, decode_ok, validate_ok, data_valid, length)
        stock = run(image, segments, symbols, False, *args)
        actual = run(image, segments, symbols, True, *args)
        if stock != actual:
            raise RuntimeError(f"MessageNotify frame mismatch {args}: {stock!r} != {actual!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_FRAME_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf_path),
               "cases": cases,
               "scope": "null, decode, command routing and child ABI under logging-disabled cuts",
               "limits": ["Real nanopb and child handler effects, enabled logging, final layout and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()
