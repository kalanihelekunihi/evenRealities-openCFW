#!/usr/bin/env python3
"""Compare bounded native and candidate MMIO store counts for image-B leaves."""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
OUT = HERE / "build"
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
PAIRS = [
    ("10005e9c", "audio_start_10005e9c", "backup_audio_start.o"),
    ("1000588c", "audio_i2s_clock_1000588c", "backup_audio_i2s.o"),
    ("1000589c", "audio_i2s_input_mode_1000589c", "backup_audio_i2s.o"),
    ("100058ac", "audio_i2s_output_mode_100058ac", "backup_audio_i2s.o"),
    ("100051d8", "analog_config_update_100051d8", "backup_analog_controls.o"),
    ("100051ec", "audio_prepare_100051ec", "backup_audio_prepare.o"),
    ("10005ab4", "set_logfbank_enable_10005ab4", "backup_audio_state.o"),
    ("10005af8", "set_fftvad_w_10005af8", "backup_audio_state.o"),
    ("10005b34", "set_fftvad_curve_1_10005b34", "backup_audio_curves.o"),
    ("10005b68", "set_fftvad_curve_2_10005b68", "backup_audio_curves.o"),
    ("10005b9c", "set_fftvad_curve_3_10005b9c", "backup_audio_curves.o"),
    ("10005bdc", "set_fftvad_curve_4_10005bdc", "backup_audio_curves.o"),
    ("10005c10", "set_fftvad_curve_5_10005c10", "backup_audio_curves.o"),
    ("10005c30", "set_fftvad_chipping_10005c30", "backup_audio_state.o"),
    ("10005c80", "get_fftvad_state_10005c80", "backup_audio_state.o"),
    ("10005cb0", "audio_read_status_10005cb0", "backup_audio_control.o"),
    ("10008048", "analog_pga_itrim_10008048", "backup_analog_controls.o"),
    ("10008064", "analog_pga_bypass_10008064", "backup_analog_controls.o"),
    ("1000807c", "analog_pga_enable_1000807c", "backup_analog_controls.o"),
    ("10008094", "analog_adc_sample_clock_10008094", "backup_analog_controls.o"),
    ("100080ac", "analog_adc_out_clock_100080ac", "backup_analog_controls.o"),
    ("100080c4", "analog_adc_input_100080c4", "backup_analog_controls.o"),
    ("100080dc", "analog_adc_reset_100080dc", "backup_analog_controls.o"),
    ("10008134", "analog_ldo_digital_control_10008134", "backup_analog_controls.o"),
]


def objdump(args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
           "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
           "--mount", f"type=bind,src={OUT},dst=/out,readonly",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + args
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def store_count(disassembly):
    return sum("st.w" in line for line in disassembly.splitlines())


def main():
    census = ROOT / "g2/research/corpus/codec/ghidra/open-2026-09-29/image_b_sram/functions-000.jsonl"
    bounds = {row["entry"]: (int(row["body_start"], 16),
              int(row["body_end_inclusive"], 16) + 1)
              for row in map(json.loads, census.read_text().splitlines())}
    compiled = {}
    for obj in {row[2] for row in PAIRS}:
        dump = objdump(["-d", "/out/" + obj])
        compiled[obj] = dump
    results = []
    for address, suffix, obj in PAIRS:
        start, end = bounds[address]
        native = objdump(["-D", "-b", "binary", "-m", "csky",
                          "--adjust-vma=0x10003000", f"--start-address=0x{start:x}",
                          f"--stop-address=0x{end:x}", "/stock/" + STOCK.name])
        source = compiled[obj]
        match = re.search(rf"(?m)^.* <[^>]*{re.escape(suffix)}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)",
                          source, re.S | re.M)
        if not match:
            raise RuntimeError(f"Missing compiled symbol {suffix}")
        native_stores = store_count(native)
        source_stores = store_count(match.group(1))
        results.append({"native_entry": address, "compiled_suffix": suffix,
                        "native_stores": native_stores, "candidate_stores": source_stores,
                        "match": native_stores == source_stores})
    result = {"stock_image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
              "scope": "per-body store count only; addresses, values, order, timing and hardware effects not proved",
              "checked": len(results), "all_store_counts_match": all(r["match"] for r in results),
              "functions": results}
    (HERE / "mmio-schedule-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(results)} bounded store counts, match={result['all_store_counts_match']}")
    if not result["all_store_counts_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
