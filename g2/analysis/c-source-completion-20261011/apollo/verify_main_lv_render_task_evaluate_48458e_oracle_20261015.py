#!/usr/bin/env python3
"""Compare Apollo render-task evaluation with controlled stock lower providers."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_render_task_evaluate_48458e.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-render-task-evaluate-48458e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = '''#include <stdint.h>
void audio_uart_lv_render_task_free_4848e8(void *t,void *d){}
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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_render_task_evaluate_48458e",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, statuses, parent_on, backend_result):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            display, layer, parent, task1, task2, candidate, descriptor, backend, callback = (
                0x20010000,0x20011000,0x20012000,0x20013000,0x20014000,
                0x20015000,0x20016000,0x20017000,0x20018000)
            tasks = (task1, task2)
            l = bytearray(0x60)
            l[0x44:0x48] = (task1 if statuses else 0).to_bytes(4,"little")
            l[0x48:0x4c] = (parent if parent_on else 0).to_bytes(4,"little")
            l[0x50] = 1 if parent_on else 0
            c.mem_write(layer,bytes(l))
            for i,address in enumerate(tasks):
                t = bytearray(0x60)
                t[0:4] = (tasks[i+1] if i+1<len(statuses) else 0).to_bytes(4,"little")
                t[0x50:0x54] = (statuses[i] if i<len(statuses) else 0).to_bytes(4,"little")
                c.mem_write(address,bytes(t))
            p = bytearray(0x60);p[0x44:0x48]=candidate.to_bytes(4,"little")
            c.mem_write(parent,bytes(p))
            q = bytearray(0x60);q[4]=7;q[0x54:0x58]=descriptor.to_bytes(4,"little")
            c.mem_write(candidate,bytes(q))
            d = bytearray(0x30);d[0x1c:0x20]=layer.to_bytes(4,"little")
            c.mem_write(descriptor,bytes(d))
            b = bytearray(0x20);b[0x0c:0x10]=(callback|1).to_bytes(4,"little")
            c.mem_write(backend,bytes(b));c.mem_write(callback,b"\x70\x47")
            c.mem_write(0x2006f684,backend.to_bytes(4,"little"))
            cuts = {((syms["audio_uart_lv_render_task_free_4848e8"]&~1)
                     if compiled else 0x4848e8):"free",
                    ((syms["audio_uart_lv_draw_dispatch_request_48462e"]&~1)
                     if compiled else 0x48462e):"dispatch"}
            trace=[]
            def hook(cpu,address,size,unused):
                op="backend" if address==callback else cuts.get(address)
                if op is None:return
                if op in ("free","backend"):
                    trace.append((op,cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)))
                else:trace.append((op,))
                result=(backend_result & 0xffffffff) if op=="backend" else 0
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE,hook)
            c.reg_write(A.UC_ARM_REG_R0,display)
            c.reg_write(A.UC_ARM_REG_R1,layer)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_render_task_evaluate_48458e"] if compiled else 0x48458e
            c.emu_start(entry|1,0x600000,count=20000)
            return (c.reg_read(A.UC_ARM_REG_R0),trace,bytes(c.mem_read(layer,0x60)),
                    bytes(c.mem_read(task1,0x60)),bytes(c.mem_read(task2,0x60)),
                    bytes(c.mem_read(candidate,0x60)))
        patterns=((),(0,),(3,),(3,0),(0,3),(3,3))
        suite=[(pattern,parent,backend) for pattern in patterns for parent in (0,1)
               for backend in (-1,0,1)]
        for case in suite:
            native,source=run(False,*case),run(True,*case)
            if native!=source:
                raise AssertionError((case,native[:2],source[:2],
                                      [a==b for a,b in zip(native[2:],source[2:])]))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_EVALUATE_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,"native_span":"0x48458e..0x484621",
             "cases":len(suite),"controlled_lower_providers":2,
             "limits":["Task free, backend callback and draw dispatch are controlled; live effects remain open.",
                       "Completed-task removal, backend decisions and parent wakeup are compared."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(suite),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
