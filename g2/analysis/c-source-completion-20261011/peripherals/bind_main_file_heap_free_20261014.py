#!/usr/bin/env python3
"""Compile bounded TLSF/file heap free outer bodies into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
P = G2 / "analysis/c-source-completion-20261011/peripherals"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-tlsf-lowers.o"
PRIOR = OUT / "tlsf-lowers-current-receipt.json"
BOUND = OUT / "apollo-main-file-heap-free.o"
RECEIPT = OUT / "file-heap-free-current-receipt.json"
ROWS = [
    ("g2_file_close_error", "audio/semihost_error_candidate/error.c", "semihost-error", 3),
    ("g2_file_pool_free", "audio/file_pool_free_candidate/pool_free.c", "pool-free", 4),
    ("audio_file_heap_free", "audio/file_heap_free_candidate/file_heap_free.c", "file-heap-free", 6),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syms(path, flag):
    result = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in result.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_TLSF_LOWERS"
    assert sha(BASE) == prior["output_sha256"]
    before = syms(BASE, "-u")
    assert len(before) == 630
    assert {row[0] for row in ROWS} <= before
    objects = []
    evidence = []
    for name, relative, result_stem, cases in ROWS:
        source = G2 / "components" / relative
        result_path = P / (result_stem + "-results.json")
        result = json.loads(result_path.read_text())
        assert result["status"].startswith("PASS_") and result["cases"] == cases
        assert result["source_sha256"] == sha(source)
        obj = OUT / (name + "-current.o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        assert syms(obj, "--defined-only") == {name}
        objects.append(obj)
        evidence.append({"symbol": name, "source": str(source.relative_to(ROOT)),
                         "source_sha256": sha(source), "object": str(obj.relative_to(ROOT)),
                         "object_sha256": sha(obj), "oracle": str(result_path.relative_to(ROOT)),
                         "oracle_sha256": sha(result_path), "cases": cases})
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = syms(BOUND, "-u")
    assert after == before - {row[0] for row in ROWS}
    assert syms(BOUND, "--defined-only") == syms(BASE, "--defined-only") | {row[0] for row in ROWS}
    assert len(after) == 627
    receipt = {
        "status": "PASS_CURRENT_MAIN_FILE_HEAP_FREE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "providers": evidence,
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_added": sorted(after - before),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Bounded ABI oracles cut allocator/mutex child effects",
                   "Semihost BKPT is intercepted in the oracle, not executed on physical hardware",
                   "Final image placement and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
