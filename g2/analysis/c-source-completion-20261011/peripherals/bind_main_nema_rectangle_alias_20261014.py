#!/usr/bin/env python3
"""Join two caller names for the native 0x522ae0 Nema rectangle command."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-event-groups.o"
PRIOR = OUT / "event-groups-current-receipt.json"
BOUND = OUT / "apollo-main-nema-rectangle-bound.o"
RECEIPT = OUT / "nema-rectangle-alias-receipt.json"
SOURCE = G2 / "components/main/ambiq_buffer_handlers_candidate_20261014/nema_mask_rectangle.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_nema_mask_rectangle_return_20261014.py"
ALIAS = "display_driver_nema_clear_522ae0"
PROVIDER = "audio_uart_nema_mask_rectangle_522ae0"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def definitions(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2]: (parts[0], parts[1]) for line in output.splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_EVENT_GROUPS_COMPILE"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    base_defs = definitions(BASE)
    assert len(before) == 571 and ALIAS in before and ALIAS not in base_defs
    assert base_defs[PROVIDER][1] == "T"
    result = subprocess.run([sys.executable, str(ORACLE)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    observed = result.stdout.strip().splitlines()[-1]
    assert observed == "PASS_NEMA_MASK_RECTANGLE_NATIVE_RETURN 144"
    subprocess.run(["arm-none-eabi-ld", "-r", "--defsym", f"{ALIAS}={PROVIDER}",
                    str(BASE), "-o", str(BOUND)], cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    defs = definitions(BOUND)
    assert after == before - {ALIAS} and defs[ALIAS] == defs[PROVIDER] == base_defs[PROVIDER]
    receipt = {
        "status": "PASS_CURRENT_MAIN_NEMA_RECTANGLE_ALIAS",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "native_entry": "0x522ae0", "alias": ALIAS, "provider": PROVIDER,
        "provider_source": str(SOURCE.relative_to(ROOT)), "provider_source_sha256": sha(SOURCE),
        "bounded_oracle": {"path": str(ORACLE.relative_to(ROOT)), "sha256": sha(ORACLE),
                           "observed": observed},
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Four-word caller ABI matches; callers ignore the provider's return",
                   "Other GPU/Nema lower calls remain unresolved",
                   "Final placement and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
