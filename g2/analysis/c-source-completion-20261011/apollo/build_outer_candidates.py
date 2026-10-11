#!/usr/bin/env python3
"""Compile isolated Apollo outer C reductions; never link into selected archives."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
out = root / "g2/build/c-source-completion-20261011/apollo"
out.mkdir(parents=True, exist_ok=True)
flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
         "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-ffreestanding",
         "-fno-builtin", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
sources = {
    "bootloader_startup_power_root": root / "g2/components/bootloader/source_candidate_20261010/startup_power_root_candidate.c",
    "bootloader_startup_void_adapter": root / "g2/components/bootloader/source_candidate_20261010/startup_power_void_adapter.c",
    "bootloader_generic_float_log": root / "g2/components/bootloader/source_candidate_20261010/generic_log_float_candidate.c",
    "main_extended_log_root": root / "g2/components/main/extended_log_root_candidate_20261011/extended_log.c",
    "main_logger_selected_adapters": root / "g2/components/main/extended_log_root_candidate_20261011/selected_helper_adapters.c",
}
receipt = {}
for name, source in sources.items():
    obj = out / (name + ".o")
    command = flags + ["-c", str(source), "-o", str(obj)]
    proc = subprocess.run(command, capture_output=True, text=True)
    imports = []
    if proc.returncode == 0:
        nm = subprocess.run(["arm-none-eabi-nm", "-u", str(obj)],
                            capture_output=True, text=True, check=True)
        imports = [line.split()[-1] for line in nm.stdout.splitlines()]
    receipt[name] = {"source": str(source.relative_to(root)),
                     "object": str(obj.relative_to(root)),
                     "compile_returncode": proc.returncode,
                     "diagnostics": proc.stderr, "imports": imports}
main_selected = root / "g2/build/source-candidates/20261010-main/main-candidates.o"
if main_selected.exists() and all(receipt[n]["compile_returncode"] == 0 for n in
                                  ("main_extended_log_root", "main_logger_selected_adapters")):
    linked = out / "main_logger_with_selected.o"
    link = subprocess.run(["arm-none-eabi-ld", "-r", "-o", str(linked),
                           str(main_selected),
                           str(out / "main_extended_log_root.o"),
                           str(out / "main_logger_selected_adapters.o")],
                          capture_output=True, text=True)
    imports = []
    if link.returncode == 0:
        nm = subprocess.run(["arm-none-eabi-nm", "-u", str(linked)],
                            capture_output=True, text=True, check=True)
        imports = [line.split()[-1] for line in nm.stdout.splitlines()]
    receipt["main_selected_composition"] = {
        "source": str(main_selected.relative_to(root)),
        "object": str(linked.relative_to(root)),
        "compile_returncode": link.returncode,
        "diagnostics": link.stderr, "imports": imports,
    }
(out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({name: {"compile_returncode": data["compile_returncode"],
                         "imports": len(data["imports"])}
                  for name, data in receipt.items()}))
sys.exit(int(any(item["compile_returncode"] for item in receipt.values())))
