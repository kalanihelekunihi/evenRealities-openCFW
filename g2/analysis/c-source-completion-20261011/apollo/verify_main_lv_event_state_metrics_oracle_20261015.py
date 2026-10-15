#!/usr/bin/env python3
"""Compare Apollo event-state style-property wrappers with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_state_metrics.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-state-metrics"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
PROPERTIES = {0x43de4a: 0x0c, 0x43dd72: 0x6a, 0x43dd7c: 0x6b,
              0x43ddd8: 0x26, 0x43dda8: 0x1d, 0x43de6a: 0x62,
              0x43ddb4: 0x20, 0x43ddcc: 0x25, 0x43ddc0: 0x24,
              0x43de54: 0x2d}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "metrics.elf"
        shim.write_text("#include <stdint.h>\nuint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_event_state_metric_43de54",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, address, value):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for place, data in segments: c.mem_write(place, data)
            c.mem_map(0x20000000, 0x400000)
            target = (syms["audio_uart_lv_style_property_44bdea"] if compiled
                      else 0x44bdea) & ~1
            trace = []
            def hook(c, at, size, _):
                if at != target: return
                trace.append(tuple(c.reg_read(r) for r in
                                   (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2)))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, 0x20011000)
            c.reg_write(A.UC_ARM_REG_R1, 0x1234abcd)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms[f"audio_uart_lv_event_state_metric_{address:x}"] if compiled else address
            c.emu_start(start | 1, 0x600000, count=1000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        cases = [(address, value) for address in PROPERTIES
                 for value in (0, 1, 0xff, 0x100, 0x12345678, 0xffffffff)]
        for index, (address, value) in enumerate(cases):
            native, source = run(False, address, value), run(True, address, value)
            if native != source: raise AssertionError((index, address, value, native, source))
            if native[1] != [(0x20011000, 0x1234abcd, PROPERTIES[address])]:
                raise AssertionError((index, native))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_METRICS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": [f"0x{address:x}" for address in PROPERTIES],
               "selectors": {f"0x{address:x}": property for address, property in PROPERTIES.items()},
               "cases": len(cases),
               "limits": ["Style-property provider is controlled; live event-state and theme effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
