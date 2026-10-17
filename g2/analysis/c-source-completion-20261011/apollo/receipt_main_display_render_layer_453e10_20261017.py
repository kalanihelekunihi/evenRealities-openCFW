#!/usr/bin/env python3
"""Bind checked LVGL render-layer pass and expose its two lower providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-layer-453e10"
PRIOR = BASE / "main-display-render-layer-init-4847c4/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_layer_453e10.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "render-layer.o", HERE / "candidate.o"
OUT = HERE / "receipt.json"
ADDED = ["audio_uart_lv_render_find_cover_453f2e",
         "audio_uart_lv_render_object_chain_453fce"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def symbols(path, option):
    return sorted({line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", option, str(path)], text=True).splitlines() if line.strip()})


def main():
    oracle = json.loads(ORACLE.read_text())
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_LAYER_453E10_C"
    assert oracle["cases"] == 65 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 109
    assert removed == ["audio_uart_lv_render_layer_453e10"] and added == ADDED
    assert "audio_uart_lv_render_layer_reset_48471a" in symbols(CURRENT, "--defined-only")
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_LAYER_453E10_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 65,
        "native_body": "0x453e10..0x453f2e plus 0x48471a..0x48475e",
        "unresolved_before": 108, "unresolved_after": 109,
        "removed_imports": removed, "new_imports": added,
        "new_provider": "audio_uart_lv_render_layer_reset_48471a",
        "remaining_gate": "Render-layer ordering, alpha clear call frames and reset assertion log match stock under controlled lower calls. Cover finder 0x453f2e, object-chain renderer 0x453fce, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
