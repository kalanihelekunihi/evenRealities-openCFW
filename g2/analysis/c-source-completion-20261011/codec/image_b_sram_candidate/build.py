#!/usr/bin/env python3
"""Compile the separate GX8002 image-B SRAM candidate; no selected-manifest edit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
SOURCE_DIR = ROOT / "g2/components/gx8002/image_b_sram_candidate"
SDK = "third-party/upstream/nationalchip-lvp-kws"
SOURCES = ["backup_address_string.c", "backup_audio_curves.c",
           "backup_audio_state.c", "backup_audio_control.c",
           "backup_analog_controls.c", "backup_audio_init.c",
           "backup_runtime_helpers.c", "backup_audio_prepare.c",
           "backup_platform_gate.c"]
IMAGE_SHA = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "build")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    prefix = ["docker", "run", "--rm", "--network=none", "--read-only",
              "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
              "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
              "--mount", f"type=bind,src={out},dst=/out", "--tmpfs", "/tmp:rw",
              "opencfw/iar-base:10.10.2-local"]
    units = []
    for name in SOURCES:
        source = SOURCE_DIR / name
        obj = out / (Path(name).stem + ".o")
        cmd = prefix + ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
                        "-mhard-float", "-O2", "-fno-builtin", "-std=c11",
                        "-Wall", "-Wextra", "-Werror",
                        "-I/repo/" + SDK + "/arch/soc/grus/include",
                        "-I/repo/" + SDK + "/include",
                        "-c",
                        "/repo/" + str(source.relative_to(ROOT)), "-o", "/out/" + obj.name]
        subprocess.run(cmd, check=True)
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                      "object": str(obj), "object_sha256": sha(obj)})
    linked = out / "image_b_sram_candidate.o"
    cmd = prefix + ["/tool/bin/csky-abiv2-elf-ld", "-r", "-o", "/out/" + linked.name]
    cmd += ["/out/" + Path(name).stem + ".o" for name in SOURCES]
    subprocess.run(cmd, check=True)
    nm_command = prefix + ["/tool/bin/csky-abiv2-elf-nm", "-u",
                           "/out/" + linked.name]
    nm_output = subprocess.run(nm_command, check=True, capture_output=True,
                               text=True).stdout
    undefined = sorted(line.split()[-1] for line in nm_output.splitlines() if line.strip())
    receipt = {"image_sha256": IMAGE_SHA, "separate_loaded_image_b": True,
               "selected_firmware_image": False, "target": "CSKY CK804EF hard-float ELF32",
               "units": units, "linked_object": str(linked),
               "linked_object_sha256": sha(linked),
               "undefined_symbols": undefined,
               "source_complete": False,
               "data_and_final_layout_complete": False}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(out / "receipt.json")


if __name__ == "__main__":
    main()
