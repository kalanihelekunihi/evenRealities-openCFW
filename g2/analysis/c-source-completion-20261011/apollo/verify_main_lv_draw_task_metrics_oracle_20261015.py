#!/usr/bin/env python3
"""Compare 43 Apollo draw-task style accessors against stock Main."""
import hashlib, json, re, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_metrics.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-task-metrics"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    specs = [(kind, int(address, 16), int(property_, 16)) for kind, address, property_ in
             re.findall(r"^(RAW|BYTE|BOOL)\(([0-9a-f]{6}), 0x([0-9a-f]+)u\)$",
                        SOURCE.read_text(), re.M)]
    if len(specs) != 43 or len({address for _, address, _ in specs}) != 43:
        raise RuntimeError("style accessor inventory changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        elf, shim = directory / "metrics.elf", directory / "shim.c"
        shim.write_text("unsigned audio_uart_lv_style_property_44bdea(void*a,unsigned b,unsigned c){return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_metric_4522e8",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, address, value, selector):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for segment_address, data in segments: c.mem_write(segment_address, data)
            c.mem_map(0x20000000, 0x400000)
            target = (syms["audio_uart_lv_style_property_44bdea"] if compiled else 0x44bdea) & ~1
            trace = []
            def hook(c, current, size, _):
                if current != target: return
                trace.append(tuple(c.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, 0x20011000)
            c.reg_write(A.UC_ARM_REG_R1, selector)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms[f"audio_uart_lv_draw_metric_{address:06x}"] if compiled else address
            c.emu_start(start | 1, 0x600000, count=1000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        values = (0, 1, 0x100, 0x12345678, 0xffffffff)
        for kind, address, property_ in specs:
            for value in values:
                selector = (address ^ value) & 0x3f
                native, source = run(False, address, value, selector), run(True, address, value, selector)
                if native != source or native[1] != [(0x20011000, selector, property_)]:
                    raise AssertionError((kind, hex(address), hex(value), native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_METRICS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x4522e8..0x452615", "accessors": len(specs),
               "cases": len(specs) * len(values),
               "limits": ["Style property return is controlled; full builder and live theme state remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(specs), len(specs) * len(values), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
