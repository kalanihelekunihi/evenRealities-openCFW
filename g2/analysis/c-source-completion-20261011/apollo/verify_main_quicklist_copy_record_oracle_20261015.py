#!/usr/bin/env python3
"""Compare compiled QuickList record conversion with native Apollo bytes."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_copy_record_4f55e0.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-mode-one"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    shim = "void *audio_queue_copy_bytes(void*a,const void*b,unsigned c){return a;}\n"
    with tempfile.TemporaryDirectory() as td:
        sh = Path(td) / "shim.c"
        sh.write_text(shim)
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_copy_record_4f55e0",
                        str(SRC), str(sh), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, source_present, destination_present, length, seed):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x100000)
            src = 0x20010000 if source_present else 0
            dst = 0x20020000 if destination_present else 0
            pattern = bytes((i*17+seed) & 255 for i in range(232))
            if src:
                u.mem_write(src, pattern)
                u.mem_write(src+0xe2, length.to_bytes(2, "little"))
            if dst:
                u.mem_write(dst, b"\xa5"*296)
            copy_addr = (syms["audio_queue_copy_bytes"] & ~1) if compiled else 0x439be4
            trace = []

            def hook(uc, address, size, unused):
                if address != copy_addr:
                    return
                d, s, n = (uc.reg_read(r) for r in
                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                trace.append((d, s, n))
                if n:
                    uc.mem_write(d, bytes(uc.mem_read(s, n)))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, src)
            u.reg_write(A.UC_ARM_REG_R1, dst)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_copy_record_4f55e0"] if compiled else 0x4f55e0
            u.emu_start(entry | 1, 0x600000, count=1000)
            return trace, bytes(u.mem_read(dst, 296)) if dst else None

        count = 0
        for source_present, destination_present, length, seed in itertools.product(
                (False, True), (False, True), (0, 1, 199, 200, 201, 0xffff), (0, 37)):
            old = run(False, source_present, destination_present, length, seed)
            new = run(True, source_present, destination_present, length, seed)
            if old != new:
                raise AssertionError((source_present, destination_present, length, seed,
                                      old[0], new[0], old[1] == new[1]))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_COPY_RECORD_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f55e0..0x4f5635", "cases": count,
               "limits": ["Byte-copy lower provider is controlled at native interface.",
                          "Final placement and hardware behavior remain open."]}
    (OUT / "copy-oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
