#!/usr/bin/env python3
"""Stock/C oracle for MessageNotify whitelist-check validation."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/message_notify_whitelist_check_4d7624.c"
OUT = G2 / "build/c-firmware/20261016/main-message-notify-whitelist-check"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = '''#include <stdint.h>
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_ring_pb_assert_509b48(const void*a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(image, segments, symbols, compiled, body_valid, ident, flags):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    cpu.mem_map(0x400000, 0x400000)
    cpu.mem_write(0x438000, image)
    cpu.mem_map(0x100000, 0x100000)
    for address, content in segments:
        cpu.mem_write(address, content)
    cpu.mem_map(0x20000000, 0x100000)
    payload = 0x20010000
    cpu.mem_write(payload, bytes(range(24)))
    labels = {"copy": (0x439c04, "audio_uart_checksum_copy"),
              "fault": (0x509b48, "audio_ring_pb_assert_509b48"),
              "flags": (0x43d0ce, "audio_log_flags"),
              "extended": (0x43d574, "audio_log_extended"),
              "compact": (0x43ce9e, "compressed_log_output")}
    cuts = {(symbols[name] & ~1) if compiled else native: kind
            for kind, (native, name) in labels.items()}
    calls = []

    def cstr(address):
        result = bytearray()
        for offset in range(180):
            b = cpu.mem_read(address + offset, 1)[0]
            if not b:
                break
            result.append(b)
        return result.decode("latin1")

    def hook(machine, pc, width, unused):
        kind = cuts.get(pc)
        if kind is None:
            return
        a, b, c, d = (machine.reg_read(reg) for reg in
                      (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                       A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
        result = 0
        if kind == "copy":
            calls.append((kind, c))
            machine.mem_write(a, bytes(machine.mem_read(b, c)))
        elif kind == "fault":
            record = bytes(machine.mem_read(a, 20))
            words = [int.from_bytes(record[i:i+4], "little") for i in range(0, 20, 4)]
            calls.append((kind, words[0], words[1], cstr(words[2]),
                          cstr(words[3]), words[4]))
        elif kind == "flags":
            calls.append((kind,))
            result = flags
        elif kind == "extended":
            calls.append((kind, a, cstr(b), cstr(c), cstr(d),
                          int.from_bytes(machine.mem_read(machine.reg_read(A.UC_ARM_REG_SP), 4), "little")))
        elif kind == "compact":
            calls.append((kind, a, cstr(b), cstr(c)))
        machine.reg_write(A.UC_ARM_REG_R0, result)
        machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.reg_write(A.UC_ARM_REG_R0, ident)
    cpu.reg_write(A.UC_ARM_REG_R1, payload if body_valid else 0)
    cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
    entry = symbols["audio_message_notify_rx_whitelist_check_4d7624"] if compiled else 0x4d7624
    cpu.emu_start(entry | 1, 0x600000, count=1200)
    return cpu.reg_read(A.UC_ARM_REG_R0), calls


def main():
    image = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(image).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "whitelist-check-oracle-stub.c"
    stub.write_text(STUB)
    elf_path = OUT / "whitelist-check-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                    "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_message_notify_rx_whitelist_check_4d7624",
                    str(SOURCE), str(stub), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}
    cases = 0
    for args in itertools.product((False, True), (0, 1, 255, 0x100),
                                  (0, 1, 2, 4, 7)):
        stock = run(image, segments, symbols, False, *args)
        actual = run(image, segments, symbols, True, *args)
        if stock != actual:
            raise RuntimeError(f"whitelist-check mismatch {args}: {stock!r} != {actual!r}")
        cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MESSAGE_NOTIFY_WHITELIST_CHECK_C_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "payload_sha256": PIN, "oracle_elf_sha256": sha(elf_path),
               "cases": cases,
               "scope": "null and nonnull, fault record, logging flags and ABI return",
               "limits": ["Fault handler and logger side effects and final placement remain open."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], cases, sha(path))


if __name__ == "__main__":
    main()
