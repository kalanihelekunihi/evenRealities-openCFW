#!/usr/bin/env python3
"""Compare LVGL draw-label submission and local text duplication with native."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_label_489fe0.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-label-489fe0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = {
    "task_alloc": (0x4843ee, "audio_uart_lv_render_task_alloc_4843ee"),
    "malloc": (0x44f718, "audio_uart_lv_malloc"),
    "copy": (0x454738, "audio_uart_lv_grid_copy_454738"),
    "queue": (0x484476, "audio_uart_lv_render_task_queue_484476"),
    "length": (0x454768, "audio_uart_lv_string_length_454768"),
    "log": (0x44d25c, "audio_uart_lvgl_log"),
}
SHIM = "#include <stdint.h>\n" + "\n".join(
    f"__attribute__((noinline)) uint32_t {name}(void*a,void*b,void*c,void*d)"
    "{(void)a;(void)b;(void)c;(void)d;return 0;}"
    for key, (_, name) in CALLS.items() if key != "log") + \
    "\n__attribute__((noinline)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){(void)a;(void)b;(void)c;(void)d;(void)e;}\n"


def put(cpu, address, value):
    cpu.mem_write(address, (value & 0xffffffff).to_bytes(4, "little"))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != PAYLOAD_SHA:
        raise RuntimeError("Apollo payload changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_label_489fe0",
                        str(SRC), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, opacity, text_kind, font_present, local):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x400000)
            layer, descriptor, area, text, task, copy, duplicate = (
                0x20011000, 0x20012000, 0x20013000, 0x20014000,
                0x20017000, 0x20018000, 0x20019000)
            cpu.mem_write(layer, bytes(0x100))
            cpu.mem_write(descriptor, bytes(0x100))
            cpu.mem_write(area, bytes(0x20))
            cpu.mem_write(task, bytes(0x100))
            cpu.mem_write(copy, bytes(0x100))
            cpu.mem_write(duplicate, bytes(0x100))
            cpu.mem_write(text, b"" if text_kind == 1 else b"hello\0")
            for i, value in enumerate((1, 2, 3, 4)):
                put(cpu, area + i * 4, value)
            put(cpu, descriptor + 0x1c, 0 if text_kind == 0 else text)
            put(cpu, descriptor + 0x20, 0x20015000 if font_present else 0)
            put(cpu, descriptor + 0x4c, 5)
            cpu.mem_write(descriptor + 0x50, bytes([opacity]))
            cpu.mem_write(descriptor + 0x54, bytes([1 if local else 0]))
            targets = {(syms[name] if compiled else addr) & ~1: key
                       for key, (addr, name) in CALLS.items()}
            trace = []
            malloc_count = 0

            def string(cpu, address):
                return bytes(cpu.mem_read(address, 256)).split(b"\0", 1)[0].decode("ascii")

            def hook(cpu, address, size, _):
                nonlocal malloc_count
                key = targets.get(address)
                if key is None:
                    return
                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                result = 0
                if key == "task_alloc":
                    trace.append((key, r0, r1))
                    result = task
                elif key == "malloc":
                    trace.append((key, r0))
                    result = (copy, duplicate)[malloc_count]
                    malloc_count += 1
                elif key == "copy":
                    trace.append((key, r2))
                    cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
                elif key == "queue":
                    trace.append((key, r0, r1))
                elif key == "length":
                    result = len(string(cpu, r0).encode())
                elif key == "log":
                    trace.append((key, r0, r2, string(cpu, cpu.reg_read(A.UC_ARM_REG_R1)),
                                  string(cpu, cpu.reg_read(A.UC_ARM_REG_R3))))
                cpu.reg_write(A.UC_ARM_REG_R0, result)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, layer)
            cpu.reg_write(A.UC_ARM_REG_R1, descriptor)
            cpu.reg_write(A.UC_ARM_REG_R2, area)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_lv_draw_label_489fe0"] if compiled else 0x489fe0
            cpu.emu_start(entry | 1, 0x600000, count=50000)
            return (trace, bytes(cpu.mem_read(task, 0x60)),
                    bytes(cpu.mem_read(copy, 0x64)),
                    bytes(cpu.mem_read(duplicate, 8)))

        cases = list(itertools.product((0, 2, 3, 255), (0, 1, 2),
                                       (False, True), (False, True)))
        for case in cases:
            stock, source = run(False, *case), run(True, *case)
            if stock != source:
                raise AssertionError((case, stock, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_LABEL_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": digest,
               "upstream": "third-party/upstream/lvgl/src/draw/lv_draw_label.c",
               "native_spans": ["0x489fe0..0x48a0bd", "0x4547f2"],
               "cases": len(cases),
               "limits": ["Task allocation, copies and queue finalization are controlled.",
                          "Allocation failure and hardware rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()
