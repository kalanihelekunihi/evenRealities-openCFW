#!/usr/bin/env python3
"""System-entry platform-init alias versus locked stock and selected dispatcher."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/main_init"
spec = importlib.util.spec_from_file_location("main_verify", BASE / "verify_main_init.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/platform_system_init_alias.c"
SOURCE = BASE / "main_init.c"


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-platform-system-init-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "source.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
                            "-c", str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "module.ld"),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.v.elf.elf_info(elf)
        trace, cases = {}, []
        for argument in [0, 1, 0xffffffff]:
            for mode_result in [0, 7, 0xffffffff]:
                for slot_target in v.SLOT_TARGETS:
                    pair = [v.MainInitMachine(), v.MainInitMachine(True, segs, dict(syms))]
                    pair[1].symbols["opencfw_boot_main_init"] = syms["opencfw_boot_platform_system_init"]
                    for machine in pair:
                        machine.mode_result = mode_result
                        machine.slot_target = slot_target
                        machine.w(v.SLOT, slot_target)
                    results = [m.run("main_init", [argument]) for m in pair]
                    assert results[0]["events"] == results[1]["events"] == v.expected_events(mode_result, slot_target)
                    trace.update(pair[0].trace)
                    cases.append({"argument": argument, "mode_status": mode_result,
                                  "slot_target": slot_target, "events": results[0]["events"]})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.SHA, "source_elf_sha256": v.v.sha(elf),
                  "source_sha256": v.v.sha(SOURCE), "alias_sha256": v.v.sha(ALIAS),
                  "stock_entry": "0x41b863", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Startup system-entry calls with argument zero; nonzero arguments confirm the dispatcher ignores this word.",
                             "All platform, allocator, storage and logger services are controlled at stock entries. RAM callback slot is synthetic and terminal spin is stopped by the verifier.",
                             "Compatible M4 execution is compared; M55 archive compilation and direct relocation are checked separately. No actual boot or formatter ABI claim."]}
        Path(__file__).with_name("platform-system-init-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
