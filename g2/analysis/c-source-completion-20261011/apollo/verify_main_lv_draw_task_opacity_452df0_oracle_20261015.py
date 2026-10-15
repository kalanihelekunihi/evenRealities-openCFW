#!/usr/bin/env python3
"""Controlled stock comparison of Apollo draw-task opacity helpers."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_opacity_452df0.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-opacity-452df0"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        elf, shim = directory / "opacity.elf", directory / "shim.c"
        shim.write_text("unsigned audio_uart_lv_style_property_44bdea(void*a,unsigned b,unsigned c){return 0;}\n"
                        "unsigned audio_uart_lv_effective_opacity_44c47a(void*a,unsigned b){return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_task_opacity_452df0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, selector, style_present, style_alpha, object_alpha, effective):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj, task, style = 0x20011000, 0x20013000, 0x20014000
            c.mem_write(obj, bytes([0x43]) * 0x80)
            t = bytearray([0xa5] * 0x70)
            t[16:20] = (style if style_present else 0).to_bytes(4, "little")
            c.mem_write(task, bytes(t))
            c.mem_write(style, bytes([0x19]) * 0x38 + bytes([style_alpha]) + bytes([0x29]) * 7)
            targets = {(syms[name] if compiled else native) & ~1: native for name, native in (
                ("audio_uart_lv_style_property_44bdea", 0x44bdea),
                ("audio_uart_lv_effective_opacity_44c47a", 0x44c47a))}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                args = tuple(c.reg_read(r) for r in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1))
                trace.append((native, args, c.reg_read(A.UC_ARM_REG_R2) if native == 0x44bdea else None))
                c.reg_write(A.UC_ARM_REG_R0, object_alpha if native == 0x44bdea else effective)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj)
            c.reg_write(A.UC_ARM_REG_R1, selector)
            c.reg_write(A.UC_ARM_REG_R2, task)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_task_opacity_452df0"] if compiled else 0x452df0
            c.emu_start(start | 1, 0x600000, count=5000)
            return c.reg_read(A.UC_ARM_REG_R0), trace, bytes(c.mem_read(task, 0x70))
        suite = [(selector, present, alpha, obj_alpha, effective)
                 for selector in (0, 1, 4) for present in (False, True)
                 for alpha, obj_alpha, effective in ((0, 0, 0), (1, 2, 3),
                                                     (128, 255, 77), (253, 3, 255),
                                                     (255, 255, 128))]
        for index, cfg in enumerate(suite):
            native, source = run(False, *cfg), run(True, *cfg)
            if native != source: raise AssertionError((index, cfg, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_OPACITY_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x4525fe..0x452609", "0x452df0..0x452e21"],
               "cases": len(suite), "controlled_providers": ["0x44bdea", "0x44c47a"],
               "limits": ["Provider returns are controlled; full draw-task builder and live style state remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
