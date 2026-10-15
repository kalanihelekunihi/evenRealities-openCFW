#!/usr/bin/env python3
"""Rebuild the FreeRTOS event-group and scheduler source closure for Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-source-refresh2"
BUILD = OUT / "apollo_main"
BASE_RECEIPT = OUT / "main-hci-decoder-composition-receipt.json"
BASE = BUILD / "candidate-hci-composed.o"
FINAL = BUILD / "candidate-scheduler-closure.o"
RECEIPT = OUT / "main-scheduler-event-group-receipt.json"
SOURCES = {
    "event_groups_subset": G2 / "components/foundation/freertos_event_group/event_groups_subset.c",
    "timer_pend_subset": G2 / "components/foundation/freertos_event_group/timer_pend_subset.c",
    "unordered": G2 / "components/foundation/freertos_ready/unordered_unblock.c",
    "resume": G2 / "components/foundation/freertos_resume/tasks_resume.c",
    "tick": G2 / "components/foundation/freertos_tick/tasks_tick.c",
    "critical": G2 / "components/foundation/freertos_daemon/task_critical.c",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_MAIN_HCI_DECODER_SOURCE_COMPOSITION"
    assert base["linked_object_sha256"] == sha(BASE)
    old_receipt = G2 / "build/c-firmware/20261014/main-root-dependencies/event-groups-current-receipt.json"
    old = json.loads(old_receipt.read_text())
    assert old["status"] == "PASS_CURRENT_MAIN_EVENT_GROUPS_COMPILE"
    for row in old["source_units"]:
        assert sha(ROOT / row["source"]) == row["source_sha256"]
    for row in old["compatibility_headers"] + old["pinned_freertos_sources"]:
        assert sha(ROOT / row["path"]) == row["sha256"]
    oracle = old["bounded_oracle"]
    assert sha(ROOT / oracle["path"]) == oracle["sha256"]
    provenance_paths = [G2 / f"components/foundation/{name}/SOURCE_PROVENANCE.json"
                        for name in ("freertos_ready", "freertos_resume", "freertos_tick",
                                     "freertos_daemon")]
    tasks = ROOT / "third-party/upstream/freertos-kernel/tasks.c"
    ready = json.loads(provenance_paths[0].read_text())
    assert ready["upstream_files"][0]["sha256"] == sha(tasks)
    assert ready["projected_functions"]["vTaskRemoveFromUnorderedEventList"]["projection"] == "unordered_unblock.c"
    for path in provenance_paths[1:3]:
        assert json.loads(path.read_text())["upstream_tasks_sha256"] == sha(tasks)
    objects = []
    for label, source in SOURCES.items():
        obj = BUILD / f"refresh-{label}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    assert len(before) == 560 and len(after) == 558
    assert before - after == {"xEventGroupSetBits", "xEventGroupSetBitsFromISR"}
    assert not after - before
    receipt = {
        "status": "PASS_MAIN_EVENT_GROUP_SCHEDULER_SOURCE_CLOSURE",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_event_group_receipt": str(old_receipt.relative_to(ROOT)),
        "prior_event_group_receipt_sha256": sha(old_receipt),
        "provenance": {str(p.relative_to(ROOT)): sha(p) for p in provenance_paths},
        "upstream_tasks": str(tasks.relative_to(ROOT)), "upstream_tasks_sha256": sha(tasks),
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in SOURCES.values()},
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Unordered event-list removal is a source projection using recovered scheduler RAM; native behavior and complete task ABI remain unproved.",
                  "Bounded WSF signal cases do not qualify scheduler, ISR timing, or hardware behavior.",
                  "Other Main imports and final placement remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
