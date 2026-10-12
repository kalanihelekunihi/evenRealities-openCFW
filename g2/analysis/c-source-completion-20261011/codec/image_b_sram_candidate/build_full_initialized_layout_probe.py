#!/usr/bin/env python3
"""Relocatable-only image-B layout experiment with all 300 typed data bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate"
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
SCRIPT = HERE / "image_b_full_initialized_layout_probe.ld"
EXCLUDE = {
    "backup_clock_tables.c", "backup_clock_module_select.c",
    "backup_clock_frequency.c", "backup_platform_gate.c",
    "backup_initialized_runtime_data.c", "backup_fft_profile_data.c",
}
EXPERIMENTAL = {
    "clock_single_owner": ("backup_clock_single_owner_experiment.c", True),
    "initialized_runtime_sections": ("backup_initialized_runtime_data.c", True),
    "fft_profile_sections": ("backup_fft_profile_data.c", True),
    "sample_app_record": ("backup_sample_app_initialized_record.c", False),
    "sample_app_init": ("backup_sample_app_init.c", False),
    "sample_app_begin": ("backup_sample_app_begin.c", False),
    "sample_app_leaves": ("backup_sample_app_leaf_callbacks.c", False),
    "sample_app_event": ("backup_sample_app_event_ambient.c", False),
    "sample_app_command": ("backup_sample_app_command.c", False),
    "sample_app_audio_callback": ("backup_sample_app_audio_callback.c", False),
    "retained_slots": ("backup_runtime_retained_slots.c", False),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def target(tool, out, args):
    command = [
        "docker", "run", "--rm", "--network=none", "--read-only",
        "--platform", "linux/amd64",
        "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
        "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
        "--mount", f"type=bind,src={out},dst=/out",
        "--tmpfs", "/tmp:rw", "opencfw/iar-base:10.10.2-local",
        f"/tool/bin/csky-abiv2-elf-{tool}", *args,
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(" ".join(command) + "\n" + completed.stdout + completed.stderr)
    return completed.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--selected-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=HERE / "build-full-initialized-layout-probe")
    parser.add_argument("--script", type=Path, default=SCRIPT)
    args = parser.parse_args()
    receipt = json.loads(args.selected_receipt.read_text())
    if not receipt.get("separate_loaded_image_b") or len(receipt["units"]) < 231:
        raise RuntimeError("input is not the selected 231-unit image-B receipt")
    out = args.output.resolve()
    script = args.script.resolve()
    if not script.is_relative_to(ROOT):
        raise RuntimeError("linker script must be in repository")
    out.mkdir(parents=True, exist_ok=True)
    objects = []
    selected = []
    for unit in receipt["units"]:
        if Path(unit["source"]).name in EXCLUDE:
            continue
        source = ROOT / unit["source"]
        obj = Path(unit["object"])
        if sha(source) != unit["source_sha256"] or sha(obj) != unit["object_sha256"]:
            raise RuntimeError(f"selected source/object drift: {source}")
        objects.append(obj)
        selected.append(unit["source"])
    generated = []
    for stem, (name, data_sections) in EXPERIMENTAL.items():
        if any(Path(source).name == name for source in selected):
            continue
        source = SOURCE / name
        obj = out / f"{stem}.o"
        opts = ["-mcpu=ck804ef", "-mhard-float", "-O2", "-fno-builtin",
                "-std=c11", "-Wall", "-Wextra", "-Werror"]
        if data_sections:
            opts.append("-fdata-sections")
        opts += ["-I/repo/third-party/upstream/nationalchip-lvp-kws/arch/soc/grus/include",
                 "-I/repo/third-party/upstream/nationalchip-lvp-kws/include",
                 "-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility/libc",
                 "-I/repo/g2/components/gx8002/image_b_sram_candidate",
                 "-c", f"/repo/{source.relative_to(ROOT)}", "-o", f"/out/{obj.name}"]
        target("gcc", out, opts)
        objects.append(obj)
        generated.append({"source": str(source.relative_to(ROOT)),
                          "source_sha256": sha(source), "object_sha256": sha(obj)})
    output = out / "image_b_full_initialized_layout_probe.o"
    object_names = []
    for obj in objects:
        try:
            object_names.append("/repo/" + str(obj.relative_to(ROOT)))
        except ValueError:
            object_names.append("/out/" + obj.name)
    target("ld", out, ["-r", "-T", f"/repo/{script.relative_to(ROOT)}",
                       "-o", "/out/" + output.name, *object_names])
    sections = target("objdump", out, ["-h", "/out/" + output.name])
    symbols = target("nm", out, ["-u", "/out/" + output.name])
    expected = {
        ".gsensor_state": (0x20016f60, 4),
        ".audio_runtime_state": (0x20016f64, 16),
        ".sample_app_pointer": (0x20016f74, 4),
        ".sample_app_record": (0x20016f78, 32),
        ".audio_uart_tx": (0x20016f98, 32),
        ".imcra_profile": (0x20016fb8, 84),
        ".rifft_profile": (0x2001700c, 20),
        ".rfft_profile": (0x20017020, 20),
        ".kernel_coefficients": (0x20017034, 88),
    }
    for section, (address, size) in expected.items():
        line = next((line for line in sections.splitlines()
                     if line.split()[1:2] == [section]), None)
        if line is None:
            raise RuntimeError(f"missing section {section}")
        parts = line.split()
        if int(parts[2], 16) != size or int(parts[3], 16) != address:
            raise RuntimeError(f"wrong extent/placement: {line}")
    data = {
        "selected_receipt": str(args.selected_receipt.resolve()),
        "selected_receipt_sha256": sha(args.selected_receipt),
        "linker_script": str(script.relative_to(ROOT)),
        "linker_script_sha256": sha(script),
        "selected_objects_reused": len(selected),
        "experimental_units": generated,
        "normal_copy_typed_bytes": sum(size for _, size in expected.values()),
        "normal_copy_stock_bytes": 300,
        "normal_copy_load_address_scripted": "0x10016f60",
        "normal_copy_runtime_address": "0x20016f60",
        "normal_copy_end": "0x1001708c/0x2001708c",
        "load_address_verified_by_relocatable_link": False,
        "layout_object": str(output),
        "layout_object_sha256": sha(output),
        "undefined_symbols": sorted(line.split()[-1] for line in symbols.splitlines() if line.strip()),
        "scope": "relocatable section placement only; no final ELF, vector/reset, CRT copy or hardware execution",
    }
    path = out / "receipt.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
