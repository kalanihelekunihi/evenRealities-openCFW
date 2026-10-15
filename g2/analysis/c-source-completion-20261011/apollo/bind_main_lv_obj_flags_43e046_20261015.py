#!/usr/bin/env python3
"""Bind native-compared LV object state bit wrappers."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_flags_43e046.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43e046"
BASE = G2 / "build/c-firmware/20261015/main-lv-event-accessors-4518d8/apollo-main-lv-event-accessors-4518d8.o"
ORACLE = HERE / "verify_main_lv_obj_flags_43e046_oracle_20261015.py"
OWNED = {"audio_uart_lv_obj_flag_set_43e046", "audio_uart_lv_obj_flag_clear_43e086"}
LOWER = {"audio_uart_lv_obj_state_apply_43ebec"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_flags_43e046.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_FLAGS_ORACLE" or
            oracle["cases"] != 70 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("flag wrapper oracle changed")
    if (symbols(obj, "--defined-only") != OWNED or
            symbols(obj, "-u") != {"audio_uart_lvgl_log"} | LOWER):
        raise RuntimeError("flag wrapper object contract changed")
    linked = OUT / "apollo-main-lv-obj-flags-43e046.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before != LOWER or len(before) != 239 or
            len(after) != 238 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("flag wrapper linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_FLAGS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": sorted(LOWER), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["State flag wrappers have native-compared C bodies; their 0x43ebec state-apply provider and downstream effects remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
