#!/usr/bin/env python3
"""Rebind recorded native-address NOR flash names in current C Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261014/main-suspended-delay-assert/apollo-main-suspended-delay.o"
PRIOR = G2 / "build/c-firmware/20261014/main-root-dependencies/pool-state-norflash-remaining-current-receipt.json"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
OUT = G2 / "build/c-firmware/20261014/main-norflash-recorded-aliases"
ALIASES = {
    "g2_norflash_diagnostic_4733ee": "g2_log_transport_queue_failure",
    "g2_norflash_scheduler_state_44906c": "audio_uart_ring_kernel_state",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def values(path):
    rows = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only",
                                    str(path)], text=True)
    return {parts[2]: parts[0] for line in rows.splitlines()
            if len(parts := line.split()) == 3}


def main():
    prior = json.loads(PRIOR.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if prior["status"] != "PASS_POOLED_MAIN_NORFLASH_RECORDED_ALIASES":
        raise RuntimeError("prior alias receipt changed")
    if any(prior["aliases"].get(alias) != provider or
           manifest["apollo_main"].get(alias) != provider
           for alias, provider in ALIASES.items()):
        raise RuntimeError("recorded alias mapping changed")
    before = names(BASE, "-u")
    defined = values(BASE)
    if not set(ALIASES) <= before or not set(ALIASES.values()) <= defined.keys():
        raise RuntimeError("current Main symbols changed")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "apollo-main-norflash-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(f"--defsym={alias}={provider}" for alias, provider in ALIASES.items()),
                    "-o", str(linked)], check=True)
    after = names(linked, "-u")
    bound = values(linked)
    if len(before) != 484 or len(after) != 482 or before - after != set(ALIASES) or after - before:
        raise RuntimeError("unexpected Main import delta")
    if any(bound.get(alias) != bound.get(provider) for alias, provider in ALIASES.items()):
        raise RuntimeError("alias/provider address mismatch")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_NORFLASH_RECORDED_C_ALIASES",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "prior_receipt": str(PRIOR.relative_to(ROOT)), "prior_receipt_sha256": sha(PRIOR),
        "alias_manifest": str(MANIFEST.relative_to(ROOT)), "alias_manifest_sha256": sha(MANIFEST),
        "aliases": ALIASES, "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["Prior address and source identity evidence is reused; this pass checks current symbol binding.",
                   "NOR flash runtime and final Main placement remain unqualified."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
