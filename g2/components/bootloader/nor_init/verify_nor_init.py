#!/usr/bin/env python3
"""Compare 0x420476/0x42059e instructions with source under synthetic HAL cuts."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location(
    "bootv", ROOT / "g2/components/bootloader/update_core/verify.py"
)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES["nor_init"] = 0x420476

HANDLED = {
    0x420254, 0x41f9d8, 0x42052a, 0x420f10, 0x4201ba,
    0x420890, 0x420c5c, 0x41fe62, 0x41fe28, 0x4176ce,
    0x415ff4, 0x4262e0, 0x415fae,
}
STOP = 0x08000000
INPUT_BYTES = bytes.fromhex("12 34 56")
HANDLE_SLOT = 0x200270dc
HANDLE = 0x20006000


class NorInitMachine(v.Machine):
    def __init__(self, *args, init_status=0, read_status=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_status = init_status
        self.read_status = read_status
        self.w(HANDLE_SLOT, HANDLE)

    def cstr(self, address):
        data = bytearray()
        while len(data) < 512:
            byte = self.cpu.mem_read(address + len(data), 1)[0]
            if byte == 0:
                return data.decode("ascii")
            data.append(byte)
        raise AssertionError(("unterminated string", hex(address)))

    def code(self, uc, pc, size, user):
        if pc not in HANDLED:
            super().code(uc, pc, size, user)
            return

        r0, r1, r2, r3 = self.args()
        if pc == 0x420254:
            self.events.append(["mspi_initialize", r0, r1, r2])
            self.ret(self.init_status)
        elif pc == 0x41f9d8:
            self.events.append(["delay_argument", r0])
            self.ret()
        elif pc == 0x42052a:
            self.events.append(["reset_enable_disable_commands"])
            self.ret()
        elif pc == 0x420f10:
            self.events.append(["configure_xip_read_mode"])
            self.ret()
        elif pc == 0x4201ba:
            self.events.append(["read_flash_status_register"])
            self.ret()
        elif pc == 0x415ff4:
            uc.mem_write(r0, b"\0" * r1)
            self.ret()
        elif pc == 0x4262e0:
            handle, command, timeout = r0, r1, r2
            raw = bytearray(uc.mem_read(command, 24))
            length = struct.unpack_from("<I", raw)[0]
            destination = struct.unpack_from("<I", raw, 20)[0]
            rx = INPUT_BYTES[:length]
            if self.read_status == 0 and rx:
                uc.mem_write(destination, rx)
            raw[20:24] = b"\0" * 4
            self.events.append([
                "mspi_blocking_transfer", handle, timeout, raw.hex(),
                rx.hex() if self.read_status == 0 else "",
            ])
            self.ret(self.read_status)
        elif pc == 0x415fae:
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            self.events.append([
                "status_transfer_error", r0, r1, r2, r3, self.u(sp),
            ])
            self.ret()
        elif pc == 0x420890:
            self.events.append(["flash_xip_setup"])
            self.ret()
        elif pc == 0x420c5c:
            self.events.append(["flash_xip_mode", r0])
            self.ret()
        elif pc == 0x41fe62:
            self.events.append(["create_flash_runtime_flags"])
            self.ret()
        elif pc == 0x41fe28:
            self.events.append(["power_flash_mspi"])
            self.ret()
        elif pc == 0x4176ce:
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            line = self.u(sp)
            fmt = self.cstr(self.u(sp + 4))
            message = [r0, self.cstr(r1), self.cstr(r2),
                       self.cstr(r3), line, fmt]
            if line in (0x284, 0x28e, 0x292):
                message.append(self.u(sp + 8))
            self.events.append(["log", *message])
            self.ret()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert v.sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    trace = {}
    cases = []

    for init_status, read_status in [
        (0, 0), (0, 5), (0, 0xffffffff), (1, 0), (7, 0), (0xffffffff, 0),
    ]:
        pair = [
            NorInitMachine(init_status=init_status, read_status=read_status),
            NorInitMachine(True, segments, symbols,
                           init_status=init_status, read_status=read_status),
        ]
        results = [m.run("nor_init", [0, 0, 0, 0]) for m in pair]
        assert results[0]["return"] == results[1]["return"], (init_status, read_status, results)
        assert results[0]["events"] == results[1]["events"], (
            init_status, read_status, results[0]["events"], results[1]["events"]
        )
        trace.update(pair[0].trace)
        cases.append({
            "init_status": init_status,
            "read_status": read_status,
            "return": results[0]["return"],
            "events": results[0]["events"],
        })

    used = {
        int(pc, 0) + offset
        for pc, raw in trace.items()
        for offset in range(len(bytes.fromhex(raw)))
    }
    sources = [p for p in HERE.iterdir()
               if p.suffix in {".c", ".h", ".ld", ".py"} or p.name == "Makefile"]
    source_hashes = {p.name: v.sha(p) for p in sources}
    reused_status = ROOT / (
        "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/"
        "nor-read-status"
    )
    source_hashes["reused/nor_read_status.c"] = v.sha(
        reused_status / "nor_read_status.c")
    source_hashes["reused/nor_read_status.h"] = v.sha(
        reused_status / "nor_read_status.h")
    report = {
        "status": "PASS",
        "cases": len(cases),
        "comparisons": cases,
        "distinct_original_trace_bytes": len(used),
        "original_trace": trace,
        "original_sha256": v.SHA,
        "elf_sha256": v.sha(args.elf),
        "source_sha256": source_hashes,
        "limits": [
            "Original 0x420476, 0x42059e, and 0x4205f4 instructions execute; MSPI initialization, delay, command operations, XIP setup, runtime flag creation, power control, and logging are synthetic exact-address providers.",
            "The lower-level blocking MSPI transfer at 0x4262e0 returns selected outcomes and supplies three synthetic JEDEC bytes; this does not exercise MSPI hardware or prove flash timing/identification on a device.",
            "Original 0x415ff4 command-buffer clearing is modeled by zeroing synthetic RAM. This tests the initializer's error/success branches for listed statuses only; it does not reconstruct the MSPI initializer at 0x420254, command helpers, reset/XIP setup, flash status-register read, or flag-group implementation.",
            "No physical hardware, flash access, flash modification, complete image, full boot, or byte-identical rebuild is claimed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("status", "cases", "distinct_original_trace_bytes")}))


if __name__ == "__main__":
    main()
