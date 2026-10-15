#!/usr/bin/env python3
"""Bind native-compared Apollo LV base event-state body."""
import hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
HERE = Path(__file__).resolve().parent
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_event_state_43e442.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-event-state-43e442"
BASE = G2 / "build/c-firmware/20261015/main-lv-event-state-small-helpers/apollo-main-lv-event-state-small-helpers.o"
ORACLE = HERE / "verify_main_lv_obj_event_state_43e442_oracle_20261015.py"
OWNED = {"audio_uart_lv_obj_event_state_43e442"}
LOWER = {"audio_uart_lv_draw_scrollbars_43e63e",
         "audio_uart_lv_draw_task_build_452616",
         "audio_uart_lv_draw_task_init_451b9c",
         "audio_uart_lv_draw_task_render_451c6e"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path, mode):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", mode, str(path)], text=True).splitlines()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_event_state_43e442.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle = json.loads((OUT / "oracle.json").read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_EVENT_STATE_ORACLE" or
            oracle["cases"] != 18 or oracle["controlled_provider_count"] != 21 or
            oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("event-state oracle changed")
    imported = symbols(obj, "-u")
    if (symbols(obj, "--defined-only") != OWNED or len(imported) != 21 or
            imported - symbols(BASE, "--defined-only") != LOWER):
        raise RuntimeError("event-state object contract changed")
    linked = OUT / "apollo-main-lv-obj-event-state-43e442.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    before, after = symbols(BASE, "-u"), symbols(linked, "-u")
    if (before - after != OWNED or after - before != LOWER or len(before) != 236 or
            len(after) != 239 or not OWNED <= symbols(linked, "--defined-only")):
        raise RuntimeError("event-state linked contract changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_EVENT_STATE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object_sha256": sha(obj), "oracle_sha256": sha(OUT / "oracle.json"),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_owned_symbols": sorted(OWNED), "imports_resolved": sorted(OWNED),
               "imports_added": sorted(LOWER), "source_complete": False,
               "full_payload_linked": False, "hardware_proof": False,
               "limits": ["All three event-code branches are native-compared with controlled children; four lower draw providers, live style and rendering remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__": main()
