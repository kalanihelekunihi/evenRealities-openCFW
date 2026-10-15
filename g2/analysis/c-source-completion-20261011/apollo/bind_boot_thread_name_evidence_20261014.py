#!/usr/bin/env python3
"""Tie native thread-name path evidence to the selected bootloader C build."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OLD = G2 / "build/c-firmware/20261013/root-boot-gate-refresh-round447-final/apollo_bootloader"
OUT = G2 / "build/c-firmware/20261014/boot-thread-name-current"
SOURCE = G2 / "components/bootloader/thread_creation/thread_name_getter.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_thread_name_native_20261014.py"
RESULT = ORACLE.with_name("boot-thread-name-native-results.json")
INVENTORY = OLD / "objects/inventory.json"
BOUND = OLD / "resident-rom-bound.o"
BOUND_RECEIPT = OLD / "resident-rom-bound.o.receipt.json"
OBJECT = OUT / "thread-name.o"
RECEIPT = OUT / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inventory = json.loads(INVENTORY.read_text())
    selected = [row for row in inventory["units"] if row["source"] == str(SOURCE.relative_to(ROOT))]
    assert len(selected) == 1 and selected[0]["status"] == "selected"
    assert selected[0]["defined"] == {"opencfw_boot_thread_name_get": "T"}
    assert inventory["global_weak_providers"]["opencfw_boot_thread_name_get"]["source"] == selected[0]["source"]
    prior = json.loads(BOUND_RECEIPT.read_text())
    assert prior["output_sha256"] == sha(BOUND) and prior["output_unresolved"] == []
    assert "opencfw_boot_thread_name_get" in names(BOUND, "-g", "--defined-only")
    output = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert output.stdout.strip().splitlines()[-1] == "PASS_BOOT_THREAD_NAME_NATIVE_BOUNDED 15"
    oracle = json.loads(RESULT.read_text())
    assert oracle["status"] == "PASS_BOOT_THREAD_NAME_NATIVE_BOUNDED"
    assert oracle["fatal_path_events"] == [["mask"], ["store_intent", 0xffffffff, 0]]
    assert oracle["source_sha256"] == sha(SOURCE)
    assert oracle["native_body_sha256"] == "ef653d1c39b35cde0a187c605a8b15d9b9204ee77c1067fdd4c848f99f964fd6"
    argv = list(selected[0]["compiler"])
    argv[argv.index("-o") + 1] = str(OBJECT)
    source_sha = sha(SOURCE)
    subprocess.run(argv, cwd=ROOT, check=True, capture_output=True)
    assert sha(SOURCE) == source_sha
    assert names(OBJECT, "-g", "--defined-only") == {"opencfw_boot_thread_name_get"}
    receipt = {
        "status": "PASS_CURRENT_BOOT_THREAD_NAME_BOUNDED_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": source_sha,
        "object": str(OBJECT.relative_to(ROOT)), "object_sha256": sha(OBJECT),
        "selected_inventory": str(INVENTORY.relative_to(ROOT)),
        "selected_inventory_sha256": sha(INVENTORY),
        "bound_bootloader": str(BOUND.relative_to(ROOT)), "bound_bootloader_sha256": sha(BOUND),
        "bound_bootloader_receipt": str(BOUND_RECEIPT.relative_to(ROOT)),
        "bound_bootloader_receipt_sha256": sha(BOUND_RECEIPT),
        "native_body_sha256": oracle["native_body_sha256"],
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "result": str(RESULT.relative_to(ROOT)), "result_sha256": sha(RESULT),
                           "returning_cases": oracle["cases"]},
        "source_complete": False, "full_payload_linked": False,
        "limits": oracle["limits"] + ["Selected bootloader still lacks whole-image source and placement proof"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
