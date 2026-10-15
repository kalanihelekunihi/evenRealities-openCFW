#!/usr/bin/env python3
"""Native/C comparison for the Apollo display ID membership predicate."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_refresh_enabled_4434d0.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-refresh"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    assert int.from_bytes(blob[0x4437d4-0x438000:0x4437d8-0x438000], "little") == 0x200744d8
    assert int.from_bytes(blob[0x443768-0x438000:0x44376c-0x438000], "little") == 0x200744e0
    with tempfile.TemporaryDirectory() as td:
        shim = Path(td) / "shim.c"
        shim.write_text("unsigned audio_uart_display_active; unsigned audio_uart_display_background;\n")
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_refresh_enabled_4434d0", str(SRC), str(shim),
                        "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in
                subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        count = 0
        for active, background, requested in itertools.product((0, 1, 2, 0xffffffff), repeat=3):
            results = []
            for compiled in (False, True):
                u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                u.mem_map(0x400000, 0x400000)
                u.mem_write(0x438000, blob)
                u.mem_map(0x100000, 0x100000)
                for addr, data in segments:
                    u.mem_write(addr, data)
                u.mem_map(0x20000000, 0x100000)
                a = syms["audio_uart_display_active"] if compiled else 0x200744d8
                b = syms["audio_uart_display_background"] if compiled else 0x200744e0
                u.mem_write(a, active.to_bytes(4, "little"))
                u.mem_write(b, background.to_bytes(4, "little"))
                u.reg_write(A.UC_ARM_REG_R0, requested)
                u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
                u.reg_write(A.UC_ARM_REG_LR, 0x600001)
                entry = syms["audio_quicklist_refresh_enabled_4434d0"] if compiled else 0x4434d0
                u.emu_start(entry | 1, 0x600000, count=100)
                results.append(u.reg_read(A.UC_ARM_REG_R0))
            if results[0] != results[1]:
                raise AssertionError((active, background, requested, results))
            count += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_ENABLED_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4434d0..0x4434e7", "cases": count,
               "limits": ["Final RAM placement and runtime producers remain open."]}
    (OUT / "enabled-oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], count)


if __name__ == "__main__":
    main()
