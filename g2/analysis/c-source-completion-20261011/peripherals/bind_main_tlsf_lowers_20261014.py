#!/usr/bin/env python3
"""Compile the source-owned TLSF lower cluster into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
ANALYSIS = G2 / "analysis/c-source-completion-20261011/peripherals"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
SRC = G2 / "components/audio/file_pool_free_candidate"
BASE = OUT / "apollo-main-littlefs-lowers.o"
PRIOR = OUT / "littlefs-lowers-current-receipt.json"
BOUND = OUT / "apollo-main-tlsf-lowers.o"
RECEIPT = OUT / "tlsf-lowers-current-receipt.json"
STEMS = ("tlsf_leaf", "tlsf_mark_free", "tlsf_block_next", "tlsf_merge",
         "tlsf_merge_leaves", "tlsf_absorb", "tlsf_absorb_leaves",
         "tlsf_lists", "tlsf_mapping", "tlsf_free_lists", "tlsf_align")
CASES = {"leaf": 48, "mark-free": 6, "block-next": 8, "merge": 4,
         "merge-leaves": 18, "absorb": 8, "absorb-leaves": 12, "lists": 6,
         "free-lists": 15}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def syms(path, option):
    output = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_LITTLEFS_LOWERS"
    assert sha(BASE) == prior["output_sha256"]
    before = syms(BASE, "-u")
    assert len(before) == 643
    oracle_rows = []
    for suffix, cases in CASES.items():
        path = ANALYSIS / f"tlsf-{suffix}-results.json"
        result = json.loads(path.read_text())
        assert result["status"].startswith("PASS_TLSF_") and result["cases"] == cases
        for stem, source_hash in (result["source_sha256"].items()
                                  if isinstance(result["source_sha256"], dict)
                                  else [("tlsf_" + suffix.replace("-", "_"), result["source_sha256"])]):
            assert sha(SRC / (stem + ".c")) == source_hash
        oracle_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path), "cases": cases})
    objects = []
    for stem in STEMS:
        source = SRC / (stem + ".c")
        obj = OUT / "tlsf-current" / (stem + ".o")
        obj.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        objects.append(obj)
    definitions = set().union(*(syms(obj, "--defined-only") for obj in objects))
    assert len(definitions) == sum(len(syms(obj, "--defined-only")) for obj in objects)
    assert not definitions & syms(BASE, "--defined-only")
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = syms(BOUND, "-u")
    assert after == before - definitions
    assert syms(BOUND, "--defined-only") == syms(BASE, "--defined-only") | definitions
    assert len(after) == 630
    receipt = {
        "status": "PASS_CURRENT_MAIN_TLSF_LOWERS",
        "base_receipt": str(PRIOR.relative_to(ROOT)),
        "base_receipt_sha256": sha(PRIOR),
        "sources": [{"path": str((SRC / (stem + ".c")).relative_to(ROOT)),
                     "sha256": sha(SRC / (stem + ".c")),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)}
                    for stem, obj in zip(STEMS, objects, strict=True)],
        "bounded_oracles": oracle_rows,
        "definitions_added": sorted(definitions),
        "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Bounded TLSF oracle cases do not qualify all allocator states",
                   "Mapping geometry follows pinned TLSF evidence; current mapping oracle not rerun in this wave",
                   "Final image placement and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
