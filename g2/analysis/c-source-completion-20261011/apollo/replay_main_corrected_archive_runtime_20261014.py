#!/usr/bin/env python3
"""Replay Apollo DM row and runtime C providers from corrected source."""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
BASE = BUILD / "main-corrected-archive-master-replay/50-main-hci-cmd-state.o"
START = "g2/build/c-firmware/20261014/main-hci-cmd-state/apollo-main-hci-cmd-state.o"
END = "g2/build/c-firmware/20261014/main-device-timer-runtime-state/apollo-main-device-timer-runtime-state.o"
OUT = BUILD / "main-corrected-archive-runtime-replay"
REMOVED = {"audio_uart_input_ring", "audio_uart_display_ring",
           "audio_os_message_queue_put", "audio_os_thread_flags_set",
           "audio_input_error_log"}
ADDED = {"audio_uart_sync_schedule_queue"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"upstream artifact changed: {name}")
    return path


def source_unchanged_or_same_object(row, field):
    source = ROOT / row[field]
    digest = row[field + "_sha256"]
    if sha(source) == digest:
        return None
    if field != "source" or "object" not in row:
        raise RuntimeError(f"source text changed without object check: {row[field]}")
    with tempfile.TemporaryDirectory() as directory:
        rebuilt = Path(directory) / "current.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c",
                        str(source), "-o", str(rebuilt)], check=True)
        if sha(rebuilt) != row["object_sha256"]:
            old = ROOT / row["object"]
            old_defs = names(old, "-g", "--defined-only")
            new_defs = names(rebuilt, "-g", "--defined-only")
            deferred = {"audio_ble_encrypt_tick_200742f4"}
            if (source.name != "ancc_cache_cells.c" or new_defs - old_defs != deferred
                    or old_defs - new_defs or not {"audio_ble_ancc_connection_tick"} <= old_defs):
                raise RuntimeError(f"source drift changes compiled object: {row[field]}")
            output = subprocess.check_output(["arm-none-eabi-nm", "-g", str(rebuilt)], text=True)
            addresses = {parts[-1]: parts[0] for line in output.splitlines()
                         if len(parts := line.split()) == 3}
            if addresses["audio_ble_encrypt_tick_200742f4"] != addresses["audio_ble_ancc_connection_tick"]:
                raise RuntimeError("deferred ANCC alias does not share tick storage")
            return {"source": row[field], "recorded_source_sha256": digest,
                    "current_source_sha256": sha(source),
                    "deferred_linker_alias": "audio_ble_encrypt_tick_200742f4=audio_ble_ancc_connection_tick",
                    "pinned_stage_object_sha256": row["object_sha256"]}
    return {"source": row[field], "recorded_source_sha256": digest,
            "current_source_sha256": sha(source),
            "recompiled_object_sha256": row["object_sha256"]}


def chain():
    by_link = {}
    for path in BUILD.glob("**/*receipt*.json"):
        try:
            row = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(row, dict) and row.get("base_object") and row.get("linked_object"):
            key = row["linked_object"]
            if key in by_link:
                raise RuntimeError(f"duplicate receipt for {key}")
            by_link[key] = (path, row)
    result = []
    cursor = END
    while cursor != START:
        if cursor not in by_link:
            raise RuntimeError(f"missing replay predecessor: {cursor}")
        path, row = by_link[cursor]
        result.append((path, row))
        cursor = row["base_object"]
        if len(result) > 100:
            raise RuntimeError("replay predecessor cycle")
    return list(reversed(result))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    current = BASE
    records = []
    previous_historical_link = None
    for index, (receipt_path, row) in enumerate(chain(), 1):
        label = receipt_path.parent.name
        historical_base = ROOT / row["base_object"]
        recorded_base_sha = row.get("base_sha256", row.get("base_object_sha256"))
        if not historical_base.is_file() or not recorded_base_sha:
            raise RuntimeError(f"missing historical base: {label}")
        actual_base_sha = sha(historical_base)
        base_drift = None
        if actual_base_sha != recorded_base_sha:
            if previous_historical_link != row["base_object"]:
                raise RuntimeError(f"unattributed historical base drift: {label}")
            base_drift = {"recorded_sha256": recorded_base_sha,
                          "current_sha256": actual_base_sha,
                          "reason": "verified predecessor was regenerated from its current source object"}
        old = checked(row["linked_object"], row["linked_object_sha256"])
        objects = []
        if "object" in row:
            objects.append(checked(row["object"], row["object_sha256"]))
        if "objects" in row:
            if not isinstance(row["objects"], dict):
                raise RuntimeError(f"unexpected object manifest: {label}")
            objects.extend(checked(p, h) for p, h in row["objects"].items())
        aliases = {}
        if "linker_alias" in row:
            name, provider = row["linker_alias"].split("=", 1)
            aliases[name] = provider
        if "aliases" in row:
            aliases.update(row["aliases"])
        if label == "main-dm-row-relink":
            checked(row["overlay_object"], row["overlay_object_sha256"])
            checked(row["overlay"], row["overlay_sha256"])
            for field in ("source",):
                if field in row:
                    checked(row[field], row[field + "_sha256"])
        if label == "main-encrypt-tick-alias":
            aliases["audio_ble_encrypt_tick_200742f4"] = "audio_ble_ancc_connection_tick"
        if not objects and not aliases and label != "main-dm-row-relink":
            raise RuntimeError(f"no replay input recorded: {label}")
        drift = []
        for field in ("source", "table_source", "alias_user_source"):
            if field in row and field + "_sha256" in row:
                checked_drift = source_unchanged_or_same_object(row, field)
                if checked_drift:
                    drift.append(checked_drift)
        target = OUT / f"{index:02d}-{label}.o"
        base_for_link = current
        if label == "main-dm-row-relink":
            shutil.copyfile(current, target)
        else:
            subprocess.run(["arm-none-eabi-ld", "-r", str(base_for_link),
                            *(str(obj) for obj in objects),
                            *(f"--defsym={name}={provider}" for name, provider in aliases.items()),
                            "-o", str(target)], check=True)
        old_u, new_u = names(old, "-u"), names(target, "-u")
        if old_u - new_u != REMOVED or new_u - old_u != ADDED:
            raise RuntimeError(f"unexpected import delta at {label}: {old_u-new_u}, {new_u-old_u}")
        if names(old, "-g", "--defined-only") != names(target, "-g", "--defined-only"):
            raise RuntimeError(f"provider set changed at {label}")
        records.append({"stage": label, "receipt": str(receipt_path.relative_to(ROOT)),
                        "receipt_sha256": sha(receipt_path),
                        "old_object": row["linked_object"], "old_sha256": sha(old),
                        "new_object": str(target.relative_to(ROOT)), "new_sha256": sha(target),
                        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in objects},
                        "direct_archive_dm_row": label == "main-dm-row-relink",
                        "aliases": aliases, "historical_base_hash_drift": base_drift,
                        "source_text_drift_with_identical_object": drift,
                        "old_unresolved": len(old_u),
                        "new_unresolved": len(new_u)})
        current = target
        previous_historical_link = row["linked_object"]
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_RUNTIME_REPLAY_C",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "stages": records,
        "linked_object": str(current.relative_to(ROOT)), "linked_object_sha256": sha(current),
        "unresolved_after": records[-1]["new_unresolved"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["DM row and runtime replay use the direct source archive member; corrected input identity and later logger waves remain.",
                   "Provider parity and import delta do not prove final placement or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(records), records[-1]["old_unresolved"],
          records[-1]["new_unresolved"], sha(path))


if __name__ == "__main__":
    main()
