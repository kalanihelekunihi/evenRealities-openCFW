#!/usr/bin/env python3
"""Bind the stock-compared list animation initializer."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_list_anim_init_58966c.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-start-5e716c/apollo-main-terminal-ui-start-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-list-anim-init-58966c/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-list-anim-init-58966c"
SYMBOL = "audio_terminal_list_anim_init_58966c"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_LIST_ANIM_INIT_C_ORACLE"
            or oracle["cases"] != 4 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("list animation init oracle changed")
    before = imports(BASE)
    if len(before) != 169 or SYMBOL not in before:
        raise RuntimeError("Apollo list animation init frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_list_anim_init.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-list-anim-init-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before or len(after) != 168:
        raise RuntimeError("list animation init binding frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_INIT_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 169, "unresolved_after": 168,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
