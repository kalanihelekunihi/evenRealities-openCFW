#!/usr/bin/env python3
"""Compare stock 0x4205F4 with the readable wrapper candidate.

Only the stock clear helper, MSPI transfer, and error-event helper are
intercepted. All inputs and output buffers are synthetic RAM.
"""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ENTRY = 0x4205F4
HANDLE_SLOT = 0x200270DC
HANDLE = 0x20006000
v.ENTRIES["status_transfer"] = ENTRY


class StatusMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        if source:
            self.symbols["opencfw_boot_status_transfer"] = self.symbols[
                "opencfw_bl_mspi_status_transfer"]
        self.fixture = {}
        self.providers = []

    def code(self, uc, pc, size, user):
        if pc == 0x415FF4:
            dst, size = self.args()[:2]
            uc.mem_write(dst, b"\0" * size)
            self.ret(0)
            return
        if pc == 0x4262E0:
            handle, command, timeout = self.args()[:3]
            raw = bytes(uc.mem_read(command, 24))
            length, scrambling, dcx, direction, send_addr, address = \
                struct.unpack_from("<IBBBB I", raw)
            send_instr = raw[12]
            instruction = struct.unpack_from("<H", raw, 14)[0]
            turnaround, write_latency, continuation = raw[16:19]
            destination = struct.unpack_from("<I", raw, 20)[0]
            rx = bytes.fromhex(self.fixture.get("rx_hex", ""))
            if rx and length:
                uc.mem_write(destination, (rx * ((min(length, len(rx) * 64) + len(rx) - 1) // len(rx)))[:min(length, len(rx) * 64)])
            status = self.fixture.get("transfer_status", 0)
            self.providers.append(["transfer", handle, timeout, {
                "length": length, "scrambling": scrambling, "dcx": dcx,
                "direction": direction, "send_address": send_addr,
                "address": address, "send_instruction": send_instr,
                "instruction": instruction, "turnaround": turnaround,
                "write_latency": write_latency,
                "continuation": continuation, "destination": destination,
                "raw": raw.hex()}, status])
            self.ret(status)
            return
        if pc == 0x415FAE:
            module, instruction, address, length = self.args()
            sp = uc.reg_read(v.a.UC_ARM_REG_SP)
            status = self.u(sp)
            self.providers.append(["error", module, instruction, address,
                                   length, status])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def invoke(self, params, fixture):
        self.fixture = fixture
        self.providers = []
        self.w(HANDLE_SLOT, fixture.get("handle", HANDLE))
        destination = params[3]
        if destination:
            self.cpu.mem_write(destination, b"\xa5" * 64)
        # AAPCS fifth argument is at entry SP; Machine.run supplies registers
        # only, so seed the caller stack slot before starting either body.
        self.w(v.SP, params[4])
        result = self.run("status_transfer", params[:4])
        result["providers"] = self.providers
        result["rx"] = (bytes(self.cpu.mem_read(destination,
            min(params[4], 64))).hex() if destination and params[4] else "")
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    cases_to_run = [
        ([5, 0, 0, 0x20008000, 1], {"rx_hex": "01"}),
        ([0x9f, 0, 0, 0x20008000, 3], {"rx_hex": "102030"}),
        ([0x6c, 0x123456, 1, 0x20008004, 16], {"rx_hex": "1122334455667788"}),
        ([0x12345, 0x01fffff0, 0x101, 0x20008008, 0x1000], {"rx_hex": "cafe"}),
        ([0x12345, 0x234567, 0x101, 0x2000800a, 1], {"transfer_status": 7}),
        ([5, 0x123456, 0x100, 0x2000800c, 4], {"rx_hex": "aabbccdd"}),
        ([5, 0, 0, 0x20008010, 1], {"transfer_status": 0x80000007}),
        ([5, 0x01ffffff, 1, 0x20008014, 1], {}),
        ([5, 0x02000000, 0, 0x20008018, 1], {}),
        ([5, 0, 0, 0x2000801c, 0x20000], {}),
        ([5, 0, 0, 0, 1], {}),
        ([5, 0, 0, 0x20008020, 0], {}),
        ([5, 0, 0, 0x20008024, 1], {"handle": 0}),
    ]
    for params, fixture in cases_to_run:
        machines = [StatusMachine(), StatusMachine(True, segments, symbols)]
        try:
            results = [m.invoke(params, fixture) for m in machines]
        except Exception:
            print("execution failure", params, fixture,
                  [(m.source, hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)))
                   for m in machines])
            raise
        keys = ["return", "providers", "rx"]
        left = {k: results[0][k] for k in keys}
        right = {k: results[1][k] for k in keys}
        assert left == right, (params, fixture, left, right)
        trace.update(machines[0].trace)
        cases.append({"arguments": params, "fixture": fixture,
                      "observed": left})
    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    out = {
        "status": "PASS", "cases": len(cases),
        "original_sha256": v.SHA, "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in HERE.iterdir()
                           if p.suffix in [".c", ".h", ".ld", ".py"]},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace, "comparisons": cases,
        "limits": [
            "The exact stock 0x415FF4 clear body is stubbed as byte-zeroing; source uses an aggregate initialized command.",
            "MSPI transfer is an injected provider which records command bytes and can return a selected status or synthetic RX bytes.",
            "The error helper 0x415FAE is intercepted; no logging/runtime internals or hardware transfer are claimed.",
            "No length, alignment, overflow, or end-address guard is added beyond checks in this wrapper.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("status", "cases", "distinct_original_instruction_bytes")},
                     indent=2))


if __name__ == "__main__":
    main()
