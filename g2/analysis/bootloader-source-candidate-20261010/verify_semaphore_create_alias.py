#!/usr/bin/env python3
"""Platform semaphore alias versus locked stock and selected constructor."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/initializer_callbacks"
spec = importlib.util.spec_from_file_location("semaphore_verify", BASE / "verify_semaphore_create.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/semaphore_create_alias.c"
SOURCE = BASE / "semaphore_create.c"


def main():
    assert v.hashlib.sha256(v.v.BLOB.read_bytes()).hexdigest() == v.v.LOCKED_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-semaphore-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(Path(__file__).with_name("semaphore-alias-module.ld")),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        machines = [v.Machine(False, segs, syms), v.Machine(True, segs, syms)]
        machines[1].symbols["opencfw_boot_semaphore_create"] = syms["opencfw_bl_semaphore_create"]
        cases = []
        for maximum, initial, guard, factory, put in itertools.product(
                [0, 1, 2, 0xffffffff], [0, 1, 2], [0, 1], [False, True], [0, 1, 2]):
            params = [maximum, initial, False, 0, 0, guard, factory, put]
            observed = [m.run(*params) for m in machines]
            assert observed[0] == observed[1], (params, observed)
            cases.append({"parameters": params, "observed": observed[0]})
        trace = {hex(pc): raw for pc, raw in machines[0].trace.items()}
        used = {int(pc, 16) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.LOCKED_SHA,
                  "source_elf_sha256": v.hashlib.sha256(elf.read_bytes()).hexdigest(),
                  "source_sha256": v.hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  "alias_sha256": v.hashlib.sha256(ALIAS.read_bytes()).hexdigest(),
                  "stock_entry": "0x416763", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["The selected platform caller passes (1,0,NULL); the matrix broadens maximum, initial count and controlled factory status.",
                             "Guard, queue factories, queue put and free are controlled cuts. No live scheduler, heap, ISR or physical I2C behavior is established.",
                             "Compatible M4 source executes in Unicorn; M55 archive compilation and direct relocation are checked separately."]}
        Path(__file__).with_name("semaphore-create-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
