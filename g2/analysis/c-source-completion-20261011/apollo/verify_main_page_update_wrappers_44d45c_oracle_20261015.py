#!/usr/bin/env python3
"""Compare bounded Apollo update wrappers against the official payload."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_page_update_wrappers_44d45c.c"
OUT = G2 / "build/c-firmware/20261015/main-page-update-wrappers-44d45c"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_page_update_core_44d63a(void *p,void *(*first)(void *),void *(*next)(void *,void *)){return 0;}
void *audio_uart_lv_list_first(void *p){return 0;}
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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_update_unbound_44d45c",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, bound, has_callback, core_result):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            page, callback = 0x20010000, 0x20018000
            initial = bytearray(range(64))
            initial[0x14:0x18] = ((callback | 1) if has_callback else 0).to_bytes(4, "little")
            u.mem_write(page, bytes(initial))
            native_entry = 0x44d4b6 if bound else 0x44d45c
            name = "audio_uart_page_update_bound_44d4b6" if bound else "audio_uart_page_update_unbound_44d45c"
            cuts = {(syms["audio_uart_page_update_core_44d63a"] & ~1) if compiled else 0x44d63a: "core",
                    callback: "callback"}
            trace = []

            def hook(cpu, address, size, unused):
                op = cuts.get(address)
                if op is None:
                    return
                args = [cpu.reg_read(reg) for reg in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)]
                if op == "core":
                    first_name = "audio_uart_lv_list_first_482ce4" if bound else "audio_uart_lv_list_first"
                    next_name = "audio_uart_lv_list_next_482cfa" if bound else "audio_uart_lv_list_next"
                    first = (syms[first_name] | 1) if compiled else (0x482ce5 if bound else 0x482cd9)
                    next_ptr = (syms[next_name] | 1) if compiled else (0x482cfb if bound else 0x482cf1)
                    trace.append((op, args[0], args[1] == first, args[2] == next_ptr))
                    cpu.reg_write(A.UC_ARM_REG_R0, core_result)
                else:
                    trace.append((op, args[0], args[1]))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, page)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms[name] if compiled else native_entry) | 1, 0x600000, count=100000)
            return trace, bytes(u.mem_read(page, 64))

        count = 0
        for bound in (False, True):
            for has_callback in (False, True):
                for core_result in (0, 1, 0x100):
                    native = run(False, bound, has_callback, core_result)
                    source = run(True, bound, has_callback, core_result)
                    if native != source:
                        raise AssertionError((bound, has_callback, core_result,
                                              native[0], source[0], native[1] == source[1]))
                    count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_WRAPPERS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest,
               "native_spans": ["0x44d45c..0x44d4b5", "0x44d4b6..0x44d50f"],
               "cases": count,
               "limits": ["Only non-null page paths are native-compared.",
                          "Traversal and callback targets are controlled; pointer identities and native returns are not compared.",
                          "Null-page diagnostic arguments and hardware behavior remain unverified."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
