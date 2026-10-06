#!/usr/bin/env python3
"""Compare stock mspi_cq_init with source, intercepting lower cmdq init."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location(
    "bootverify", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)

ENTRY = 0x423F28
CMDQ_INIT = 0x427794
STATE_BASE = 0x2001CAA0
STATE_STRIDE = 0x8D0
CMDQ_HANDLE_OFFSET = 0x828
v.ENTRIES["cq_init"] = ENTRY


class CqInitMachine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        # Extend synthetic target RAM for module255's computed output slot.
        self.cpu.mem_map(0x20040000, 0x00100000)
        if source:
            self.symbols["opencfw_boot_cq_init"] = self.symbols[
                "opencfw_bl_mspi_cq_init"]
            self.cmdq_init_address = self.symbols["am_hal_cmdq_init"] & ~1
        else:
            self.cmdq_init_address = CMDQ_INIT
        self.provider_calls = []
        self.provider_result = 0

    def code(self, uc, pc, size, user):
        if pc == self.cmdq_init_address:
            hw_if, config, handle_slot, _ = self.args()
            raw = bytes(uc.mem_read(config, 9))
            prior_handle = self.u(handle_slot)
            self.provider_calls.append({
                "hw_if": hw_if,
                "config_size_word": int.from_bytes(raw[0:4], "little"),
                "config_buffer_word": int.from_bytes(raw[4:8], "little"),
                "config_option_byte": raw[8],
                "handle_slot": handle_slot,
                "prior_handle_word": prior_handle,
            })
            self.ret(self.provider_result)
            return
        super().code(uc, pc, size, user)

    def invoke(self, case):
        module = case["module"] & 0xffffffff
        slot = (STATE_BASE + module * STATE_STRIDE + CMDQ_HANDLE_OFFSET) & 0xffffffff
        slot_word = 0xC0DEC0DE ^ module
        self.w(slot, slot_word)
        self.provider_calls = []
        self.provider_result = case["provider_result"]
        result = self.run("cq_init", [module, case["queue_size_input"],
                                       case["queue_buffer"]])
        return {
            # mspi_cq_init's caller ignores the lower API's result; do not
            # assign a source-language return contract to its leftover R0.
            "providers": self.provider_calls,
            "slot_after": self.u(slot),
            "expected_slot": slot_word,
        }


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    assert sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases = [
        {"module": 0, "queue_size_input": 0, "queue_buffer": 0,
         "provider_result": 0},
        {"module": 0, "queue_size_input": 1, "queue_buffer": 0x20010000,
         "provider_result": 1},
        {"module": 1, "queue_size_input": 2, "queue_buffer": 0x20023400,
         "provider_result": 7},
        {"module": 1, "queue_size_input": 3, "queue_buffer": 0x20024500,
         "provider_result": 0},
        {"module": 2, "queue_size_input": 0x12345678,
         "queue_buffer": 0x20035600, "provider_result": 0},
        {"module": 3, "queue_size_input": 0xffffffff,
         "queue_buffer": 0xffffffff, "provider_result": 3},
        {"module": 255, "queue_size_input": 0x80000001,
         "queue_buffer": 0x20046700, "provider_result": 0},
        {"module": 0xffffffff, "queue_size_input": 0xabcdef01,
         "queue_buffer": 0x20057800, "provider_result": 0},
    ]
    machines = [CqInitMachine(), CqInitMachine(True, segments, symbols)]
    trace = {}
    comparisons = []
    for case in cases:
        results = [m.invoke(case) for m in machines]
        if results[0] != results[1]:
            raise AssertionError({"case": case, "stock": results[0],
                                  "source": results[1]})
        trace.update(machines[0].trace)
        comparisons.append({"case": case, "observed": results[0]})

    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    tracked = [p for p in HERE.iterdir() if p.is_file() and
               p.suffix in {".c", ".h", ".ld", ".py"}]
    output = {
        "status": "PASS",
        "cases": len(comparisons),
        "original_sha256": v.SHA,
        "original_function_range": ["0x00423f28", "0x00423f54"],
        "original_function_sha256": "8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05",
        "elf_sha256": sha(args.elf),
        "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in tracked},
        "distinct_original_instruction_bytes": len(used),
        "original_trace": trace,
        "comparisons": comparisons,
        "limits": [
            "Only am_hal_cmdq_init is intercepted; it records selected config bytes and the output-slot pointer, then returns a fixture status without creating a queue.",
            "Config bytes beyond offsets0..8 are not compared; the stock wrapper's stack frame overlaps saved-register slots, and this probe does not infer their meaning.",
            "The output handle slot is seeded but not modified by the stub; no real queue handle or state is produced.",
            "This validates the 44-byte wrapper only, not am_hal_cmdq_init, queue operation, hardware, or byte-identical compiled code."
        ]
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in
                      ["status", "cases", "distinct_original_instruction_bytes"]}))


if __name__ == "__main__":
    main()
