#!/usr/bin/env python3
"""Compare lifecycle wrappers against the pinned combined source ELF.

The source ELF's linked kernel-start implementation is intercepted as the
same explicit synthetic boundary used for the stock kernel-start routine.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
VERIFY = ROOT / "g2/components/bootloader/update_core/verify.py"
spec = importlib.util.spec_from_file_location("bootverify", VERIFY)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.ENTRIES.update(kernel_initialize=0x416058,
                 kernel_state=0x416088,
                 kernel_start=0x4160B0)

class Machine(v.Machine):
    def __init__(self, source=False, segments=(), symbols=None):
        super().__init__(source, segments, symbols)
        self.kernel_start_pcs = {0x418148}
        if source and "opencfw_bl_kernel_start" in self.symbols:
            self.kernel_start_pcs.add(self.symbols["opencfw_bl_kernel_start"] & ~1)

    def code(self, uc, pc, size, user):
        if pc in self.kernel_start_pcs:
            self.events.append(["kernel-start", self.u(0x200270D4)])
            self.ret(0xDEADBEEF)
            return
        super().code(uc, pc, size, user)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    assert sha(v.BLOB) == v.SHA
    _, segments, symbols = v.elf.elf_info(args.elf)
    cases, trace = [], {}
    names = ["kernel_initialize", "kernel_state", "kernel_start"]
    for name, mode, state, primask, basepri, ipsr in itertools.product(
            names, [1, 2, 0], [0, 1, 2], [0, 1], [0, 48], [0, 3]):
        pair = [Machine(), Machine(True, segments, dict(symbols))]
        outputs = []
        for m in pair:
            m.w(0x20027150, 0 if mode == 1 else 1)
            m.w(0x2002716C, 0 if mode == 2 else 1)
            m.w(0x200270D4, state)
            for reg, value in ((v.a.UC_ARM_REG_PRIMASK, primask),
                               (v.a.UC_ARM_REG_BASEPRI, basepri),
                               (v.a.UC_ARM_REG_IPSR, ipsr)):
                m.cpu.reg_write(reg, value)
            result = m.run(name, [])
            outputs.append({"return": result["return"], "events": result["events"],
                            "state": m.u(0x200270D4),
                            "primask": m.cpu.reg_read(v.a.UC_ARM_REG_PRIMASK),
                            "basepri": m.cpu.reg_read(v.a.UC_ARM_REG_BASEPRI)})
        assert outputs[0] == outputs[1], (name, mode, state, primask, basepri,
                                          ipsr, outputs)
        trace.update(pair[0].trace)
        cases.append({"function": name, "mode": mode, "state": state,
                      "primask": primask, "basepri": basepri, "ipsr": ipsr,
                      "observed": outputs[0]})
    used = {int(pc, 0) + i for pc, raw in trace.items()
            for i in range(len(bytes.fromhex(raw)))}
    tracked = [HERE / "verify_kernel_state_candidate.py",
               ROOT / "g2/components/bootloader/thread_creation/lifecycle.c",
               ROOT / "g2/components/bootloader/thread_creation/verify_lifecycle.py",
               args.elf]
    report = {"status": "PASS", "cases": len(cases),
              "distinct_original_trace_bytes": len(used),
              "original_sha256": v.SHA, "elf_sha256": sha(args.elf),
              "source_sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT)
                                else str(p): sha(p) for p in tracked},
              "original_trace": trace, "comparisons": cases,
              "limits": ["Original 0x416088 and source opencfw_boot_kernel_state execute directly with the same no-argument, uint32 return ABI.",
                         "The stock kernel-start leaf and the combined ELF's linked opencfw_bl_kernel_start are intercepted with a fixed return value; this isolates wrapper state behavior.",
                         "Context/IPSR/PRIMASK/BASEPRI and memory are synthetic; no real scheduler, interrupt delivery, hardware, or byte-equality claim."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in
                      ["status", "cases", "distinct_original_trace_bytes"]}))

if __name__ == "__main__":
    main()
