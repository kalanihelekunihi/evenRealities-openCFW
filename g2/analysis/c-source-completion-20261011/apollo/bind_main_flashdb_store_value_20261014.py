#!/usr/bin/env python3
"""Bind bounded native-matched FlashDB KV store to Main C providers."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/settings_flashdb_store_value.c"
USER = G2 / "components/audio/uart_thread_source_candidate/settings_flashdb_kv_write.c"
BASE = G2 / "build/c-firmware/20261014/main-flashdb-gc-move/apollo-main-flashdb-gc-move.o"
OUT = G2 / "build/c-firmware/20261014/main-flashdb-store-value"
ORACLE = Path(__file__).with_name("verify_main_flashdb_store_value_oracle_20261014.py")
CHILDREN = {"audio_flashdb_prepare_space", "g2_flashdb_cache_update",
            "g2_flashdb_crc32", "g2_flashdb_db_path", "g2_flashdb_flash_write",
            "g2_flashdb_print", "g2_flashdb_sector_cache_lookup",
            "g2_flashdb_write_status", "g2_log_candidate_module_length"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        elf = ELFFile(stream)
        segment = next(item for item in elf.iter_segments() if item["p_type"] == "PT_LOAD")
        body = segment.data()[0x544d60-segment["p_vaddr"]:0x544f6c-segment["p_vaddr"]]
        if len(body) != 0x20c or body[:4] != bytes.fromhex("2de9f04f"):
            raise RuntimeError("native FlashDB KV store body changed")
    if "audio_flashdb_store_value" not in USER.read_text():
        raise RuntimeError("FlashDB KV store caller changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "settings_flashdb_store_value.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_flashdb_store_value"} or names(obj, "-u") != CHILDREN:
        raise RuntimeError("compiled FlashDB KV store provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if "audio_flashdb_store_value" not in before or not CHILDREN <= providers:
        raise RuntimeError("Main FlashDB KV store caller or lower providers changed")
    linked = OUT / "apollo-main-flashdb-store-value.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"audio_flashdb_store_value"} or after-before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    subprocess.run([sys.executable, str(ORACLE)], check=True,
                   capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_FLASHDB_STORE_VALUE_ORACLE" or oracle["cases"] != 12:
        raise RuntimeError("FlashDB KV store oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_FLASHDB_STORE_VALUE_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": "0x544d60", "native_selected_body_sha256": hashlib.sha256(body).hexdigest(),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "lower_providers": sorted(CHILDREN),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Twelve routed paths use intercepted lower FlashDB effects; real flash persistence, hardware errors and timing remain unproved.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
