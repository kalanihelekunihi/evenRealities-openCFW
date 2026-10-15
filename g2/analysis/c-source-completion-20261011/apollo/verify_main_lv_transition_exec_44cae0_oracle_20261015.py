#!/usr/bin/env python3
"""Compare Apollo transition interpolation, property lookup and refresh."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_exec_44cae0.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-exec-44cae0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = """#include <stdint.h>
uint32_t audio_uart_lv_color_rgb_mix_482dd8(uint32_t a,uint32_t b,uint32_t x)
{(void)a;(void)b;(void)x;return 0;}
uint32_t audio_uart_lv_style_get_prop_44b7ce(void *s,uint32_t p,uint32_t *out)
{(void)s;(void)p;(void)out;return 0;}
void audio_uart_page_style_value_482868(void *s,uint32_t p,uint32_t v)
{(void)s;(void)p;(void)v;}
void audio_uart_page_style_refresh_44bc8c(void *o,uint32_t s,uint32_t p)
{(void)o;(void)s;(void)p;}
"""
NATIVE = {"mix": 0x482dd8, "get": 0x482946,
          "set": 0x482868, "refresh": 0x44bc8c, "equal": 0x44102e}
COMPILED = {"mix": "audio_uart_lv_color_rgb_mix_482dd8",
            "get": "audio_uart_lv_style_get_prop_44b7ce",
            "set": "audio_uart_page_style_value_482868",
            "refresh": "audio_uart_page_style_refresh_44bc8c"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main payload changed")
    if payload[0x78f270 - 0x438000:0x78f278 - 0x438000] != b"\0" * 8:
        raise RuntimeError("transition flash defaults changed")
    with tempfile.TemporaryDirectory() as temporary:
        elf = Path(temporary) / "exec.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_transition_exec_44cae0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {parts[2]: int(parts[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(parts := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, property, step, start, end, found, present, previous):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, payload)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            node, obj, records, style = 0x20010000, 0x20011000, 0x20012000, 0x20013000
            row = bytearray(0x20)
            row[0:4] = obj.to_bytes(4, "little")
            row[4] = property
            row[8:12] = (0x123456).to_bytes(4, "little")
            row[12:16] = (start & 0xffffffff).to_bytes(4, "little")
            row[16:20] = (end & 0xffffffff).to_bytes(4, "little")
            cpu.mem_write(node, bytes(row))
            object_bytes = bytearray(0x50)
            object_bytes[0x0c:0x10] = records.to_bytes(4, "little")
            object_bytes[0x2a:0x2c] = (2 << 4).to_bytes(2, "little")
            cpu.mem_write(obj, bytes(object_bytes))
            rows = bytearray(16)
            rows[0:4] = (style + 0x100).to_bytes(4, "little")
            rows[4:8] = (0x01000001).to_bytes(4, "little")
            rows[8:12] = style.to_bytes(4, "little")
            rows[12:16] = (0x02000000 | (0x123456 if found else 0x654321)).to_bytes(4, "little")
            cpu.mem_write(records, bytes(rows))
            trace = []
            hooks = {address & ~1: name for name, address in NATIVE.items()}
            if compiled:
                hooks = {names[symbol] & ~1: name for name, symbol in COMPILED.items()}

            def hook(uc, address, size, unused):
                name = hooks.get(address)
                if name is None:
                    return
                r0, r1, r2 = (uc.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if name == "mix":
                    trace.append((name, r0, r1, r2))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x7f332211)
                elif name == "get":
                    trace.append((name, r0, r1))
                    if present:
                        put(uc, r2, previous)
                    uc.reg_write(A.UC_ARM_REG_R0, 1 if present else 0)
                elif name == "equal":
                    uc.reg_write(A.UC_ARM_REG_R0, 1 if (r0 & 0xffffff) == (r1 & 0xffffff) else 0)
                elif name == "set":
                    trace.append((name, r0, r1, r2))
                elif name == "refresh":
                    trace.append((name, r0, r1, r2))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, node)
            cpu.reg_write(A.UC_ARM_REG_R1, step & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = names["audio_uart_lv_transition_exec_44cae0"] if compiled else 0x44cae0
            try:
                cpu.emu_start(entry | 1, 0x600000, count=100000)
            except Exception as error:
                raise RuntimeError((compiled, property, step, hex(cpu.reg_read(A.UC_ARM_REG_PC)),
                                    trace)) from error
            return trace, bytes(cpu.mem_read(node, 0x20)), bytes(cpu.mem_read(obj, 0x50))

        cases = [
            (0x10, 128, 2, 258, False, False, 0),
            (0x10, 0, 2, 258, True, False, 0),
            (0x10, 255, 2, 258, True, True, 258),
            (0x10, 128, 2, 258, True, False, 0),
            (0x10, 128, 2, 258, True, True, 130),
            (0x10, 128, 2, 258, True, True, 129),
            (0x34, 254, 3, 7, True, False, 0),
            (0x35, 255, 3, 7, True, False, 0),
            (0x69, -1, 3, 7, True, False, 0),
            (0x5a, 128, 3, 7, True, False, 0),
            (0x68, 255, 3, 7, True, False, 0),
            (0x64, 127, 3, 7, True, False, 0),
            (0x64, 128, 3, 7, True, False, 0),
            (0x64, 128, 0, 7, True, False, 0),
            (0x64, 128, 3, 0, True, False, 0),
            (0x1c, 0, 0xff112233, 0xaa445566, True, False, 0),
            (0x23, 255, 0xff112233, 0xaa445566, True, False, 0),
            (0x31, 128, 0xff112233, 0xaa445566, True, False, 0),
            (0x39, 128, 0xff112233, 0xaa445566, True, True, 0x00332211),
            (0x3d, 128, 0xff112233, 0xaa445566, True, False, 0),
            (0x45, 128, 0xff112233, 0xaa445566, True, False, 0),
            (0x58, 128, 0xff112233, 0xaa445566, True, False, 0),
            (0x11, 1, 2, 258, True, False, 0),
            (0x11, -1, 2, 258, True, False, 0),
        ]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[0], source[0],
                                      native[1] == source[1], native[2] == source[2]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_EXEC_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x44cae0..0x44cc7d", "cases": len(cases),
               "flash_default_addresses": ["0x78f270", "0x78f274"],
               "flash_default_bytes_sha256": hashlib.sha256(b"\0" * 8).hexdigest(),
               "limits": ["Twenty-four interpolation and refresh cases compared with controlled lower provider results.",
                          "RGB mixer output, live style mutation, and display effects remain lower-provider behavior."]}
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()
