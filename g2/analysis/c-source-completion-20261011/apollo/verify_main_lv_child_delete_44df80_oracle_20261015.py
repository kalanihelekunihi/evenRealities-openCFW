#!/usr/bin/env python3
"""Controlled native/C comparison for Apollo LVGL child deletion."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_child_delete_44df80.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-child-delete-44df80"
DEPS = {
    "event": (0x451670, "audio_uart_lv_obj_event_451670"),
    "style": (0x450228, "audio_uart_lv_style_destroy_450228"),
    "child": (0x44dce2, "audio_uart_lv_child_get_44dce2"),
    "group": (0x43e1be, "audio_uart_lv_obj_group_43e1be"),
    "input_next": (0x452edc, "audio_uart_lv_input_next_452edc"),
    "input_unlink": (0x44df60, "audio_uart_lv_input_unlink_44df60"),
    "input_active": (0x452ffa, "audio_uart_lv_input_active_452ffa"),
    "cleanup": (0x484052, "audio_uart_lv_cleanup_matching_484052"),
    "obj_cleanup": (0x44d16e, "audio_uart_lv_obj_delete_cleanup_44d16e"),
    "display": (0x44dc0a, "audio_uart_lv_display_for_object"),
    "index": (0x44de92, "audio_uart_lv_child_index_44de92"),
    "realloc": (0x44f76a, "audio_uart_lv_realloc_44f76a"),
    "free": (0x44f758, "audio_uart_lv_heap_free"),
    "filter": (0x44d7b8, "audio_uart_page_delete_event_filter_44d7b8"),
}
SHIM = '''#include <stdint.h>
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t n,void *q){return 0;}
void audio_uart_lv_style_destroy_450228(void *p){}
void *audio_uart_lv_child_get_44dce2(void *p,uint32_t n){return 0;}
void *audio_uart_lv_obj_group_43e1be(void *p){return 0;}
void *audio_uart_lv_input_next_452edc(void *p){return 0;}
void audio_uart_lv_input_unlink_44df60(void *p,void *q){}
void *audio_uart_lv_input_active_452ffa(void){return 0;}
uint32_t audio_uart_lv_cleanup_matching_484052(void *p,void *q){return 0;}
void audio_uart_lv_obj_delete_cleanup_44d16e(void *p){}
void *audio_uart_lv_display_for_object(void *p){return 0;}
uint32_t audio_uart_lv_child_index_44de92(void *p){return 0;}
void *audio_uart_lv_realloc_44f76a(void *p,uint32_t n){return p;}
void audio_uart_lv_heap_free(void *p){}
void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,... ){}
void audio_uart_page_delete_event_filter_44d7b8(void *p){}
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
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_child_delete_44df80",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, allowed, parented, size, position, style,
                child_present=False, input_mode=0, active_mode=0):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            obj, parent, spec, parent_spec = 0x20010000, 0x20011000, 0x20012000, 0x20013000
            display, array = 0x20014000, 0x20015000
            child, child_array, input_obj = 0x20016000, 0x20017000, 0x20018000
            def write(addr, value, width=4):
                u.mem_write(addr, value.to_bytes(width, "little"))
            def read(addr, width=4):
                return int.from_bytes(u.mem_read(addr, width), "little")
            write(obj + 4, parent if parented else 0)
            write(obj + 8, spec if style or child_present else 0)
            write(spec, child_array)
            write(spec + 0x30, 1 if child_present else 0, 2)
            write(child_array, child)
            write(child + 4, obj)
            write(parent + 8, parent_spec)
            write(parent_spec, array)
            write(parent_spec + 0x30, size, 2)
            write(display + 0x2b8, array)
            write(display + 0x2d4, size)
            for i in range(size):
                write(array + i * 4, obj if i == position else 0x20020000 + i * 4)
            if input_mode:
                u.mem_write(input_obj, bytes([3 if input_mode == 2 else 1]))
                for offset in (0x68, 0x6c, 0x70, 0x74, 0x78):
                    write(input_obj + offset, obj if input_mode != 3 else 0x20020000)
                write(input_obj + 0xb8, 0)
            trace = []
            live_child = child_present
            cuts = {(syms[name] & ~1) if compiled else address: kind
                    for kind, (address, name) in DEPS.items()}
            def label(value):
                return {obj: "object", parent: "parent", child: "child",
                        input_obj: "input", spec + 8: "style",
                        display: "display", array: "array",
                        child_array: "child_array", 0: "null"}.get(value, hex(value))
            def hook(cpu, address, insn_size, unused):
                nonlocal live_child
                kind = cuts.get(address)
                if kind is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                if kind == "event":
                    trace.append((kind, label(r0), r1, cpu.reg_read(A.UC_ARM_REG_R2)))
                    result = allowed
                elif kind in ("style", "group", "obj_cleanup", "display", "index", "free"):
                    trace.append((kind, label(r0)))
                    result = {"group": 0, "display": display,
                              "index": 0 if r0 == child else position}.get(kind, 0)
                    if kind == "free" and r0 == child:
                        live_child = False
                elif kind == "child":
                    trace.append((kind, label(r0), r1))
                    result = child if r0 == obj and live_child else 0
                elif kind == "input_next":
                    trace.append((kind, label(r0)))
                    result = input_obj if input_mode and r0 == 0 else 0
                elif kind == "input_unlink":
                    trace.append((kind, label(r0), label(r1)))
                    result = 0
                elif kind == "input_active":
                    trace.append((kind,))
                    result = obj if active_mode else 0
                elif kind == "cleanup":
                    # The pointer differs after linking; callback identity is checked symbolically.
                    expected = (syms["audio_uart_lv_delete_event_callback_44df20"] | 1) if compiled else 0x44df21
                    trace.append((kind, "callback" if r0 == expected else hex(r0), label(r1)))
                    result = 0
                elif kind == "realloc":
                    trace.append((kind, label(r0), r1))
                    result = r0
                else:
                    raise AssertionError((kind, address))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, obj)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            origin = syms["audio_uart_lv_child_delete_44df80"] if compiled else 0x44df80
            u.emu_start(origin | 1, 0x600000, count=100000)
            return (trace, read(obj + 0x2a, 2),
                    read((parent_spec + 0x30) if parented else (display + 0x2d4),
                         2 if parented else 4),
                    [read(array + i * 4) for i in range(size)],
                    read(spec + 0x30, 2), read(child + 0x2a, 2),
                    [read(input_obj + offset) for offset in (0x68, 0x6c, 0x70, 0x74, 0x78)]
                    if input_mode else [])

        cases = list(itertools.product((0, 1), (0, 1), (1, 2, 3), (0, 1), (0, 1)))
        cases = [c for c in cases if c[3] < c[2]]
        cases += [(1, parented, size, 0, 1, True, input_mode, 1)
                  for parented, size, input_mode in itertools.product(
                      (0, 1), (1, 2), (0, 1, 2, 3))]
        cases += [(1, parented, size, 0, 0, False, input_mode, active)
                  for parented, size, input_mode, active in itertools.product(
                      (0, 1), (1, 2), (1, 2, 3), (0, 1))]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_CHILD_DELETE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44df80..0x44e139",
               "cases": len(cases),
               "limits": ["Controlled event, child-list, input-list, callback-cleanup, and allocation helpers.",
                          "Populated-child recursion and input field effects compared with controlled lower helpers; live helper mutations, allocator failure, and screen ownership remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__":
    main()
