#!/usr/bin/env python3
"""Build the six image candidates and report what is still missing.

This consumes source builders, not official payload bytes. A relocatable link
may retain imports; --require-complete rejects such a result and incomplete
source coverage even when every currently selected translation unit compiles.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv: list[str], log: Path) -> dict:
    # Qualify the source actually handed to a compiler while parallel workers edit.
    source = None
    if "-c" in argv and argv.index("-c") + 1 < len(argv):
        name = argv[argv.index("-c") + 1]
        source = ROOT / name.removeprefix("/repo/") if name.startswith("/repo/") else Path(name)
        if not source.is_absolute():
            source = ROOT / source
        if not source.is_file():
            source = None
    before = digest(source) if source else None
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    after = digest(source) if source and source.is_file() else None
    stable = source is None or before == after
    log.parent.mkdir(parents=True, exist_ok=True)
    note = "\nSource changed during compilation; candidate qualification rejected.\n" if not stable else ""
    log.write_text(result.stdout + result.stderr + note)
    receipt = {"argv": argv, "returncode": result.returncode if stable else 1,
               "process_returncode": result.returncode,
               "log": str(log.relative_to(ROOT)), "log_sha256": digest(log)}
    if source:
        receipt["compile_source_snapshot"] = {"path": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
            "sha256_before": before, "sha256_after": after, "stable_during_command": stable}
    return receipt


def symbol_census(path: Path) -> dict:
    nm = shutil.which("arm-none-eabi-nm")
    if not nm:
        raise RuntimeError("arm-none-eabi-nm is required")
    proc = subprocess.run([nm, "-g", str(path)], capture_output=True, text=True,
                          check=True)
    return parse_symbols(proc.stdout)


def parse_symbols(output: str) -> dict:
    definitions: dict[str, list[str]] = {}
    undefined = set()
    weak_undefined = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        kind, name = parts[-2:]
        if kind == "U":
            undefined.add(name)
        elif kind in {"w", "v"}:
            weak_undefined.add(name)
        elif kind in "TDRBSCWVA":
            definitions.setdefault(name, []).append(kind)
    duplicates = sorted(name for name, kinds in definitions.items()
                        if sum(k not in "WV" for k in kinds) > 1)
    return {"defined_symbols": sorted(definitions),
            "unresolved_symbols": sorted(undefined - definitions.keys()),
            "optional_weak_reference_symbols": sorted(weak_undefined - definitions.keys()),
            "duplicate_strong_symbols": duplicates}


def compose(archives: list[Path], output: Path, log: Path) -> dict:
    ld = shutil.which("arm-none-eabi-ld")
    if not ld:
        raise RuntimeError("arm-none-eabi-ld is required")
    receipt = command([ld, "-r", "--whole-archive", *map(str, archives),
                       "--no-whole-archive", "-o", str(output)], log)
    if receipt["returncode"] == 0:
        receipt.update(symbol_census(output))
        receipt["output"] = str(output.relative_to(ROOT))
        receipt["output_sha256"] = digest(output)
    return receipt


def experimental_arm_sources(image: str, folder: Path) -> tuple[list[Path], list[dict]]:
    manifest = json.loads((HERE / "experimental-sources.json").read_text())
    objects, receipts = [], []
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra"]
    if image == "apollo_bootloader":
        flags += ["-fshort-enums", "-fwrapv"]
    for index, source in enumerate(manifest.get(image, [])):
        path = ROOT / source
        obj = folder / f"experimental-{index:03d}.o"
        depfile = folder / f"experimental-{index:03d}.d"
        source_flags = []
        if source == "g2/components/main/full_formatter_native_candidate/fp_primitives.c":
            # Seven stock Main helpers contain authenticated double-precision
            # VFP operations; the default single-precision assembler rejects them.
            source_flags = ["-mfpu=fpv5-d16", "-Werror"]
        receipt = command(["clang", *flags, *source_flags, "-MD", "-MF", str(depfile),
                           "-c", str(path), "-o", str(obj)],
                          folder / f"experimental-{index:03d}.log")
        receipt.update(source=source, source_sha256=digest(path),
                       validation="experimental C reduction; not admitted stock-equivalent provider")
        if receipt["returncode"] == 0:
            receipt.update(object=str(obj.relative_to(ROOT)), object_sha256=digest(obj))
            deps = shlex.split(depfile.read_text().split(":", 1)[1].replace("\\\n", " "))
            receipt["header_inputs"] = {
                str(Path(dep).relative_to(ROOT)): digest(Path(dep))
                for dep in deps if Path(dep).is_relative_to(ROOT)}
            objects.append(obj)
        receipts.append(receipt)
    return objects, receipts


def arm_image(image: str, out: Path, experimental: bool = False) -> dict:
    folder = out / image
    folder.mkdir(parents=True, exist_ok=True)
    commands = []
    if image == "apollo_bootloader":
        dest = folder / "objects"
        commands.append(command([sys.executable,
            "g2/components/bootloader/source_candidate_20261010/build.py",
            "--output", str(dest)], folder / "compile.log"))
        archives = [dest / "libbootloader_source_candidate_m55.a"]
        receipt_paths = [dest / "inventory.json"]
    elif image == "apollo_main":
        # Main and Audio are two subgraphs of the same official Apollo MAIN
        # image. The Bootloader is a separate image and is never added here.
        dest = folder / "audio"
        commands.append(command([sys.executable,
            "g2/components/audio/source_candidate_20261010/build_arm_inventory.py",
            str(dest)], folder / "audio-compile.log"))
        main_out = folder / "main"
        script = (
            "import importlib.util,pathlib; "
            "s=importlib.util.spec_from_file_location('main_candidate',"
            "'g2/components/main/source_candidate_20261010/build.py'); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "m.OUT=pathlib.Path(" + repr(str(main_out)) + "); m.main()"
        )
        commands.append(command([sys.executable, "-c", script],
                                folder / "main-compile.log"))
        archives = [dest / "libaudio-source-candidates.a",
                    main_out / "main-candidates.a"]
        receipt_paths = [dest / "compile-results.json",
                         dest / "archive-selection.json", main_out / "receipt.json"]
    else:
        component = image
        builder = f"g2/components/{component}/source_candidate_20261010/build.py"
        commands.append(command([sys.executable, builder], folder / "compile.log"))
        if image == "case":
            archives = [ROOT / "g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a"]
            receipt_paths = [ROOT / "g2/analysis/case-source-candidate-round2-20261010/receipt.json"]
        else:
            archives = [ROOT / "g2/components/touch/source_candidate_20261010/build/touch-source-candidate.a"]
            receipt_paths = [ROOT / "g2/components/touch/source_candidate_20261010/build/receipt.json"]
    result = {"build_commands": commands,
              "candidate_compilation_passed": all(c["returncode"] == 0 for c in commands),
              "artifacts": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)}
                            for p in archives + receipt_paths if p.is_file()]}
    extra = []
    if experimental and image in {"apollo_main", "apollo_bootloader"}:
        extra, result["experimental_compile"] = experimental_arm_sources(image, folder)
        result["candidate_compilation_passed"] &= all(r["returncode"] == 0 for r in result["experimental_compile"])
    if result["candidate_compilation_passed"] and all(p.is_file() for p in archives):
        result["relocatable_link"] = compose(archives + extra, folder / "candidate.o",
                                             folder / "relocatable-link.log")
        result["candidate_compilation_passed"] &= result["relocatable_link"]["returncode"] == 0
    if experimental and image == "case":
        candidate = folder / "libcase_command_candidate.a"
        build = command([sys.executable,
            "g2/analysis/c-source-completion-20261011/m0/build_case_candidate.py",
            "--output", str(candidate)], folder / "experimental-compile.log")
        result["experimental_case"] = {"build_command": build,
            "validation": "Distinct full command graph; not a selected CASE provider replacement"}
        result["candidate_compilation_passed"] &= build["returncode"] == 0
        if build["returncode"] == 0:
            result["experimental_case"]["relocatable_link"] = compose(
                [candidate], folder / "experimental-case.o",
                folder / "experimental-link.log")
            receipt = candidate.with_suffix(candidate.suffix + ".receipt.json")
            result["experimental_case"]["source_receipt"] = {
                "path": str(receipt.relative_to(ROOT)), "sha256": digest(receipt)}
            result["candidate_compilation_passed"] &= result["experimental_case"]["relocatable_link"]["returncode"] == 0
            result["experimental_case"]["combined_selected_link"] = compose(
                archives + [candidate], folder / "experimental-case-combined.o",
                folder / "experimental-combined-link.log")
            result["candidate_compilation_passed"] &= result["experimental_case"]["combined_selected_link"]["returncode"] == 0
        startup_output = folder / "experimental-case-command-startup.o"
        startup_build = command([sys.executable,
            "g2/analysis/c-source-completion-20261011/m0/build_case_command_startup_experiment.py",
            "--output", str(startup_output)], folder / "experimental-command-startup.log")
        result["experimental_case"]["command_startup_build"] = startup_build
        result["candidate_compilation_passed"] &= startup_build["returncode"] == 0
        if startup_build["returncode"] == 0:
            startup_receipt = startup_output.with_suffix(startup_output.suffix + ".receipt.json")
            result["experimental_case"]["command_startup_artifact"] = {
                "path": str(startup_output.relative_to(ROOT)), "sha256": digest(startup_output),
                "receipt_path": str(startup_receipt.relative_to(ROOT)),
                "receipt_sha256": digest(startup_receipt),
                "validation": "Combined experimental command and startup graph; final native layout remains unqualified"}
        absolute_output = folder / "experimental-case.elf"
        absolute_build = command([sys.executable,
            "g2/analysis/c-source-completion-20261011/m0/build_case_absolute_experiment.py",
            "--output", str(absolute_output)], folder / "experimental-absolute-link.log")
        result["experimental_case"]["absolute_build"] = absolute_build
        result["candidate_compilation_passed"] &= absolute_build["returncode"] == 0
        if absolute_build["returncode"] == 0:
            result["experimental_case"]["absolute_artifact"] = {
                "path": str(absolute_output.relative_to(ROOT)), "sha256": digest(absolute_output),
                "validation": "Standalone experimental source ELF; stock layout and hardware operation unqualified"}
    return result


def codec_image(out: Path, experimental: bool = False) -> dict:
    folder = out / "codec"
    folder.mkdir(parents=True, exist_ok=True)
    tool = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
    compiler = tool / "bin/csky-abiv2-elf-gcc"
    if not compiler.is_file() or not shutil.which("docker"):
        return {"candidate_compilation_passed": False,
                "blocked_by": "Retained qualified C-SKY compiler or Docker missing"}
    prefix = [shutil.which("docker"), "run", "--rm", "--network=none",
              "--read-only", "--platform", "linux/amd64", "--mount",
              f"type=bind,src={tool},dst=/tool,readonly", "--mount",
              f"type=bind,src={ROOT},dst=/repo,readonly", "--mount",
              f"type=bind,src={folder},dst=/out", "--tmpfs", "/tmp:rw",
              "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-gcc"]
    sdk = "third-party/upstream/nationalchip-lvp-kws"
    flags = ["-mcpu=ck804ef", "-mhard-float", "-O2", "-fno-builtin",
             "-fstrict-volatile-bitfields", "-ffunction-sections", "-fdata-sections"]
    includes = ["-I/repo/" + sdk + "/" + x for x in
                ["include/utility/libdsp", "include", "arch/soc/grus/include", "include/utility"]]
    sources = ["TransformFunctions/" + x + ".c" for x in
               ["csky_cfft_radix4_q15", "csky_rfft_q15", "csky_radix4_butterfly_q15",
                "csky_split_rfft_q15", "csky_bitreversal", "csky_cfft_q15", "csky_cfft_radix4by2_q15"]]
    sources += ["BasicMathFunctions/csky_shift_q15.c", "SupportFunctions/csky_copy_q15.c",
                "SupportFunctions/csky_fill_q15.c"]
    commands, inputs, header_inputs, objects = [], {}, {}, []
    source_paths = [sdk + "/utility/libdsp/Source/" + source for source in sources]
    if experimental:
        source_paths.append("g2/components/gx8002/app_callback_candidate/callbacks.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/board_uart.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/request_send.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/queue_full.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/queue_read.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/uart_message_start.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/channel_runtime.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_irq.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_cache.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_queue.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_timestamp.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_small.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_discover.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_commands.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_transfer.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_protect.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_range.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_xip.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_platform_config.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_platform_read.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_platform_gate.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_queries.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_frequency.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_divider_dto.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_module_source.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_lowpower.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_timer_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_tws_tick.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_memset.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_tws_audio_callback.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_audio_record_callback.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_audio_irq.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_audio_irq_entry.S")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_queue_get.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_tws_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_tws_context.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_tws_buffer_update.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_tws_buffer_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_memmove.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_vad.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_decoder.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_mode_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_mode_callbacks.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_app_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_register_power.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_watchdog.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_kws_lifecycle.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_lifecycle.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_children.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_npu_registers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_kws_flash_load.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_model_sizes.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_input.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_exit.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_ain_reset.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_config.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_board.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_register_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_config_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_digital_inputs.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_sadc.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_analog_registers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_evad.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_buffer_queries.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_modes.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_pcm.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_logfbank.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_spectrum.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_i2s.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_standby.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_buffer_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_ctc_offset_clear.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_idle_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_max_kws_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_tws_message.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_run_task.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_resume.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_npu_reset.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_npu_registers_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_npu_register_helpers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_submit.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_submit_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_main_exit.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_suspend.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_power_suspend.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_printf.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_tinyprintf.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_console_output.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_kws_strategy.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_system_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_system_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_system_dma_board.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_board_pin_setup.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_power_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_board_pin_configure.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_padmux_gpio.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_print_max_kws.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_dma_isr.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_dma_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_configure.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_fifo_depth.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_isr.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_spi_master_probe.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_spi_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_spi_quick_transfer.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_max_score.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_max_score_lowers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_async_register.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_async_initialize.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_async_lowers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_dma_abort.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_misc_native_leaves.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_read.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_receive_callback.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_body_probe.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_receive_dma_dispatch.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_dma_receive.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_dma_transfer.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_dma_configure.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_send_path.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_transmit_lowers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_transmit_dma.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_crc32_binding.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_isr.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_controls.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_config_wrappers.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_register_config.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_lodac.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_aout_config_pcm.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_audio_output_lifecycle.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_aout_suspend_resume.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_npu_interrupt_queries.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_isr.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_process_status.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_snpu_overtime.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_gpio_irq_disable.c")
        source_paths.extend(
            f"third-party/upstream/llvm-compiler-rt-format-20.1.8/{name}.c"
            for name in ("adddf3", "divdf3", "fixunsdfsi", "floatunsidf", "muldf3")
        )
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_app_ticks.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_xip_uart_async_tick.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_boot_literals.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_pll.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_voltage.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_digital_voltage_ambient.S")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_vectors_candidate.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_reset_entry_candidate.S")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_exception_entry.S")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_system_initialize_candidate.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_initialize_candidate.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_main_candidate.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_board_init.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_interface_support.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_interface.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_program_erase.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_otp_config.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_otp_mode.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_otp_lowpower.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_uid.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_otp_transmit.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_otp_write.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_otp_read.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_probe.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_dispatch.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_timer_runtime.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clear_bss.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_start_mode.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_memcpy.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_cache_variants.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_kws_queue.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_product_tables.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_clock_runtime_defaults.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_uart_product_descriptors.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_board_product_state.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_product_otp_data.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_flash_product_catalog.c")
        source_paths.append("g2/components/gx8002/app_callback_candidate/resident_module_product_data.c")
        source_paths.append(sdk + "/base/src/crc32.c")
    for rel in source_paths:
        source = rel
        inputs[rel] = digest(ROOT / rel)
        name = Path(source).stem + ".o"
        extra = ["-DFOR_X86_64=1"] if Path(source).stem == "csky_bitreversal" else []
        if rel.startswith("g2/components/gx8002/app_callback_candidate/") or rel == sdk + "/base/src/crc32.c":
            # Recovered headers and pinned CRC access the same RAM through byte,
            # halfword and word views; make the target compiler contract explicit.
            extra.append("-fno-strict-aliasing")
        source_includes = includes
        if rel == sdk + "/base/src/crc32.c":
            source_includes = ["-I/repo/g2/components/gx8002/app_callback_candidate/crc_port"] + includes
        depname = Path(source).stem + ".d"
        language_flags = ["-std=c11"] if Path(source).suffix == ".c" else []
        commands.append(command(prefix + flags + language_flags + source_includes + extra +
                                ["-MD", "-MF", "/out/" + depname,
                                 "-c", "/repo/" + rel, "-o", "/out/" + name],
                                folder / (name + ".log")))
        depfile = folder / depname
        if commands[-1]["returncode"] == 0 and depfile.is_file():
            deps = shlex.split(depfile.read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    header_inputs[str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    real = tool / dep.removeprefix("/tool/")
                    header_inputs[dep] = digest(real)
        objects.append("/out/" + name)
    changed_sources = sorted(rel for rel, sha in inputs.items() if digest(ROOT / rel) != sha)
    result = {"build_commands": commands, "source_inputs": inputs, "header_inputs": header_inputs,
              "source_snapshot_coherent_at_link": not changed_sources,
              "sources_changed_after_compile": changed_sources,
              "compiler_sha256": digest(compiler), "candidate_compilation_passed":
              all(c["returncode"] == 0 for c in commands) and not changed_sources,
              "configuration_note": "FOR_X86_64 enables generic C bitreversal bodies on C-SKY; not the stock producing recipe"}
    if result["candidate_compilation_passed"]:
        link = command(prefix + ["-mcpu=ck804ef", "-mhard-float", "-nostdlib",
                       "-nostartfiles", "-Wl,-r", "-Wl,-A,ck803", *objects,
                       "-o", "/out/candidate.o"],
                       folder / "relocatable-link.log")
        result["relocatable_link"] = link
        result["candidate_compilation_passed"] &= link["returncode"] == 0
        if link["returncode"] == 0:
            result["output_sha256"] = digest(folder / "candidate.o")
            census = command(prefix[:-1] + ["/tool/bin/csky-abiv2-elf-nm", "-g",
                             "/out/candidate.o"], folder / "symbols.log")
            link["symbol_command"] = census
            if census["returncode"] == 0:
                link.update(parse_symbols((folder / "symbols.log").read_text()))
    if experimental:
        # UART boot stage 1 is a distinct loaded program, not a resident
        # translation unit of image-A stage 2. Keep its candidate separate.
        stage1_sources = [
            "g2/components/gx8002/app_callback_candidate/uart_stage1_io.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_pmu_bits.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_bringup.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_xip.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_handshake.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_rail.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_delay.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_startup_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_reset.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_pmu_desc.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_config.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_postamble.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_pmu_bit_modify.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_division.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_beacon.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_announce.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_transfer.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_minimal_stock.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_railc.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_railb.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_pmu_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_raila.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_clock_rate.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage1_pmu_data.c",
        ]
        stage1_commands = []
        for rel in stage1_sources:
            stage1_commands.append(command(prefix + flags + ["-std=c11", "-Wall",
                "-Wextra", "-Werror", "-c", "/repo/" + rel, "-o",
                "/out/" + Path(rel).stem + ".o"],
                folder / (Path(rel).stem + ".log")))
        result["uart_stage1_candidate"] = {
            "sources": {rel: digest(ROOT / rel) for rel in stage1_sources},
            "build_commands": stage1_commands,
            "compiled": all(c["returncode"] == 0 for c in stage1_commands),
            "separate_loaded_stage": True,
            "covered_stock_bodies": 31,
            "additional_unseeded_stock_bodies": ["0x100001bc", "0x100003bc",
                                                 "0x10001bf8", "0x10000ea0"],
            "retained_decompiled_stage1_bodies": 32,
        }
        stage2_sources = [
            "g2/components/gx8002/app_callback_candidate/uart_stage2_reset.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_reset_children.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_init_clock.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_small.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_app_setup.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_clock_subinit.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_request_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_console.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_uart.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_format_engine.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_format_number.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_cache.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pmu_desc.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pmu_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pmu_data.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_lookup.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_uart_helpers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_callback_helpers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_control_helpers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_cache_ranges.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_help.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_setup.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_uart_apply.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pmu_bit_modify.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_clock_rate.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_raila.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_railb.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_railc.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_resource.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_start.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_handlers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_hardware.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_descriptors.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_program.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_init.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_timer_init.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_service.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pin_boot.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pin_config.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_package_pool.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_console_string.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_helpers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_data.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_reboot.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_watchdog_reset.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_watchdog_kick.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_help_entry.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_wdt.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_watchdog_callback.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_watchdog_configure.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_watchdog_irq.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_parse_unsigned.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pool_allocator.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_uart_isr.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_report.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_repl.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_io.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_backspace.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_shell_line_editor.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_flash.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_flash_descriptor.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pool_wrappers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_serialdown_helpers.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_command_serialdown.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_crc.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pool_free_dispatch.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pool_alloc_core.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_pool_free_core.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_gap_small.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_spi_io.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_limb.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_spi_erase.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_spi_page_write.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_unpack.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_compare.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_compare_words.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_to_int.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_irq_hardware_alt.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_pack.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_from_uint.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_add_internal.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_add_words.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_to_uint.c",
            "g2/components/gx8002/app_callback_candidate/uart_stage2_fp_mul_div.c",
        ]
        stage2_commands = [command(prefix + flags + ["-std=c11", "-Wall", "-Wextra",
            "-Werror", "-c", "/repo/" + rel,
            "-o", "/out/" + Path(rel).stem + ".o"],
            folder / (Path(rel).stem + ".o.log")) for rel in stage2_sources]
        result["uart_stage2_reset_candidate"] = {
            "sources": {rel: digest(ROOT / rel) for rel in stage2_sources},
            "build_commands": stage2_commands,
            "compiled": all(c["returncode"] == 0 for c in stage2_commands),
            "separate_loaded_stage": True, "stock_entry": "0x10002900",
        }
        # Image-B SRAM is a separate loaded program. Its C-SKY source and
        # unresolved contracts must not be linked into image-A candidate.o.
        image_b_builder = (ROOT / "g2/analysis/c-source-completion-20261011/codec/"
                           "image_b_sram_candidate/build.py")
        image_b_folder = folder / "image-b-sram"
        image_b_command = command([sys.executable, str(image_b_builder),
                                   "--output", str(image_b_folder)],
                                  folder / "image-b-sram-build.log")
        image_b = {"separate_loaded_stage": True,
                   "selected_firmware_image": False,
                   "source_complete": False,
                   "data_and_final_layout_complete": False,
                   "builder": str(image_b_builder.relative_to(ROOT)),
                   "builder_sha256": digest(image_b_builder),
                   "build_command": image_b_command,
                   "compiled": image_b_command["returncode"] == 0}
        image_b_receipt = image_b_folder / "receipt.json"
        if image_b["compiled"] and image_b_receipt.is_file():
            subreceipt = json.loads(image_b_receipt.read_text())
            stable = all(digest(ROOT / unit["source"]) == unit["source_sha256"]
                         for unit in subreceipt["units"])
            image_b.update(receipt=str(image_b_receipt.relative_to(ROOT)),
                           receipt_sha256=digest(image_b_receipt),
                           source_snapshot_coherent=stable,
                           source_inputs={unit["source"]: unit["source_sha256"]
                                          for unit in subreceipt["units"]},
                           linked_output_sha256=subreceipt["linked_object_sha256"],
                           undefined_symbols=subreceipt["undefined_symbols"])
            image_b["compiled"] &= stable
        result["image_b_sram_candidate"] = image_b
    return result


def ble_image(out: Path, include_experimental: bool = False) -> dict:
    folder = out / "ble_em9305"
    folder.mkdir(parents=True, exist_ok=True)
    source = ROOT / "g2/components/em9305/qpc_queue_candidate/qequeue_init.c"
    obj = folder / "queue-abi-model.o"
    check = command(["clang", "--target=i386-none-elf", "-std=c11",
                     "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra",
                     "-Werror", "-c", str(source), "-o", str(obj)],
                    folder / "queue-abi-model.log")
    check.update(source=str(source.relative_to(ROOT)), source_sha256=digest(source),
                 validation="32-bit field-offset compile check; not ARC firmware compilation")
    if check["returncode"] == 0:
        check.update(object_sha256=digest(obj))
    result = {"candidate_compilation_passed": False, "portable_abi_check": check}
    config = json.loads((HERE / "arc-toolchain.json").read_text())
    tool = ROOT / config["tool_path"]
    compiler = tool / "bin/arc-elf32-gcc"
    if not compiler.is_file() or not shutil.which("docker"):
        result["blocked_by"] = "Pinned ARC EM compiler missing; controller product port/source also absent"
        return result
    if digest(compiler) != config["compiler_sha256"]:
        raise RuntimeError("ARC compiler differs from the verified release binary")
    prefix = [shutil.which("docker"), "run", "--rm", "--network=none",
              "--read-only", "--platform", "linux/amd64", "--mount",
              f"type=bind,src={tool},dst=/tool,readonly", "--mount",
              f"type=bind,src={ROOT},dst=/repo,readonly", "--mount",
              f"type=bind,src={folder},dst=/out", "--tmpfs", "/tmp:rw",
              config["runtime_image"]]
    build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
        "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
        "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/queue.d",
        "-c", "/repo/" + str(source.relative_to(ROOT)), "-o", "/out/queue.o"],
        folder / "arc-compile.log")
    result.update(target_compile=build, compiler_sha256=digest(compiler),
                  toolchain_manifest_sha256=digest(HERE / "arc-toolchain.json"),
                  source_sha256=digest(source),
                  remaining_source="Producing QP/C port, controller/application source, product data and record layout")
    result["candidate_compilation_passed"] = build["returncode"] == 0
    if build["returncode"] == 0:
        deps = shlex.split((folder / "queue.d").read_text().split(":", 1)[1].replace("\\\n", " "))
        result["header_inputs"] = {}
        for dep in deps:
            if dep.startswith("/repo/"):
                real = ROOT / dep.removeprefix("/repo/")
                result["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
            elif dep.startswith("/tool/"):
                result["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
        objects = ["/out/queue.o"]
        if include_experimental:
            scheduler = ROOT / "g2/components/em9305/qpc_scheduler_candidate/scheduler.c"
            scheduler_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/scheduler.d",
                "-c", "/repo/" + str(scheduler.relative_to(ROOT)), "-o", "/out/scheduler.o"],
                folder / "scheduler-compile.log")
            scheduler_build.update(source=str(scheduler.relative_to(ROOT)), source_sha256=digest(scheduler))
            result["experimental_scheduler_compile"] = scheduler_build
            if scheduler_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            scheduler_build["object_sha256"] = digest(folder / "scheduler.o")
            deps = shlex.split((folder / "scheduler.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            scheduler_build["header_inputs"] = {}
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    scheduler_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    scheduler_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/scheduler.o")
            port = ROOT / "g2/components/em9305/qpc_scheduler_candidate/log2p1_port.c"
            port_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/log2p1.d",
                "-c", "/repo/" + str(port.relative_to(ROOT)), "-o", "/out/log2p1.o"],
                folder / "log2p1-compile.log")
            port_build.update(source=str(port.relative_to(ROOT)), source_sha256=digest(port))
            result["experimental_log2p1_compile"] = port_build
            if port_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            port_build["object_sha256"] = digest(folder / "log2p1.o")
            deps = shlex.split((folder / "log2p1.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            port_build["header_inputs"] = {}
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    port_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    port_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            port_build["instruction_listing"] = command(prefix + ["/tool/bin/arc-elf32-objdump",
                "-d", "/out/log2p1.o"], folder / "log2p1-instructions.log")
            listing = (folder / "log2p1-instructions.log").read_text()
            port_build["stock_custom_operation_encoding_present"] = (
                port_build["instruction_listing"]["returncode"] == 0 and
                "3d2f 1000" in listing and "log2p1" in listing)
            if not port_build["stock_custom_operation_encoding_present"]:
                result["candidate_compilation_passed"] = False
                return result
            objects.append("/out/log2p1.o")
            activation = ROOT / "g2/components/em9305/qpc_scheduler_candidate/activate.c"
            activation_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/activate.d",
                "-c", "/repo/" + str(activation.relative_to(ROOT)), "-o", "/out/activate.o"],
                folder / "activate-compile.log")
            activation_build.update(source=str(activation.relative_to(ROOT)), source_sha256=digest(activation))
            result["experimental_activation_compile"] = activation_build
            if activation_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            activation_build["object_sha256"] = digest(folder / "activate.o")
            activation_build["header_inputs"] = {}
            deps = shlex.split((folder / "activate.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    activation_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    activation_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/activate.o")
            assertion = ROOT / "g2/components/em9305/qpc_scheduler_candidate/assert.c"
            assertion_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/assert.d",
                "-c", "/repo/" + str(assertion.relative_to(ROOT)), "-o", "/out/assert.o"],
                folder / "assert-compile.log")
            assertion_build.update(source=str(assertion.relative_to(ROOT)), source_sha256=digest(assertion))
            result["experimental_assertion_compile"] = assertion_build
            if assertion_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            assertion_build["object_sha256"] = digest(folder / "assert.o")
            assertion_build["header_inputs"] = {}
            deps = shlex.split((folder / "assert.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    assertion_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    assertion_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/assert.o")
            collector = ROOT / "g2/components/em9305/qpc_scheduler_candidate/event_gc.c"
            collector_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/event_gc.d",
                "-c", "/repo/" + str(collector.relative_to(ROOT)), "-o", "/out/event_gc.o"],
                folder / "event-gc-compile.log")
            collector_build.update(source=str(collector.relative_to(ROOT)), source_sha256=digest(collector))
            result["experimental_collector_compile"] = collector_build
            if collector_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            collector_build["object_sha256"] = digest(folder / "event_gc.o")
            collector_build["header_inputs"] = {}
            deps = shlex.split((folder / "event_gc.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    collector_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    collector_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/event_gc.o")
            queue_pool = ROOT / "g2/components/em9305/qpc_scheduler_candidate/queue_pool.c"
            queue_pool_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/queue_pool.d",
                "-c", "/repo/" + str(queue_pool.relative_to(ROOT)), "-o", "/out/queue_pool.o"],
                folder / "queue-pool-compile.log")
            queue_pool_build.update(source=str(queue_pool.relative_to(ROOT)), source_sha256=digest(queue_pool))
            result["experimental_queue_pool_compile"] = queue_pool_build
            if queue_pool_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            queue_pool_build["object_sha256"] = digest(folder / "queue_pool.o")
            queue_pool_build["header_inputs"] = {}
            deps = shlex.split((folder / "queue_pool.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    queue_pool_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    queue_pool_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/queue_pool.o")
            framework_init = ROOT / "g2/components/em9305/qpc_scheduler_candidate/framework_init.c"
            framework_init_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/framework_init.d",
                "-c", "/repo/" + str(framework_init.relative_to(ROOT)), "-o", "/out/framework_init.o"],
                folder / "framework-init-compile.log")
            framework_init_build.update(source=str(framework_init.relative_to(ROOT)), source_sha256=digest(framework_init))
            result["experimental_framework_init_compile"] = framework_init_build
            if framework_init_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            framework_init_build["object_sha256"] = digest(folder / "framework_init.o")
            framework_init_build["header_inputs"] = {}
            deps = shlex.split((folder / "framework_init.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    framework_init_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    framework_init_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/framework_init.o")
            memory_fill = ROOT / "g2/components/em9305/qpc_scheduler_candidate/memory_fill.c"
            memory_fill_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/memory_fill.d",
                "-c", "/repo/" + str(memory_fill.relative_to(ROOT)), "-o", "/out/memory_fill.o"],
                folder / "memory-fill-compile.log")
            memory_fill_build.update(source=str(memory_fill.relative_to(ROOT)), source_sha256=digest(memory_fill))
            result["experimental_memory_fill_compile"] = memory_fill_build
            if memory_fill_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            memory_fill_build["object_sha256"] = digest(folder / "memory_fill.o")
            memory_fill_build["header_inputs"] = {}
            deps = shlex.split((folder / "memory_fill.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    memory_fill_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    memory_fill_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/memory_fill.o")
            startup_hook = ROOT / "g2/components/em9305/qpc_scheduler_candidate/startup_hook.c"
            startup_hook_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/startup_hook.d",
                "-c", "/repo/" + str(startup_hook.relative_to(ROOT)), "-o", "/out/startup_hook.o"],
                folder / "startup-hook-compile.log")
            startup_hook_build.update(source=str(startup_hook.relative_to(ROOT)), source_sha256=digest(startup_hook))
            result["experimental_startup_hook_compile"] = startup_hook_build
            if startup_hook_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            startup_hook_build["object_sha256"] = digest(folder / "startup_hook.o")
            startup_hook_build["header_inputs"] = {}
            deps = shlex.split((folder / "startup_hook.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    startup_hook_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    startup_hook_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/startup_hook.o")
            framework_run = ROOT / "g2/components/em9305/qpc_scheduler_candidate/framework_run.c"
            framework_run_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/framework_run.d",
                "-c", "/repo/" + str(framework_run.relative_to(ROOT)), "-o", "/out/framework_run.o"],
                folder / "framework-run-compile.log")
            framework_run_build.update(source=str(framework_run.relative_to(ROOT)), source_sha256=digest(framework_run))
            result["experimental_framework_run_compile"] = framework_run_build
            if framework_run_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            framework_run_build["object_sha256"] = digest(folder / "framework_run.o")
            framework_run_build["header_inputs"] = {}
            deps = shlex.split((folder / "framework_run.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    framework_run_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    framework_run_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/framework_run.o")
            idle = ROOT / "g2/components/em9305/qpc_scheduler_candidate/idle.c"
            idle_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/idle.d",
                "-c", "/repo/" + str(idle.relative_to(ROOT)), "-o", "/out/idle.o"],
                folder / "idle-compile.log")
            idle_build.update(source=str(idle.relative_to(ROOT)), source_sha256=digest(idle))
            result["experimental_idle_compile"] = idle_build
            if idle_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            idle_build["object_sha256"] = digest(folder / "idle.o")
            idle_build["header_inputs"] = {}
            deps = shlex.split((folder / "idle.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    idle_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    idle_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/idle.o")
            resume = ROOT / "g2/components/em9305/qpc_scheduler_candidate/resume.c"
            resume_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/resume.d",
                "-c", "/repo/" + str(resume.relative_to(ROOT)), "-o", "/out/resume.o"],
                folder / "resume-compile.log")
            resume_build.update(source=str(resume.relative_to(ROOT)), source_sha256=digest(resume))
            result["experimental_resume_compile"] = resume_build
            if resume_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            resume_build["object_sha256"] = digest(folder / "resume.o")
            resume_build["header_inputs"] = {}
            deps = shlex.split((folder / "resume.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    resume_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    resume_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/resume.o")
            sleep_mode_branch = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_mode_branch.c"
            sleep_mode_branch_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_mode_branch.d",
                "-c", "/repo/" + str(sleep_mode_branch.relative_to(ROOT)), "-o", "/out/sleep_mode_branch.o"],
                folder / "sleep_mode_branch-compile.log")
            sleep_mode_branch_build.update(source=str(sleep_mode_branch.relative_to(ROOT)), source_sha256=digest(sleep_mode_branch))
            result["experimental_sleep_mode_branch_compile"] = sleep_mode_branch_build
            if sleep_mode_branch_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_mode_branch_build["object_sha256"] = digest(folder / "sleep_mode_branch.o")
            sleep_mode_branch_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_mode_branch.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_mode_branch_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_mode_branch_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_mode_branch.o")
            sleep_outer = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_outer.c"
            sleep_outer_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_outer.d",
                "-c", "/repo/" + str(sleep_outer.relative_to(ROOT)), "-o", "/out/sleep_outer.o"],
                folder / "sleep_outer-compile.log")
            sleep_outer_build.update(source=str(sleep_outer.relative_to(ROOT)), source_sha256=digest(sleep_outer))
            result["experimental_sleep_outer_compile"] = sleep_outer_build
            if sleep_outer_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_outer_build["object_sha256"] = digest(folder / "sleep_outer.o")
            sleep_outer_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_outer.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_outer_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_outer_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_outer.o")
            sleep_controller_branch = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_controller_branch.c"
            sleep_controller_branch_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_controller_branch.d",
                "-c", "/repo/" + str(sleep_controller_branch.relative_to(ROOT)), "-o", "/out/sleep_controller_branch.o"],
                folder / "sleep_controller_branch-compile.log")
            sleep_controller_branch_build.update(source=str(sleep_controller_branch.relative_to(ROOT)), source_sha256=digest(sleep_controller_branch))
            result["experimental_sleep_controller_branch_compile"] = sleep_controller_branch_build
            if sleep_controller_branch_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_controller_branch_build["object_sha256"] = digest(folder / "sleep_controller_branch.o")
            sleep_controller_branch_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_controller_branch.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_controller_branch_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_controller_branch_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_controller_branch.o")
            sleep_metadata = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_metadata.c"
            sleep_metadata_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_metadata.d",
                "-c", "/repo/" + str(sleep_metadata.relative_to(ROOT)), "-o", "/out/sleep_metadata.o"],
                folder / "sleep_metadata-compile.log")
            sleep_metadata_build.update(source=str(sleep_metadata.relative_to(ROOT)), source_sha256=digest(sleep_metadata))
            result["experimental_sleep_metadata_compile"] = sleep_metadata_build
            if sleep_metadata_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_metadata_build["object_sha256"] = digest(folder / "sleep_metadata.o")
            sleep_metadata_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_metadata.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_metadata_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_metadata_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_metadata.o")
            sleep_metadata_prepare = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_metadata_prepare.c"
            sleep_metadata_prepare_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_metadata_prepare.d",
                "-c", "/repo/" + str(sleep_metadata_prepare.relative_to(ROOT)), "-o", "/out/sleep_metadata_prepare.o"],
                folder / "sleep_metadata_prepare-compile.log")
            sleep_metadata_prepare_build.update(source=str(sleep_metadata_prepare.relative_to(ROOT)), source_sha256=digest(sleep_metadata_prepare))
            result["experimental_sleep_metadata_prepare_compile"] = sleep_metadata_prepare_build
            if sleep_metadata_prepare_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_metadata_prepare_build["object_sha256"] = digest(folder / "sleep_metadata_prepare.o")
            sleep_metadata_prepare_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_metadata_prepare.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_metadata_prepare_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_metadata_prepare_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_metadata_prepare.o")
            sleep_registered_callback = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_registered_callback.c"
            sleep_registered_callback_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_registered_callback.d",
                "-c", "/repo/" + str(sleep_registered_callback.relative_to(ROOT)), "-o", "/out/sleep_registered_callback.o"],
                folder / "sleep_registered_callback-compile.log")
            sleep_registered_callback_build.update(source=str(sleep_registered_callback.relative_to(ROOT)), source_sha256=digest(sleep_registered_callback))
            result["experimental_sleep_registered_callback_compile"] = sleep_registered_callback_build
            if sleep_registered_callback_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_registered_callback_build["object_sha256"] = digest(folder / "sleep_registered_callback.o")
            sleep_registered_callback_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_registered_callback.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_registered_callback_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_registered_callback_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_registered_callback.o")
            sleep_registry = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_registry.c"
            sleep_registry_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_registry.d",
                "-c", "/repo/" + str(sleep_registry.relative_to(ROOT)), "-o", "/out/sleep_registry.o"],
                folder / "sleep_registry-compile.log")
            sleep_registry_build.update(source=str(sleep_registry.relative_to(ROOT)), source_sha256=digest(sleep_registry))
            result["experimental_sleep_registry_compile"] = sleep_registry_build
            if sleep_registry_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_registry_build["object_sha256"] = digest(folder / "sleep_registry.o")
            sleep_registry_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_registry.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_registry_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_registry_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_registry.o")
            sleep_metadata_sync = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_metadata_sync.c"
            sleep_metadata_sync_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_metadata_sync.d",
                "-c", "/repo/" + str(sleep_metadata_sync.relative_to(ROOT)), "-o", "/out/sleep_metadata_sync.o"],
                folder / "sleep_metadata_sync-compile.log")
            sleep_metadata_sync_build.update(source=str(sleep_metadata_sync.relative_to(ROOT)), source_sha256=digest(sleep_metadata_sync))
            result["experimental_sleep_metadata_sync_compile"] = sleep_metadata_sync_build
            if sleep_metadata_sync_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_metadata_sync_build["object_sha256"] = digest(folder / "sleep_metadata_sync.o")
            sleep_metadata_sync_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_metadata_sync.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_metadata_sync_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_metadata_sync_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_metadata_sync.o")
            sleep_sync_query = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_query.c"
            sleep_sync_query_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_sync_query.d",
                "-c", "/repo/" + str(sleep_sync_query.relative_to(ROOT)), "-o", "/out/sleep_sync_query.o"],
                folder / "sleep_sync_query-compile.log")
            sleep_sync_query_build.update(source=str(sleep_sync_query.relative_to(ROOT)), source_sha256=digest(sleep_sync_query))
            result["experimental_sleep_sync_query_compile"] = sleep_sync_query_build
            if sleep_sync_query_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_sync_query_build["object_sha256"] = digest(folder / "sleep_sync_query.o")
            sleep_sync_query_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_sync_query.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_sync_query_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_sync_query_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_sync_query.o")
            sleep_sync_restore = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_restore.c"
            sleep_sync_restore_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_sync_restore.d",
                "-c", "/repo/" + str(sleep_sync_restore.relative_to(ROOT)), "-o", "/out/sleep_sync_restore.o"],
                folder / "sleep_sync_restore-compile.log")
            sleep_sync_restore_build.update(source=str(sleep_sync_restore.relative_to(ROOT)), source_sha256=digest(sleep_sync_restore))
            result["experimental_sleep_sync_restore_compile"] = sleep_sync_restore_build
            if sleep_sync_restore_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_sync_restore_build["object_sha256"] = digest(folder / "sleep_sync_restore.o")
            sleep_sync_restore_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_sync_restore.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_sync_restore_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_sync_restore_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_sync_restore.o")
            sleep_sync_update = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_update.c"
            sleep_sync_update_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_sync_update.d",
                "-c", "/repo/" + str(sleep_sync_update.relative_to(ROOT)), "-o", "/out/sleep_sync_update.o"],
                folder / "sleep_sync_update-compile.log")
            sleep_sync_update_build.update(source=str(sleep_sync_update.relative_to(ROOT)), source_sha256=digest(sleep_sync_update))
            result["experimental_sleep_sync_update_compile"] = sleep_sync_update_build
            if sleep_sync_update_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_sync_update_build["object_sha256"] = digest(folder / "sleep_sync_update.o")
            sleep_sync_update_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_sync_update.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_sync_update_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_sync_update_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_sync_update.o")
            sleep_sync_convert = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_convert.c"
            sleep_sync_convert_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_sync_convert.d",
                "-c", "/repo/" + str(sleep_sync_convert.relative_to(ROOT)), "-o", "/out/sleep_sync_convert.o"],
                folder / "sleep_sync_convert-compile.log")
            sleep_sync_convert_build.update(source=str(sleep_sync_convert.relative_to(ROOT)), source_sha256=digest(sleep_sync_convert))
            result["experimental_sleep_sync_convert_compile"] = sleep_sync_convert_build
            if sleep_sync_convert_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_sync_convert_build["object_sha256"] = digest(folder / "sleep_sync_convert.o")
            sleep_sync_convert_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_sync_convert.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_sync_convert_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_sync_convert_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_sync_convert.o")
            sleep_sync_divide = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_sync_divide.c"
            sleep_sync_divide_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_sync_divide.d",
                "-c", "/repo/" + str(sleep_sync_divide.relative_to(ROOT)), "-o", "/out/sleep_sync_divide.o"],
                folder / "sleep_sync_divide-compile.log")
            sleep_sync_divide_build.update(source=str(sleep_sync_divide.relative_to(ROOT)), source_sha256=digest(sleep_sync_divide))
            result["experimental_sleep_sync_divide_compile"] = sleep_sync_divide_build
            if sleep_sync_divide_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_sync_divide_build["object_sha256"] = digest(folder / "sleep_sync_divide.o")
            sleep_sync_divide_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_sync_divide.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_sync_divide_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_sync_divide_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_sync_divide.o")
            sleep_queries = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_queries.c"
            sleep_queries_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_queries.d",
                "-c", "/repo/" + str(sleep_queries.relative_to(ROOT)), "-o", "/out/sleep_queries.o"],
                folder / "sleep_queries-compile.log")
            sleep_queries_build.update(source=str(sleep_queries.relative_to(ROOT)), source_sha256=digest(sleep_queries))
            result["experimental_sleep_queries_compile"] = sleep_queries_build
            if sleep_queries_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_queries_build["object_sha256"] = digest(folder / "sleep_queries.o")
            sleep_queries_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_queries.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_queries_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_queries_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_queries.o")
            sleep_clock = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_clock.c"
            sleep_clock_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_clock.d",
                "-c", "/repo/" + str(sleep_clock.relative_to(ROOT)), "-o", "/out/sleep_clock.o"],
                folder / "sleep_clock-compile.log")
            sleep_clock_build.update(source=str(sleep_clock.relative_to(ROOT)), source_sha256=digest(sleep_clock))
            result["experimental_sleep_clock_compile"] = sleep_clock_build
            if sleep_clock_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_clock_build["object_sha256"] = digest(folder / "sleep_clock.o")
            sleep_clock_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_clock.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_clock_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_clock_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_clock.o")
            sleep_controller_mode = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_controller_mode.c"
            sleep_controller_mode_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_controller_mode.d",
                "-c", "/repo/" + str(sleep_controller_mode.relative_to(ROOT)), "-o", "/out/sleep_controller_mode.o"],
                folder / "sleep_controller_mode-compile.log")
            sleep_controller_mode_build.update(source=str(sleep_controller_mode.relative_to(ROOT)), source_sha256=digest(sleep_controller_mode))
            result["experimental_sleep_controller_mode_compile"] = sleep_controller_mode_build
            if sleep_controller_mode_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_controller_mode_build["object_sha256"] = digest(folder / "sleep_controller_mode.o")
            sleep_controller_mode_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_controller_mode.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_controller_mode_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_controller_mode_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_controller_mode.o")
            sleep_mode_ready = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_mode_ready.c"
            sleep_mode_ready_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_mode_ready.d",
                "-c", "/repo/" + str(sleep_mode_ready.relative_to(ROOT)), "-o", "/out/sleep_mode_ready.o"],
                folder / "sleep_mode_ready-compile.log")
            sleep_mode_ready_build.update(source=str(sleep_mode_ready.relative_to(ROOT)), source_sha256=digest(sleep_mode_ready))
            result["experimental_sleep_mode_ready_compile"] = sleep_mode_ready_build
            if sleep_mode_ready_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_mode_ready_build["object_sha256"] = digest(folder / "sleep_mode_ready.o")
            sleep_mode_ready_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_mode_ready.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_mode_ready_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_mode_ready_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_mode_ready.o")
            sleep_refresh = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_refresh.c"
            sleep_refresh_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_refresh.d",
                "-c", "/repo/" + str(sleep_refresh.relative_to(ROOT)), "-o", "/out/sleep_refresh.o"],
                folder / "sleep_refresh-compile.log")
            sleep_refresh_build.update(source=str(sleep_refresh.relative_to(ROOT)), source_sha256=digest(sleep_refresh))
            result["experimental_sleep_refresh_compile"] = sleep_refresh_build
            if sleep_refresh_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_refresh_build["object_sha256"] = digest(folder / "sleep_refresh.o")
            sleep_refresh_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_refresh.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_refresh_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_refresh_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_refresh.o")
            sleep_slot_update = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_slot_update.c"
            sleep_slot_update_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_slot_update.d",
                "-c", "/repo/" + str(sleep_slot_update.relative_to(ROOT)), "-o", "/out/sleep_slot_update.o"],
                folder / "sleep_slot_update-compile.log")
            sleep_slot_update_build.update(source=str(sleep_slot_update.relative_to(ROOT)), source_sha256=digest(sleep_slot_update))
            result["experimental_sleep_slot_update_compile"] = sleep_slot_update_build
            if sleep_slot_update_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_slot_update_build["object_sha256"] = digest(folder / "sleep_slot_update.o")
            sleep_slot_update_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_slot_update.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_slot_update_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_slot_update_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_slot_update.o")
            sleep_program_slot = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_program_slot.c"
            sleep_program_slot_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_program_slot.d",
                "-c", "/repo/" + str(sleep_program_slot.relative_to(ROOT)), "-o", "/out/sleep_program_slot.o"],
                folder / "sleep_program_slot-compile.log")
            sleep_program_slot_build.update(source=str(sleep_program_slot.relative_to(ROOT)), source_sha256=digest(sleep_program_slot))
            result["experimental_sleep_program_slot_compile"] = sleep_program_slot_build
            if sleep_program_slot_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_program_slot_build["object_sha256"] = digest(folder / "sleep_program_slot.o")
            sleep_program_slot_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_program_slot.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_program_slot_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_program_slot_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_program_slot.o")
            sleep_enter_mode = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_enter_mode.c"
            sleep_enter_mode_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_enter_mode.d",
                "-c", "/repo/" + str(sleep_enter_mode.relative_to(ROOT)), "-o", "/out/sleep_enter_mode.o"],
                folder / "sleep_enter_mode-compile.log")
            sleep_enter_mode_build.update(source=str(sleep_enter_mode.relative_to(ROOT)), source_sha256=digest(sleep_enter_mode))
            result["experimental_sleep_enter_mode_compile"] = sleep_enter_mode_build
            if sleep_enter_mode_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_enter_mode_build["object_sha256"] = digest(folder / "sleep_enter_mode.o")
            sleep_enter_mode_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_enter_mode.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_enter_mode_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_enter_mode_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_enter_mode.o")
            sleep_rom_bindings = ROOT / "g2/components/em9305/qpc_scheduler_candidate/sleep_rom_bindings.c"
            sleep_rom_bindings_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/sleep_rom_bindings.d",
                "-c", "/repo/" + str(sleep_rom_bindings.relative_to(ROOT)), "-o", "/out/sleep_rom_bindings.o"],
                folder / "sleep_rom_bindings-compile.log")
            sleep_rom_bindings_build.update(source=str(sleep_rom_bindings.relative_to(ROOT)), source_sha256=digest(sleep_rom_bindings))
            result["experimental_sleep_rom_bindings_compile"] = sleep_rom_bindings_build
            if sleep_rom_bindings_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            sleep_rom_bindings_build["object_sha256"] = digest(folder / "sleep_rom_bindings.o")
            sleep_rom_bindings_build["header_inputs"] = {}
            deps = shlex.split((folder / "sleep_rom_bindings.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    sleep_rom_bindings_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    sleep_rom_bindings_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/sleep_rom_bindings.o")
            controller_init = ROOT / "g2/components/em9305/qpc_scheduler_candidate/controller_init.c"
            controller_init_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/controller_init.d",
                "-c", "/repo/" + str(controller_init.relative_to(ROOT)), "-o", "/out/controller_init.o"],
                folder / "controller_init-compile.log")
            controller_init_build.update(source=str(controller_init.relative_to(ROOT)), source_sha256=digest(controller_init))
            result["experimental_controller_init_compile"] = controller_init_build
            if controller_init_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            controller_init_build["object_sha256"] = digest(folder / "controller_init.o")
            controller_init_build["header_inputs"] = {}
            deps = shlex.split((folder / "controller_init.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    controller_init_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    controller_init_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/controller_init.o")
            controller_timer_helpers = ROOT / "g2/components/em9305/qpc_scheduler_candidate/controller_timer_helpers.c"
            controller_timer_helpers_build = command(prefix + ["/tool/bin/arc-elf32-gcc", "-mcpu=arcem",
                "-mcode-density", "-std=c11", "-ffreestanding", "-fno-builtin",
                "-O2", "-fno-strict-aliasing", "-Wall", "-Wextra", "-Werror", "-MD", "-MF", "/out/controller_timer_helpers.d",
                "-c", "/repo/" + str(controller_timer_helpers.relative_to(ROOT)), "-o", "/out/controller_timer_helpers.o"],
                folder / "controller_timer_helpers-compile.log")
            controller_timer_helpers_build.update(source=str(controller_timer_helpers.relative_to(ROOT)), source_sha256=digest(controller_timer_helpers))
            result["experimental_controller_timer_helpers_compile"] = controller_timer_helpers_build
            if controller_timer_helpers_build["returncode"] != 0:
                result["candidate_compilation_passed"] = False
                return result
            controller_timer_helpers_build["object_sha256"] = digest(folder / "controller_timer_helpers.o")
            controller_timer_helpers_build["header_inputs"] = {}
            deps = shlex.split((folder / "controller_timer_helpers.d").read_text().split(":", 1)[1].replace("\\\n", " "))
            for dep in deps:
                if dep.startswith("/repo/"):
                    real = ROOT / dep.removeprefix("/repo/")
                    controller_timer_helpers_build["header_inputs"][str(real.relative_to(ROOT))] = digest(real)
                elif dep.startswith("/tool/"):
                    controller_timer_helpers_build["header_inputs"][dep] = digest(tool / dep.removeprefix("/tool/"))
            objects.append("/out/controller_timer_helpers.o")

        link = command(prefix + ["/tool/bin/arc-elf32-ld", "-r", *objects,
                       "-o", "/out/candidate.o"], folder / "relocatable-link.log")
        result["relocatable_link"] = link
        result["candidate_compilation_passed"] &= link["returncode"] == 0
        if link["returncode"] == 0:
            output = folder / "candidate.o"
            header = output.read_bytes()[:52]
            result["arc_em_elf32_little_endian"] = (
                header[:6] == b"\x7fELF\x01\x01" and
                int.from_bytes(header[18:20], "little") == 195)
            result["candidate_compilation_passed"] &= result["arc_em_elf32_little_endian"]
            link["output_sha256"] = digest(output)
            nm = command(prefix + ["/tool/bin/arc-elf32-nm", "-g", "/out/candidate.o"],
                         folder / "symbols.log")
            if nm["returncode"] == 0:
                link.update(parse_symbols((folder / "symbols.log").read_text()))
            result["target_attributes"] = command(prefix + ["/tool/bin/arc-elf32-readelf",
                "-h", "-A", "/out/candidate.o"], folder / "target-attributes.log")
            result["arc_em_target_attributes_verified"] = (
                result["target_attributes"]["returncode"] == 0 and
                "Tag_ARC_CPU_base: ARCEM" in (folder / "target-attributes.log").read_text())
            result["candidate_compilation_passed"] &= result["arc_em_target_attributes_verified"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="append", choices=[
        "apollo_bootloader", "apollo_main", "case", "touch", "ble_em9305", "codec"])
    parser.add_argument("--output", type=Path, default=ROOT / "g2/build/c-firmware/latest")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--include-experimental", action="store_true",
                        help="Also build experimental Boot, Main/Audio, CASE, codec and ARC scheduler C bodies; behavioral admission remains open")
    args = parser.parse_args()
    target = json.loads((ROOT / "g2/workflow/target.json").read_text())
    gates = json.loads((HERE / "source-gates.json").read_text())
    out = args.output.resolve()
    if not out.is_relative_to(ROOT):
        parser.error("output must be inside the repository for relative provenance")
    out.mkdir(parents=True, exist_ok=True)
    images = args.image or [c["id"] for c in target["components"]]
    results = {}
    for image in images:
        print(f"Building {image}", flush=True)
        try:
            if image in {"apollo_bootloader", "apollo_main", "case", "touch"}:
                result = arm_image(image, out, args.include_experimental)
            elif image == "codec":
                result = codec_image(out, args.include_experimental)
            else:
                result = ble_image(out, args.include_experimental)
            result["source_gates"] = gates[image]
            result["source_complete"] = False
            result["full_payload_linked"] = False
            results[image] = result
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            results[image] = {"candidate_compilation_passed": False,
                             "source_complete": False, "error": str(exc),
                             "source_gates": gates[image], "full_payload_linked": False}
        print(json.dumps({"image": image, "candidate_compilation_passed":
                          results[image]["candidate_compilation_passed"],
                          "source_complete": False}), flush=True)
    receipt = {"captured_utc": datetime.now(timezone.utc).isoformat(),
               "target_id": target["target_id"], "target_sha256": digest(ROOT / "g2/workflow/target.json"),
               "source_gate_sha256": digest(HERE / "source-gates.json"),
               "experimental_source_manifest_sha256": digest(HERE / "experimental-sources.json"),
               "builder_sha256": digest(Path(__file__).resolve()), "images": results,
               "complete_source_payloads": 0,
               "limits": ["No official payload bytes are consumed by this coordinator",
                          "Imports and data/layout ownership remain distinct source gates",
                          "Compilation does not establish stock equivalence or hardware operation"]}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if args.require_complete:
        return 2 if any(not r["source_complete"] for r in results.values()) else 0
    return 1 if any(not r["candidate_compilation_passed"] for r in results.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
