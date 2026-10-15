#!/usr/bin/env python3
"""Native/C QuickList record ID lookup comparison."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_find_record_4f5636.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-find-record"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    assert int.from_bytes(blob[0x4f5c3c-0x438000:0x4f5c40-0x438000], "little") == 0x2012a72c
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_find_record_4f5636", str(SRC), "-o", str(elf)],
                       check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        cases = []
        for count in (0, 1, 2, 20, 40):
            requests = {0, 0x100, 0x101, 0x100+max(count-1, 0), 0x100+count,
                        0x100+count+1, 0xffffffff}
            for request in sorted(requests):
                results = []
                for compiled in (False, True):
                    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                    u.mem_map(0x400000, 0x400000)
                    u.mem_write(0x438000, blob)
                    u.mem_map(0x100000, 0x100000)
                    for addr, data in segments:
                        u.mem_write(addr, data)
                    u.mem_map(0x20000000, 0x200000)
                    base = 0x2012a72c
                    u.mem_write(base, count.to_bytes(2, "little"))
                    for index in range(count):
                        u.mem_write(base+296*index+0x114, (0x100+index).to_bytes(4, "little"))
                    u.reg_write(A.UC_ARM_REG_R0, request)
                    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
                    u.reg_write(A.UC_ARM_REG_LR, 0x600001)
                    entry = syms["audio_quicklist_find_record_4f5636"] if compiled else 0x4f5636
                    u.emu_start(entry | 1, 0x600000, count=1000)
                    results.append(u.reg_read(A.UC_ARM_REG_R0))
                if results[0] != results[1]:
                    raise AssertionError((count, request, results))
                cases.append((count, request))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_FIND_RECORD_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5636..0x4f5661", "cases": len(cases),
               "limits": ["Final RAM placement and runtime producers remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()
