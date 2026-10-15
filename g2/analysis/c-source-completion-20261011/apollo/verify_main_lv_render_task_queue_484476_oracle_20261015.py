#!/usr/bin/env python3
"""Compare controlled Apollo render-task queue finalization with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_render_task_queue_484476.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-render-task-queue-484476"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = '''#include <stdint.h>
uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *p,uint32_t n){return 0;}
uint32_t audio_uart_lv_obj_event_451670(void *p,uint32_t n,void *q){return 0;}
void audio_uart_lvgl_log(uint32_t l,const char *s,uint32_t n,const char *f,... ){}
void audio_uart_lv_refresh_tasks_484548(void){}
'''
LOWER = [("flag", 0x43e0e0, "audio_uart_lv_obj_has_flag_43e0e0"),
         ("event", 0x451670, "audio_uart_lv_obj_event_451670"),
         ("log", 0x44d25c, "audio_uart_lvgl_log"),
         ("refresh", 0x484548, "audio_uart_lv_refresh_tasks_484548")]

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
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_render_task_queue_484476",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, busy, object_on, node_on, handled, flag_on):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            state, task, desc, node, obj, callback = (0x2006f684, 0x20011000,
                                                      0x20012000, 0x20013000,
                                                      0x20014000, 0x20015000)
            s = bytearray(0x30)
            s[0:4] = (node if node_on else 0).to_bytes(4, "little")
            s[0x20] = busy
            c.mem_write(state, bytes(s))
            t = bytearray([0xa5] * 0x60)
            t[0x54:0x58] = desc.to_bytes(4, "little")
            c.mem_write(task, bytes(t))
            d = bytearray(0x30)
            d[0:4] = (obj if object_on else 0).to_bytes(4, "little")
            c.mem_write(desc, bytes(d))
            n = bytearray(0x20)
            n[0x10:0x14] = (callback | 1).to_bytes(4, "little")
            c.mem_write(node, bytes(n))
            c.mem_write(callback, b"\x70\x47")
            cuts = {(syms[name] & ~1) if compiled else address: label
                    for label, address, name in LOWER}
            trace = []
            def hook(cpu, address, size, unused):
                op = "callback" if address == callback else cuts.get(address)
                if op is None: return
                r0, r1, r2, r3 = (cpu.reg_read(r) for r in (A.UC_ARM_REG_R0,
                    A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if op == "flag": trace.append((op, r0, r1)); result = flag_on
                elif op == "event": trace.append((op, r0, r1, r2, int.from_bytes(cpu.mem_read(state+0x20,1),"little"))); result = 0
                elif op == "callback":
                    trace.append((op, r0, r1))
                    if handled: cpu.mem_write(task+0x58, b"\x01")
                    result = 0
                elif op == "log": trace.append((op, r0, r1, r2, r3, int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little"))); result = 0
                else: trace.append((op,)); result = 0
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, 0x20016000)
            c.reg_write(A.UC_ARM_REG_R1, task)
            c.reg_write(A.UC_ARM_REG_R2, 0x12345678)
            c.reg_write(A.UC_ARM_REG_R3, 0x87654321)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_lv_render_task_queue_484476"] if compiled else 0x484476
            c.emu_start(entry | 1, 0x600000, count=20000)
            return (c.reg_read(A.UC_ARM_REG_R0), trace,
                    bytes(c.mem_read(state, 0x30)), bytes(c.mem_read(task, 0x60)),
                    bytes(c.mem_read(desc, 0x30)), bytes(c.mem_read(node, 0x20)))
        suite = [(busy, object_on, node_on, handled, flag_on)
                 for busy in (0,1) for object_on in (0,1) for node_on in (0,1)
                 for handled in (0,1) for flag_on in (0,1)]
        for case in suite:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[:2], source[:2],
                                      [a == b for a,b in zip(native[2:], source[2:])]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_QUEUE_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x484476..0x484527", "cases": len(suite),
               "controlled_lower_providers": len(LOWER),
               "limits": ["Four lower providers and the callback are controlled; no live display refresh or logger effects.",
                          "Both busy states, object event, callback result, and task bytes compared."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
