#!/usr/bin/env python3
"""Build the bounded vendor completion provider into current Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-vendor-complete-round436/vendor_complete.c"
PRIOR = SOURCE.parent / "vendor-complete-receipt.json"
ALIAS_RECEIPT = OUT / "hci-source-aliases-receipt.json"
BASE = OUT / "apollo-main-hci-aliases.o"
PROVIDER = OUT / "hci-vendor-complete-current.o"
BOUND = OUT / "apollo-main-hci-vendor-bound.o"
RECEIPT = OUT / "hci-vendor-current-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*argv):
    return subprocess.check_output(argv, cwd=ROOT, text=True)


def defs(path):
    return {line.split()[2] for line in run("arm-none-eabi-nm", "--defined-only", str(path)).splitlines()
            if len(line.split()) == 3}


def imports(path):
    return set(run("arm-none-eabi-nm", "-u", str(path)).split()) - {"U"}


def main():
    previous = json.loads(PRIOR.read_text())
    alias = json.loads(ALIAS_RECEIPT.read_text())
    assert previous["status"] == "completed"
    assert sha(SOURCE) == previous["source_unit"]["source_sha256"]
    for relative, expected in previous["pinned_source_hashes"].items():
        assert sha(ROOT / relative) == expected
    native = ROOT / previous["native_branch_evidence"]["path"]
    assert sha(native) == previous["native_branch_evidence"]["sha256"]
    assert alias["status"] == "PASS_SEVEN_SOURCE_HCI_ALIASES"
    assert sha(BASE) == alias["output_sha256"]
    before = imports(BASE)
    assert len(before) == 647 and "hciCoreVsCmdCmplRcvd" in before
    subprocess.run([
        "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
        "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(PROVIDER),
    ], cwd=ROOT, check=True)
    assert defs(PROVIDER) == {"hciCoreVsCmdCmplRcvd"}
    assert not imports(PROVIDER)
    assert "hciCoreVsCmdCmplRcvd" not in defs(BASE)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(PROVIDER), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = imports(BOUND)
    assert after == before - {"hciCoreVsCmdCmplRcvd"}
    assert defs(BOUND) == defs(BASE) | defs(PROVIDER)
    assert "hciCb" in after
    receipt = {
        "status": "PASS_CURRENT_MAIN_HCI_VENDOR_PROVIDER",
        "base_receipt": str(ALIAS_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(ALIAS_RECEIPT),
        "prior_behavior_receipt": str(PRIOR.relative_to(ROOT)),
        "prior_behavior_receipt_sha256": sha(PRIOR),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "provider_object": str(PROVIDER.relative_to(ROOT)),
        "provider_object_sha256": sha(PROVIDER),
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "resolved": "hciCoreVsCmdCmplRcvd",
        "output": str(BOUND.relative_to(ROOT)),
        "output_sha256": sha(BOUND),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Provider models the native inlined event-type branch, not an independent stock function", "hciCb product RAM allocation remains unresolved", "Final placement and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
