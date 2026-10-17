#!/usr/bin/env python3
"""Replay the final thirteen Main object/data bindings from corrected C source."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261016"
FEATURE = BUILD / "main-combined-ram-settings-font-feature-replay/receipt.json"
FINAL = BUILD / "main-ring-descriptor-data-20002c48/receipt.json"
OLD_START = "g2/build/c-firmware/20261016/main-combined-ram-current-replay/239-main-terminal-rx-frame-5ce990.o"
OUT = BUILD / "main-combined-ram-settings-font-final-replay"
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *args, str(path)], text=True).splitlines()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("final replay input changed: " + name)
    return path


def chain():
    by_link = {}
    for path in BUILD.glob("**/receipt.json"):
        try:
            row = json.loads(path.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(row, dict) and row.get("base_object") and row.get("linked_object"):
            key = row["linked_object"]
            if key in by_link:
                raise RuntimeError("duplicate final replay predecessor: " + key)
            by_link[key] = (path, row)
    final = json.loads(FINAL.read_text())
    cursor = final["linked_object"]
    rows = []
    while cursor != OLD_START:
        if cursor not in by_link or len(rows) >= 20:
            raise RuntimeError("incomplete final Main chain: " + cursor)
        path, row = by_link[cursor]
        rows.append((path, row))
        cursor = row["base_object"]
    rows.reverse()
    if len(rows) != 13:
        raise RuntimeError("final Main binding count changed")
    return rows


def main():
    feature = json.loads(FEATURE.read_text())
    if feature["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_FEATURE_REPLAY_C" or \
            feature["stages_replayed"] != 683:
        raise RuntimeError("corrected feature replay changed")
    current = checked(feature["linked_object"], feature["linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    stages = []
    for index, (receipt_path, row) in enumerate(chain(), 1):
        digest = row.get("linked_sha256", row.get("linked_object_sha256"))
        old = checked(row["linked_object"], digest)
        if "object" in row:
            inputs = [checked(row["object"], row["object_sha256"])]
        else:
            value = row.get("objects")
            if not isinstance(value, dict) or not all(
                    isinstance(name, str) and name.endswith(".o") and
                    isinstance(hash_value, str) for name, hash_value in value.items()):
                raise RuntimeError("final binding objects not attributable: " + str(receipt_path))
            inputs = [checked(name, hash_value) for name, hash_value in value.items()]
        new = OUT / f"{index:02d}-{receipt_path.parent.name}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", str(current),
                        *(str(path) for path in inputs), "-o", str(new)], check=True)
        old_u, new_u = names(old, "-u"), names(new, "-u")
        old_d, new_d = names(old, "-g", "--defined-only"), \
                       names(new, "-g", "--defined-only")
        if old_u - new_u != REMOVED or new_u - old_u or \
                new_d - old_d != PROVIDERS or old_d - new_d:
            raise RuntimeError("font repair drift at " + receipt_path.parent.name +
                               f": {old_u-new_u} {new_u-old_u} {new_d-old_d} {old_d-new_d}")
        stages.append({"stage": receipt_path.parent.name,
                       "receipt": str(receipt_path.relative_to(ROOT)),
                       "receipt_sha256": sha(receipt_path),
                       "prior_object": row["linked_object"], "prior_sha256": sha(old),
                       "inputs": {str(path.relative_to(ROOT)): sha(path) for path in inputs},
                       "linked": str(new.relative_to(ROOT)), "linked_sha256": sha(new),
                       "imports_remaining": len(new_u)})
        current = new
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_FINAL_REPLAY_C",
               "feature_receipt": str(FEATURE.relative_to(ROOT)),
               "feature_receipt_sha256": sha(FEATURE),
               "stages": stages, "stages_replayed": len(stages),
               "linked_object": str(current.relative_to(ROOT)),
               "linked_sha256": sha(current),
               "unresolved_after": stages[-1]["imports_remaining"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "settings_extent_bytes": 104,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Current Apollo Main partial-link candidate carries the corrected C font loader, selected initialized RAM, 104-byte settings state and all previous providers. Full firmware source, final RAM map, startup copy and physical operation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], len(stages), receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
