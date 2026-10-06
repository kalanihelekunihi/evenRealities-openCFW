#!/usr/bin/env python3
"""Compare setup path with 0x4205F4 source linked in place of its stub.

The original poll path executes 0x42074E -> stock 0x4205F4. The candidate
executes its compiled source status-transfer function. Only the lower MSPI
blocking transfer and error helper are injected; no physical hardware.
"""
import argparse
import importlib.util
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location("setup_profile",
    HERE / "verify_nor_read_setup.py")
setup_profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup_profile)
v = setup_profile.v
ENTRY = 0x4205F4
v.ENTRIES["status_direct"] = ENTRY


class LinkedSetupMachine(setup_profile.SetupMachine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        if source:
            self.symbols["opencfw_boot_status_direct"] = self.symbols[
                "opencfw_bl_mspi_status_transfer"]

    def code(self, uc, pc, size, user):
        if pc == ENTRY:
            # Let the original function execute; the candidate routes this
            # alias to a distinct source address and does not hit this hook.
            setup_profile.v.Machine.code(self, uc, pc, size, user)
            return
        if pc == 0x4262E0:
            handle, command, timeout = self.args()[:3]
            raw = bytes(uc.mem_read(command, 24))
            length = struct.unpack_from("<I", raw)[0]
            send_address = raw[7]
            address = struct.unpack_from("<I", raw, 8)[0]
            instruction = struct.unpack_from("<H", raw, 14)[0]
            destination = struct.unpack_from("<I", raw, 20)[0]
            ix = self.poll_index
            statuses = self.fixture.get("transfer_statuses", [])
            status = (statuses[ix] if ix < len(statuses)
                      else self.fixture.get("transfer_status", 0))
            rx_bytes = self.fixture.get("rx_bytes", [])
            if ix < len(rx_bytes):
                rx = bytes([rx_bytes[ix] & 0xff])
            else:
                rx = bytes.fromhex(self.fixture.get("rx_hex", ""))
            if length and rx:
                count = min(length, max(1, len(rx)))
                uc.mem_write(destination, (rx * ((count + len(rx) - 1) // len(rx)))[:count])
            canonical = raw[:20] + b"\0\0\0\0"
            self.provider_events.append(["mspi_transfer", handle, timeout,
                length, send_address, address, instruction,
                int(destination != 0), canonical.hex(), status])
            self.poll_index += 1
            self.ret(status)
            return
        if pc == 0x415FAE:
            module, instruction, address, length = self.args()
            sp = uc.reg_read(setup_profile.v.a.UC_ARM_REG_SP)
            status = self.u(sp)
            self.provider_events.append(["status_error", module,
                instruction, address, length, status])
            self.ret(0)
            return
        super().code(uc, pc, size, user)

    def invoke_direct(self, params, fixture):
        self.setup(fixture)
        self.w(setup_profile.v.SP, params[4])
        result = self.run("status_direct", params[:4])
        result["providers"] = self.provider_events
        result["rx"] = bytes(self.cpu.mem_read(params[3],
            min(params[4], 64))).hex() if params[3] and params[4] else ""
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _, segments, symbols = v.elf.elf_info(args.elf)
    rows = [
        ("delay", [], {"rx_bytes": [0]}),
        ("delay", [], {"rx_bytes": [1, 0]}),
        ("delay", [], {"transfer_statuses": [7, 0], "rx_bytes": [0, 0]}),
        ("configure", [], {}),
        ("configure", [], {"disable_status": 4}),
    ]
    cases, trace = [], {}
    for name, callargs, fixture in rows:
        machines = [LinkedSetupMachine(),
                    LinkedSetupMachine(True, segments, symbols)]
        try:
            results = [m.invoke(name, callargs, fixture) for m in machines]
        except Exception:
            print("execution failure", name, fixture,
                  [(m.source, hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC)))
                   for m in machines])
            raise
        keys = ["providers", "xip_state", "power_state", "status_template"]
        left = {k: results[0][k] for k in keys}
        right = {k: results[1][k] for k in keys}
        assert left == right, (name, fixture, left, right)
        trace.update(machines[0].trace)
        cases.append({"function": name, "fixture": fixture,
                      "observed": left})

    direct_rows = [
        ([5, 0, 0, 0x20008200, 3], {"rx_hex": "112233"}),
        ([0x12345, 0x345678, 0x101, 0x20008210, 1],
         {"transfer_status": 9}),
    ]
    for callargs, fixture in direct_rows:
        machines = [LinkedSetupMachine(),
                    LinkedSetupMachine(True, segments, symbols)]
        results = [m.invoke_direct(callargs, fixture) for m in machines]
        left = {k: results[0][k] for k in ("return", "providers", "rx")}
        right = {k: results[1][k] for k in ("return", "providers", "rx")}
        assert left == right, (callargs, fixture, left, right)
        trace.update(machines[0].trace)
        cases.append({"function": "status_direct", "arguments": callargs,
                      "fixture": fixture, "observed": left})

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    out = {
        "status": "PASS", "cases": len(cases),
        "original_sha256": v.SHA, "elf_sha256": v.sha(args.elf),
        "source_sha256": {p.name: v.sha(p) for p in HERE.iterdir()
                           if p.suffix in [".c", ".h", ".ld", ".py"]},
        "linked_status_source_sha256": {
            p.name: v.sha(p) for p in
            (HERE.parent / "nor-read-status").iterdir()
            if p.suffix in [".c", ".h", ".ld"]},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace, "comparisons": cases,
        "limits": [
            "This linked profile removes the 0x4205F4 return stub: stock executes its poll and status-transfer functions; source routes the poll ABI to compiled nor_read_status.c.",
            "Only 0x4262E0 transfer and 0x415FAE status-error helper are injected. Synthetic RX byte/status values do not represent physical MSPI behavior.",
            "Poll readiness, 1-byte length, status-error path, direct 3-byte stack length, and direct error logging are covered; no physical power/timing/flash behavior is claimed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("status", "cases", "distinct_original_instruction_bytes")},
                     indent=2))


if __name__ == "__main__":
    main()
