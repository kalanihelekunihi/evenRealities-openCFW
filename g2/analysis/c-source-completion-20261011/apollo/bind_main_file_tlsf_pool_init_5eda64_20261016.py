#!/usr/bin/env python3
"""Link stock-compared TLSF pool initializer without claiming boot wiring."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/file_tlsf_pool_init_5eda64.c"
BASE = G2 / "build/c-firmware/20261016/main-file-heap-ram-cells/apollo-main-file-heap-ram-cells-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-file-tlsf-pool-init"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_file_tlsf_pool_init_5eda64"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_FILE_TLSF_POOL_INIT_C_ORACLE" or \
            oracle["cases"] != 16 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("TLSF pool initializer oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "file_tlsf_pool_init_5eda64.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER}:
        raise RuntimeError("TLSF pool initializer symbols changed")
    before = names(BASE, "-u")
    if len(before) != 176 or PROVIDER in names(BASE, "--defined-only"):
        raise RuntimeError("Apollo pool initializer base changed")
    linked = OUT / "apollo-main-file-tlsf-pool-init-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if after != before or PROVIDER not in names(linked, "--defined-only"):
        raise RuntimeError("Apollo pool initializer frontier changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_TLSF_POOL_INIT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 176, "unresolved_after": 176,
               "imports_resolved": [], "imports_added": [], "provider_linked": PROVIDER,
               "startup_wired": False, "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Stock backing RAM 0x20208e70..0x20279670 is referenced but not yet reserved.",
                          "Boot ordering and global placement remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 176, 176, sha(path))

if __name__ == "__main__":
    main()
