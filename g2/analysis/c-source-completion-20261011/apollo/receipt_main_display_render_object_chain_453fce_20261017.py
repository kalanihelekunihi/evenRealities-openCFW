#!/usr/bin/env python3
"""Bind checked LVGL object-chain renderer to Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261017"
HERE = BASE / "main-display-render-object-chain-453fce"
PRIOR = BASE / "main-display-render-find-cover-453f2e/candidate.o"
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_render_object_chain_453fce.c"
ORACLE, OBJECT, CURRENT = HERE / "oracle-receipt.json", HERE / "object-chain.o", HERE / "candidate.o"
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
    assert oracle["status"] == "PASS_DIRECT_MAIN_DISPLAY_RENDER_OBJECT_CHAIN_453FCE_C"
    assert oracle["cases"] == 144 and oracle["source_sha256"] == sha(SOURCE)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(PRIOR), str(OBJECT), "-o", str(CURRENT)],
                   check=True)
    prior, current = symbols(PRIOR, "-u"), symbols(CURRENT, "-u")
    removed, added = sorted(set(prior) - set(current)), sorted(set(current) - set(prior))
    assert len(prior) == 108 and len(current) == 108
    assert removed == ["audio_uart_lv_render_object_chain_453fce"]
    assert added == ["audio_uart_lv_draw_object_4541b6"]
    record = {
        "status": "PASS_MAIN_DISPLAY_RENDER_OBJECT_CHAIN_453FCE_INTEGRATION",
        "prior_candidate": ref(PRIOR), "candidate_object": ref(CURRENT),
        "source": ref(SOURCE), "oracle": ref(ORACLE), "oracle_cases": 144,
        "native_body": "0x453fce..0x454074, including two ancestor levels",
        "unresolved_before": 108, "unresolved_after": 108,
        "removed_imports": removed, "new_imports": added,
        "remaining_gate": "Object-chain ancestor sibling and event ordering match stock under controlled lower calls. Draw-object body 0x4541b6, deeper hierarchies, other Main imports, whole-image source and hardware behavior remain open.",
        "source_complete": False, "flashable": False, "hardware_proof": False,
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(current), sha(OUT))


if __name__ == "__main__":
    main()
