#!/usr/bin/env python3
"""Compare Apollo display/task refresh walk with controlled stock lower calls."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_refresh_tasks_484548.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-refresh-tasks-484548"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_lv_render_task_evaluate_48458e(void *d,void *l){return 0;}
void audio_uart_lv_draw_dispatch_request_48462e(void){}
'''

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf, shim = Path(directory) / "test.elf", Path(directory) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_refresh_tasks_484548",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, displays, layer_mask, eval_mask, callback_on):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            display = (0x20010000, 0x20011000)
            layer = (0x20012000, 0x20013000)
            node, callback = 0x20014000, 0x20015000
            c.mem_write(0x2006f54c, (0).to_bytes(4,"little") +
                        (display[0] if displays else 0).to_bytes(4,"little"))
            c.mem_write(0x2006f684, (node if callback_on else 0).to_bytes(4,"little"))
            n = bytearray(0x20)
            n[0x14:0x18] = (callback | 1).to_bytes(4,"little")
            c.mem_write(node, bytes(n))
            c.mem_write(callback, b"\x70\x47")
            for i in range(2):
                d = bytearray(0x300)
                d[4:8] = (display[i+1] if i+1 < displays else 0).to_bytes(4,"little")
                d[0x2ac:0x2b0] = (layer[i] if i < displays and layer_mask & (1<<i) else 0).to_bytes(4,"little")
                c.mem_write(display[i], bytes(d))
                c.mem_write(layer[i], bytes(0x60))
            cuts = {((syms["audio_uart_lv_render_task_evaluate_48458e"] & ~1)
                     if compiled else 0x48458e): "evaluate",
                    ((syms["audio_uart_lv_draw_dispatch_request_48462e"] & ~1)
                     if compiled else 0x48462e): "dispatch"}
            trace = []
            def hook(cpu, address, size, unused):
                op = "idle" if address == callback else cuts.get(address)
                if op is None: return
                if op == "evaluate":
                    d, l = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                    trace.append((op, d, l))
                    result = 1 if (eval_mask & (1 << layer.index(l))) else 0
                elif op == "idle": trace.append((op, cpu.reg_read(A.UC_ARM_REG_R0))); result=0
                else: trace.append((op,)); result=0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_lv_refresh_tasks_484548"] if compiled else 0x484548
            c.emu_start(entry | 1, 0x600000, count=20000)
            return trace, bytes(c.mem_read(0x2006f54c,8)), bytes(c.mem_read(0x2006f684,4)), \
                [bytes(c.mem_read(x,0x300)) for x in display]
        suite = [(displays, mask, eval_mask, callback_on)
                 for displays in (0,1,2) for mask in (0,1,2,3)
                 for eval_mask in (0,1,2,3) for callback_on in (0,1)
                 if mask & ~((1<<displays)-1) == 0]
        for case in suite:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native[0], source[0], native[1:]==source[1:]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_REFRESH_TASKS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x44fa22..0x44fa3d", "0x484528..0x484547", "0x484548..0x48458d"],
               "cases": len(suite), "controlled_lower_providers": 2,
               "limits": ["Task evaluation and draw dispatch are controlled; live provider effects remain open.",
                          "Display list, task walk, idle callbacks and persistent work flag are compared."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
