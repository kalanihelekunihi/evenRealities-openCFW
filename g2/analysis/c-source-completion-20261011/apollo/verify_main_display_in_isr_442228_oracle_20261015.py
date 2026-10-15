#!/usr/bin/env python3
"""Compare Apollo IPSR query with compiled C."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_in_isr_442228.c"
OUT = G2 / "build/c-firmware/20261015/main-display-in-isr-442228"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "oracle.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_in_isr_442228",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, ipsr):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            u.reg_write(A.UC_ARM_REG_IPSR, ipsr)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_display_in_isr_442228"] if compiled else 0x442228) | 1,
                        0x600000, count=1000)
            return u.reg_read(A.UC_ARM_REG_R0)
        cases = (0, 1, 2, 3, 7, 15, 31, 32, 63, 127, 255)
        for case in cases:
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_IN_ISR_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x442228..0x442237",
               "cases": len(cases),
               "limits": ["IPSR register comparison only; real interrupt timing remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
