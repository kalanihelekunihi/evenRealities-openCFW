#!/usr/bin/env python3
"""Bounded Ablation whole-main call-graph audit against GNU decoding."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import lief

from ablation.analyzers.binary_context import BinaryContext


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "g2/workflow/state.json").exists())
ELF = ROOT / "g2/analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTIONS = ROOT / "g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl"
OBJDUMP = Path("/opt/homebrew/bin/arm-none-eabi-objdump")
EXPECTED_STOCK_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
EXPECTED_ELF_SHA256 = "36c9b79de3b961d36ad343a1402a112298603111cbe1d5875e1b471694159d1a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_functions():
    records = []
    for line in FUNCTIONS.read_text().splitlines():
        row = json.loads(line)
        if row.get("external"):
            continue
        start = int(row["entry"], 16) & ~1
        ranges = [(int(a, 16), int(b, 16) + 1) for a, b in row["ranges"]]
        records.append({"start": start, "name": row["name"], "ranges": ranges})
    # There are overlapping/thunk records. BinaryContext itself requires unique starts.
    by_start = {}
    for row in records:
        by_start.setdefault(row["start"], row)
    return records, [by_start[x] for x in sorted(by_start)]


def in_ranges(address: int, ranges) -> bool:
    return any(a <= address < b for a, b in ranges)


def main():
    assert sha256(STOCK) == EXPECTED_STOCK_SHA256
    assert sha256(ELF) == EXPECTED_ELF_SHA256
    records, unique = load_functions()
    starts = [r["start"] for r in unique]
    by_start = {r["start"]: r for r in unique}

    ctx = BinaryContext.build(str(ELF))
    initial = {
        "func_starts": len(ctx.func_starts),
        "thumb_funcs": len(ctx.thumb_funcs),
        "call_edges": len(ctx.call_edges),
        "strings": len(ctx.strings),
        "string_xrefs": sum(len(v) for v in ctx._str_xref_idx.values()),
    }
    # Reviewed adapter: the historical corpus and stock image are Thumb. Rebuild only
    # the in-memory call index; do not write Ablation caches or registries.
    ctx.func_starts = starts
    ctx.thumb_funcs = set(starts)
    parsed = lief.parse(ELF.read_bytes())
    ctx._build_call_graph(ELF.read_bytes(), parsed)
    ablation = Counter((owner, target) for owner, target, _ in ctx.call_edges)

    proc = subprocess.run(
        [str(OBJDUMP), "-D", "-marm", "-Mforce-thumb", str(ELF)],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    (HERE / "objdump.stderr.txt").write_text(proc.stderr)
    # GNU syntax: 4cff84: f7ff fee...  bl 4cfd66 <...>
    insn_re = re.compile(r"^\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+){1,2}(blx?)\s+([0-9a-f]+)")
    decoded = []
    current_idx = 0
    for line in proc.stdout.splitlines():
        m = insn_re.match(line)
        if not m:
            continue
        site, target = int(m.group(1), 16), int(m.group(3), 16) & ~1
        while current_idx + 1 < len(starts) and starts[current_idx + 1] <= site:
            current_idx += 1
        owner = starts[current_idx] if starts and starts[current_idx] <= site else None
        if owner is None:
            continue
        row = by_start[owner]
        decoded.append((owner, site, target, in_ranges(site, row["ranges"])))
    native_body = Counter((owner, target) for owner, _, target, body in decoded if body)
    native_gap = Counter((owner, target) for owner, _, target, body in decoded if not body)

    missing = native_body - ablation
    extra = ablation - native_body
    # Extra calls that GNU also decodes between a function's retained body ranges.
    extra_explained_by_gap = Counter()
    for key, count in extra.items():
        extra_explained_by_gap[key] = min(count, native_gap[key])
    unexplained = extra - extra_explained_by_gap
    intersection = native_body & ablation

    # Ablation deliberately caps each Thumb-function scan at 4096 bytes.
    capped = []
    capped_starts = set()
    for i, row in enumerate(unique):
        next_start = starts[i + 1] if i + 1 < len(starts) else None
        span = (next_start - row["start"]) if next_start else None
        if span is not None and span > 4096:
            capped_starts.add(row["start"])
            capped.append({"start": hex(row["start"]), "name": row["name"], "next_start_span": span})
    missing_capped = Counter({k: v for k, v in missing.items() if k[0] in capped_starts})
    missing_uncapped = missing - missing_capped

    def samples(counter, limit=30):
        out = []
        for (owner, target), count in counter.most_common(limit):
            out.append({"owner": hex(owner), "name": by_start[owner]["name"], "target": hex(target), "count": count})
        return out

    result = {
        "inputs": {
            "stock": str(STOCK.relative_to(ROOT)), "stock_sha256": sha256(STOCK),
            "elf": str(ELF.relative_to(ROOT)), "elf_sha256": sha256(ELF),
            "functions": str(FUNCTIONS.relative_to(ROOT)), "functions_sha256": sha256(FUNCTIONS),
            "ablation_git": subprocess.check_output(["git", "-C", str(ROOT / "third-party/tools/ablation"), "rev-parse", "HEAD"], text=True).strip(),
            "objdump_version": subprocess.check_output([str(OBJDUMP), "--version"], text=True).splitlines()[0],
        },
        "initial_unadapted_context": initial,
        "reviewed_adapter": {"historical_records": len(records), "unique_function_starts": len(starts), "all_marked_thumb": True},
        "counts": {
            "ablation_edges": sum(ablation.values()), "ablation_unique_owner_target": len(ablation),
            "native_body_calls": sum(native_body.values()), "native_body_unique_owner_target": len(native_body),
            "native_gap_calls": sum(native_gap.values()),
            "validated_body_calls_present": sum(intersection.values()),
            "missing_body_calls": sum(missing.values()), "extra_calls": sum(extra.values()),
            "missing_from_capped_owners": sum(missing_capped.values()),
            "missing_from_uncapped_owners": sum(missing_uncapped.values()),
            "extra_explained_by_native_gap": sum(extra_explained_by_gap.values()),
            "extra_unexplained": sum(unexplained.values()), "capped_function_spans": len(capped),
        },
        "missing_samples": samples(missing),
        "missing_uncapped_samples": samples(missing_uncapped),
        "gap_extra_samples": samples(extra_explained_by_gap),
        "unexplained_extra_samples": samples(unexplained),
        "capped_samples": capped[:30],
        "method": "Ablation BinaryContext.build, inject reviewed starts/Thumb state, rebuild private in-memory call graph; compare owner-target multisets with GNU force-Thumb direct BL/BLX decoded only at retained historical body ranges.",
    }
    (HERE / "evidence.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["counts"], indent=2))


if __name__ == "__main__":
    main()
