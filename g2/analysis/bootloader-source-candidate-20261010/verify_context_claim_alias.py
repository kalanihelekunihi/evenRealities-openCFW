#!/usr/bin/env python3
"""Platform-finish context claim alias versus locked stock and selected source."""
import hashlib
import importlib.util
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("claim_verify", BASE / "verify_context_claim.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/context_claim_alias.c"
SOURCE = BASE / "context_claim.c"


def main():
    assert hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-context-claim-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T",
                        str(Path(__file__).with_name("context-claim-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        assert syms["opencfw_boot_iom_contexts"] == v.POOL
        for name, (address, _, _) in v.CALLS.items():
            syms.setdefault(name, address | 1)
        original, source = v.Machine(False, segs, syms), v.Machine(True, segs, syms)
        source.symbols["opencfw_boot_context_claim"] = syms["opencfw_bl_context_claim"]
        cases = []
        for module, output, flags in itertools.product(
                range(11), [0, v.OUT], [0, 0x02000000, 0x800abcde, 0x01000000, 0xfe123456]):
            observed = []
            for m in [original, source]:
                m.reset()
                for i in range(8):
                    m.cpu.mem_write(v.POOL + i * v.STRIDE, struct.pack("<I", flags))
                status = m.call("claim", [module, output])
                observed.append(m.observation(status))
            assert observed[0] == observed[1], (module, output, flags, observed)
            cases.append({"module": module, "output": output, "flags": flags,
                          "observed": observed[0]})
        trace = {hex(pc): raw for pc, raw in original.trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x42c4c7", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Platform-finish passes a module index and pointer to its transfer word; synthetic output uses an equivalent 32-bit pointer slot.",
                             "Full eight-slot claim pool and output state are compared. No context release, hardware binding or concurrent claim behavior is established."]}
        Path(__file__).with_name("context-claim-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
