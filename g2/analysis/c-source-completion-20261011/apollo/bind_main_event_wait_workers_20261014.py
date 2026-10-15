#!/usr/bin/env python3
"""Compose the bounded event-wait worker and two native-compared children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCES = G2 / "components/audio/event_wait_source_candidate"
ORACLES = G2 / "analysis/c-source-completion-20261011/peripherals"
BASE = G2 / "build/c-firmware/20261014/main-event-wait-outer/apollo-main-event-wait-outer.o"
OUT = G2 / "build/c-firmware/20261014/main-event-wait-workers"
ROWS = (
    ("wait_bits.c", "wait-bits-ready-results.json", "PASS_EVENT_WAIT_READY_BOUNDED", 20),
    ("place_unordered.c", "place-unordered-results.json", "PASS_EVENT_PLACE_UNORDERED", 9),
    ("reset_item_value.c", "reset-item-results.json", "PASS_EVENT_RESET_ITEM", 12),
)
PROVIDERS = {"g2_event_wait_bits", "g2_event_place_unordered", "g2_event_reset_item_value"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    coverage = []
    for filename, result_name, status, cases in ROWS:
        source, oracle = SOURCES / filename, ORACLES / result_name
        result = json.loads(oracle.read_text())
        if (result.get("status") != status or result.get("cases") != cases
                or result.get("source_sha256") != sha(source)):
            raise RuntimeError(f"stale native comparison: {result_name}")
        obj = OUT / (Path(filename).stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                        "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)
        objects.append(obj)
        coverage.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                         "oracle": str(oracle.relative_to(ROOT)), "oracle_sha256": sha(oracle),
                         "native_cases": cases, "object": str(obj.relative_to(ROOT)),
                         "object_sha256": sha(obj)})
    defined = set().union(*(names(obj, "-g", "--defined-only") for obj in objects))
    if defined != PROVIDERS:
        raise RuntimeError(f"event-wait provider set changed: {defined}")
    before = names(BASE, "-u")
    if "g2_event_wait_bits" not in before:
        raise RuntimeError("Apollo Main event wait worker import changed")
    linked = OUT / "apollo-main-event-wait-workers.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *(str(obj) for obj in objects),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"g2_event_wait_bits"} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVENT_WAIT_WORKERS_C",
        "coverage": coverage,
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native comparisons cover immediate/zero-timeout wait, nine list placements, and twelve reset-item cases; full blocked-wait scheduling remains open.",
                   "Corrected archive replay, whole-image link, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
