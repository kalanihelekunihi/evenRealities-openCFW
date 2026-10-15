#!/usr/bin/env python3
"""Integrate the bounded native-compared CMSIS event-wait outer C body."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/event_wait_source_candidate/event_wait.c"
OTA = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/event-wait-results.json"
BASE = G2 / "build/c-firmware/20261014/main-logger-ble-state/apollo-main-logger-ble-state.o"
OUT = G2 / "build/c-firmware/20261014/main-event-wait-outer"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle.get("status") != "PASS_EVENT_WAIT_BOUNDED" or oracle.get("cases") != 288
            or oracle.get("source_sha256") != sha(SOURCE)
            or oracle.get("ota_sha256") != sha(OTA)):
        raise RuntimeError("event-wait native comparison no longer matches current inputs")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "event_wait.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defined = names(obj, "-g", "--defined-only")
    imports = names(obj, "-u")
    if defined != {"audio_event_wait", "osEventFlagsWait"} or imports != {"audio_irq_context", "g2_event_wait_bits"}:
        raise RuntimeError(f"event-wait object contract changed: {defined}, {imports}")
    before = names(BASE, "-u")
    if "audio_event_wait" not in before or "g2_event_wait_bits" in before:
        raise RuntimeError("Apollo Main event-wait imports changed")
    linked = OUT / "apollo-main-event-wait-outer.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_event_wait"} or after - before != {"g2_event_wait_bits"}:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_EVENT_WAIT_OUTER_C",
        "native_oracle": str(ORACLE.relative_to(ROOT)), "native_oracle_sha256": sha(ORACLE),
        "native_cases": oracle["cases"], "official_ota": str(OTA.relative_to(ROOT)),
        "official_ota_sha256": sha(OTA),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Prior 288-case oracle covers only the CMSIS outer body with IRQ and FreeRTOS wait cuts.",
                   "g2_event_wait_bits blocking/waiter behavior remains a live source and native-validation gate.",
                   "Corrected archive replay, whole-image link, and hardware behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
