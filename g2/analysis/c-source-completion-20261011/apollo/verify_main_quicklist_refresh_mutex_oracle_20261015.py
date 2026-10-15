#!/usr/bin/env python3
"""Compare QuickList mutex lock/unlock C with native paths and controlled CMSIS calls."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_refresh_mutex_4ffac8.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-refresh"
NATIVE = {"acquire": 0x4497b6, "release": 0x44981c, "flags": 0x43d0ce,
          "extended": 0x43d574, "compact": 0x43ce9e}
COMPILED = {"acquire": "audio_file_mutex_acquire", "release": "audio_file_mutex_release",
            "flags": "audio_log_flags", "extended": "audio_log_extended",
            "compact": "compressed_log_output"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    shim = '''#include <stdint.h>
void *audio_quicklist_storage_mutex;
int32_t audio_file_mutex_acquire(void*a,uint32_t b){return 0;}
int32_t audio_file_mutex_release(void*a){return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){return 0;}
'''
    with tempfile.TemporaryDirectory() as td:
        sh = Path(td) / "shim.c"
        sh.write_text(shim)
        elf = Path(td) / "test.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_quicklist_refresh_lock_4ffac8", str(SRC), str(sh),
                        "-o", str(elf)], check=True)
        symbols = {p[2]: int(p[0], 16) for line in
                   subprocess.check_output(["arm-none-eabi-nm", str(elf)], text=True).splitlines()
                   if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]

        def run(compiled, which, mutex, acquired, flags):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000)
            u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments:
                u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x100000)
            cell = symbols["audio_quicklist_storage_mutex"] if compiled else 0x200748f0
            u.mem_write(cell, mutex.to_bytes(4, "little"))
            cuts = ({(symbols[name] & ~1): key for key, name in COMPILED.items()}
                    if compiled else {addr: key for key, addr in NATIVE.items()})
            trace = []

            def hook(uc, address, size, unused):
                key = cuts.get(address)
                if key is None:
                    return
                if key == "acquire":
                    trace.append((key, uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1)))
                    uc.reg_write(A.UC_ARM_REG_R0, acquired)
                elif key == "release":
                    trace.append((key, uc.reg_read(A.UC_ARM_REG_R0)))
                elif key == "flags":
                    uc.reg_write(A.UC_ARM_REG_R0, flags)
                else:
                    trace.append((key, uc.reg_read(A.UC_ARM_REG_R0)))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            name = "audio_quicklist_refresh_" + which + "_" + ("4ffac8" if which == "lock" else "4ffb26")
            entry = symbols[name] if compiled else (0x4ffac8 if which == "lock" else 0x4ffb26)
            u.emu_start(entry | 1, 0x600000, count=1000)
            result = u.reg_read(A.UC_ARM_REG_R0) if which == "lock" else None
            return result, trace

        cases = []
        for which in ("lock", "unlock"):
            for mutex in (0, 0x20071000):
                for acquired in (0, 1):
                    for flags in (0, 2, 4):
                        old = run(False, which, mutex, acquired, flags)
                        new = run(True, which, mutex, acquired, flags)
                        if old != new:
                            raise AssertionError((which, mutex, acquired, flags, old, new))
                        cases.append((which, mutex, acquired, flags))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_MUTEX_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_spans": ["0x4ffac8..0x4ffb25", "0x4ffb26..0x4ffb37"],
               "cases": len(cases), "limits": ["CMSIS calls controlled at their native interfaces.",
               "Final mutex placement and hardware behavior remain open."]}
    (OUT / "mutex-oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()
