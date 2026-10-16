#!/usr/bin/env python3
"""Bind native-compared completed-UID batch sender into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_aux_update_4f6328.c"
OUT = G2 / "build/c-firmware/20261015/main-quicklist-aux-update"
BASE = G2 / "build/c-firmware/20261015/main-quicklist-mode-three/apollo-main-quicklist-mode-three.o"
ORACLE = HERE / "verify_main_quicklist_aux_update_oracle_20261015.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_aux_update_4f6328.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)],
                   check=True)
    linked = OUT / "apollo-main-quicklist-aux-update.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)],
                   check=True)
    before, after = imports(BASE), imports(linked)
    if before - after != {"audio_quicklist_aux_update_4f6328"} or \
            after - before != {"audio_quicklist_send_completed_5591b0"}:
        raise RuntimeError("QuickList auxiliary update import contract changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True,
                   text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_AUX_UPDATE_ORACLE" or \
            oracle["cases"] != 21 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("QuickList auxiliary update oracle changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_AUX_UPDATE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["QuickList send provider 0x5591b0 requires C ownership.",
                          "Packet sender and logs use controlled lower interfaces.",
                          "Final RAM placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
