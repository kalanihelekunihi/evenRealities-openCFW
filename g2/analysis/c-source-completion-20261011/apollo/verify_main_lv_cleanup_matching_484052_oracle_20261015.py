#!/usr/bin/env python3
"""Compare Apollo deferred callback matching with compiled C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_cleanup_matching_484052.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-cleanup-matching-484052"
SHIM = '''#include <stdint.h>
void *audio_uart_lv_timer_iter_4645ec(void *p){return 0;}
void audio_uart_lv_timer_remove_4644ee(void *p){}
void audio_uart_lv_heap_free(void *p){}
void audio_uart_lv_delete_event_callback_44df20(void *p){}
'''
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_cleanup_matching_484052",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, count, callback_mask, user_mask, timer_mask):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            nodes = [0x20010000 + i * 0x100 for i in range(count)]
            args = [0x20011000 + i * 0x100 for i in range(count)]
            user = 0x20020000
            callback = (syms["audio_uart_lv_delete_event_callback_44df20"] | 1) if compiled else 0x44df21
            timer_callback = (syms["audio_uart_lv_async_dispatch_4840ac"] | 1) if compiled else 0x4840ad
            def put(addr, value): u.mem_write(addr, value.to_bytes(4, "little"))
            for i, node in enumerate(nodes):
                put(node + 8, timer_callback if timer_mask & (1 << i) else 0x20030001)
                put(node + 0xc, args[i])
                put(args[i], callback if callback_mask & (1 << i) else 0x20030001)
                put(args[i] + 4, user if user_mask & (1 << i) else 0x20021000)
            cuts = {
                (syms["audio_uart_lv_timer_iter_4645ec"] & ~1) if compiled else 0x4645ec: "iter",
                (syms["audio_uart_lv_timer_remove_4644ee"] & ~1) if compiled else 0x4644ee: "remove",
                (syms["audio_uart_lv_heap_free"] & ~1) if compiled else 0x44f758: "free",
            }
            trace = []
            active = list(nodes)
            def label(value):
                return "null" if value == 0 else f"node{nodes.index(value)}" if value in nodes else \
                    f"arg{args.index(value)}" if value in args else hex(value)
            def hook(cpu, address, size, user_data):
                kind = cuts.get(address)
                if kind is None: return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append((kind, label(r0)))
                if kind == "iter":
                    result = active[0] if r0 == 0 and active else \
                        nodes[nodes.index(r0) + 1] if r0 in nodes and nodes.index(r0) + 1 < len(nodes) else 0
                else:
                    if kind == "remove": active.remove(r0)
                    result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, callback)
            u.reg_write(A.UC_ARM_REG_R1, user)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_cleanup_matching_484052"] if compiled else 0x484052) | 1,
                        0x600000, count=100000)
            return trace, [label(n) for n in active], u.reg_read(A.UC_ARM_REG_R0) & 0xff
        cases = [(count, cb, user, timer) for count in range(4)
                 for cb, user, timer in itertools.product(range(1 << count), repeat=3)]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
        def run_dispatch(compiled, callback_arg):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            node, arg, callback = 0x20010000, 0x20011000, 0x20030001
            u.mem_write(node + 0xc, arg.to_bytes(4, "little"))
            u.mem_write(arg, callback.to_bytes(4, "little"))
            u.mem_write(arg + 4, callback_arg.to_bytes(4, "little"))
            cuts = {
                (syms["audio_uart_lv_timer_remove_4644ee"] & ~1) if compiled else 0x4644ee: "remove",
                (syms["audio_uart_lv_heap_free"] & ~1) if compiled else 0x44f758: "free",
                callback & ~1: "callback",
            }
            trace = []
            def hook(cpu, address, size, user_data):
                kind = cuts.get(address)
                if kind is None: return
                trace.append((kind, cpu.reg_read(A.UC_ARM_REG_R0)))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, node)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_async_dispatch_4840ac"] if compiled else 0x4840ac) | 1,
                        0x600000, count=10000)
            return trace
        dispatch_cases = (0, 1, 0x20020000, 0xffffffff)
        for case in dispatch_cases:
            native, source = run_dispatch(False, case), run_dispatch(True, case)
            if native != source: raise AssertionError(("dispatch", case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_CLEANUP_MATCHING_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x484052..0x4840a9",
               "cases": len(cases) + len(dispatch_cases),
               "limits": ["Timer iteration/removal, frees, and callback invocation controlled; live timer side effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["cases"])

if __name__ == "__main__": main()
