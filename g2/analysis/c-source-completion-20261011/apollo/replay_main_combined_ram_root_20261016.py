#!/usr/bin/env python3
"""Replay Main root composition from the combined C-owned RAM archive."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
EARLY = G2 / "build/c-firmware/20261016/main-combined-ram-early-replay/receipt.json"
OLD = G2 / "build/c-firmware/20261014/main-corrected-archive-root-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-root-replay"
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


def link(label, base, objects, options=()):
    target = OUT / f"apollo-main-combined-{label}.o"
    subprocess.run(["arm-none-eabi-ld", "-r", *options, str(base),
                    *(str(obj) for obj in objects), "-o", str(target)], check=True)
    return target


def main():
    early = json.loads(EARLY.read_text())
    old = json.loads(OLD.read_text())
    if early["status"] != "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_EARLY_REPLAY_C" or \
            old["status"] != "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_ROOT_REPLAY_C":
        raise RuntimeError("replay receipts changed")
    current = checked(early["linked_object"], early["linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in old["stages"]:
        baseline = checked(row["new_object"], row["new_sha256"])
        inputs = [checked(name, digest) for name, digest in row["inputs"].items()]
        if row["stage"] == "hci_composed":
            upstream = checked(row["upstream_receipt"], row["upstream_receipt_sha256"])
            source = json.loads(upstream.read_text())
            by_name = {Path(name).name: checked(name, digest)
                       for name, digest in source["objects"].items()}
            decoder = link("hci-decoder", current,
                           [by_name["refresh-hci-decoders.o"]])
            joins = link("hci-joins", decoder, [],
                         [f"--defsym={alias}={provider}"
                          for alias, provider in row["hci_aliases"].items()])
            vendor = link("hci-vendor", joins,
                          [by_name["refresh-hci-vendor-complete.o"]])
            linked = link(row["stage"], vendor, inputs, row["link_options"])
        else:
            linked = link(row["stage"], current, inputs, row["link_options"])
        before_u, after_u = names(baseline, "-u"), names(linked, "-u")
        before_d = names(baseline, "-g", "--defined-only")
        after_d = names(linked, "-g", "--defined-only")
        removed = before_u & ADDED
        if before_u - after_u != removed or after_u - before_u or \
                after_d - before_d != ADDED or before_d - after_d:
            raise RuntimeError(f"unexpected RAM replay delta at {row['stage']}")
        rows.append({"stage": row["stage"], "baseline": row["new_object"],
                     "baseline_sha256": row["new_sha256"],
                     "linked": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
                     "imports_resolved_vs_baseline": sorted(removed),
                     "imports_remaining": len(after_u),
                     "providers_added_vs_baseline": sorted(ADDED),
                     "inputs": row["inputs"], "link_options": row["link_options"]})
        current = linked
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_ROOT_REPLAY_C",
        "early_receipt": str(EARLY.relative_to(ROOT)), "early_receipt_sha256": sha(EARLY),
        "old_root_receipt": str(OLD.relative_to(ROOT)), "old_root_receipt_sha256": sha(OLD),
        "stages": rows, "linked_object": str(current.relative_to(ROOT)),
        "linked_sha256": sha(current), "unresolved_after": rows[-1]["imports_remaining"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Root composition only; master, runtime, libraries, tail and later C bindings remain to replay.",
                   "Symbol parity does not establish stock execution, final RAM layout or hardware behavior."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
