#!/usr/bin/env python3
"""Replay the five early Main stages from the combined C-owned RAM archive."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
RAM_RECEIPT = G2 / "build/c-firmware/20261016/main-registry-ring-connect-ram/receipt.json"
OLD_RECEIPT = G2 / "build/c-firmware/20261014/main-corrected-archive-early-replay/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-combined-ram-early-replay"
NEW_PROVIDERS = {"audio_registry_ring_connect_buffer", "audio_terminal_ui_state_base"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *options, str(path)], text=True).splitlines()
        if line.strip()}


def checked(name, digest):
    path = ROOT / name
    if sha(path) != digest:
        raise RuntimeError(f"upstream artifact changed: {name}")
    return path


def main():
    ram = json.loads(RAM_RECEIPT.read_text())
    if ram["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_AND_RING_RAM_C_ARCHIVE" or \
            set(ram["combined_input_providers_added"]) != NEW_PROVIDERS or \
            ram["combined_input_imports_removed"] != ["audio_registry_ring_connect_buffer"]:
        raise RuntimeError("combined RAM archive receipt changed")
    old = json.loads(OLD_RECEIPT.read_text())
    if old["status"] != "PASS_EXPERIMENTAL_MAIN_CORRECTED_ARCHIVE_EARLY_REPLAY_C" or \
            [row["stage"] for row in old["stages"]] != [
                "cordio", "delay", "event", "power", "smp_rows"]:
        raise RuntimeError("early-stage replay contract changed")
    current = checked(ram["combined_linked_object"], ram["combined_linked_sha256"])
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in old["stages"]:
        baseline = checked(row["new_object"], row["new_sha256"])
        children = [checked(name, digest) for name, digest in row["inputs"].items()]
        linked = OUT / f"apollo-main-combined-{row['stage']}.o"
        subprocess.run(["arm-none-eabi-ld", "-r", *row["link_options"], str(current),
                        *(str(child) for child in children), "-o", str(linked)], check=True)
        before_u, after_u = names(baseline, "-u"), names(linked, "-u")
        before_d = names(baseline, "-g", "--defined-only")
        after_d = names(linked, "-g", "--defined-only")
        removed = before_u & NEW_PROVIDERS
        if before_u - after_u != removed or after_u - before_u or \
                after_d - before_d != NEW_PROVIDERS or before_d - after_d:
            raise RuntimeError(f"RAM replay changed unanticipated symbols at {row['stage']}")
        rows.append({"stage": row["stage"], "baseline": row["new_object"],
                     "baseline_sha256": row["new_sha256"],
                     "linked": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
                     "imports_resolved_vs_baseline": sorted(removed),
                     "imports_remaining": len(after_u),
                     "providers_added_vs_baseline": sorted(NEW_PROVIDERS),
                     "inputs": row["inputs"], "link_options": row["link_options"]})
        current = linked
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_COMBINED_RAM_EARLY_REPLAY_C",
        "combined_ram_receipt": str(RAM_RECEIPT.relative_to(ROOT)),
        "combined_ram_receipt_sha256": sha(RAM_RECEIPT),
        "prior_early_receipt": str(OLD_RECEIPT.relative_to(ROOT)),
        "prior_early_receipt_sha256": sha(OLD_RECEIPT),
        "stages": rows, "linked_object": str(current.relative_to(ROOT)),
        "linked_sha256": sha(current), "unresolved_after": rows[-1]["imports_remaining"],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Five early stages only; root, master, runtime, library, tail and later C bindings remain to replay.",
                   "Symbol parity does not establish final RAM layout, native behavior or hardware operation."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
