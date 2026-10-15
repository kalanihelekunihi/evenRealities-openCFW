#!/usr/bin/env python3
"""Compare Apollo LV event extent arithmetic and call order with stock."""
import hashlib, itertools, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_compass_452c66.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-compass-452c66"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ADDRESSES = (0x452450, 0x452498, 0x45246e, 0x45245a, 0x452464,
             0x452410, 0x45243a, 0x452446, 0x4522d4, 0x4522de)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    names = {address: f"audio_uart_lv_compass_part_{address:x}" for address in ADDRESSES}
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "compass.elf"
        shim.write_text("#include <stdint.h>\n" + "\n".join(
            f"int32_t {name}(void*a,uint32_t b){{(void)a;(void)b;return 0;}}"
            for name in names.values()) + "\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_compass_452c66",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        first = [(0, 3, 0, 0, 0), (10, 2, 1, -4, 5), (10, 3, 2, -4, 5),
                 (-11, 3, 2, -7, 3), (15, 0x103, -3, 4, -20),
                 (1, 3, -100, 4, 8)]
        second = [(0, 3, 0), (10, 2, 2), (10, 3, -3), (-5, 3, 10)]
        base = [(-4, -2), (0, 0), (3, -2), (5, 8)]
        cases = [a + b + c for a, b, c in itertools.product(first, second, base)]
        def run(compiled, case):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            values = dict(zip(ADDRESSES, case))
            targets = {(syms[name] if compiled else address) & ~1: address
                       for address, name in names.items()}
            trace = []
            def hook(c, address, size, _):
                native = targets.get(address)
                if native is None: return
                trace.append((native, c.reg_read(A.UC_ARM_REG_R0), c.reg_read(A.UC_ARM_REG_R1)))
                c.reg_write(A.UC_ARM_REG_R0, values[native] & 0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, 0x20011000)
            c.reg_write(A.UC_ARM_REG_R1, 0x1234abcd)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_compass_452c66"] if compiled else 0x452c66
            c.emu_start(start | 1, 0x600000, count=10000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_COMPASS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x452c66..0x452d41", "cases": len(cases),
               "controlled_providers": [f"0x{address:x}" for address in ADDRESSES],
               "limits": ["Metric providers are controlled; actual font/layout values and device rendering remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
