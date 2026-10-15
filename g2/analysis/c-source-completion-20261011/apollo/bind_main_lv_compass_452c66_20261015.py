#!/usr/bin/env python3
"""Bind native-compared LV event extent helper."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_compass_452c66.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-compass-452c66"
BASE = G2 / "build/c-firmware/20261015/main-lv-invalidate-alias-4405d4/apollo-main-lv-invalidate-alias-4405d4.o"
ORACLE = HERE / "verify_main_lv_compass_452c66_oracle_20261015.py"
OWNED = {"audio_uart_lv_compass_452c66"}
ADDRESSES = (0x452450, 0x452498, 0x45246e, 0x45245a, 0x452464,
             0x452410, 0x45243a, 0x452446, 0x4522d4, 0x4522de)
LOWER = {f"audio_uart_lv_compass_part_{address:x}" for address in ADDRESSES}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_compass_452c66.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_COMPASS_ORACLE" or
            oracle["cases"] != 96 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("LV extent oracle changed")
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != LOWER:
        raise RuntimeError("LV extent object contract changed")
    linked = OUT / "apollo-main-lv-compass-452c66.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before != LOWER or len(before) != 237 or
            len(after) != 246 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("LV extent linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_COMPASS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": sorted(LOWER), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Extent arithmetic and provider call order are native-compared; ten lower metrics and live layout values remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
