#!/usr/bin/env python3
"""Compare Apollo draw-task conditional color composition with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_variant_452e68.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-color-variant-452e68"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
HOOKS = {"audio_uart_lv_draw_color_chain_44c582": 0x44c582,
         "audio_uart_lv_draw_color_composite_44c54a": 0x44c54a,
         "audio_uart_lv_color_with_alpha_440fde": 0x440fde,
         "audio_uart_lv_color_blend_482ef6": 0x482ef6}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        elf, shim = directory / "variant.elf", directory / "shim.c"
        shim.write_text("unsigned audio_uart_lv_draw_color_chain_44c582(void*a,unsigned b){return 0;}\n"
                        "unsigned audio_uart_lv_draw_color_composite_44c54a(void*a,unsigned b,unsigned c){return 0;}\n"
                        "unsigned audio_uart_lv_color_with_alpha_440fde(unsigned a,unsigned b){return 0;}\n"
                        "unsigned audio_uart_lv_color_blend_482ef6(unsigned a,unsigned b){return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_color_variant_452e68",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, has_style, selector, alpha, fallback_alpha):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj, task, style = 0x20011000, 0x20013000, 0x20014000
            fallback = 0x56789abc
            task_data = bytearray(0x70)
            task_data[16:20] = (style if has_style else 0).to_bytes(4, "little")
            c.mem_write(task, bytes(task_data))
            style_data = bytearray(0x50)
            style_data[0x39:0x3d] = ((alpha << 24) | 0x123456).to_bytes(4, "little")
            c.mem_write(style, bytes(style_data))
            targets = {(syms[name] if compiled else native) & ~1: native
                       for name, native in HOOKS.items()}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if native == 0x44c582:
                    value = (alpha << 24) | 0xabcdef
                    trace.append((native, r0, r1, value))
                elif native == 0x44c54a:
                    value = (alpha << 24) | 0x778899
                    trace.append((native, r0, r1, r2, value))
                elif native == 0x440fde:
                    value = (r0 & 0x00ffffff) | ((r1 & 0xff) << 24)
                    trace.append((native, r0, r1, value))
                else:
                    value = (r0 ^ r1 ^ 0x31415926) & 0xffffffff
                    trace.append((native, r0, r1, value))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj)
            c.reg_write(A.UC_ARM_REG_R1, selector)
            c.reg_write(A.UC_ARM_REG_R2, task)
            c.reg_write(A.UC_ARM_REG_R3, fallback)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.mem_write(0x203ff000, int(fallback_alpha).to_bytes(4, "little"))
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_color_variant_452e68"] if compiled else 0x452e68
            c.emu_start(start | 1, 0x600000, count=5000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        suite = [(present, selector, alpha, fallback_alpha)
                 for present in (False, True) for selector in (0, 1, 4)
                 for alpha in (0, 1, 128, 255)
                 for fallback_alpha in (0, 1, 253, 255)]
        for index, cfg in enumerate(suite):
            native, source = run(False, *cfg), run(True, *cfg)
            if native != source: raise AssertionError((index, cfg, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_VARIANT_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x452e68..0x452ecf", "cases": len(suite),
               "controlled_providers": list(HOOKS.values()),
               "limits": ["Color chain, composition, packing and blend returns are controlled; live rendering remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
