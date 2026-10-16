#!/usr/bin/env python3
"""Resolve the UART graphics call name to the verified Nema mode provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_graphics_nema_mode_alias_513924.c"
PROVIDER_SOURCE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/nema_mode.c"
ORACLE = G2 / "analysis/c-source-completion-20261011/peripherals/ambiq-nema-mode-native-results.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-scroll-view-step-44f40c/apollo-main-lv-scroll-view-step-44f40c.o"
OUT = G2 / "build/c-firmware/20261015/main-graphics-nema-alias-513924"
OWNED = {"audio_uart_display_graphics_blend_513924"}
PROVIDER = {"display_driver_nema_mode_513924"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_AMBIQ_NEMA_MODE_NATIVE" or oracle["cases"] != 2420 or \
       oracle["source_sha256"] != sha(PROVIDER_SOURCE) or \
       oracle["native_body_sha256"] != "e79ac2b12d6efcbb7291339da418ec904f2b1819fae4727a0c959477896014fc":
        raise RuntimeError("Nema mode provider evidence changed")
    obj = OUT / "display_graphics_nema_mode_alias_513924.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != PROVIDER:
        raise RuntimeError("Nema call-name object contract changed")
    if not PROVIDER <= symbols(BASE, "--defined-only"):
        raise RuntimeError("Nema mode provider missing from Main")
    linked = OUT / "apollo-main-graphics-nema-alias-513924.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if before - after != OWNED or after - before or len(before) != 232 or len(after) != 231:
        raise RuntimeError("Nema call-name linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_GRAPHICS_NEMA_ALIAS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "provider_source": str(PROVIDER_SOURCE.relative_to(ROOT)),
               "provider_source_sha256": sha(PROVIDER_SOURCE),
               "provider_oracle": str(ORACLE.relative_to(ROOT)),
               "provider_oracle_sha256": sha(ORACLE), "provider_oracle_cases": 2420,
               "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 232, "unresolved_after": 231,
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": [], "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["The existing Nema mode implementation has 2420 stock comparisons.",
                          "This C wrapper maps one caller name to that provider; live GPU behavior remains unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
