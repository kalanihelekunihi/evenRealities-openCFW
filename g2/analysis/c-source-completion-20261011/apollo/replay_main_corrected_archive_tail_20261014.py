#!/usr/bin/env python3
"""Finish Apollo replay from corrected archive and attach bounded event wait C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
BASE = BUILD / "main-corrected-archive-runtime-replay/24-main-device-timer-runtime-state.o"
OUT = BUILD / "main-corrected-archive-tail-replay"
HISTORICAL = ("main-input-identity-relink", "main-hub-timer-runtime-state",
              "main-log-runtime-cells", "main-log-buffer-state", "main-logger-ble-state")
REMOVED = {"audio_uart_input_ring", "audio_uart_display_ring",
           "audio_os_message_queue_put", "audio_os_thread_flags_set",
           "audio_input_error_log"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def checked(name, expected):
    path = ROOT / name
    if sha(path) != expected:
        raise RuntimeError(f"source or object changed: {name}")
    return path


def compare(label, old, new, expected_added):
    old_u, new_u = names(old, "-u"), names(new, "-u")
    if old_u - new_u != REMOVED or new_u - old_u != expected_added:
        raise RuntimeError(f"unexpected corrected delta at {label}: {old_u-new_u}, {new_u-old_u}")
    if names(old, "-g", "--defined-only") != names(new, "-g", "--defined-only"):
        raise RuntimeError(f"provider set changed at {label}")
    return len(old_u), len(new_u)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    current = BASE
    records = []
    for index, directory in enumerate(HISTORICAL, 1):
        receipt_path = BUILD / directory / "receipt.json"
        row = json.loads(receipt_path.read_text())
        old = checked(row["linked_object"], row["linked_object_sha256"])
        checked(row["base_object"], row["base_sha256"])
        source = checked(row["source"], row["source_sha256"])
        obj = checked(row["object"], row["object_sha256"])
        target = OUT / f"{index:02d}-{directory}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", str(current), str(obj),
                        "-o", str(target)], check=True)
        if directory == "main-input-identity-relink":
            before, after = names(current, "-u"), names(target, "-u")
            expected = {"audio_uart_input_event_flags", "audio_uart_input_mutex",
                        "audio_uart_input_queue", "audio_uart_input_queue_failure_context",
                        "audio_uart_sync_schedule_queue", "g2_display_ring"}
            if before-after != expected or after-before:
                raise RuntimeError(f"clean input identity import delta changed: {before-after}, {after-before}")
        old_n, new_n = compare(directory, old, target, set())
        records.append({"stage": directory,
                        "upstream_receipt": str(receipt_path.relative_to(ROOT)),
                        "upstream_receipt_sha256": sha(receipt_path),
                        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                        "old_object": row["linked_object"], "old_sha256": sha(old),
                        "input_object": str(obj.relative_to(ROOT)), "input_sha256": sha(obj),
                        "new_object": str(target.relative_to(ROOT)), "new_sha256": sha(target),
                        "old_unresolved": old_n, "new_unresolved": new_n})
        current = target
    for index, directory in enumerate(("main-event-wait-outer", "main-event-wait-workers"),
                                      len(HISTORICAL) + 1):
        receipt_path = BUILD / directory / "receipt.json"
        row = json.loads(receipt_path.read_text())
        old = checked(row["linked_object"], row["linked_object_sha256"])
        if directory == "main-event-wait-outer":
            sources = [checked(row["source"], row["source_sha256"])]
            objects = [checked(row["object"], row["object_sha256"])]
        else:
            sources = [checked(item["source"], item["source_sha256"])
                       for item in row["coverage"]]
            objects = [checked(item["object"], item["object_sha256"])
                       for item in row["coverage"]]
        target = OUT / f"{index:02d}-{directory}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                        *(str(obj) for obj in objects), "-o", str(target)], check=True)
        old_n, new_n = compare(directory, old, target, set())
        records.append({"stage": directory,
                        "upstream_receipt": str(receipt_path.relative_to(ROOT)),
                        "upstream_receipt_sha256": sha(receipt_path),
                        "sources": {str(p.relative_to(ROOT)): sha(p) for p in sources},
                        "old_object": row["linked_object"], "old_sha256": sha(old),
                        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
                        "new_object": str(target.relative_to(ROOT)), "new_sha256": sha(target),
                        "old_unresolved": old_n, "new_unresolved": new_n})
        current = target
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_TAIL_REPLAY_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "stages": records,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": records[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Corrected six-member audio archive and recorded Apollo providers are composed; 367 imports still need source ownership.",
                   "DM row functions compile directly from the refreshed archive member; no weak overlay is linked.",
                   "Final placement, whole-image link, native behavior beyond bounded oracles, and hardware remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(records), records[-1]["old_unresolved"],
          records[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
