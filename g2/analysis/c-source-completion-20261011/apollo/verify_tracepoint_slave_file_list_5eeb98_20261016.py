#!/usr/bin/env python3
"""Compare stock/C slave file-list decode, merge, and reply branches."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/tracepoint_slave_file_list_5eeb98.c"
OUT = G2 / "build/c-firmware/20261016/main-tracepoint-slave-file-list"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
uint8_t audio_tracepoint_reply_buffer[0x206];
uint8_t audio_tracepoint_local_file_list_ready;
uint8_t audio_tracepoint_file_list_ready_extent_tail_20074ae5[3];
const uint8_t audio_tracepoint_message_descriptor[24]={0};
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_pb_stream_init(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_pb_decode(void*a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
void*audio_settings_copy_text(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;return a;}
uint32_t audio_tracepoint_send_to_phone_5edfd8(const uint8_t*a){(void)a;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(image, segments, symbols, compiled, present, length, decode_ok,
        command, which, slave_count, local_count, ready, send_result, flags):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, image)
    cpu.mem_map(0x100000, 0x100000)
    for address, content in segments:
        cpu.mem_write(address, content)
    cpu.mem_map(0x20000000, 0x400000)
    data = 0x20010000
    cpu.mem_write(data, bytes(range(32)))
    reply = symbols["audio_tracepoint_reply_buffer"] if compiled else 0x2037bbc8
    first = (symbols["audio_tracepoint_local_file_list_ready"]
             if compiled else 0x20074ae4)
    tail = (symbols["audio_tracepoint_file_list_ready_extent_tail_20074ae5"]
            if compiled else 0x20074ae5)
    descriptor = (symbols["audio_tracepoint_message_descriptor"]
                  if compiled else 0x77cd84)
    seed = bytearray([0x5a] * 0x206)
    seed[0] = 1
    seed[4:6] = local_count.to_bytes(2, "little")
    for i in range(16):
        name = (f"local{i:02d}".encode() + b"\0")
        seed[6+i*32:6+i*32+len(name)] = name
    cpu.mem_write(reply, bytes(seed))
    ready_bytes = ready.to_bytes(4, "little")
    cpu.mem_write(first, ready_bytes[:1])
    cpu.mem_write(tail, ready_bytes[1:])
    labels = {"zero": (0x43c0e4, "audio_uart_buffer_zero"),
              "init": (0x48f49c, "audio_uart_pb_stream_init"),
              "copy": (0x439c04, "audio_uart_checksum_copy"),
              "decode": (0x490120, "audio_uart_pb_decode"),
              "text": (0x44b5a0, "audio_settings_copy_text"),
              "send": (0x5edfd8, "audio_tracepoint_send_to_phone_5edfd8"),
              "flags": (0x43d0ce, "audio_log_flags"),
              "extended": (0x43d574, "audio_log_extended"),
              "compact": (0x43ce9e, "compressed_log_output")}
    cuts = {(symbols[name] & ~1) if compiled else native: kind
            for kind, (native, name) in labels.items()}
    effects = []
    decoded = None

    def cstr(address):
        return bytes(cpu.mem_read(address, 200)).split(b"\0")[0].decode("latin1")

    def hook(machine, pc, width, unused):
        nonlocal decoded
        kind = cuts.get(pc)
        if kind is None:
            return
        a, b, c, d = (machine.reg_read(reg) for reg in
                      (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                       A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
        result = 0
        if kind == "flags":
            effects.append((kind,))
            result = flags
        elif kind == "zero":
            decoded = a
            effects.append((kind, b, c))
            machine.mem_write(a, bytes([c & 255]) * b)
        elif kind == "init":
            effects.append((kind, b == data, c))
            machine.mem_write(a, (0x12345679).to_bytes(4, "little") +
                              b.to_bytes(4, "little") + c.to_bytes(4, "little") + bytes(4))
        elif kind == "copy":
            effects.append((kind, c))
            machine.mem_write(a, bytes(machine.mem_read(b, c)))
        elif kind == "decode":
            effects.append((kind, b == descriptor, c == decoded))
            if decode_ok:
                content = bytearray(0x206)
                content[0] = command
                content[1] = 0x47
                content[2:4] = which.to_bytes(2, "little")
                content[4:6] = slave_count.to_bytes(2, "little")
                for i in range(16):
                    name = (f"slave{i:02d}".encode() + b"\0")
                    content[6+i*32:6+i*32+len(name)] = name
                machine.mem_write(c, bytes(content))
            else:
                machine.mem_write(a+12, (0x77ee00).to_bytes(4, "little"))
            result = int(decode_ok)
        elif kind == "text":
            effects.append((kind, (a-reply-6)//32, (b-decoded-6)//32, c))
            src = bytes(machine.mem_read(b, c))
            nul = src.find(0)
            machine.mem_write(a, src if nul < 0 else src[:nul+1] + bytes(c-nul-1))
            result = a
        elif kind == "send":
            effects.append((kind, a == reply, bytes(machine.mem_read(a, 0x206))))
            result = send_result
        elif kind == "extended":
            effects.append((kind, a, cstr(b), cstr(c), cstr(d)))
        elif kind == "compact":
            effects.append((kind, a, cstr(b)))
        machine.reg_write(A.UC_ARM_REG_R0, result)
        machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(A.UC_ARM_REG_R0, data if present else 0)
    cpu.reg_write(A.UC_ARM_REG_R1, length)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    entry = symbols["audio_tracepoint_handle_slave_file_list_5eeb98"] if compiled else 0x5eeb98
    cpu.emu_start(entry | 1, 0x600000, count=40000)
    return (cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(reply, 0x206)),
            bytes(cpu.mem_read(first, 1) + cpu.mem_read(tail, 3)), effects)


def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "slave-file-list-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "slave-file-list-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_tracepoint_handle_slave_file_list_5eeb98",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    scenarios = list(itertools.product((False, True), (0, 32), (False, True),
                                       (0, 1, 2), (0, 3, 4), (0, 1, 17),
                                       (0, 1, 15, 16, 17), (0, 1, 0x100),
                                       (0, 5), (0,)))
    for args in scenarios:
        stock = run(image, segments, symbols, False, *args)
        actual = run(image, segments, symbols, True, *args)
        if stock != actual:
            raise RuntimeError(f"tracepoint slave mismatch {args}: stock={stock[0],stock[2],stock[3][:8]} C={actual[0],actual[2],actual[3][:8]}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_TRACEPOINT_SLAVE_FILE_LIST_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf_path),
               "cases": cases,
               "scope": "decode, command, ready-word, 16-row merge, reply bytes, send result under logging-disabled cuts",
               "limits": ["Enabled logging, real nanopb, string copy and send side effects, final RAM placement and hardware remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()
