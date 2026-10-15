#!/usr/bin/env python3
"""Compare Apollo event-state area copy and style wrappers with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_event_state_small_helpers.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-event-state-small-helpers"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
METRICS = {0x43de06: 0x35, 0x43ddfc: 0x30}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "helpers.elf"
        shim.write_text("#include <stdint.h>\nuint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_event_area_copy_43dcc0",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            kind, address, value = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for place, data in segments: c.mem_write(place, data)
            c.mem_map(0x20000000, 0x400000)
            destination, source = 0x20011000, 0x20012000
            c.mem_write(destination, bytes([0xa5]) * 0x30)
            c.mem_write(source, bytes((i + value) & 0xff for i in range(0x30)))
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
            c.reg_write(A.UC_ARM_REG_R0, destination)
            c.reg_write(A.UC_ARM_REG_R1, source if kind == "copy" else 0x1234abcd)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            name = ("audio_uart_lv_event_area_copy_43dcc0" if kind == "copy"
                    else f"audio_uart_lv_event_state_metric_{address:x}")
            start = syms[name] if compiled else address
            c.emu_start(start | 1, 0x600000, count=1000)
            output = bytes(c.mem_read(destination, 0x30))
            return (output, trace) if kind == "copy" else (c.reg_read(A.UC_ARM_REG_R0), trace, output)
        cases = [("copy", 0x43dcc0, value) for value in range(10)]
        cases += [("metric", address, value) for address in METRICS
                  for value in (0, 1, 0xff, 0x100, 0x12345678, 0xffffffff)]
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
            if case[0] == "metric" and native[1] != [(0x20011000, 0x1234abcd, METRICS[case[1]])]:
                raise AssertionError((index, native))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_SMALL_HELPERS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x43dcc0..0x43dcd9", "0x43de06", "0x43ddfc"],
               "cases": len(cases),
               "limits": ["Valid nonoverlapping area pointers and controlled style provider only; live draw effects remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
