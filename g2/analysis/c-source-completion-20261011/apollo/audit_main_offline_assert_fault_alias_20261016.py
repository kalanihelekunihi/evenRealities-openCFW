#!/usr/bin/env python3
"""Pin the shared nonreturning assertion fault boundary in Main C."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-flashdb-print-sink-alias/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-offline-assert-fault-alias"
OBJ = OUT / "candidate.o"
OWNER = G2 / "components/audio/scheduler_delay_candidate/suspended_assert.c"
LINK = G2 / "analysis/c-source-completion-20261011/apollo/main_offline_assert_fault_alias.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines() if line.strip()}


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    # Authenticated 0x454b60 fault arm: call mask, store zero to 0xffffffff, loop.
    expected = bytes.fromhex("a5f1a0fa00205ff0ff310860fee7")
    native = payload[0x454b60-0x438000:0x454b6e-0x438000]
    if native != expected:
        raise RuntimeError(f"native scheduler assertion arm changed: {native.hex()}")
    source = OWNER.read_text()
    if ("audio_mask_save()" not in source or "UINT32_MAX" not in source
            or "for (;;)" not in source or "noreturn" not in source):
        raise RuntimeError("C fatal boundary changed")
    symbols = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", str(OBJ)], text=True).splitlines():
        fields = line.split()
        if fields and fields[-1] in ("audio_delay_scheduler_assert", "offline_assert"):
            symbols[fields[-1]] = fields
    if (set(symbols) != {"audio_delay_scheduler_assert", "offline_assert"} or
            symbols["audio_delay_scheduler_assert"][0] != symbols["offline_assert"][0] or
            undefined(BASE) - undefined(OBJ) != {"offline_assert"} or
            undefined(OBJ) - undefined(BASE) or
            len(undefined(BASE)) != 127 or len(undefined(OBJ)) != 126):
        raise RuntimeError("assertion alias or import reduction changed")
    record = {
        "status": "PASS_BOUNDED_MAIN_SHARED_NONRETURNING_ASSERT_FAULT_ALIAS",
        "stock_payload_sha256": PAYLOAD_SHA,
        "native_fault_arm": "0x454b60..0x454b6d", "native_fault_arm_sha256": hashlib.sha256(native).hexdigest(),
        "owner_source": str(OWNER.relative_to(ROOT)), "owner_source_sha256": sha(OWNER),
        "linker_script": str(LINK.relative_to(ROOT)), "linker_script_sha256": sha(LINK),
        "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
        "candidate_object": str(OBJ.relative_to(ROOT)), "candidate_object_sha256": sha(OBJ),
        "unresolved_before": 127, "unresolved_after": 126,
        "source_complete": False, "flashable": False, "hardware_proof": False,
        "limits": ["This binds the common nonreturning fault boundary; it does not compare every caller's diagnostic prefix or invalid-input branch.",
                   "The invalid-address write is intentionally not executed in an oracle or on hardware.",
                   "The Main image still lacks many executable and initialized-data providers."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["unresolved_after"], sha(receipt))


if __name__ == "__main__":
    main()
