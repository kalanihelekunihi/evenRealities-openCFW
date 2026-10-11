#!/usr/bin/env python3
"""NOR/HAL power alias versus locked stock and selected adapter source."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/nor_mspi_power"
OLD = ROOT / "g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-power"
spec = importlib.util.spec_from_file_location("power_verify", OLD / "verify_power_control.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/hal_power_control_alias.c"
SOURCES = [BASE / "power_control.c", BASE / "power_control_adapter.c"]


def main():
    assert v.sha(v.IMAGE) == v.IMAGE_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-hal-power-alias-") as tmp:
        p = Path(tmp)
        objects = []
        for i, source in enumerate([ALIAS, *SOURCES]):
            obj = p / f"unit_{i}.o"
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-std=c11", "-O2",
                            "-ffunction-sections", "-fdata-sections", "-c", str(source),
                            "-o", str(obj)], check=True)
            objects.append(obj)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(OLD / "module.ld"),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segs, syms = v.elf.elf_info(elf)
        fixtures = [
            ("bad-magic", {"magic": 0}, 1, 0, {}, 0),
            ("invalid-operation", {}, 3, 0, {}, 0),
            ("operation-byte-truncation", {}, 0x102, 0, {}, 0),
            ("clock-request-error", {}, 0, 0, {0: 9}, 0),
            ("clock-request-error-retain", {"save_valid": 1, "clock_class": 5}, 0, 1, {0: 7}, 0),
            ("operation-zero-enable", {}, 0, 0, {}, 0),
            ("operation-zero-restore", {"save_valid": 1, "clock_class": 3}, 0, 1, {}, 0),
            ("operation-zero-restore-cq", {"save_valid": 1, "clock_class": 4, "cqcfg": 1}, 0, 1, {}, 0),
            ("power-down-no-retain", {}, 1, 0, {}, 0),
            ("power-down-retain", {"cqcfg": 0}, 2, 1, {}, 0),
            ("power-down-retain-cq", {"cqcfg": 0x80000001}, 1, 1, {}, 0),
            ("xip-delay", {"xip": 1, "delay": 123}, 1, 0, {}, 0),
            ("release-all-error", {}, 2, 0, {}, 6),
            ("module-byte-user-byte", {"module": 0x101}, 0x101, 0, {}, 0),
        ]
        trace, cases = {}, []
        for name, fixture, operation, retain, clocks, release in fixtures:
            pair = [v.Machine(False, clock_status=clocks, release_status=release),
                    v.Machine(True, segs, dict(syms), clock_status=clocks,
                              release_status=release)]
            pair[1].symbols["opencfw_bl_power_control"] = syms["opencfw_hal_power_control"]
            observed = []
            for m in pair:
                m.setup(fixture)
                observed.append(m.run(operation, retain))
            assert observed[0] == observed[1], (name, observed[0]["events"], observed[1]["events"])
            trace.update(pair[0].trace)
            cases.append({"name": name, "operation": operation, "retain": retain,
                          "return": observed[0]["return"], "events": observed[0]["events"],
                          "handle_sha256": v.hashlib.sha256(bytes.fromhex(observed[0]["handle"])).hexdigest(),
                          "mmio_sha256": v.hashlib.sha256(bytes.fromhex(observed[0]["mmio"])).hexdigest()})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.IMAGE_SHA, "source_elf_sha256": v.sha(elf),
                  "alias_sha256": v.sha(ALIAS),
                  "source_sha256": {str(x.relative_to(ROOT)): v.sha(x) for x in SOURCES},
                  "stock_entry": "0x426809", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["NOR init callers pass handle, operation and retain in R0-R2 and consume status; fixture set includes their 0/2 operations and retain 1.",
                             "Mode/CQ/clock/interrupt/delay callbacks are controlled; MMIO is synthetic RAM. No physical power transition or elapsed-time proof.",
                             "Compatible M4 execution is compared; M55 archive compilation and direct relocation are checked separately."]}
        Path(__file__).with_name("hal-power-control-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({key: report[key] for key in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
