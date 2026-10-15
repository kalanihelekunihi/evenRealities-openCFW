#!/usr/bin/env python3
"""Compare Apollo LV color composition and ancestor walk with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_composition_44c54a.c"
LEAVES = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_color_helpers.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-color-composition-44c54a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
HOOKS = {"audio_uart_lv_style_property_44bdea": 0x44bdea,
         "audio_uart_lv_obj_parent_44dca2": 0x44dca2,
         "audio_uart_lv_color_blend_482ef6": 0x482ef6}
PROVIDERS = (("audio_uart_lv_draw_color_composite_44c54a", 0x44c54a),
             ("audio_uart_lv_draw_color_chain_44c582", 0x44c582))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        elf, shim = directory / "composition.elf", directory / "shim.c"
        shim.write_text("unsigned audio_uart_lv_style_property_44bdea(void*a,unsigned b,unsigned c){return 0;}\n"
                        "void* audio_uart_lv_obj_parent_44dca2(void*a){return 0;}\n"
                        "unsigned audio_uart_lv_color_blend_482ef6(unsigned a,unsigned b){return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_color_chain_44c582",
                        str(SOURCE), str(LEAVES), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, name, address, selector, base, depth, alphas):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for segment_address, data in segments: c.mem_write(segment_address, data)
            c.mem_map(0x20000000, 0x400000)
            objects = [0x20011000 + i * 0x100 for i in range(4)]
            targets = {(syms[symbol] if compiled else native) & ~1: native
                       for symbol, native in HOOKS.items()}
            trace = []
            def hook(c, current, size, _):
                native = targets.get(current)
                if native is None: return
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if native == 0x44bdea:
                    index = objects.index(r0)
                    value = (0x12345678 ^ (index * 0x01020304) ^ r1) if r2 == 0x78 else alphas[index]
                    trace.append((native, r0, r1, r2, value))
                elif native == 0x44dca2:
                    index = objects.index(r0)
                    value = objects[index + 1] if index < depth else 0
                    trace.append((native, r0, value))
                else:
                    value = ((r0 ^ r1) + 0x31415926) & 0xffffffff
                    trace.append((native, r0, r1, value))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, objects[0])
            c.reg_write(A.UC_ARM_REG_R1, selector)
            c.reg_write(A.UC_ARM_REG_R2, base)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            c.emu_start((syms[name] if compiled else address) | 1, 0x600000, count=10000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        suite = []
        for name, address in PROVIDERS:
            for selector in (0, 1, 4):
                for depth in (0, 1, 3):
                    for alphas in ((0, 0, 0, 0), (1, 128, 255, 253),
                                   (255, 0, 2, 200)):
                        suite.append((name, address, selector, 0x87654321, depth, alphas))
        for index, cfg in enumerate(suite):
            native, source = run(False, *cfg), run(True, *cfg)
            if native != source: raise AssertionError((index, cfg, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_COMPOSITION_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "leaf_source": str(LEAVES.relative_to(ROOT)), "leaf_source_sha256": sha(LEAVES),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x44c54a..0x44c5d3", "cases": len(suite),
               "controlled_providers": list(HOOKS.values()),
               "limits": ["Style, parent and blend providers are controlled; live theme and color blend implementation remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
