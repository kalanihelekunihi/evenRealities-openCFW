#!/usr/bin/env python3
"""Compile the separate GX8002 image-B SRAM candidate; no selected-manifest edit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import shutil

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
SOURCE_DIR = ROOT / "g2/components/gx8002/image_b_sram_candidate"
SDK = "third-party/upstream/nationalchip-lvp-kws"
SOURCES = ["backup_beamforming_process_core_entry.c", "backup_beamforming_core_entry_bindings.c", "backup_beamforming_process_whole_candidate.c", "backup_beamforming_process_post_ring.c", "backup_beamforming_process_frame_loop.c", "backup_beamforming_process_frame_state.c", "backup_beamforming_process_channel_loop.c", "backup_beamforming_process_output_finish.c", "backup_beamforming_process_overlap_add.c", "backup_beamforming_process_channel_fft.c", "backup_beamforming_process_output_prepare.c", "backup_beamforming_process_adapt_stage.c", "backup_beamforming_process_coeff_update.c", "backup_beamforming_process_block_scale.c", "backup_beamforming_process_energy_stat.c", "backup_beamforming_process_matrix_stage.c", "backup_beamforming_complex_block_dot.c", "backup_beamforming_complex_matrix_product.c", "backup_beamforming_process_residual.c", "backup_beamforming_process_pack.c", "backup_beamforming_process_diagonal.c", "backup_beamforming_process_ring_average.c", "backup_beamforming_process_thresholds.c", "backup_beamforming_energy_whole_candidate.c", "backup_beamforming_energy_gain_numeric.c", "backup_beamforming_energy_smoothing.c", "backup_beamforming_energy_prefix.c", "backup_beamforming_complex_rows.c", "backup_beamforming_complex_matrix.c", "backup_beamforming_complex_negative_ratio.c", "backup_beamforming_complex_ratio.c", "backup_beamforming_process_prepare.c", "backup_beamforming_process_band.c", "backup_beamforming_process_dimensions.c", "backup_beamforming_create_whole_candidate.c", "backup_beamforming_create_overlap.c", "backup_beamforming_create_temp.c", "backup_beamforming_create_window.c", "backup_beamforming_create_buffers.c", "backup_beamforming_create_angles.c", "backup_beamforming_create_allocations.c", "backup_beamforming_create_prefix.c", "backup_beamforming_angle_whole_candidate.c", "backup_beamforming_angle_phase_table.c", "backup_beamforming_angle_table.c", "backup_beamforming_angle_linear_sweep.c", "backup_beamforming_angle_sweep.c", "backup_beamforming_angle_normalize.c", "backup_beamforming_reciprocal.S", "backup_beamforming_angle_phase_vectors.c", "backup_beamforming_angle_nonzero_mode.c", "backup_beamforming_angle_sine_matrix.c", "backup_beamforming_angle_spacing.c", "backup_beamforming_angle_geometry.c", "backup_beamforming_angle_allocations.c", "backup_beamforming_angle_entry.c", "backup_floor_scalbn_double.c", "backup_kernel_rem_pio2_fdlibm.c", "backup_rem_pio2_fdlibm.c", "backup_fabs_double.c", "backup_trigonometry_kernel.c", "backup_trigonometry_fdlibm.c", "backup_beamforming_process_wrapper.c", "backup_beamforming_create_wrapper.c", "backup_denoise_beamforming_init.c", "backup_imcra_layout.c", "backup_runtime_divide_u64_u32.c", "backup_imcra_allocation_size.c", "backup_clock_tables.c", "backup_initialized_runtime_data.c", "backup_crt_clear_bss.c", "backup_address_string.c", "backup_audio_curves.c",
           "backup_audio_state.c", "backup_audio_control.c",
           "backup_analog_controls.c", "backup_audio_init.c",
           "backup_runtime_helpers.c", "backup_audio_prepare.c",
           "backup_platform_gate.c", "backup_audio_i2s.c",
           "backup_platform_read.c",
           "backup_platform_write.c",
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
           "backup_audio_out_table_native_leaves.c",
           "backup_audio_out_table_config.c",
           "backup_audio_out_db_curve.c",
           "backup_audio_out_irq_init.c",
           "backup_audio_out_pcm_config.c",
           "backup_audio_out_initialized_data.c",
           "backup_audio_out_callback_table_candidate.c",
           "backup_audio_ring.c", "backup_audio_resource_controls.c",
           "backup_audio_resource_records.c", "backup_runtime_copy.c",
           "backup_runtime_move.c", "backup_runtime_state_init.c",
           "backup_runtime_debug_route.c", "backup_runtime_heap_init.c",
           "backup_runtime_printf.c", "backup_runtime_heap_coalesce.c",
           "backup_runtime_heap_alloc.c", "backup_runtime_heap_calloc.c",
           "backup_runtime_heap_free.c", "backup_runtime_heap_realloc.c",
           "backup_runtime_alloc_alias.c", "backup_audio_channel_prepare.c",
           "backup_audio_vad_policy.c", "backup_clock_module_select.c",
           "backup_audio_registration.c", "backup_audio_record_callback.c",
           "backup_audio_pcm_control.c", "backup_audio_gain_log.c",
           "backup_audio_config_callback.c", "backup_boot_slot_toggle.c",
           "backup_uart_width_code.c", "backup_audio_registration_table.c",
           "backup_crc32.c", "backup_audio_registration_dispatch.c",
           "backup_audio_uart_tx_start.c", "backup_audio_uart_packet_send.c",
           "backup_audio_uart_segment_send.c", "backup_uart_dma_send.c",
           "backup_uart_dma_apply.c", "backup_uart_dma_apply_ambient_entry.c", "backup_audio_uart_dma_complete.c",
           "backup_audio_uart_tx_complete.c", "backup_uart_dma_receive.c",
           "backup_uart_dma_receive_apply.c",
           "backup_audio_uart_receive_packet.c", "backup_native_zero_word_read_experiment.c",
           "backup_audio_uart_rx_dma_complete.c",
           "backup_audio_uart_rx_irq.c", "backup_audio_uart_shutdown.c",
           "backup_audio_uart_open.c", "backup_audio_uart_suspend_resume.c",
           "backup_uart_configure.c", "backup_uart_apply.c",
           "backup_uart_irq.c", "backup_audio_uart_ring_enqueue.c",
           "backup_denoise_state_init.c", "backup_imcra_state_init.c",
           "backup_imcra_cosine_lookup.c", "backup_runtime_extend_float.c",
           "backup_power_float_entry.c", "backup_power_float_core.c",
           "backup_float_primitives.c", "backup_sqrtf.c",
           "backup_scalbnf.c", "backup_logf.c",
           "backup_logf_entry.c", "backup_imcra_block_scale.c",
           "backup_imcra_substate_a.c", "backup_imcra_substate_bc.c",
           "backup_imcra_constructor.c",
           "backup_imcra_substate_d_finish.c",
           "backup_imcra_substate_d.c", "backup_expf.c",
           "backup_exp_double.c", "backup_audio_out_dispatch.c",
           "backup_tokenizer.c", "backup_format_emit.c",
           "backup_expf_entry.c", "backup_gsensor_workstate.c",
           "backup_dsp_config_entry.c", "backup_dsp_transform.c",
           "backup_rfft_q15.c", "backup_rfft_split_sdk.c",
           "backup_rfft_split_inverse_dsp.c",
           "backup_fft_butterfly_sdk.c", "backup_fft_radix4by2_sdk.c",
           "backup_fft_bitreversal.c",
           "backup_cfft_q15.c",
           "backup_fft_profile_data.c",
           "backup_fft_tables_512.c",
           "backup_dsp_vector_simple.c",
           "backup_runtime_truncdfsf2.c"]
RUNTIME_SOURCE_DIR = ROOT / "third-party/upstream/llvm-compiler-rt-format-20.1.8"
SOURCES += ["backup_fp_environment_csky.c"]
SOURCES += [
    "backup_clock_runtime_initialized_records.c",
    "backup_uart_initialized_records.c",
    "backup_audio_runtime_initialized_state.c",
    "backup_audio_uart_tx_template.c",
    "backup_trigonometry_kernel_coefficients.c",
    "backup_stage2_vector_reset_experiment.c",
    "backup_stage2_system_init_experiment.c",
    "backup_stage2_board_init_experiment.c",
    "backup_stage2_main_experiment.c",
    "backup_stage2_mode_experiment.c",
    "backup_stage2_mode_callbacks_experiment.c",
    "backup_stage2_system_done_experiment.c",
    "backup_stage2_app_event_tick_experiment.c",
    "backup_stage2_app_event_init_experiment.c",
    "backup_clock_mux_select_experiment.c",
    "backup_clock_register_apply_experiment.c",
    "backup_stage2_exception_experiment.c",
    "backup_stage2_exception_anchor.c",
    "backup_clock_state_refresh_experiment.c",
    "backup_clock_trim_apply_experiment.c",
    "backup_stage2_clock_init_experiment.c",
    "backup_stage2_clock_gate_bits.c",
    "backup_stage2_denoise_audio_callback_experiment.c",
    "backup_stage2_denoise_mode_init_experiment.c",
    "backup_stage2_denoise_runtime_storage.c",
    "backup_stage2_main_initial_experiment.c",
    "backup_stage2_main_initial_leaves.c",
    "backup_stage2_console_port.c",
    "backup_stage2_gpio_irq_masks.c",
    "backup_stage2_irq_descriptors.c",
    "backup_stage2_cache_initialize_children.c",
    "backup_stage2_flash_probe_wait.c",
    "backup_stage2_flash_probe_state.c",
    "backup_stage2_rtc_tick_configure.c",
    "backup_stage2_timer_initialize.c",
    "backup_stage2_timer_records.c",
    "backup_stage2_pmu_initialize.c",
    "backup_stage2_pmu_record.c",
    "backup_stage2_board_pins_initialize.c",
    "backup_stage2_board_pins_ready.c",
    "backup_stage2_pinmux_children.c",
    "backup_stage2_board_pins_finish.c",
    "backup_stage2_board_devices_initialize.c",
    "backup_stage2_spi_device_state.c",
    "backup_stage2_spi_callbacks_simple.c",
    "backup_stage2_spi_transfer_candidate.c",
    "backup_stage2_mode5_tick_entry.c",
    "backup_stage2_mode5_tick_slices.c",
    "backup_stage2_generic_irq.c",
    "backup_stage2_drc_process.c",
    "backup_stage2_imcra_process_prefix.c",
    "backup_stage2_imcra_adaptive_prefix.c",
    "backup_stage2_imcra_minimum_smoothing.c",
    "backup_stage2_imcra_minimum_flags.c",
    "backup_stage2_imcra_flagged_smoothing.c",
    "backup_stage2_imcra_gain_table.c",
    "backup_stage2_imcra_noise_update.c",
    "backup_stage2_imcra_history_rotate.c",
    "backup_stage2_imcra_spectral_output.c",
    "backup_stage2_imcra_cold_initialize.c",
    "backup_stage2_imcra_process.c",
    "backup_flash_callback_chunked_write.c",
    "backup_flash_callback_wrappers.c",
    "backup_flash_callback_table.c",
    "backup_flash_callback_profile_leaves.c",
    "backup_flash_callback_page_write.c",
    "backup_flash_callback_read.c",
    "backup_flash_callback_initialize.c",
    "backup_flash_low_transactions.c",
    "backup_flash_callback_info_read.c",
    "backup_runtime_c_abi_aliases.c",
    "backup_runtime_retained_slots.c",
]
SOURCES += [RUNTIME_SOURCE_DIR / name for name in (
    "adddf3.c", "subdf3.c", "muldf3.c", "divdf3.c",
    "fixdfsi.c", "fixunsdfsi.c", "floatsidf.c", "floatunsidf.c",
    "comparedf2.c", "udivdi3.c", "umoddi3.c",
    "ashldi3.c", "lshrdi3.c")]
IMAGE_SHA = "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
SDK_TRANSFORM_DEPENDENCIES = {
    "backup_rfft_split_sdk.c": "csky_split_rfft_q15.c",
    "backup_fft_butterfly_sdk.c": "csky_radix4_butterfly_q15.c",
    "backup_fft_radix4by2_sdk.c": "csky_cfft_radix4by2_q15.c",
}
PINNED_INCLUDE_DEPENDENCIES = {
    "backup_beamforming_angle_whole_candidate.c": SOURCE_DIR / "backup_beamforming_angle_work.h",
    "backup_beamforming_angle_allocations.c": SOURCE_DIR / "backup_beamforming_angle_work.h",
    "backup_beamforming_angle_geometry.c": SOURCE_DIR / "backup_beamforming_angle_work.h",
    "backup_rem_pio2_fdlibm.c": ROOT / "third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/e_rem_pio2.c",
    "backup_kernel_rem_pio2_fdlibm.c": ROOT / "third-party/upstream/android-bionic-fdlibm-a27d2baa/libm/src/k_rem_pio2.c",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "build")
    parser.add_argument("--reuse-receipt", type=Path,
                        help="reuse hash-verified unchanged objects from this target receipt")
    parser.add_argument("--include-sample-app-experiment", action="store_true",
                        help="include the unqualified sample-app record and callback cohort")
    parser.add_argument("--size-experiment", action="store_true",
                        help="compile a separate all-source -Os layout experiment")
    parser.add_argument("--size-plan", action="store_true",
                        help="compile four size-qualified units at -Os, retaining other -O2 objects")
    parser.add_argument("--size-fft-o2", action="store_true",
                        help="all -Os except pinned FFT butterfly source at measured smaller -O2")
    parser.add_argument("--size-imcra-init-o2", action="store_true",
                        help="also compile measured smaller IMCRA state initializer at -O2")
    args = parser.parse_args()
    if args.include_sample_app_experiment:
        SOURCES.extend([
            "backup_sample_app_initialized_record.c",
            "backup_sample_app_leaf_callbacks.c",
            "backup_sample_app_init.c",
            "backup_sample_app_event_ambient.c",
            "backup_sample_app_audio_callback.c",
            "backup_sample_app_begin.c",
            "backup_sample_app_command.c",
        ])
    if args.size_experiment and args.size_plan:
        raise RuntimeError("choose one size experiment")
    if args.size_fft_o2 and not args.size_experiment:
        raise RuntimeError("FFT -O2 variant requires --size-experiment")
    if args.size_imcra_init_o2 and not args.size_fft_o2:
        raise RuntimeError("IMCRA -O2 variant requires --size-fft-o2")
    o2_exceptions = set()
    if args.size_fft_o2:
        o2_exceptions.add("backup_fft_butterfly_sdk.c")
    if args.size_imcra_init_o2:
        o2_exceptions.add("backup_imcra_state_init.c")
    size_plan_sources = {
        "backup_runtime_printf.c", "backup_stage2_mode5_tick_entry.c",
        "backup_stage2_main_initial_experiment.c", "backup_power_float_core.c",
    }
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    prefix = ["docker", "run", "--rm", "--network=none", "--read-only",
              "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
              "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
              "--mount", f"type=bind,src={out},dst=/out", "--tmpfs", "/tmp:rw",
              "opencfw/iar-base:10.10.2-local"]
    prior = None
    if args.reuse_receipt:
        prior = json.loads(args.reuse_receipt.read_text())
        if prior.get("image_sha256") != IMAGE_SHA or not prior.get("separate_loaded_image_b"):
            raise RuntimeError("reuse receipt is not this image-B source target")
        expected_prior_optimization = (
            "all-Os-fft-imcra-O2" if args.size_imcra_init_o2 else
            "all-Os-fft-O2" if args.size_fft_o2 else
            "all-Os" if args.size_experiment else "-O2")
        if prior.get("optimization", "-O2") != expected_prior_optimization:
            raise RuntimeError("reuse receipt optimization differs from requested objects")
        prior = {unit["source"]: unit for unit in prior["units"]}
    units = []
    for name in SOURCES:
        source = SOURCE_DIR / name
        obj = out / (Path(name).stem + ".o")
        source_before = sha(source)
        source_name = str(source.relative_to(ROOT))
        sdk_dep_name = SDK_TRANSFORM_DEPENDENCIES.get(Path(name).name)
        dependency = (ROOT / SDK / "utility/libdsp/Source/TransformFunctions" /
                      sdk_dep_name) if sdk_dep_name else PINNED_INCLUDE_DEPENDENCIES.get(Path(name).name)
        dependency_sha = sha(dependency) if dependency else None
        cached = prior.get(source_name) if prior is not None else None
        if (cached is not None and
                not (args.size_plan and Path(name).name in size_plan_sources)
                and not (Path(name).name in o2_exceptions)
                and cached["source_sha256"] == source_before
                and cached.get("dependency_sha256") == dependency_sha):
            old_object = Path(cached["object"])
            if sha(old_object) != cached["object_sha256"]:
                raise RuntimeError(f"reuse object hash differs: {old_object}")
            if old_object.resolve() != obj.resolve():
                shutil.copyfile(old_object, obj)
            units.append({"source": source_name, "source_sha256": source_before,
                          "object": str(obj), "object_sha256": sha(obj),
                          "dependency_sha256": dependency_sha,
                          "reused_from": str(args.reuse_receipt)})
            continue
        cmd = prefix + ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
                        "-mhard-float",
                        "-Os" if (args.size_experiment and
                                  Path(name).name not in o2_exceptions) or
                        (args.size_plan and Path(name).name in size_plan_sources)
                        else "-O2", "-fno-builtin", "-std=c11",
                        "-Wall", "-Wextra", "-Werror",
                        "-I/repo/" + SDK + "/arch/soc/grus/include",
                        "-I/repo/" + SDK + "/include",
                        "-I/repo/" + SDK + "/include/utility/libc",
                        "-I/repo/g2/components/gx8002/image_b_sram_candidate",
                        "-c",
                        "/repo/" + str(source.relative_to(ROOT)), "-o", "/out/" + obj.name]
        if Path(name).name in SDK_TRANSFORM_DEPENDENCIES:
            # Pinned upstream csi_gcc.h has an unrelated unsigned ABS macro
            # warning; this upstream SIMD source also intentionally aliases
            # Q15 pairs with packed 32-bit words.
            cmd[cmd.index("-c"):cmd.index("-c")] = [
                "-fno-strict-aliasing", "-Wno-error=type-limits",
                "-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility/libdsp",
                "-I/repo/third-party/upstream/nationalchip-lvp-kws/include/utility"]
        if Path(name).name == "backup_kernel_rem_pio2_fdlibm.c":
            # Pinned k_rem_pio2.c retains a one-line for/body + next
            # statement; the syntax is intentional and source hash pinned.
            cmd[cmd.index("-c"):cmd.index("-c")] = [
                "-Wno-error=misleading-indentation"]
        subprocess.run(cmd, check=True)
        source_after = sha(source)
        if source_before != source_after:
            raise RuntimeError(f"source changed during image-B compile: {source}")
        if dependency and sha(dependency) != dependency_sha:
            raise RuntimeError(f"SDK dependency changed during image-B compile: {dependency}")
        units.append({"source": source_name, "source_sha256": source_after,
                      "object": str(obj), "object_sha256": sha(obj),
                      "dependency_sha256": dependency_sha})
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
               "sample_app_experiment": args.include_sample_app_experiment,
               "sample_app_callbacks_qualified": False,
               "units": units, "linked_object": str(linked),
               "linked_object_sha256": sha(linked),
               "undefined_symbols": undefined,
        "source_complete": False,
        "optimization": "all-Os-fft-imcra-O2" if args.size_imcra_init_o2 else
                        "all-Os-fft-O2" if args.size_fft_o2 else
                        "all-Os" if args.size_experiment else
                        "four-unit-Os" if args.size_plan else "-O2",
               "data_and_final_layout_complete": False}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(out / "receipt.json")


if __name__ == "__main__":
    main()
