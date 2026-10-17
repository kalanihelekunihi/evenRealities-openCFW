#!/usr/bin/env python3
"""Replay current Main source chain with C-relocated locale callbacks."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261016"
START = BUILD / "main-locale-relocatable-archive/receipt.json"
CORE = BUILD / "main-combined-ram-settings-font-core-replay/receipt.json"
FEATURE = BUILD / "main-combined-ram-settings-font-feature-replay/receipt.json"
FINAL = BUILD / "main-combined-ram-settings-font-final-replay/receipt.json"
OUT = BUILD / "main-locale-relocatable-current-replay"
REMOVED = {"audio_uart_ring_locale_dispatch_200044c0"}
PROVIDERS = {"audio_uart_ring_locale_dispatch_200044c0",
             "audio_uart_locale_ascii_space_4d4384",
             "audio_uart_locale_ascii_lower_4d4398"}
EXPECTED_START_STATUS = "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_ARCHIVE_C"
RESULT_STATUS = "PASS_EXPERIMENTAL_MAIN_LOCALE_RELOCATABLE_CURRENT_REPLAY_C"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("locale replay input changed: " + name)
    return path


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def link(target, base, inputs=(), options=()):
    subprocess.run(["arm-none-eabi-ld", "-r", *options, str(base),
                    *(str(path) for path in inputs), "-o", str(target)], check=True)
    return target


def main():
    source = json.loads(START.read_text())
    if source["status"] != EXPECTED_START_STATUS:
        raise RuntimeError("locale archive status changed")
    current = checked(source["linked_object"], source["linked_object_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = []
    prior_receipts = []
    count = 0
    for group, receipt_path in (("core", CORE), ("feature", FEATURE), ("final", FINAL)):
        prior = json.loads(receipt_path.read_text())
        prior_receipts.append({"path": str(receipt_path.relative_to(ROOT)),
                               "sha256": sha(receipt_path)})
        stage_groups = prior["groups"] if group != "final" else [{"group": "final",
                                                                    "stages": prior["stages"]}]
        for segment in stage_groups:
            for row in segment["stages"]:
                count += 1
                old = checked(row["linked"], row["linked_sha256"])
                input_rows = row["inputs"]
                inputs = [checked(name, digest) for name, digest in input_rows.items()]
                options = row.get("options")
                if options is None:
                    options = [f"--defsym={name}={provider}"
                               for name, provider in row.get("aliases", {}).items()]
                if "receipt" in row:
                    checked(row["receipt"], row["receipt_sha256"])
                if group == "core" and segment["group"] == "root" and \
                        row["stage"] == "hci_composed":
                    old_root_path = G2 / "build/c-firmware/20261014/main-corrected-archive-root-replay/receipt.json"
                    old_root = json.loads(old_root_path.read_text())
                    hci = next(item for item in old_root["stages"]
                               if item["stage"] == "hci_composed")
                    hci_source = checked(hci["upstream_receipt"],
                                         hci["upstream_receipt_sha256"])
                    hci_inputs = {Path(name).name: checked(name, digest)
                                  for name, digest in json.loads(hci_source.read_text())["objects"].items()}
                    current = link(OUT / f"{count:03d}-hci-decoder.o", current,
                                   [hci_inputs["refresh-hci-decoders.o"]])
                    current = link(OUT / f"{count:03d}-hci-joins.o", current,
                                   options=[f"--defsym={name}={provider}"
                                            for name, provider in hci["hci_aliases"].items()])
                    current = link(OUT / f"{count:03d}-hci-vendor.o", current,
                                   [hci_inputs["refresh-hci-vendor-complete.o"]])
                target = OUT / f"{count:03d}-{group}-{segment['group']}-{row['stage']}.o"
                if not inputs and not options:
                    shutil.copyfile(current, target)
                else:
                    current = link(target, current, inputs, options)
                old_u, new_u = names(old, "-u"), names(target, "-u")
                old_d, new_d = names(old, "-g", "--defined-only"), \
                               names(target, "-g", "--defined-only")
                if old_u - new_u != REMOVED & old_u or new_u - old_u or \
                        new_d - old_d != PROVIDERS or old_d - new_d:
                    raise RuntimeError("locale replay drift at " + row["stage"] +
                                       f": {old_u-new_u} {new_u-old_u} "
                                       f"{new_d-old_d} {old_d-new_d}")
                evidence.append({"stage": row["stage"], "group": group,
                                 "segment": segment["group"],
                                 "prior_object": row["linked"],
                                 "prior_sha256": sha(old), "inputs": input_rows,
                                 "options": options,
                                 "linked": str(target.relative_to(ROOT)),
                                 "linked_sha256": sha(target),
                                 "imports_remaining": len(new_u)})
                current = target
    if count != 801:
        raise RuntimeError("locale replay stage count changed")
    receipt = {"status": RESULT_STATUS,
               "archive_receipt": str(START.relative_to(ROOT)),
               "archive_receipt_sha256": sha(START),
               "prior_receipts": prior_receipts,
               "stages": evidence, "stages_replayed": count,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_sha256": sha(current),
               "unresolved_after": evidence[-1]["imports_remaining"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "settings_extent_bytes": 104,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Current Main partial link now uses C callbacks in the two accessed locale slots. Remaining stock pointer fields, table mutation, other imports and whole-image gates remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], count, receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
