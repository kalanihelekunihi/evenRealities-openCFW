#!/usr/bin/env python3
"""Compare stock RGB bits for 0x482dd8 and draw-task helper 0x452e22."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_rgb_mix_452e22.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-rgb-mix-452e22"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
HOOKS = {"audio_uart_lv_draw_color_chain_44c582": 0x44c582,
         "audio_uart_lv_draw_color_composite_44c54a": 0x44c54a}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        elf, shim = directory / "rgb.elf", directory / "shim.c"
        shim.write_text("unsigned audio_uart_lv_draw_color_chain_44c582(void*a,unsigned b){return 0;}\n"
                        "unsigned audio_uart_lv_draw_color_composite_44c54a(void*a,unsigned b,unsigned c){return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_rgb_mix_452e22",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, helper, first, second, alpha, has_style=False, selector=0):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj, task, style = 0x20011000, 0x20013000, 0x20014000
            task_data = bytearray(0x70)
            task_data[16:20] = (style if has_style else 0).to_bytes(4, "little")
            c.mem_write(task, bytes(task_data))
            style_data = bytearray(0x50)
            style_data[0x39:0x3d] = ((alpha << 24) | (first & 0xffffff)).to_bytes(4, "little")
            c.mem_write(style, bytes(style_data))
            targets = {(syms[name] if compiled else native) & ~1: native
                       for name, native in HOOKS.items()}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                value = (alpha << 24) | (first & 0xffffff)
                trace.append((native, r0, r1, r2 if native == 0x44c54a else None, value))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            if helper:
                c.reg_write(A.UC_ARM_REG_R0, obj)
                c.reg_write(A.UC_ARM_REG_R1, selector)
                c.reg_write(A.UC_ARM_REG_R2, task)
                c.reg_write(A.UC_ARM_REG_R3, second)
                name, address = "audio_uart_lv_draw_rgb_mix_452e22", 0x452e22
            else:
                c.reg_write(A.UC_ARM_REG_R0, first)
                c.reg_write(A.UC_ARM_REG_R1, second)
                c.reg_write(A.UC_ARM_REG_R2, alpha)
                name, address = "audio_uart_lv_color_rgb_mix_482dd8", 0x482dd8
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            c.emu_start((syms[name] if compiled else address) | 1, 0x600000, count=5000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        alphas = (0, 1, 2, 3, 64, 128, 252, 253, 254, 255)
        colors = ((0x123456, 0xaabbcc), (0xffffff, 0x000000),
                  (0x00ff80, 0x8000ff))
        suite = [(False, first, second, alpha, False, 0)
                 for alpha in alphas for first, second in colors]
        suite += [(True, first, second, alpha, present, selector)
                  for present in (False, True) for selector in (0, 1, 4)
                  for alpha in alphas for first, second in colors]
        upper_mismatch = 0
        for index, cfg in enumerate(suite):
            native, source = run(False, *cfg), run(True, *cfg)
            if (native[0] & 0xffffff, native[1]) != (source[0] & 0xffffff, source[1]):
                raise AssertionError((index, cfg, native, source))
            upper_mismatch += (native[0] >> 24) != (source[0] >> 24)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_RGB_MIX_LOW24_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x482dd8..0x482e4b", "0x452e22..0x452e67"],
               "cases": len(suite), "compared_return_mask": "0x00ffffff",
               "upper_byte_mismatch_cases": upper_mismatch,
               "limits": ["Stock mixer leaves top return byte unwritten; only RGB bytes and controlled lower call traces are compared. Other callers' use of the top byte remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), upper_mismatch, sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
