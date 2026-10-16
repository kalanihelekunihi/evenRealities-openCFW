#!/usr/bin/env python3
"""Controlled native/C QuickList storage-to-UI dispatcher comparison."""
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
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_refresh_ready_4f5e18.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-refresh"
NATIVE = {"one": 0x4f5718, "two": 0x4f5a1c, "two_detail": 0x4f5838,
          "three": 0x4f5c4c}
COMPILED = {"one": "audio_quicklist_mode_one_4f5718",
            "two": "audio_quicklist_mode_two_4f5a1c",
            "two_detail": "audio_quicklist_mode_two_detail_4f5838",
            "three": "audio_quicklist_mode_three_4f5c4c"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    assert int.from_bytes(blob[0x4f676c-0x438000:0x4f6770-0x438000], "little") == 0x20102c3e
    assert int.from_bytes(blob[0x4f6760-0x438000:0x4f6764-0x438000], "little") == 0x2012a72c
    shim = "\n".join("unsigned %s(unsigned a){return 0;}" % x for x in COMPILED.values())
    with tempfile.TemporaryDirectory() as td:
        sh = Path(td) / "shim.c"
        sh.write_text(shim + "\n")
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_refresh_ready_4f5e18", str(SRC), str(sh),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, mode, detail, result):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x200000)
            u.mem_write(0x20102c3e, bytes([mode]))
            u.mem_write(0x2012d579, bytes([detail]))
            u.mem_write(0x2012d578, b"\xa5")
            cuts = ({(syms[name] & ~1): key for key, name in COMPILED.items()}
                    if compiled else {addr: key for key, addr in NATIVE.items()})
            trace = []

            def hook(uc, address, size, unused):
                key = cuts.get(address)
                if key is None:
                    return
                trace.append((key, uc.reg_read(A.UC_ARM_REG_R0)))
                uc.reg_write(A.UC_ARM_REG_R0, result)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_quicklist_refresh_ready_4f5e18"] if compiled else 0x4f5e18
            u.emu_start(entry | 1, 0x600000, count=1000)
            return u.reg_read(A.UC_ARM_REG_R0), trace, bytes(u.mem_read(0x2012d578, 1))

        count = 0
        for mode, detail, result in itertools.product((0, 1, 2, 3, 4, 255),
                                                      (0, 1, 2, 3, 255), (0, 1, 0x1234)):
            old, new = run(False, mode, detail, result), run(True, mode, detail, result)
            if old != new:
                raise AssertionError((mode, detail, result, old, new))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_READY_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5e18..0x4f5e7b", "cases": count,
               "limits": ["Four lower QuickList mode handlers remain separate providers.",
                          "Final RAM placement and runtime producers remain open."]}
    (OUT / "ready-oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
