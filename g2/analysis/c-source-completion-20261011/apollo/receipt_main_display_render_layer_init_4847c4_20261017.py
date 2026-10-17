#!/usr/bin/env python3
"""Bind checked LVGL layer initialization and display-list provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-layer-init-4847c4"
PRIOR = BASE / "main-display-render-wait-484622/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_layer_init_4847c4.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "layer-init.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_LAYER_INIT_4847C4_C"
    assert oracle["cases"] == 37 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 109 and len(current) == 108
    assert removed == ["audio_uart_lv_render_layer_init_4847c4"] and not added
    assert "audio_uart_lv_render_layer_base_init_4846de" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_LAYER_INIT_4847C4_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 37,
        "native_body": "0x4846de..0x48475e plus 0x4847c4..0x484836 through return or null assertion log",
        "unresolved_before": 109, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "new_provider": "audio_uart_lv_render_layer_base_init_4846de",
        "remaining_gate": "Layer base initialization, display-list insertion and null assertion log match stock under controlled lower calls. Render layer 0x453e10, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
