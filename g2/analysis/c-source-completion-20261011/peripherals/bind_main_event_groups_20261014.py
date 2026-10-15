#!/usr/bin/env python3
"""Bind pinned FreeRTOS event-set and deferred ISR source bodies into Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-thread-audio-lowers.o"
PRIOR = OUT / "thread-audio-lowers-current-receipt.json"
BOUND = OUT / "apollo-main-event-groups.o"
RECEIPT = OUT / "event-groups-current-receipt.json"
SOURCE_DIR = G2 / "components/foundation/freertos_event_group"
STEMS = ("event_groups_subset", "timer_pend_subset")
HEADERS = ("event_group.h", "event_group_compat.h")
PINNED = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/FreeRTOSv10.5.1/Source"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nm(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3
            and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_THREAD_AUDIO_LOWERS_COMPILE"
    assert sha(BASE) == prior["output_sha256"]
    before = nm(BASE, "-u")
    assert len(before) == 573
    wanted = {"xEventGroupSetBits", "xEventGroupSetBitsFromISR"}
    assert wanted <= before
    objects = []
    rows = []
    seen = defined(BASE)
    for stem in STEMS:
        source = SOURCE_DIR / (stem + ".c")
        obj = OUT / (stem + "-current.o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-I", str(SOURCE_DIR),
                        "-c", str(source), "-o", str(obj)], cwd=ROOT, check=True)
        names = defined(obj)
        assert names and not names & seen, (stem, names & seen)
        seen |= names
        objects.append(obj)
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                     "defined": sorted(names)})
    assert wanted <= seen and "xTimerPendFunctionCallFromISR" in seen
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = nm(BOUND, "-u")
    assert defined(BOUND) == seen
    assert before - after == wanted and not after - before and len(after) == 571
    oracle = G2 / "analysis/c-source-completion-20261011/peripherals/verify_ble_wsf_os_signal_native.py"
    result = subprocess.run([sys.executable, str(oracle)], cwd=ROOT,
                            text=True, capture_output=True, check=True)
    assert result.stdout.strip().splitlines()[-1] == "PASS_BLE_WSF_OS_SIGNAL_NATIVE 16"
    receipt = {
        "status": "PASS_CURRENT_MAIN_EVENT_GROUPS_COMPILE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows,
        "compatibility_headers": [{"path": str((SOURCE_DIR / h).relative_to(ROOT)), "sha256": sha(SOURCE_DIR / h)} for h in HEADERS],
        "pinned_freertos_sources": [{"path": str((PINNED / h).relative_to(ROOT)), "sha256": sha(PINNED / h)} for h in ("event_groups.c", "timers.c")],
        "bounded_oracle": {"path": str(oracle.relative_to(ROOT)), "sha256": sha(oracle),
                           "observed": result.stdout.strip().splitlines()[-1]},
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["FreeRTOS source uses recovered sparse ABI and live timer queue RAM at 0x20074ab0",
                   "Bounded WSF signal cases do not prove scheduler or ISR runtime behavior",
                   "Final placement and hardware operation remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
