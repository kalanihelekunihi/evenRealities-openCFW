#!/usr/bin/env python3
"""Replay combined Main early/root/library-to-tail stages with font and settings fixes."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261016"
START = BUILD / "main-combined-ram-settings-font-archive/receipt.json"
OUT = BUILD / "main-combined-ram-settings-font-core-replay"
GROUPS = ("early", "root", "late")
REMOVED = {"audio_uart_ring_secondary_active"}
PROVIDERS = {"audio_uart_font_primary_active", "audio_uart_font_secondary_active"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError("combined core input changed: " + name)
    return path


def names(path, *options):
    return {row.split()[-1] for row in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()}


def link(path, base, inputs=(), options=()):
    subprocess.run(["arm-none-eabi-ld", "-r", *options, str(base),
                    *(str(item) for item in inputs), "-o", str(path)], check=True)
    return path


def main():
    start = json.loads(START.read_text())
    if start["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_ARCHIVE_C":
        raise RuntimeError("combined archive status changed")
    current = checked(start["linked_object"], start["linked_object_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    groups, sequence = [], 0
    for group in GROUPS:
        prior_path = BUILD / f"main-combined-ram-{group}-replay/receipt.json"
        prior = json.loads(prior_path.read_text())
        rows = []
        for row in prior["stages"]:
            sequence += 1
            old = checked(row["linked"], row["linked_sha256"])
            inputs = [checked(name, digest) for name, digest in row["inputs"].items()]
            options = list(row.get("link_options", [])) + [
                f"--defsym={name}={provider}"
                for name, provider in row.get("aliases", {}).items()]
            extras = {}
            if group == "root" and row["stage"] == "hci_composed":
                old_root = json.loads((G2 / "build/c-firmware/20261014/main-corrected-archive-root-replay/receipt.json").read_text())
                hci = next(item for item in old_root["stages"] if item["stage"] == "hci_composed")
                source = checked(hci["upstream_receipt"], hci["upstream_receipt_sha256"])
                hci_inputs = {Path(name).name: checked(name, digest) for name, digest
                              in json.loads(source.read_text())["objects"].items()}
                current = link(OUT / f"{sequence:03d}-hci-decoder.o", current,
                               [hci_inputs["refresh-hci-decoders.o"]])
                extras[str(current.relative_to(ROOT))] = sha(current)
                current = link(OUT / f"{sequence:03d}-hci-joins.o", current,
                               options=[f"--defsym={name}={provider}"
                                        for name, provider in hci["hci_aliases"].items()])
                extras[str(current.relative_to(ROOT))] = sha(current)
                current = link(OUT / f"{sequence:03d}-hci-vendor.o", current,
                               [hci_inputs["refresh-hci-vendor-complete.o"]])
                extras[str(current.relative_to(ROOT))] = sha(current)
            new = link(OUT / f"{sequence:03d}-{group}-{row['stage']}.o", current,
                       inputs, options)
            old_u, new_u = names(old, "-u"), names(new, "-u")
            old_d, new_d = names(old, "-g", "--defined-only"), \
                           names(new, "-g", "--defined-only")
            if old_u - new_u != REMOVED or new_u - old_u or \
                    new_d - old_d != PROVIDERS or old_d - new_d:
                raise RuntimeError("font repair drift at " + group + "/" + row["stage"] +
                                   f": {old_u-new_u} {new_u-old_u} {new_d-old_d} {old_d-new_d}")
            rows.append({"stage": row["stage"], "prior_object": row["linked"],
                         "prior_sha256": sha(old), "inputs": row["inputs"],
                         "options": options, "intermediate": extras,
                         "linked": str(new.relative_to(ROOT)),
                         "linked_sha256": sha(new), "imports_remaining": len(new_u)})
            current = new
        groups.append({"group": group, "prior_receipt": str(prior_path.relative_to(ROOT)),
                       "prior_receipt_sha256": sha(prior_path), "stages": rows,
                       "linked_object": str(current.relative_to(ROOT)),
                       "linked_sha256": sha(current)})
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_SETTINGS_FONT_CORE_REPLAY_C",
               "archive_receipt": str(START.relative_to(ROOT)),
               "archive_receipt_sha256": sha(START), "groups": groups,
               "stages_replayed": sequence,
               "linked_object": str(current.relative_to(ROOT)),
               "linked_sha256": sha(current),
               "unresolved_after": groups[-1]["stages"][-1]["imports_remaining"],
               "imports_resolved": sorted(REMOVED),
               "providers_added": sorted(PROVIDERS),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Early through tail replay carries all four RAM/settings/font source corrections; post-tail and current feature stages remain."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], sequence, receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
