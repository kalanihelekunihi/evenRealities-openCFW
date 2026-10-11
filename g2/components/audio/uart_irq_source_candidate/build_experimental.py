#!/usr/bin/env python3
"""Compile the isolated UART IRQ graph and optionally link admitted archives."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SOURCES = ("irq_service", "lower_dma", "rx_abort", "read_abort", "read_sm",
           "fifo_bridge", "tx_bridge", "delay_bridge")

def run(command):
    p = subprocess.run(command, text=True, capture_output=True)
    if p.returncode:
        raise SystemExit(f"command failed ({p.returncode}): {command!r}\n{p.stderr}")
    return p.stdout

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def undefined(path):
    return [line.rsplit(maxsplit=1)[-1] for line in run(["arm-none-eabi-nm", "-u", str(path)]).splitlines()]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--audio-archive", type=Path)
    parser.add_argument("--main-object", type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    objects = []
    for stem in SOURCES:
        source = HERE / f"{stem}.c"
        obj = out / f"{stem}.o"
        run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-std=c11", "-ffreestanding", "-O2", "-Wall", "-Wextra",
             "-Wno-unused-function", "-c", str(source), "-o", str(obj)])
        objects.append(obj)
    composed = out / "uart-irq-composed.o"
    run(["arm-none-eabi-ld", "-r", "-o", str(composed), *map(str, objects)])
    result = {"sources": {str((HERE / f"{stem}.c").relative_to(ROOT)): sha(HERE / f"{stem}.c") for stem in SOURCES},
              "object_sha256": sha(composed), "unresolved_composed": undefined(composed),
              "scope": "experimental source graph; no behavioral or byte-equality admission"}
    if args.audio_archive:
        archive = args.audio_archive.resolve()
        linked = out / "uart-plus-audio.o"
        run(["arm-none-eabi-ld", "-r", "-o", str(linked), str(composed),
             "--whole-archive", str(archive), "--no-whole-archive"])
        result["audio_archive_sha256"] = sha(archive)
        result["unresolved_with_audio"] = undefined(linked)
        result["linked_with_audio_sha256"] = sha(linked)
    if args.main_object:
        main_obj = args.main_object.resolve()
        linked = out / "uart-plus-main.o"
        run(["arm-none-eabi-ld", "-r", "-o", str(linked), str(main_obj), str(composed)])
        result["main_object_sha256"] = sha(main_obj)
        result["unresolved_with_main"] = undefined(linked)
        result["linked_with_main_sha256"] = sha(linked)
    (out / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"composed_imports": len(result["unresolved_composed"]),
                      "audio_imports": len(result.get("unresolved_with_audio", [])),
                      "main_imports": len(result.get("unresolved_with_main", []))}))

if __name__ == "__main__":
    main()
