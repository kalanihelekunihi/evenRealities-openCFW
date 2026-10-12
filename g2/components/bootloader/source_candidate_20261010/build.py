#!/usr/bin/env python3
"""Inventory and archive source-owned bootloader C providers only."""
import argparse
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/components/bootloader"
INCLUDES = [
    BASE / "filesystem/freestanding_include",
    BASE / "filesystem",
    BASE / "allocator/freestanding_include",
    BASE / "initializer_callbacks",
    ROOT / "g2/components/foundation/ambiq_mspi",
    ROOT / "g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status",
    ROOT / "third-party/upstream/ambiqhal-apollo510/mcu/apollo510",
    ROOT / "third-party/upstream/ambiqhal-apollo510/CMSIS/AmbiqMicro/Include",
    ROOT / "g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include",
    ROOT / "third-party/upstream/cmsis-5-590/CMSIS/Core/Include",
    ROOT / "third-party/upstream/llvm-compiler-rt-format-20.1.8",
]
FLAGS = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
         "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
         "-ffreestanding", "-fno-builtin", "-std=c11", "-O2", "-fwrapv",
         "-ffunction-sections", "-fdata-sections", "-DNDEBUG",
         "-DLFS_NO_DEBUG", "-DLFS_NO_WARN", "-DLFS_NO_ERROR", "-DLFS_NO_ASSERT",
         "-DLFS_NO_INTRINSICS", "-DLFS_DEFINES=boot_lfs_defines.h"]
PREFERRED_PROVIDERS = {
    # The accepted remaining-native checkpoint binds all 27 selector slots;
    # the earlier pcm21-selector6 data image binds fewer slots.
    "g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/initialized_data.c",
}
ASSEMBLY_SOURCES = [
    "runtime_memory/boot_assert.S",
    "runtime_memory/double_compare_flags.S",
    "runtime_memory/native_empty_leaves.S",
    "runtime_memory/iar_constraint_dispatch_entry.S",
    "application_storage/storage_callback_veneers.S",
    "initializer_callbacks/callback_table.S",
    "initializer_callbacks/startup_clockmux_entry.S",
    "initializer_callbacks/startup_mcu_memory_entry.S",
    "initializer_callbacks/native_uart_log_abi_wrapper.S",
    "initializer_callbacks/uart_rx_drain32_abi.S",
    "initializer_callbacks/hardware_readiness_gate.S",
    "filesystem/native_unmount_abi_wrapper.S",
    "startup/reset.S",
    "startup/fpu.S",
    "startup/itcm_helpers.S",
    "startup/init_records.S",
    "startup/record_adapters.S",
    "startup/vector_handlers.S",
    "startup/vectors.S",
    "thread_creation/exception_entry.S",
    "application_storage/info_read_rom_thunk.S",
    "clock_manager/mode_publisher_abi.S",
    "nor_commands/nor_timing_wrapper.S",
    "nor_mspi_init/irq_guard.S",
    "platform_control/critical_save.S",
    "platform_control/runtime_transition_entry.S",
    "platform_startup/delay_math.S",
    "platform_startup/local_providers.S",
    "thread_creation/first_task_transfer.S",
    "update_core/handoff.S",
    "source_candidate_20261010/startup_root_entry.S",
]
ISOLATED_CANDIDATES = {
    "source_candidate_20261010/startup_power_root_candidate.c",
    "source_candidate_20261010/tlsf_printf_candidate.c",
}


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def symbols(obj):
    proc = run(["arm-none-eabi-nm", "-g", str(obj)])
    if proc.returncode:
        raise RuntimeError(proc.stderr)
    defined, undefined = {}, []
    for line in proc.stdout.splitlines():
        match = re.match(r"(?:[0-9a-fA-F]+\s+)?([A-Za-z])\s+(\S+)$", line.strip())
        if not match:
            continue
        kind, name = match.groups()
        if kind == "U":
            undefined.append(name)
        elif kind.isupper() or kind in "wuv":
            defined[name] = kind
    return defined, undefined


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    sources = sorted(BASE.rglob("*.c")) + [BASE / p for p in ASSEMBLY_SOURCES]
    for index, source in enumerate(sources):
        rel = source.relative_to(ROOT).as_posix()
        record = {"source": rel, "headers": re.findall(r'^\s*#\s*include\s*[<"]([^>"]+)', source.read_text(errors="replace"), re.M)}
        if source.relative_to(BASE).as_posix() in ISOLATED_CANDIDATES:
            record["status"] = "isolated_candidate_excluded"
            records.append(record)
            continue
        if source.stem.endswith("test") or source.name in {"host_test.c", "boot_mount_test.c"}:
            record["status"] = "fixture_excluded"
            records.append(record)
            continue
        obj = out / f"unit_{index:03d}.o"
        command = FLAGS + [f"-I{p}" for p in INCLUDES] + ["-c", str(source), "-o", str(obj)]
        if source.relative_to(BASE).as_posix() == "filesystem/upstream/lfs.c":
            command = [flag for flag in command if flag not in ("-DNDEBUG", "-DLFS_NO_ASSERT")]
            command.insert(command.index("-c"), "-DOPENCFW_NATIVE_LFS_ASSERT")
        if source.suffix == ".S":
            command = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                       "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-c",
                       str(source), "-o", str(obj)]
        if source.name == "fp_primitives.c" and source.parent.name == "iar_format_native":
            # This evidenced formatter unit uses binary64 VFP (see its README
            # and the accepted native-formatter closure), unlike the common SP profile.
            command[command.index("-mfpu=fpv5-sp-d16")] = "-mfpu=fpv5-d16"
        if source.name == "nor_mspi_queue.c":
            # The component README identifies its clockgen as a duplicate and
            # documents this source switch for the separate provider.
            command.insert(command.index("-c"), "-DOPENCFW_USE_EXTERNAL_MSPI_CLOCKGEN")
        result = run(command)
        record["compiler"] = command
        if result.returncode:
            record["status"] = "compile_failed"
            record["diagnostic"] = result.stderr[:3000]
        else:
            record["status"] = "compiled"
            record["object"] = obj.name
            record["defined"], record["undefined"] = symbols(obj)
        records.append(record)
    # Prefer canonical, shallow paths and keep one strong GLOBAL provider per name.
    candidates = sorted((r for r in records if r["status"] == "compiled"),
                        key=lambda r: (0 if r["source"] in PREFERRED_PROVIDERS else 1,
                                       r["source"].count("/"), r["source"]))
    providers = {}
    selected = []
    for record in candidates:
        collisions = sorted(name for name, kind in record["defined"].items()
                            if kind not in "WwVv" and name in providers
                            and providers[name]["kind"] not in "WwVv")
        if collisions:
            record["status"] = "duplicate_provider_excluded"
            record["collisions"] = {name: providers[name]["source"] for name in collisions}
            continue
        selected.append(record)
        for name, kind in record["defined"].items():
            if name not in providers or providers[name]["kind"] in "WwVv":
                providers[name] = {"source": record["source"], "kind": kind}
        record["status"] = "selected"
    archive = out / "libbootloader_source_candidate_m55.a"
    archive.unlink(missing_ok=True)
    archive_result = run(["arm-none-eabi-ar", "rcsD", str(archive)] + [str(out / r["object"]) for r in selected])
    unresolved = sorted({name for r in selected for name in r["undefined"] if name not in providers})
    report = {"target": "arm-none-eabi/cortex-m55", "archive": str(archive),
              "archive_returncode": archive_result.returncode, "archive_stderr": archive_result.stderr,
              "counts": {status: sum(r["status"] == status for r in records) for status in
                         sorted({r["status"] for r in records})},
              "global_weak_providers": providers, "unresolved_externals": unresolved,
              "units": records}
    (out / "inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"counts": report["counts"], "providers": len(providers),
                      "unresolved": len(unresolved), "archive_returncode": archive_result.returncode}))
    return int(bool(archive_result.returncode))


if __name__ == "__main__":
    raise SystemExit(main())
