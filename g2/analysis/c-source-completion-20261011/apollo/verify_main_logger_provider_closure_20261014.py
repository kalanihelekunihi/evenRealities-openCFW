#!/usr/bin/env python3
"""Recompose the pinned Main logger C graph after LittleFS closure."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-logger-provider-closure"
BASE = G2 / "build/c-firmware/20261014/main-littlefs-provider-closure/apollo-main-littlefs-providers.o"
PINNED = G2 / "build/c-firmware/20261014/main-root-dependencies/logger-graph-current-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def main():
    prior = json.loads(PINNED.read_text())
    if prior["status"] != "PASS_CURRENT_MAIN_LOGGER_GRAPH_COMPILE":
        raise RuntimeError("pinned logger receipt changed")
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    sources = {}
    for unit in prior["source_units"]:
        source = ROOT / unit["source"]
        if sha(source) != unit["source_sha256"]:
            raise RuntimeError(f"logger source drift: {source}")
        if source.name in {"event_scheduler_adapters.c", "event_unblock.c"}:
            # The current Main graph already owns these FreeRTOS functions.
            continue
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        sources[unit["source"]] = unit["source_sha256"]
        objects.append(obj)
    linked = OUT / "apollo-main-logger-providers.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "--defsym=g2_log_general_vformat=g2_log_vformat",
                    "-o", str(linked)], check=True)
    before, after = imports(BASE), imports(linked)
    ambient_strings = {"g2_log_process_string", "g2_log_thread_string",
                       "g2_log_time_string"}
    expected = {name for name in before if name.startswith("g2_log_")} - ambient_strings
    if not expected <= before - after:
        raise RuntimeError(f"logger imports retained: {sorted(expected & after)}")
    if after - before:
        raise RuntimeError(f"logger closure introduced imports: {sorted(after - before)}")
    if len(before) != 544 or len(after) != 518:
        raise RuntimeError("Main logger closure count changed")
    receipt = {
        "status": "PASS_MAIN_LOGGER_PROVIDER_SOURCE_COMPOSITION",
        "pinned_logger_receipt": str(PINNED.relative_to(ROOT)),
        "pinned_logger_receipt_sha256": sha(PINNED),
        "base_object": str(BASE.relative_to(ROOT)),
        "base_object_sha256": sha(BASE),
        "sources": sources,
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "imports_resolved": sorted(before - after),
        "imports_added": [],
        "ambient_string_contracts": sorted(ambient_strings & after),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Process, thread, and time strings retain external runtime contracts.",
                   "Native logger transport, formatting edge cases, and hardware behavior remain unqualified.",
                   "Other Main imports and final placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
