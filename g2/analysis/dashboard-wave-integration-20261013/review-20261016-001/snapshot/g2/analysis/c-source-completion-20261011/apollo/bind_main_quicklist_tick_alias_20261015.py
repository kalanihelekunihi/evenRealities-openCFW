#!/usr/bin/env python3
"""Bind QuickList clock call to the already source-defined local-time routine."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_tick_alias_44a1c6.c"
CONTEXT = G2 / "components/audio/audio_log_format_source_candidate/context.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-store-many/apollo-main-quicklist-store-many.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-tick-alias"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/verify_audio_log_context.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        elf = ELFFile(stream)
        segment = next(item for item in elf.iter_segments() if item["p_type"] == "PT_LOAD")
        body = segment.data()[0x44a1c6-segment["p_vaddr"]:0x44a1ea-segment["p_vaddr"]]
        if body[:2] != bytes.fromhex("80b5") or len(body) != 0x24:
            raise RuntimeError("QuickList/native log-context body changed")
    oracle = subprocess.run([sys.executable, str(ORACLE)], check=True,
                            capture_output=True, text=True)
    if "PASS_AUDIO_LOG_CONTEXT 35" not in oracle.stdout:
        raise RuntimeError("local-time native/C comparison changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_tick_alias_44a1c6.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_quicklist_tick_now"} or names(obj, "-u") != {"audio_log_context"}:
        raise RuntimeError("QuickList clock alias provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if "audio_quicklist_tick_now" not in before or "audio_log_context" not in providers:
        raise RuntimeError("Main local-time provider boundary changed")
    linked = OUT / "apollo-main-quicklist-tick-alias.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_quicklist_tick_now"} or after - before:
        raise RuntimeError("QuickList clock alias import delta changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_TICK_ALIAS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": "0x44a1c6", "native_body_sha256": hashlib.sha256(body).hexdigest(),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "context_source": str(CONTEXT.relative_to(ROOT)), "context_source_sha256": sha(CONTEXT),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "context_oracle_script": str(ORACLE.relative_to(ROOT)), "context_oracle_script_sha256": sha(ORACLE),
        "context_oracle_status": oracle.stdout.strip(),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Local-time context native/C comparison uses controlled snapshot, epoch and timezone inputs.",
                   "Real RTC behavior, timezone installation, startup and hardware execution remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
