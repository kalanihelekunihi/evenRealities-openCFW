#!/usr/bin/env python3
"""Replay LittleFS, logger, FreeType and jump C atop the corrected Main root."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
BASE = BUILD / "main-corrected-archive-root-replay/apollo-main-corrected-scheduler.o"
OUT = BUILD / "main-corrected-archive-library-replay"
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


def link(label, base, objects, aliases=None):
    path = OUT / f"apollo-main-corrected-{label}.o"
    options = [f"--defsym={key}={value}" for key, value in (aliases or {}).items()]
    subprocess.run(["arm-none-eabi-ld", "-r", str(base),
                    *(str(p) for p in objects), *options, "-o", str(path)], check=True)
    return path


def stage(label, receipt_path, base, objects, aliases=None):
    evidence = json.loads(receipt_path.read_text())
    old = checked(evidence["linked_object"], evidence["linked_object_sha256"])
    new = link(label, base, objects, aliases)
    old_u, new_u = names(old, "-u"), names(new, "-u")
    if old_u - new_u != REMOVED or new_u - old_u != ADDED:
        raise RuntimeError(f"unexpected import delta at {label}: {old_u-new_u}, {new_u-old_u}")
    if names(old, "-g", "--defined-only") != names(new, "-g", "--defined-only"):
        raise RuntimeError(f"provider set changed at {label}")
    return new, {"stage": label, "upstream_receipt": str(receipt_path.relative_to(ROOT)),
                 "upstream_receipt_sha256": sha(receipt_path),
                 "old_object": evidence["linked_object"], "old_sha256": sha(old),
                 "new_object": str(new.relative_to(ROOT)), "new_sha256": sha(new),
                 "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
                 "aliases": aliases or {}, "old_unresolved": len(old_u),
                 "new_unresolved": len(new_u)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    current = BASE
    for label, directory in (("littlefs", "main-littlefs-provider-closure"),
                             ("logger", "main-logger-provider-closure")):
        receipt_path = BUILD / directory / "receipt.json"
        receipt = json.loads(receipt_path.read_text())
        objects = [checked(p, h) for p, h in receipt["objects"].items()]
        aliases = {"g2_log_general_vformat": "g2_log_vformat"} if label == "logger" else None
        current, row = stage(label, receipt_path, current, objects, aliases)
        records.append(row)
    freetype_receipt = BUILD / "main-freetype-source-closure/receipt.json"
    freetype = json.loads(freetype_receipt.read_text())
    prior = BUILD / "main-root-dependencies"
    ft_objects = []
    for name in ("freetype-modules-current-receipt.json", "freetype-base-current-receipt.json"):
        receipt = json.loads((prior / name).read_text())
        if receipt["freetype_submodule_commit"] != "86bc8a95056c97a810986434a3f268cbe67f2902":
            raise RuntimeError("FreeType revision changed")
        for unit in receipt["source_units"]:
            checked(unit["source"], unit["source_sha256"])
            ft_objects.append(checked(unit["object"], unit["object_sha256"]))
    gzip = json.loads((prior / "freetype-gzip-current-receipt.json").read_text())
    checked(gzip["source"], gzip["source_sha256"])
    ft_objects.append(checked(gzip["object"], gzip["object_sha256"]))
    aliases = freetype["aliases"]
    alias_manifest = checked(freetype["alias_manifest"], freetype["alias_manifest_sha256"])
    mapping = json.loads(alias_manifest.read_text())["apollo_main"]
    if any(mapping.get(k) != v for k, v in aliases.items()):
        raise RuntimeError("FreeType alias manifest changed")
    libc_objects = [checked(p, h) for p, h in freetype["portable_libc_objects"].items()]
    current, row = stage("freetype", freetype_receipt, current,
                         ft_objects + libc_objects, aliases)
    records.append(row)
    jump_receipt = BUILD / "main-freetype-source-closure/jump-c-receipt.json"
    jump = json.loads(jump_receipt.read_text())
    checked(jump["source"], jump["source_sha256"])
    current, row = stage("jump", jump_receipt, current,
                         [checked(jump["c_object"], jump["c_object_sha256"])])
    records.append(row)
    for label, directory in (("ambiq_leaves", "main-ambiq-leaf-closure"),
                             ("transform_area", "main-transform-area-closure"),
                             ("ambiq_buffer", "main-ambiq-buffer-closure"),
                             ("ambiq_image", "main-ambiq-image-closure")):
        receipt_path = BUILD / directory / "receipt.json"
        evidence = json.loads(receipt_path.read_text())
        objects = [checked(p, h) for p, h in evidence["objects"].items()]
        aliases = ({"display_driver_nema_clear_522ae0":
                    "audio_uart_nema_mask_rectangle_522ae0"}
                   if label == "ambiq_buffer" else None)
        current, row = stage(label, receipt_path, current, objects, aliases)
        records.append(row)
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_LIBRARY_AMBIQ_REPLAY_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "stages": records,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": records[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Replay covers eight library and Ambiq stages; later Apollo composition stages remain.",
                   "Provider parity and import delta do not establish native behavior or placement."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], records[-1]["old_unresolved"], records[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
