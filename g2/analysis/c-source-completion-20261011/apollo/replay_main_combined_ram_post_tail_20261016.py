#!/usr/bin/env python3
"""Replay all recorded post-tail C stages from combined RAM source."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
TAIL = G2 / "build/c-firmware/20261016/main-combined-ram-late-replay/receipt.json"
HISTORICAL = G2 / "build/c-firmware/20261014/main-post-tail-c-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-post-tail-replay"
COUNT = 444
ADDED = {"audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"artifact changed: {name}")
    return path


def names(path, *options):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()
        if line.strip()}


def main():
    tail = json.loads(TAIL.read_text())
    old = json.loads(HISTORICAL.read_text())
    if tail["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_LATE_REPLAY_C" or \
            old["status"] != "PASS_EXPERIMENTAL_MAIN_POST_TAIL_C_REPLAY" or \
            len(old["stages"]) < COUNT:
        raise RuntimeError("post-tail replay input changed")
    current = checked(tail["linked_object"], tail["linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, row in enumerate(old["stages"][:COUNT], 1):
        baseline = checked(row["linked_object"], row["linked_sha256"])
        evidence = json.loads(checked(row["receipt"], row["receipt_sha256"]).read_text())
        objects = []
        if "object" in evidence:
            objects.append(checked(evidence["object"], evidence["object_sha256"]))
        if "objects" in evidence:
            if not isinstance(evidence["objects"], list):
                raise RuntimeError(f"unexpected object list: {row['stage']}")
            objects.extend(checked(item["path"], item["sha256"])
                           for item in evidence["objects"])
        if not objects and "sources" in evidence and isinstance(evidence["sources"], list):
            for source_index, item in enumerate(evidence["sources"]):
                digest = item.get("object_sha256")
                if digest is None and isinstance(evidence.get("object_sha256"), list):
                    digest = evidence["object_sha256"][source_index]
                if digest is None:
                    raise RuntimeError(f"unrecorded source object: {row['stage']}")
                obj = (ROOT / row["receipt"]).parent / (Path(item["path"]).stem + ".o")
                if sha(obj) != digest:
                    raise RuntimeError(f"source object changed: {obj}")
                objects.append(obj)
        if not objects and "object_sha256" in evidence:
            directory = (ROOT / row["receipt"]).parent
            matches = [path for path in directory.glob("*.o")
                       if sha(path) == evidence["object_sha256"]]
            if len(matches) != 1:
                raise RuntimeError(f"object hash not unique: {row['stage']}")
            objects.append(matches[0])
        for extra_key in ("class_object_sha256", "table_object_sha256"):
            if extra_key in evidence:
                directory = (ROOT / row["receipt"]).parent
                matches = [path for path in directory.glob("*.o")
                           if sha(path) == evidence[extra_key]]
                if len(matches) != 1:
                    raise RuntimeError(f"extra object missing or ambiguous: {row['stage']}")
                objects.append(matches[0])
        aliases = evidence.get("same_entry_aliases", {})
        if "alias_target" in evidence:
            owned = evidence["source_owned_symbols"]
            if len(owned) != 1:
                raise RuntimeError(f"ambiguous storage alias: {row['stage']}")
            aliases = {owned[0]: evidence["alias_target"]}
        if row["stage"] == "main-lvgl-runtime-state":
            contracts = evidence["native_contracts"]
            aliases = {name: f"audio_uart_display_lv_state+{cell['offset_from_root']}"
                       for name, cell in contracts.items()
                       if name != "audio_uart_display_lv_state"}
        target = OUT / f"{index:02d}-{row['stage']}.o"
        if not objects and not aliases:
            if evidence["imports_resolved"] or evidence["imports_added"] or \
                    not evidence["status"].endswith("ALREADY_C_OWNED"):
                raise RuntimeError(f"missing replay inputs: {row['stage']}")
            shutil.copyfile(current, target)
        else:
            subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                            *(str(obj) for obj in objects),
                            *(f"--defsym={name}={provider}"
                              for name, provider in aliases.items()),
                            "-o", str(target)], check=True)
        before_u, after_u = names(baseline, "-u"), names(target, "-u")
        before_d = names(baseline, "-g", "--defined-only")
        after_d = names(target, "-g", "--defined-only")
        removed = before_u & ADDED
        if before_u - after_u != removed or after_u - before_u or \
                after_d - before_d != ADDED or before_d - after_d:
            raise RuntimeError(f"unexpected RAM replay delta at {row['stage']}: "
                               f"imports {before_u-after_u}, {after_u-before_u}; "
                               f"providers {after_d-before_d}, {before_d-after_d}")
        rows.append({"stage": row["stage"], "historical_receipt": row["receipt"],
                     "historical_receipt_sha256": row["receipt_sha256"],
                     "baseline": row["linked_object"], "baseline_sha256": row["linked_sha256"],
                     "linked": str(target.relative_to(ROOT)), "linked_sha256": sha(target),
                     "inputs": {str(obj.relative_to(ROOT)): sha(obj) for obj in objects},
                     "aliases": aliases, "imports_resolved_vs_baseline": sorted(removed),
                     "imports_remaining": len(after_u),
                     "providers_added_vs_baseline": sorted(ADDED)})
        current = target
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_POST_TAIL_REPLAY_C",
        "tail_receipt": str(TAIL.relative_to(ROOT)), "tail_receipt_sha256": sha(TAIL),
        "historical_post_tail_receipt": str(HISTORICAL.relative_to(ROOT)),
        "historical_post_tail_receipt_sha256": sha(HISTORICAL),
        "stages": rows, "stage_count": len(rows),
        "linked_object": str(current.relative_to(ROOT)), "linked_sha256": sha(current),
        "unresolved_after": rows[-1]["imports_remaining"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Post-tail C stages are replayed; later October 16 bindings still require a combined-archive replay.",
                   "Provider/import parity does not prove stock execution, final RAM layout or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], receipt["stage_count"], receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
