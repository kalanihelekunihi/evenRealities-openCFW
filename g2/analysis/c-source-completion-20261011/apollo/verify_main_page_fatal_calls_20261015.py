#!/usr/bin/env python3
"""Compare Apollo page fatal logger arguments at the native call boundary."""
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
SOURCES = [G2 / "components/audio/uart_thread_source_candidate/display_page_attach_context_44d342.c",
           G2 / "components/audio/uart_thread_source_candidate/display_page_update_wrappers_44d45c.c"]
OUT = G2 / "build/c-firmware/20261015/main-page-fatal-calls"
SHIM = '''#include <stdint.h>
void audio_uart_page_unlink_44d3b2(void *p){}
void audio_uart_lv_obj_setup_layer_43e1fa(void *p){}
void *audio_uart_font_path_node_append(void *p){return 0;}
void *audio_uart_lv_list_first(void *p){return 0;}
void audio_uart_page_notify_44d5f8(void *p){}
uint32_t audio_uart_page_update_core_44d63a(void *p,void *(*first)(void *),void *(*next)(void *,void *)){return 0;}
void *audio_uart_lv_list_next(void *p,void *n){return 0;}
void *audio_uart_lv_list_first_482ce4(void *p){return 0;}
void *audio_uart_lv_list_next_482cfa(void *p,void *n){return 0;}
void audio_uart_lvgl_log(uint32_t level,const char *source,uint32_t line,const char *name,...){}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_attach_context_44d342",
                        *map(str, SOURCES), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, kind):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, context, layer = 0x20010000, 0x20012000, 0x20013000
            data = bytearray(64)
            data[8:12] = layer.to_bytes(4, "little")
            u.mem_write(page, bytes(data))
            u.mem_write(layer, b"\0" * 64)
            logger = (syms["audio_uart_lvgl_log"] & ~1) if compiled else 0x44d25c
            unlink = (syms["audio_uart_page_unlink_44d3b2"] & ~1) if compiled else 0x44d3b2
            append = (syms["audio_uart_font_path_node_append"] & ~1) if compiled else 0x482bca
            result = []

            def read_string(ptr):
                raw = bytes(u.mem_read(ptr, 128))
                return raw.split(b"\0", 1)[0].decode("utf8", "replace")

            def hook(cpu, address, size, unused):
                if address == logger:
                    sp = cpu.reg_read(A.UC_ARM_REG_SP)
                    args = [cpu.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                                      A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
                    args += [int.from_bytes(cpu.mem_read(sp+4*i,4), "little") for i in range(3)]
                    result.append((args[0], read_string(args[1]), args[2],
                                   *(read_string(a) for a in (args[3],args[4],args[5],args[6]))))
                    cpu.emu_stop()
                elif address == unlink or address == append:
                    cpu.reg_write(A.UC_ARM_REG_R0, 0)
                    cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, context if kind == "attach" else 0)
            u.reg_write(A.UC_ARM_REG_R1, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            name, native_entry = {"attach": ("audio_uart_page_attach_context_44d342",0x44d342),
                                  "next": ("audio_uart_page_update_unbound_44d45c",0x44d45c),
                                  "prev": ("audio_uart_page_update_bound_44d4b6",0x44d4b6)}[kind]
            u.emu_start((syms[name] if compiled else native_entry) | 1, 0x600000, count=10000)
            if len(result) != 1:
                raise AssertionError((kind, compiled, result))
            return result[0]

        for kind in ("attach", "next", "prev"):
            native, source = run(False, kind), run(True, kind)
            if native != source:
                raise AssertionError((kind, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_FATAL_CALLS_ORACLE",
               "sources": [{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in SOURCES],
               "official_payload_sha256": digest, "cases": 3,
               "limits": ["Logger entry arguments are compared; infinite-loop and logger internals are not executed.",
                          "Attachment case controls list insertion failure; wrapper cases use null page."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],3)


if __name__ == "__main__":
    main()
