#!/usr/bin/env python3
"""Build the recovered Main logger/formatter graph with a typed fallback join."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-littlefs-graph.o"
PRIOR = OUT / "littlefs-graph-current-receipt.json"
OBJDIR = OUT / "logger-current"
UNBOUND = OUT / "apollo-main-logger-candidate.o"
BOUND = OUT / "apollo-main-logger-bound.o"
RECEIPT = OUT / "logger-graph-current-receipt.json"
DIRS = {
    "extended_log_root_candidate_20261011": "extended_log selected_helper_adapters".split(),
    "extended_log_runtime_candidate": "bounded_formatter_adapter event_get event_scheduler_adapters event_set event_unblock locks runtime transport transport_failure transport_formatter_adapter transport_init transport_queue".split(),
    "full_formatter_outer_candidate": "float_bridge float_render fp_primitives general_format vformat".split(),
}
ORACLES = {
    "verify_main_vformat_outer.py": "PASS_MAIN_VFORMAT_OUTER 24",
    "verify_main_general_format_native.py": "PASS_MAIN_GENERAL_FORMAT 27",
    "verify_log_runtime.py": "PASS_REGISTER_AND_FATAL_PREFIX 24 4",
    "verify_main_general_format.py": "PASS_MAIN_GENERAL_FORMAT 27",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, option):
    output = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2]: (parts[0], parts[1]) for line in output.splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_LITTLEFS_GRAPH_COMPILE"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 613
    OBJDIR.mkdir(parents=True, exist_ok=True)
    rows = []
    objects = []
    seen = set(defined(BASE))
    for folder, stems in DIRS.items():
        for stem in stems:
            source = G2 / "components/main" / folder / (stem + ".c")
            obj = OBJDIR / (stem + ".o")
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                            "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                           cwd=ROOT, check=True)
            names = set(defined(obj))
            assert names and not names & seen, (source, names & seen)
            seen |= names
            rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                         "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                         "defined": sorted(names)})
            objects.append(obj)
    assert len(rows) == 19
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(UNBOUND)],
                   cwd=ROOT, check=True)
    new_imports = nm(UNBOUND, "-u") - before
    assert new_imports == {"g2_log_general_vformat"}
    # The bounded formatter's general fallback has the same four-argument
    # ARM32 va_list ABI as the selected full-grammar C formatter.
    assert defined(UNBOUND)["g2_log_vformat"][1] == "T"
    subprocess.run(["arm-none-eabi-ld", "-r", "--defsym",
                    "g2_log_general_vformat=g2_log_vformat", str(UNBOUND), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    defs = defined(BOUND)
    assert defs["g2_log_general_vformat"] == defs["g2_log_vformat"]
    assert not after - before and len(before - after) == 26 and len(after) == 587
    oracles = []
    for name, expected in ORACLES.items():
        path = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True, check=True)
        assert result.stdout.strip().splitlines()[-1] == expected, (name, result.stdout)
        oracles.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                        "observed": expected})
    receipt = {
        "status": "PASS_CURRENT_MAIN_LOGGER_GRAPH_COMPILE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows, "source_unit_count": len(rows),
        "formatter_fallback_alias": {"import": "g2_log_general_vformat", "provider": "g2_log_vformat",
                                     "equal_symbol_address": True},
        "bounded_oracles_rerun": oracles,
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Extended logger runtime and formatter oracles are bounded, not a complete grammar or output-path proof",
                   "Logger product RAM state, transport lifecycle, final placement, and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "units": len(rows),
                      "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
