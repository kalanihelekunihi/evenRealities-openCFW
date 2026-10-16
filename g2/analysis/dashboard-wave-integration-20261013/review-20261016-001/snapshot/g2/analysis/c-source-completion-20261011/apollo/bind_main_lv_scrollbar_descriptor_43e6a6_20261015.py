#!/usr/bin/env python3
"""Bind native-compared Apollo LV scrollbar draw-task descriptor."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scrollbar_descriptor_43e6a6.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-scrollbar-descriptor-43e6a6"
BASE = G2 / "build/c-firmware/20261015/main-lv-draw-scrollbars-43e63e/apollo-main-lv-draw-scrollbars-43e63e.o"
ORACLE = HERE / "verify_main_lv_scrollbar_descriptor_43e6a6_oracle_20261015.py"
OWNED = {"audio_uart_lv_scrollbar_draw_descriptor_43e6a6"}
LOWER = {"audio_uart_lv_effective_opacity_44c47a"} | {
    f"audio_uart_lv_scrollbar_metric_{address:x}" for address in
    (0x43dd9a, 0x43ddf0, 0x43dde2, 0x43de3e,
     0x43de1c, 0x43de26, 0x43de30)}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_scrollbar_descriptor_43e6a6.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_DESCRIPTOR_ORACLE" or
            oracle["cases"] != 18 or oracle["controlled_provider_count"] != 13 or
            oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("scrollbar descriptor oracle changed")
    imported = symbols(obj, "-u")
    if (symbols(obj, "--defined-only") != OWNED or len(imported) != 13 or
            imported - symbols(BASE, "--defined-only") - symbols(BASE, "-u") != LOWER):
        raise RuntimeError("scrollbar descriptor object contract changed")
    linked = OUT / "apollo-main-lv-scrollbar-descriptor-43e6a6.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before != LOWER or len(before) != 239 or
            len(after) != 246 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("scrollbar descriptor linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_DESCRIPTOR_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": sorted(LOWER), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Descriptor byte writes and return decision are native-compared; seven style wrappers, effective opacity and live rendering remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
