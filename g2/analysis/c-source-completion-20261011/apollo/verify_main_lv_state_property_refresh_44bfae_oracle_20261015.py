#!/usr/bin/env python3
"""Controlled native comparison of per-property state refresh and animation setup."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_state_property_refresh_44bfae.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-state-property-refresh-44bfae"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = """#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x100];
uint32_t audio_uart_lv_style_property_44bdea(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void *audio_uart_lv_transition_style_44c72c(void *a,uint32_t b){(void)a;(void)b;return 0;}
void audio_uart_page_style_value_482868(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_page_style_refresh_44bc8c(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
int32_t audio_uart_lv_obj_width_43fd9e(void *a){(void)a;return 0;}
int32_t audio_uart_lv_obj_height_43fdda(void *a){(void)a;return 0;}
void *audio_uart_lv_list_prepend_482b12(void *a){(void)a;return 0;}
void audio_uart_lv_anim_init_4503d6(void *a){(void)a;}
void audio_uart_lv_anim_values_4506ce(void *a,int32_t b,int32_t c){(void)a;(void)b;(void)c;}
void *audio_uart_lv_anim_start_450408(void *a){(void)a;return 0;}
void audio_uart_lvgl_log(uint32_t a,const char *b,uint32_t c,const char *d,const char *e,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;}
void audio_uart_lv_transition_exec_44cae0(void *a,uint32_t b){(void)a;(void)b;}
void audio_uart_lv_transition_ready_44cc8c(void *a){(void)a;}
void audio_uart_lv_transition_delete_44ccd8(void *a){(void)a;}
"""
NATIVE = {
    "property": 0x44bdea, "equal": 0x44102e, "transition_style": 0x44c72c,
    "style_value": 0x482868, "style_refresh": 0x44bc8c,
    "width": 0x43fd9e, "height": 0x43fdda, "list_prepend": 0x482b12,
    "anim_init": 0x4503d6, "anim_values": 0x4506ce, "anim_start": 0x450408,
    "log": 0x44d25c,
}
COMPILED = {
    "property": "audio_uart_lv_style_property_44bdea",
    "transition_style": "audio_uart_lv_transition_style_44c72c",
    "style_value": "audio_uart_page_style_value_482868",
    "style_refresh": "audio_uart_page_style_refresh_44bc8c",
    "width": "audio_uart_lv_obj_width_43fd9e",
    "height": "audio_uart_lv_obj_height_43fdda",
    "list_prepend": "audio_uart_lv_list_prepend_482b12",
    "anim_init": "audio_uart_lv_anim_init_4503d6",
    "anim_values": "audio_uart_lv_anim_values_4506ce",
    "anim_start": "audio_uart_lv_anim_start_450408",
    "log": "audio_uart_lvgl_log",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word(cpu, address):
    return int.from_bytes(cpu.mem_read(address, 4), "little")


def put_word(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as temporary:
        elf = Path(temporary) / "refresh.elf"
        shim = Path(temporary) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_state_property_refresh_44bfae",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        names = {parts[2]: int(parts[0], 16)
                 for line in subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                 if len(parts := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(part["p_vaddr"], part.data())
                        for part in ELFFile(stream).iter_segments() if part["p_type"] == "PT_LOAD"]

        def run(compiled, old, new, prop, width, height):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, payload)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            obj, entry, style_entry, node = 0x20010000, 0x20011000, 0x20013000, 0x20014000
            cpu.mem_write(obj, bytes(0x50))
            put_word(cpu, style_entry, 0x20013100)
            trans = bytearray(20)
            trans[0:2] = (370).to_bytes(2, "little")
            trans[2:4] = (35).to_bytes(2, "little")
            trans[4:8] = (0x123400).to_bytes(4, "little")
            trans[8] = prop
            trans[12:16] = (0x20015001).to_bytes(4, "little")
            trans[16:20] = (0x20015003).to_bytes(4, "little")
            cpu.mem_write(entry, bytes(trans))
            cpu.mem_write(node, bytes(0x20))
            trace, descriptor = [], None
            hooks = {address & ~1: name for name, address in NATIVE.items()}
            if compiled:
                hooks = {names[symbol] & ~1: name for name, symbol in COMPILED.items()}

            def hook(uc, address, size, unused):
                nonlocal descriptor
                name = hooks.get(address)
                if name is None:
                    return
                r0 = uc.reg_read(A.UC_ARM_REG_R0)
                r1 = uc.reg_read(A.UC_ARM_REG_R1)
                r2 = uc.reg_read(A.UC_ARM_REG_R2)
                if name == "property":
                    state = int.from_bytes(uc.mem_read(obj + 0x28, 2), "little")
                    value = old if state == 0x12 else new
                    trace.append((name, state, r1, r2, value))
                    uc.reg_write(A.UC_ARM_REG_R0, value)
                elif name == "equal":
                    uc.reg_write(A.UC_ARM_REG_R0, 1 if r0 == r1 else 0)
                elif name == "transition_style":
                    trace.append((name, r1))
                    uc.reg_write(A.UC_ARM_REG_R0, style_entry)
                elif name == "style_value":
                    trace.append((name, r0, r1, r2))
                elif name == "style_refresh":
                    trace.append((name, r1, r2))
                elif name in ("width", "height"):
                    trace.append((name,))
                    uc.reg_write(A.UC_ARM_REG_R0, width if name == "width" else height)
                elif name == "list_prepend":
                    trace.append((name,))
                    uc.reg_write(A.UC_ARM_REG_R0, node)
                elif name == "anim_init":
                    trace.append((name,))
                    data = bytearray(0x60)
                    data[0x30:0x34] = (500).to_bytes(4, "little")
                    data[0x2c:0x30] = (100).to_bytes(4, "little")
                    data[0x44:0x48] = (1).to_bytes(4, "little")
                    data[0x5c] = 0x10
                    uc.mem_write(r0, bytes(data))
                elif name == "anim_values":
                    trace.append((name, r1, r2))
                    put_word(uc, r0 + 0x24, r1)
                    put_word(uc, r0 + 0x28, 0x80000000)
                    put_word(uc, r0 + 0x2c, r2)
                elif name == "anim_start":
                    trace.append((name,))
                    data = bytearray(uc.mem_read(r0, 0x60))
                    for offset in (4, 0x0c, 0x10):
                        data[offset:offset + 4] = b"\0" * 4
                    descriptor = bytes(data)
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20017000)
                elif name == "log":
                    raise AssertionError("unexpected fatal logger")
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, obj)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x123400)
            cpu.reg_write(A.UC_ARM_REG_R2, 0x12)
            cpu.reg_write(A.UC_ARM_REG_R3, 0x34)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            put_word(cpu, 0x203ff000, entry)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            function = names["audio_uart_lv_state_property_refresh_44bfae"] if compiled else 0x44bfae
            try:
                cpu.emu_start(function | 1, 0x600000, count=100000)
            except Exception as error:
                raise RuntimeError((compiled, old, new, prop,
                                    hex(cpu.reg_read(A.UC_ARM_REG_PC)), trace)) from error
            return (trace, bytes(cpu.mem_read(obj, 0x50)),
                    bytes(cpu.mem_read(node, 0x20)), descriptor)

        cases = [
            (2, 2, 0x31, 20, 30),
            (2, 5, 0x31, 20, 30),
            (0x7fff, 7, 0x0c, 100, 60),
            (7, 0x7fff, 0x0c, 100, 60),
            (0x7fff, 0x7fff, 0x0c, 100, 60),
            (0x7fff, 7, 0x0c, -9, 15),
        ]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[0], source[0],
                                      native[1] == source[1], native[2] == source[2],
                                      native[3] == source[3]))
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LV_STATE_PROPERTY_REFRESH_ORACLE",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "official_payload_sha256": PAYLOAD_SHA, "native_span": "0x44bfae..0x44c14d",
        "cases": len(cases),
        "limits": ["Style reads, allocation and animation scheduler responses are controlled.",
                   "Fatal allocation path and live callback behavior remain open."],
    }
    path = OUT / "oracle.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(path))


if __name__ == "__main__":
    main()
