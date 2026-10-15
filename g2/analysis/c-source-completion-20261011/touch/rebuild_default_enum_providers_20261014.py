#!/usr/bin/env python3
"""Rebuild four Touch providers with the selected C objects' enum ABI."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
PRIOR_DIR = G2 / "components/touch/source_candidate_20261010/build"
PRIOR = PRIOR_DIR / "receipt.json"
CENSUS = G2 / "build/c-firmware/20261014/touch-current-census/touch-current-census-receipt.json"
OUT = G2 / "build/c-firmware/20261014/touch-default-enum-providers"
PROVIDERS = ("cy_scb_i2c", "cy_scb_common", "msclp", "syslib_asm", "syslib_delay",
             "uidiv", "zero", "reset_data", "crtbegin", "crtend")
REBUILD = {"msclp", "syslib_asm", "syslib_delay", "uidiv", "zero",
           "crtbegin", "crtend"}
WEAK = {"_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
        "__deregister_frame_info", "__register_frame_info"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_command(original, output, name):
    cmd = list(original)
    mounts = [i for i, arg in enumerate(cmd) if arg == "-v" and i + 1 < len(cmd)]
    candidates = [i + 1 for i in mounts if ":/out" in cmd[i + 1]]
    if len(candidates) != 1 or cmd[0] != "docker":
        raise RuntimeError("pinned provider container command changed")
    mount = cmd[candidates[0]]
    cmd[candidates[0]] = str(output) + mount[mount.index(":/out"):]
    compile_index = cmd.index("-c")
    cmd.insert(compile_index, "-fno-short-enums")
    cmd.insert(cmd.index("-c"), "-Wa,--noexecstack")
    return cmd


def main():
    prior = json.loads(PRIOR.read_text())
    census = json.loads(CENSUS.read_text())
    default = census["variants"]["default_enum"]
    if len(prior["provider_records"]) != len(PROVIDERS) or default["objects_compiled"] != 61:
        raise RuntimeError("Touch selected source/provider census changed")
    OUT.mkdir(parents=True, exist_ok=True)
    inputs, commands, rebuilt = [], {}, {}
    for name, record in zip(PROVIDERS, prior["provider_records"]):
        original = PRIOR_DIR / f"provider__{name}.o"
        if sha(original) != record["object_sha256"] or sha(ROOT / record["source"]) != record["source_sha256"]:
            raise RuntimeError(f"pinned Touch provider changed: {name}")
        if name not in REBUILD:
            inputs.append(original)
            continue
        output = OUT / name
        output.mkdir(exist_ok=True)
        if name.startswith("crt"):
            original_out = G2 / "analysis/touch-crtstuff-source-rebuild-2026-10-09/outputs"
            for header in ("tconfig.h", "cs-tconfig.h", "libgcc_tm.h"):
                shutil.copy2(original_out / header, output / header)
        cmd = normalized_command(record["argv"], output, name)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{name} compile failed: {result.stderr[-3000:]}")
        filename = f"{name}.o" if name.startswith("crt") else "public.o"
        obj = output / filename
        if not obj.exists():
            raise RuntimeError(f"{name} output missing")
        sections = subprocess.check_output(["arm-none-eabi-readelf", "-W", "-S", str(obj)], text=True)
        attributes = subprocess.check_output(["arm-none-eabi-readelf", "-A", str(obj)], text=True)
        if ".note.GNU-stack" not in sections:
            raise RuntimeError(f"{name} lacks a non-executable stack note")
        if name in ("msclp", "syslib_delay", "crtbegin", "crtend") and \
           "Tag_ABI_enum_size: int" not in attributes:
            raise RuntimeError(f"{name} does not use the selected 32-bit enum ABI")
        inputs.append(obj)
        commands[name] = cmd
        rebuilt[name] = {"source": record["source"], "source_sha256": record["source_sha256"],
                         "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                         "non_executable_stack_note": True,
                         "enum_size": "int" if "Tag_ABI_enum_size: int" in attributes else "not_applicable"}
    objects = [ROOT / name for name in default["object_sha256"]]
    if [row["source"] for row in prior["records"]] != list(census["selected_sources"]):
        raise RuntimeError("Touch source order changed between pinned and current builds")
    for obj in objects:
        if sha(obj) != default["object_sha256"][str(obj.relative_to(ROOT))]:
            raise RuntimeError(f"selected Touch C object changed: {obj}")
    identical = sum(sha(obj) == row["object_sha256"]
                    for obj, row in zip(objects, prior["records"]))
    if identical != len(objects):
        raise RuntimeError(f"only {identical}/{len(objects)} current Touch C objects match pinned bytes")
    history = ROOT / default["history_object"]
    if sha(history) != default["history_object_sha256"]:
        raise RuntimeError("Touch LP history object changed")
    linked = OUT / "touch-default-enum-candidate.o"
    result = subprocess.run(["arm-none-eabi-ld", "-r", *map(str, objects),
                             *map(str, inputs), str(history), "-o", str(linked)],
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"Touch relink failed: {result.stderr[-3000:]}")
    warnings = result.stderr.strip().splitlines()
    if any("uses variable-size enums" in line or "uses 32-bit enums" in line
           for line in warnings):
        raise RuntimeError(f"Touch enum ABI warning remains: {warnings}")
    if any("executable stack" in line for line in warnings):
        raise RuntimeError(f"Touch executable-stack warning remains: {warnings}")
    listing = subprocess.check_output(["arm-none-eabi-nm", "-u", str(linked)], text=True)
    strong = [parts[-1] for line in listing.splitlines()
              if (parts := line.split()) and parts[0] == "U"]
    weak = [parts[-1] for line in listing.splitlines()
            if (parts := line.split()) and parts[0] in ("w", "v")]
    if strong or set(weak) != WEAK:
        raise RuntimeError(f"Touch imports changed: strong={strong}, weak={weak}")
    receipt = {"status": "PASS_EXPERIMENTAL_TOUCH_DEFAULT_ENUM_PROVIDERS_C",
               "pinned_provider_receipt": str(PRIOR.relative_to(ROOT)),
               "pinned_provider_receipt_sha256": sha(PRIOR),
               "source_census": str(CENSUS.relative_to(ROOT)), "source_census_sha256": sha(CENSUS),
               "selected_c_objects": len(objects),
               "byte_identical_to_pinned_c_objects": identical,
               "pinned_compiler_hash_match": census["pinned_compiler_match"],
               "rebuilt_providers": rebuilt,
               "rebuild_commands": commands, "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "strong_unresolved": strong,
               "weak_unresolved": sorted(weak), "link_warnings": warnings,
               "whole_image_complete": False, "hardware_proof": False,
               "limits": ["Seven rebuilt providers use the pinned GCC 14.2 container but are new local objects, not the originally pinned bytes.",
                          "The current clang binary differs from the pinned compiler hash, although all 61 selected C object bytes match the pinned outputs.",
                          "LP history allocation extent, final RAM layout, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(objects), len(strong), len(warnings), sha(path))


if __name__ == "__main__":
    main()
