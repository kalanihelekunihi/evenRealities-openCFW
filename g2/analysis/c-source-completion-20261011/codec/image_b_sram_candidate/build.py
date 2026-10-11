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
           "backup_platform_gate.c", "backup_audio_i2s.c",
           "backup_audio_start.c", "backup_audio_mode.c",
           "backup_audio_channels.c", "backup_audio_capture.c",
           "backup_audio_irq.c", "backup_audio_paths.c",
           "backup_audio_buffers.c", "backup_audio_input_route.c",
           "backup_audio_sadc.c", "backup_audio_timer.c",
           "backup_audio_pdm.c", "backup_audio_triplet.c",
           "backup_irq_mask.c", "backup_dma_release.c",
           "backup_dma_abort.c", "backup_dma_callbacks.c",
           "backup_dma_irq.c", "backup_dma_initialize.c",
           "backup_dcache_mode.c", "backup_dcache_range.c",
           "backup_dma_select.c", "backup_dma_descriptors.c",
           "backup_dma_configure.c", "backup_dma_transfer.c",
           "backup_memory_controller.c", "backup_uart_dma_complete.c",
           "backup_uart_dma_abort.c", "backup_uart_abort_route.c",
           "backup_uart_interrupt_control.c", "backup_uart_poll_io.c",
           "backup_platform_status.c", "backup_uart_fifo_depth.c",
           "backup_clock_frequency.c", "backup_uart_debug_putchar.c",
           "backup_flash_irq.c", "backup_flash_transfer.c",
           "backup_flash_status.c", "backup_flash_erase.c",
           "backup_flash_command_frame.c", "backup_flash_protection.c",
           "backup_flash_status_lookup.c", "backup_flash_status_apply.c",
           "backup_flash_probe.c", "backup_flash_profile_data.c",
           "backup_spi_pin_control.c", "backup_spi_master_registry.c",
           "backup_rtc_reset.c", "backup_spi_irq.c",
           "backup_audio_frame_state.c", "backup_audio_frame_helpers.c",
           "backup_audio_ring.c", "backup_audio_resource_controls.c",
           "backup_audio_resource_records.c", "backup_runtime_copy.c",
           "backup_runtime_move.c", "backup_runtime_state_init.c",
           "backup_runtime_debug_route.c", "backup_runtime_heap_init.c",
           "backup_runtime_printf.c", "backup_runtime_heap_coalesce.c",
           "backup_runtime_heap_alloc.c", "backup_runtime_heap_calloc.c",
           "backup_runtime_heap_free.c", "backup_runtime_heap_realloc.c",
           "backup_runtime_alloc_alias.c", "backup_audio_channel_prepare.c",
           "backup_audio_vad_policy.c"]
RUNTIME_SOURCE_DIR = ROOT / "third-party/upstream/llvm-compiler-rt-format-20.1.8"
SOURCES += [RUNTIME_SOURCE_DIR / name for name in (
    "adddf3.c", "subdf3.c", "muldf3.c", "divdf3.c",
    "fixdfsi.c", "fixunsdfsi.c", "floatsidf.c", "floatunsidf.c",
    "comparedf2.c", "udivdi3.c", "umoddi3.c")]
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
        source_before = sha(source)
        cmd = prefix + ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
                        "-mhard-float", "-O2", "-fno-builtin", "-std=c11",
                        "-Wall", "-Wextra", "-Werror",
                        "-I/repo/" + SDK + "/arch/soc/grus/include",
                        "-I/repo/" + SDK + "/include",
                        "-I/repo/" + SDK + "/include/utility/libc",
                        "-I/repo/g2/components/gx8002/image_b_sram_candidate",
                        "-c",
                        "/repo/" + str(source.relative_to(ROOT)), "-o", "/out/" + obj.name]
        subprocess.run(cmd, check=True)
        source_after = sha(source)
        if source_before != source_after:
            raise RuntimeError(f"source changed during image-B compile: {source}")
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": source_after,
                      "object": str(obj), "object_sha256": sha(obj)})
    for unit in units:
        if sha(ROOT / unit["source"]) != unit["source_sha256"]:
            raise RuntimeError(f"source changed before image-B link: {unit['source']}")
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
