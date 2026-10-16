#!/usr/bin/env python3
"""Replay early Apollo Main composition from the corrected source archive."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OLD = G2 / "build/c-firmware/20261014/main-root-source-refresh2"
INPUT = G2 / "build/c-firmware/20261016/main-settings-ram-archive-refresh/candidate-input-settings-ram-corrected.o"
RECEIPT = OLD / "main-source-refresh-receipt.json"
OUT = G2 / "build/c-firmware/20261014/main-corrected-archive-early-replay"
REMOVED = {"audio_uart_input_ring", "audio_uart_display_ring",
           "audio_os_message_queue_put", "audio_os_thread_flags_set",
           "audio_input_error_log"}
ADDED = {"audio_uart_sync_schedule_queue", "audio_ble_dm_stack_rows_200738dc"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def checked_objects(rows):
    paths = []
    for name, expected in rows.items():
        path = ROOT / name
        if sha(path) != expected:
            raise RuntimeError(f"upstream object changed: {name}")
        paths.append(path)
    return paths


def main():
    original = json.loads(RECEIPT.read_text())
    if sha(ROOT / original["combined_object"]) != original["combined_object_sha256"]:
        raise RuntimeError("original combined root changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stages = [
        ("cordio", original["cordio_linked_object"], checked_objects(original["cordio_objects"]), []),
        ("delay", original["delay_linked_object"], [],
         ["--defsym=actual_itcm_delay=audio_itcm_delay_iterations"]),
        ("event", original["hci_event_linked_object"],
         checked_objects({original["hci_event_object"]: original["hci_event_object_sha256"]}), []),
        ("power", original["power_linked_object"], checked_objects(original["power_objects"]), []),
        ("smp_rows", original["smp_rows_linked_object"],
         checked_objects({original["smp_rows_object"]: original["smp_rows_object_sha256"]}), []),
    ]
    current = INPUT
    records = []
    for label, old_name, objects, options in stages:
        old = ROOT / old_name
        new = OUT / f"apollo-main-corrected-{label}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", *options, str(current),
                        *(str(obj) for obj in objects), "-o", str(new)], check=True)
        old_u, new_u = names(old, "-u"), names(new, "-u")
        if old_u - new_u != REMOVED or new_u - old_u != ADDED:
            raise RuntimeError(f"unexpected corrected import delta at {label}: {old_u-new_u}, {new_u-old_u}")
        if names(old, "-g", "--defined-only") != names(new, "-g", "--defined-only"):
            raise RuntimeError(f"provider set changed at {label}")
        records.append({"stage": label, "old_object": old_name, "old_sha256": sha(old),
                        "new_object": str(new.relative_to(ROOT)), "new_sha256": sha(new),
                        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
                        "link_options": options, "old_unresolved": len(old_u),
                        "new_unresolved": len(new_u)})
        current = new
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_EARLY_REPLAY_C",
        "upstream_receipt": str(RECEIPT.relative_to(ROOT)), "upstream_receipt_sha256": sha(RECEIPT),
        "corrected_root": str(INPUT.relative_to(ROOT)), "corrected_root_sha256": sha(INPUT),
        "stages": records,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": records[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Early five-stage replay only; later root and Apollo composition stages remain to replay.",
                   "Provider-set parity and import delta do not prove native behavior or image placement."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], records[-1]["old_unresolved"], records[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
