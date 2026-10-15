#!/usr/bin/env python3
"""Bind the stock Thumb HCI registration pointer to the radio GPIO callback."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-boot-logs-current-receipt.json"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_radio_boot.c"
CALLBACK = ROOT / "g2/components/foundation/radio_gpio/radio_gpio.c"
VERIFIER = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/verify_ble_hci_radio_boot.py"
OUTPUT = OUT / "apollo-main-pool-state-hci-register-callback-bound.o"
RECEIPT = OUT / "pool-state-hci-register-callback-current-receipt.json"
IMPORT = "audio_ble_hci_boot_register_source"
PROVIDER = "opencfw_radio_gpio_callback"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, option):
    data = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in data.splitlines() if line.split()}


def values(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        return {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}


def main():
    base = json.loads(BASE.read_text())
    assert base["unresolved_after"] == 422
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    before = names(prior, "-u")
    assert IMPORT in before and PROVIDER in names(prior, "--defined-only")
    comparison = subprocess.run(["/tmp/opencfw-oracle-venv/bin/python", str(VERIFIER)],
                                check=True, capture_output=True, text=True)
    assert len(comparison.stdout.splitlines()) == 5
    assert all(line.startswith("PASS ") for line in comparison.stdout.splitlines())
    subprocess.run(["arm-none-eabi-ld", "-r",
                    f"--defsym={IMPORT}={PROVIDER}+1", str(prior),
                    "-o", str(OUTPUT)], check=True)
    syms = values(OUTPUT)
    assert syms[IMPORT] == syms[PROVIDER] and syms[IMPORT] & 1 == 1
    after = names(OUTPUT, "-u")
    assert before - after == {IMPORT} and after - before == set()
    assert len(before) == 422 and len(after) == 421
    receipt = {
        "status": "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_REGISTER_CALLBACK_C",
        "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
        "corrected_caller": str(SOURCE.relative_to(ROOT)), "corrected_caller_sha256": sha(SOURCE),
        "callback_source": str(CALLBACK.relative_to(ROOT)), "callback_source_sha256": sha(CALLBACK),
        "bounded_verifier": str(VERIFIER.relative_to(ROOT)), "bounded_verifier_sha256": sha(VERIFIER),
        "bounded_results": comparison.stdout.splitlines(),
        "stock_thumb_pointer": "0x4b4a99", "alias": f"{IMPORT}={PROVIDER}+1",
        "linked_alias_thumb_value": hex(syms[IMPORT]),
        "imports_resolved": [IMPORT], "imports_added": [],
        "unresolved_before": len(before), "unresolved_after": len(after),
        "linked_object": str(OUTPUT.relative_to(ROOT)), "linked_sha256": sha(OUTPUT),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The five bounded boot scenarios compare callback pointer identity and selected child calls; whole-image placement and physical radio IRQ behavior remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
