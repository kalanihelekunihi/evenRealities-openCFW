#!/usr/bin/env python3
"""Execute stock NOR-read wrapper instructions against readable candidate.

Only its four local setup/teardown calls and MSPI blocking-transfer boundary
are synthetic deterministic providers. No NOR or device is accessed.
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

ENTRY = 0x420F70
SLOT = 0x200270DC
HANDLE = 0x20006000
BEFORE, CONFIGURE, DELAY, AFTER, TRANSFER = (
    0x41FF08, 0x420E8C, 0x4207F4, 0x41FF1E, 0x4262E0)
v.ENTRIES["nor_read"] = ENTRY


class NorMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        if source:
            self.symbols["opencfw_boot_nor_read"] = self.symbols[
                "opencfw_boot_nor_read"]
        self.transfer_status = 0
        self.calls = []

    def code(self, uc, pc, size, user):
        if pc in (BEFORE, CONFIGURE, DELAY, AFTER):
            self.calls.append({BEFORE: "before", CONFIGURE: "configure",
                               DELAY: "delay", AFTER: "after"}[pc])
            self.ret(0)
            return
        if pc == TRANSFER:
            handle, command, timeout = self.args()[:3]
            raw = bytes(uc.mem_read(command, 24))
            fields = struct.unpack("<IBBBBIBxHBBBBI", raw)
            # Also retain exact bytes so padding/layout differences are visible.
            self.calls.append({"transfer": {"handle": handle,
                "timeout_usec": timeout, "command": raw.hex(),
                "fields": list(fields)}})
            self.ret(self.transfer_status)
            return
        super().code(uc, pc, size, user)

    def invoke(self, args, fixture):
        self.calls = []
        self.transfer_status = fixture.get("transfer_status", 0)
        self.w(SLOT, fixture.get("handle", HANDLE))
        result = self.run("nor_read", args)
        result["provider_calls"] = self.calls
        return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    fixtures = [
        ([0x123456, 0x20008000, 16, 0], {}),
        ([0x123456, 0x20008000, 4096, 0xfeed], {"transfer_status": 0x80000007}),
        ([0x01ffffff, 0x20008001, 1, 0], {}),
        ([0x01fffff0, 0x20008000, 0x1000, 0], {}),
        ([0, 0x20008000, 1, 0], {}),
        ([0x2000000, 0x20008000, 1, 0], {}),
        ([0x2000001, 0x20008000, 1, 0], {}),
        ([0x123456, 0, 1, 0], {}),
        ([0x123456, 0x20008000, 0, 0], {}),
        ([0x123456, 0x20008000, 1, 0], {"handle": 0}),
    ]
    for params, fixture in fixtures:
        machines = [NorMachine(), NorMachine(True, segments, symbols)]
        results = [m.invoke(params, fixture) for m in machines]
        left = {k: results[0][k] for k in ("return", "provider_calls")}
        right = {k: results[1][k] for k in ("return", "provider_calls")}
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
            "Only the wrapper instructions execute; setup, teardown, and MSPI transfer calls are intercepted at their exact local entries.",
            "Synthetic transfer provider records the 24-byte command and returns a selected status; no flash or hardware access occurs.",
            "Address check is start-only: no end-of-device, overflow, pointer-alignment, or transfer-size guard is added by this wrapper.",
            "The wrapper issues one transfer for the full length. Higher-level littlefs controls ordinary request sizes; HAL internals are outside this test.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("status", "cases", "distinct_original_instruction_bytes")},
                     indent=2))


if __name__ == "__main__":
    main()
