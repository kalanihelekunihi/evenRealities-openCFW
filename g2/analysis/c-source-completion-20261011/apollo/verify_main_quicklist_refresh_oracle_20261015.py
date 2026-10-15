#!/usr/bin/env python3
"""Controlled native/compiled comparison for Apollo QuickList UI refresh."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SRC = G2 / "components/audio/uart_thread_source_candidate/quicklist_refresh_4f5e84.c"
IMAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-refresh"
NATIVE = {"lock": 0x4ffac8, "ready": 0x4f5e18, "unlock": 0x4ffb26,
          "flags": 0x43d0ce, "wake": 0x443484, "enabled": 0x4434d0,
          "role": 0x45a568, "send": 0x464bb2, "pending": 0x4f5596}
COMPILED = {"lock": "audio_quicklist_refresh_lock_4ffac8",
            "ready": "audio_quicklist_refresh_ready_4f5e18",
            "unlock": "audio_quicklist_refresh_unlock_4ffb26", "flags": "audio_log_flags",
            "wake": "audio_log_wake_allowed", "enabled": "audio_quicklist_refresh_enabled_4434d0",
            "role": "audio_uart_device_role_get", "send": "audio_uart_master_display_refresh",
            "pending": "audio_quicklist_refresh_pending_4f5596"}


def check_one(blob, segments, symbols, scenario, compiled):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    u.mem_map(0x400000, 0x400000)
    u.mem_write(0x438000, blob)
    u.mem_map(0x100000, 0x100000)
    for addr, data in segments:
        u.mem_write(addr, data)
    u.mem_map(0x20000000, 0x200000)
    u.mem_write(0x20075041, b"\x23")
    u.mem_write(0x20074e28, (0x4567).to_bytes(4, "little"))
    u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
    u.reg_write(A.UC_ARM_REG_LR, 0x600001)
    addresses = ({(symbols[name] & ~1): key for key, name in COMPILED.items()}
                 if compiled else {v: k for k, v in NATIVE.items()})
    trace = []

    def hook(uc, address, size, unused):
        if address not in addresses:
            return
        key = addresses[address]
        if key == "send":
            packet = bytes(uc.mem_read(uc.reg_read(A.UC_ARM_REG_R1), 8))
            trace.append((key, uc.reg_read(A.UC_ARM_REG_R0),
                          uc.reg_read(A.UC_ARM_REG_R2), uc.reg_read(A.UC_ARM_REG_R3),
                          packet[:6].hex()))
        else:
            trace.append((key, uc.reg_read(A.UC_ARM_REG_R0)) if key == "enabled" else (key,))
        uc.reg_write(A.UC_ARM_REG_R0, scenario.get(key, 0))
        uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))

    u.hook_add(UC_HOOK_CODE, hook)
    entry = symbols["audio_quicklist_refresh_4f5e84"] if compiled else 0x4f5e84
    u.emu_start(entry | 1, 0x600000, count=10000)
    state = bytes(u.mem_read(0x2012d574, 8))
    return u.reg_read(A.UC_ARM_REG_R0), trace, state


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = IMAGE.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("official Apollo image changed")
    shim = "\n".join(("unsigned %s(void){return 0;}" % name)
                      for name in COMPILED.values() if name not in
                      {"audio_quicklist_refresh_unlock_4ffb26", "audio_quicklist_refresh_pending_4f5596",
                       "audio_uart_master_display_refresh"})
    shim += "\nvoid audio_quicklist_refresh_unlock_4ffb26(void){}\n"
    shim += "void audio_quicklist_refresh_pending_4f5596(void){}\n"
    shim += "void audio_uart_master_display_refresh(unsigned a,const void*b,unsigned short c,unsigned d){}\n"
    shim += "void audio_log_extended(unsigned char a,const char*b,const char*c,const char*d,unsigned e,const char*f,...){}\n"
    shim += "unsigned compressed_log_output(unsigned a,const char*b,const char*c,...){return 0;}\n"
    with tempfile.TemporaryDirectory() as td:
        shimpath = Path(td) / "shim.c"
        shimpath.write_text(shim)
        elfpath = Path(td) / "refresh.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_quicklist_refresh_4f5e84",
                        str(SRC), str(shimpath), "-o", str(elfpath)], check=True)
        symbols = {row[2]: int(row[0], 16) for line in
                   subprocess.check_output(["arm-none-eabi-nm", str(elfpath)], text=True).splitlines()
                   if len(row := line.split()) == 3}
        with elfpath.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        cases = []
        for lock, ready, wake, enabled, role in itertools.product((0, 1), repeat=5):
            scenario = dict(lock=lock, ready=ready, wake=wake, enabled=enabled, role=role)
            old = check_one(blob, segments, symbols, scenario, False)
            new = check_one(blob, segments, symbols, scenario, True)
            if old != new:
                raise AssertionError((scenario, old, new))
            cases.append(scenario)
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_ORACLE",
               "source": str(SRC.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SRC.read_bytes()).hexdigest(),
               "official_payload_sha256": hashlib.sha256(blob).hexdigest(),
               "native_span": "0x4f5e84..0x4f5faf", "cases": len(cases),
               "controlled": ["lock", "ready", "wake", "enabled", "role", "log flags zero"],
               "limits": ["Lower calls are controlled at authentic interfaces.",
                          "Logging-enabled paths and final RAM/ROM placement remain unqualified.",
                          "This does not establish image completeness or hardware behavior."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))


if __name__ == "__main__":
    main()
