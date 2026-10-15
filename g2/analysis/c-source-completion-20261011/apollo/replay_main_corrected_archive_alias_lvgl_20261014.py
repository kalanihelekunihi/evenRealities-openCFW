#!/usr/bin/env python3
"""Replay vendor aliases, thread audio, delay, NOR and LVGL after clean source."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
BASE = BUILD / "main-corrected-archive-library-replay/apollo-main-corrected-ambiq_image.o"
OUT = BUILD / "main-corrected-archive-alias-lvgl-replay"
REMOVED = {"audio_uart_input_ring", "audio_uart_display_ring",
           "audio_os_message_queue_put", "audio_os_thread_flags_set",
           "audio_input_error_log"}
ADDED = {"audio_uart_sync_schedule_queue", "audio_ble_dm_stack_rows_200738dc"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"upstream object changed: {name}")
    return path


def stage(label, directory, base, objects=(), aliases=None):
    receipt_path = BUILD / directory / "receipt.json"
    evidence = json.loads(receipt_path.read_text())
    old = checked(evidence["linked_object"], evidence["linked_object_sha256"])
    if sha(ROOT / evidence["base_object"]) != evidence.get("base_sha256", evidence.get("base_object_sha256")):
        raise RuntimeError(f"upstream base changed at {label}")
    new = OUT / f"apollo-main-corrected-{label}.o"
    options = [f"--defsym={name}={target}" for name, target in (aliases or {}).items()]
    subprocess.run(["arm-none-eabi-ld", "-r", str(base), *(str(obj) for obj in objects),
                    *options, "-o", str(new)], check=True)
    old_u, new_u = names(old, "-u"), names(new, "-u")
    if old_u - new_u != REMOVED or new_u - old_u != ADDED:
        raise RuntimeError(f"unexpected import delta at {label}: {old_u-new_u}, {new_u-old_u}")
    if names(old, "-g", "--defined-only") != names(new, "-g", "--defined-only"):
        raise RuntimeError(f"provider set changed at {label}")
    row = {"stage": label, "upstream_receipt": str(receipt_path.relative_to(ROOT)),
           "upstream_receipt_sha256": sha(receipt_path),
           "old_object": evidence["linked_object"], "old_sha256": sha(old),
           "new_object": str(new.relative_to(ROOT)), "new_sha256": sha(new),
           "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
           "aliases": aliases or {}, "old_unresolved": len(old_u),
           "new_unresolved": len(new_u)}
    return new, row


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    vendor = json.loads((BUILD / "main-vendor-power-aliases/receipt.json").read_text())
    checked(vendor["source"], vendor["source_sha256"])
    current, row = stage("vendor_power", "main-vendor-power-aliases", BASE,
                         aliases=vendor["aliases"])
    rows.append(row)
    thread = json.loads((BUILD / "main-thread-audio-closure/receipt.json").read_text())
    objects = []
    for unit in thread["source_units"]:
        checked(unit["source"], unit["source_sha256"])
        objects.append(checked(unit["object"], unit["object_sha256"]))
    current, row = stage("thread_audio", "main-thread-audio-closure", current, objects)
    rows.append(row)
    delay = json.loads((BUILD / "main-suspended-delay-assert/receipt.json").read_text())
    checked(delay["source"], delay["source_sha256"])
    current, row = stage("delay_assert", "main-suspended-delay-assert", current,
                         [checked(delay["object"], delay["object_sha256"])])
    rows.append(row)
    nor = json.loads((BUILD / "main-norflash-recorded-aliases/receipt.json").read_text())
    manifest = checked(nor["alias_manifest"], nor["alias_manifest_sha256"])
    alias_map = json.loads(manifest.read_text())["apollo_main"]
    if any(alias_map.get(name) != target for name, target in nor["aliases"].items()):
        raise RuntimeError("NOR alias manifest changed")
    current, row = stage("norflash", "main-norflash-recorded-aliases", current,
                         aliases=nor["aliases"])
    rows.append(row)
    lvgl = json.loads((BUILD / "main-lvgl-label-graph/receipt.json").read_text())
    checked(lvgl["source_audit"], lvgl["source_audit_sha256"])
    checked(lvgl["global_source"], lvgl["global_source_sha256"])
    for unit in lvgl["source_units"]:
        checked(unit["source"], unit["source_sha256"])
    objects = [checked(row["path"], row["sha256"]) for row in lvgl["selected_objects"]]
    current, row = stage("lvgl_label", "main-lvgl-label-graph", current, objects,
                         {"audio_uart_display_lv_root": "lv_global"})
    rows.append(row)
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_ALIAS_LVGL_REPLAY_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "stages": rows,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": rows[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Five later stages replayed; master and runtime stages remain.",
                   "Provider parity and import delta do not prove final placement or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], rows[-1]["old_unresolved"], rows[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
