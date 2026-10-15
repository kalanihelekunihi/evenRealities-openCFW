#!/usr/bin/env python3
"""Native/C branch comparison for the reused BLE notify transport."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_settings_notify_ble.c"
ALIAS = G2 / "components/audio/uart_thread_source_candidate/quicklist_notify_alias_475c1a.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-notify-alias"
NATIVE = {"ota": 0x4487ac, "left": 0x46f258, "role": 0x46f1d0,
          "send": 0x47564e, "flags": 0x43d0ce}
SYMBOL = {"ota": "audio_ota_transfer_active", "left": "audio_app_is_left_slave_role",
          "role": "audio_app_is_local_slave_cmd_role", "send": "audio_ble_msg_tx",
          "flags": "audio_log_flags"}
SHIM = '''#include <stdint.h>
uint32_t audio_ota_transfer_active(void){return 0;}
uint32_t audio_app_is_left_slave_role(void){return 0;}
uint32_t audio_app_is_local_slave_cmd_role(void){return 0;}
uint32_t audio_ble_msg_tx(uint8_t a,uint8_t b,uint8_t c,uint8_t d,const void*e,uint16_t f){return 0;}
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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_ring_pb_tx_ble_475c1a",
                        str(SOURCE), str(ALIAS), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, ota, left, role, type_value, command, length):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            payload = 0x20010000
            u.mem_write(payload, b"\x51" * 64)
            cuts = {(syms[SYMBOL[op]] & ~1) if compiled else addr: op
                    for op, addr in NATIVE.items()}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if op == "send":
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    stack = bytes(cpu.mem_read(sp, 8))
                    trace.append((op, r0, r1, r2, r3, stack))
                    cpu.reg_write(A.UC_ARM_REG_R0, 0x23)
                else:
                    trace.append((op,))
                    cpu.reg_write(A.UC_ARM_REG_R0, {"ota": ota, "left": left,
                                                    "role": role, "flags": 0}[op])
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, type_value)
            u.reg_write(A.UC_ARM_REG_R1, command)
            u.reg_write(A.UC_ARM_REG_R2, payload)
            u.reg_write(A.UC_ARM_REG_R3, length)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_ring_pb_tx_ble_475c1a"] if compiled else 0x475c1a
            u.emu_start(entry | 1, 0x600000, count=100000)
            return u.reg_read(A.UC_ARM_REG_R0), trace

        cases = 0
        for ota, left, role, type_value, command, length in itertools.product(
                (0, 1), (0, 1), (0, 1), (1, 0x101), (0x0c, 0x10c), (1, 0x10001)):
            native = run(False, ota, left, role, type_value, command, length)
            source = run(True, ota, left, role, type_value, command, length)
            if native != source:
                raise AssertionError((ota, left, role, type_value, command, length,
                                      native, source))
            cases += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_NOTIFY_ALIAS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "alias": str(ALIAS.relative_to(ROOT)),
               "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
               "official_payload_sha256": digest, "native_span": "0x475c1a..0x475d5d",
               "cases": cases,
               "limits": ["Role, OTA, lower send, and logging use controlled lower interfaces.",
                          "Return and lower-call order are compared; hardware BLE behavior is open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases)


if __name__ == "__main__":
    main()
