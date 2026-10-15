#!/usr/bin/env python3
"""Bind two vendor call names to source-owned native-address power bodies."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-vendor-power-aliases"
BASE = G2 / "build/c-firmware/20261014/main-ambiq-image-closure/apollo-main-ambiq-image.o"
POWER = G2 / "components/audio/power_vendor_candidate/power.c"
PRIOR = G2 / "build/c-firmware/20261014/main-root-dependencies/pool-state-power-vendor-current-receipt.json"
ALIASES = {
    "audio_ble_vendor_irq_off_47f5b8": "audio_power_peripheral_on",
    "audio_ble_vendor_irq_on_47f7ae": "audio_power_peripheral_off",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {row.split()[-1] for row in text.splitlines() if row.strip()}


def nm_values(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True)
    return {row.split()[-1]: row.split()[0] for row in text.splitlines()
            if len(row.split()) == 3}


def main():
    old = json.loads(PRIOR.read_text())
    if old["status"] != "PASS_EXPERIMENTAL_POOLED_MAIN_APOLLO_POWER_C":
        raise RuntimeError("power C evidence changed")
    row = next(item for item in old["source_units"] if item["source"] == str(POWER.relative_to(ROOT)))
    if sha(POWER) != row["source_sha256"]:
        raise RuntimeError("power C source drift")
    checks = {item["output"] for item in old["bounded_native_checks"]}
    if not {"PASS_POWER_ENABLE_CONNECTED 56", "PASS_POWER_DISABLE_WAIT_ENTRY 14"} <= checks:
        raise RuntimeError("bounded native power checks missing")
    before = imports(BASE)
    if not set(ALIASES) <= before:
        raise RuntimeError("vendor power imports changed")
    values = nm_values(BASE)
    for provider in ALIASES.values():
        if provider not in values:
            raise RuntimeError(f"C power provider absent: {provider}")
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / "apollo-main-vendor-power-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                    *(f"--defsym={name}={provider}" for name, provider in ALIASES.items()),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if (len(before), len(after)) != (497, 495) or before - after != set(ALIASES) or after - before:
        raise RuntimeError("vendor power aliases changed import set")
    values = nm_values(linked)
    for alias, provider in ALIASES.items():
        if values.get(alias) != values.get(provider):
            raise RuntimeError(f"vendor alias differs from C address: {alias}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_VENDOR_POWER_C_ALIASES",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "source": str(POWER.relative_to(ROOT)), "source_sha256": sha(POWER),
        "power_receipt": str(PRIOR.relative_to(ROOT)),
        "power_receipt_sha256": sha(PRIOR),
        "aliases": ALIASES,
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Bounded native checks do not qualify every power transition.",
                   "Hardware rail/IRQ timing and final Main placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
