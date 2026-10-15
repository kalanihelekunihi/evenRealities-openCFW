#!/usr/bin/env python3
"""Record bounded stock/C formatter evidence for the selected CASE source."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/case/legacy_default_candidate_20261010/vformat_candidate.c"
FIRMWARE = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_case_vformat_extended.py"
ARCHIVE_RECEIPT = G2 / "analysis/case-source-candidate-round2-20261010/receipt.json"
LTO_RECEIPT = G2 / "analysis/component-goal-20261013/case-wave069-deferred-callable-types/final/receipt.json"
OUT = G2 / "build/c-firmware/20261014/case-vformat-current"
RECEIPT = OUT / "receipt.json"
FW_SHA = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert sha(FIRMWARE) == FW_SHA
    archive = json.loads(ARCHIVE_RECEIPT.read_text())
    lto = json.loads(LTO_RECEIPT.read_text())
    name = str(SOURCE.relative_to(ROOT))
    a, = [row for row in archive["sources"] if row["source"] == name]
    b, = [row for row in lto["sources"] if row["source"] == name]
    assert a["sha256"] == b["source_sha256"] == sha(SOURCE)
    assert archive["unresolved_symbols"] == []
    assert lto["status"] == "PINNED_CLANG_LTO_PROFILE_LINKED"
    assert lto["undefined_symbols"] == "" and len(lto["sources"]) == 401
    assert sha(ROOT / archive["archive"]) == archive["archive_sha256"]
    profile_elf = G2 / "analysis/component-goal-20261013/case-wave069-deferred-callable-types/final/case.elf"
    assert sha(profile_elf) == lto["elf_sha256"]
    run = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    line = run.stdout.strip().splitlines()[-1]
    match = re.fullmatch(r"PASS_VFORMAT_BASIC (\d+) actual_source_formats (\d+) "
                         r"retained_native_caller_formats (\d+) dynamic_assignment_formats (\d+)", line)
    assert match and tuple(map(int, match.groups())) == (1480, 193, 116, 40)
    receipt = {
        "status": "PASS_SELECTED_CASE_VFORMAT_EXTENDED_NATIVE_C",
        "source": name,
        "source_sha256": sha(SOURCE),
        "stock_firmware": str(FIRMWARE.relative_to(ROOT)),
        "stock_firmware_sha256": FW_SHA,
        "oracle": str(ORACLE.relative_to(ROOT)),
        "oracle_sha256": sha(ORACLE),
        "oracle_output": line,
        "cases": 1480,
        "source_formats": 193,
        "retained_native_caller_formats": 116,
        "dynamic_assignment_formats": 40,
        "selected_archive_receipt": str(ARCHIVE_RECEIPT.relative_to(ROOT)),
        "selected_archive_receipt_sha256": sha(ARCHIVE_RECEIPT),
        "linked_profile_receipt": str(LTO_RECEIPT.relative_to(ROOT)),
        "linked_profile_receipt_sha256": sha(LTO_RECEIPT),
        "linked_profile_sources": 401,
        "linked_profile_undefined_symbols": 0,
        "whole_case_image_complete": False,
        "hardware_proof": False,
        "gates": ["Bounded formatter tests do not cover malformed pointers or unbounded width, precision and callback effects.",
                  "Whole native/computed-root coverage, final placement, physical UART and device execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["cases"], sha(RECEIPT))


if __name__ == "__main__":
    main()
