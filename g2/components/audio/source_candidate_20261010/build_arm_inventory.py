#!/usr/bin/env python3
"""Rebuild every existing audio C translation unit as an ARM object, individually."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/g2-audio-arm-inventory").resolve()
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = sorted(p for p in (ROOT / "g2/components/audio").glob("*/*.c")
                 if p.parent.name not in {"source_candidate_20261010",
                                          "uart_irq_source_candidate",
                                          "power_vendor_candidate",
                                          "scheduler_delay_candidate",
                                          "classify_adapter_candidate",
                                          "thread_new_source_candidate",
                                          "event_wait_source_candidate",
                                          "file_backend_close_candidate",
                                          "file_heap_free_candidate",
                                          "file_sync_candidate",
                                          "file_pool_free_candidate",
                                          "semihost_error_candidate"})
PROVIDERS = [
    ROOT / "g2/components/audio/source_candidate_20261010/irq_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/context_yield_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/semantic_adapters.c",
    ROOT / "g2/components/audio/source_candidate_20261010/kernel_read_providers.c",
    ROOT / "g2/components/audio/source_candidate_20261010/simple_ram_getters.c",
    ROOT / "g2/components/audio/source_candidate_20261010/scheduler_suspend_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/irq_mask_pair.c",
    ROOT / "g2/components/audio/source_candidate_20261010/yield_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/daemon_static_memory.c",
    ROOT / "g2/components/audio/source_candidate_20261010/ack_event_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/itcm_copy_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_tick_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/watchdog_stop_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/critical_entry_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/encoder_setup_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/dispatch_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_control_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/next_unblock_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/list_remove_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/sorted_insert_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/callback_irq_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/clock_leaf_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_queue_unlock_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/mutex_disinherit_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/scheduler_resume_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/uart_notify_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/memory_config_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/gpio_pin_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/info_populate_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/oscillator_control_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pll_driver_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/ton_update_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/early_pcm_gpu_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/platform_planner_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/platform_prepare_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/platform_step_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/temperature_apply_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pcm21_children_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pcm21_apply_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pcm21_completion_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/spot_timer_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/wait4_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_stop_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/clock_public_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/heap_free_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_id_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/info_read_revision_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/peripheral_enabled_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/cache_disable_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/cpdlp_config_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/irq_disable_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/trace_disable_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pdm_irq_clear_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_irq_clear_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_irq_status_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/receiver_state_clear_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/queue_delete_peer_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/file_close_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/file_mutex_release_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/dsp_control_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/assert_failure_providers.c",
    ROOT / "g2/components/audio/source_candidate_20261010/i2s_clock_source_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pdm_control_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/i2s_stop_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/i2s_power_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/dmic_request_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_daemon_entry_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/transaction_release_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/i2s_request_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_wrap_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/simple_log_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/log_policy_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_queue_receive_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_reload_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_reload_insert_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/temperature_request_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_fifo_read_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/restricted_wait_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/codec_uart_hal_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/pll_postdiv_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/soft_float_math_aliases.c",
    ROOT / "g2/components/audio/source_candidate_20261010/cache_invalidate_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_aux_command_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_daemon_queue_init_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_stop_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_delete_alias.c",
    ROOT / "g2/components/audio/source_candidate_20261010/timer_start_provider.c",
    ROOT / "g2/components/audio/source_candidate_20261010/info_space_reader_provider.c",
]
FOUNDATION_PROVIDERS = [
    ROOT / "g2/components/foundation/power_domain/power_domain.c",
    ROOT / "g2/components/foundation/freertos_queue/queue_adapter.c",
    ROOT / "g2/components/foundation/freertos_queue/queue_subset.c",
    ROOT / "g2/components/foundation/freertos_ready/list_subset.c",
    ROOT / "g2/components/foundation/freertos_ready/tasks_subset.c",
    ROOT / "g2/components/foundation/freertos_ready/ready_adapter.c",
]
rows = []
for i, source in enumerate(SOURCES):
    obj = OUT / f"{i:03d}-{source.parent.name}-{source.stem}.o"
    depfile = OUT / f"{i:03d}-{source.parent.name}-{source.stem}.d"
    command = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
               "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-MD", "-MF", str(depfile), "-c",
               str(source), "-o", str(obj)]
    if source in (
        ROOT / "g2/components/audio/codec_i2s_configure_source_candidate/configure.c",
        ROOT / "g2/components/audio/audio_log_format_source_candidate/format.c",
    ):
        # Native configure uses DP VFP; retain its operation class with core-register ABI.
        command[5:5] = ["-mfpu=fpv5-d16", "-mfloat-abi=softfp", "-Werror"]
    p = subprocess.run(command, capture_output=True, text=True)
    row = {"source": str(source.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
           "object_path": str(obj),
           "command": command, "returncode": p.returncode,
           "stderr": p.stderr[-3000:]}
    if p.returncode == 0:
        row["object_sha256"] = hashlib.sha256(obj.read_bytes()).hexdigest()
        dependencies = depfile.read_text().replace("\\\n", " ").split(":", 1)[1].split()
        row["dependency_sha256"] = {str(Path(d)): hashlib.sha256(Path(d).read_bytes()).hexdigest()
                                     for d in dependencies}
    rows.append(row)
    print(f"{i+1}/{len(SOURCES)} {source.parent.name}/{source.name}: {p.returncode}", flush=True)
for i, source in enumerate(PROVIDERS + FOUNDATION_PROVIDERS, start=len(SOURCES)):
    obj = OUT / f"{i:03d}-{source.parent.name}-{source.stem}.o"
    depfile = OUT / f"{i:03d}-{source.parent.name}-{source.stem}.d"
    command = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
               "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-MD", "-MF", str(depfile),
               "-c", str(source), "-o", str(obj)]
    p = subprocess.run(command, capture_output=True, text=True)
    row = {"source": str(source.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
           "object_path": str(obj),
           "command": command, "returncode": p.returncode, "stderr": p.stderr[-3000:]}
    if p.returncode == 0:
        row["object_sha256"] = hashlib.sha256(obj.read_bytes()).hexdigest()
        dependencies = depfile.read_text().replace("\\\n", " ").split(":", 1)[1].split()
        row["dependency_sha256"] = {str(Path(d)): hashlib.sha256(Path(d).read_bytes()).hexdigest()
                                     for d in dependencies}
    rows.append(row)
    print(f"provider {source.name}: {p.returncode}", flush=True)
(OUT / "compile-results.json").write_text(json.dumps({"source_count": len(SOURCES),
    "provider_source_count": len(PROVIDERS) + len(FOUNDATION_PROVIDERS),
    "compiled": sum(r["returncode"] == 0 for r in rows), "rows": rows}, indent=2) + "\n")
if all(r["returncode"] == 0 for r in rows):
    archive = OUT / "libaudio-source-candidates.a"
    # The bridge embeds UART text; the snapshot successor supersedes earlier
    # producer text. Both pairs otherwise create duplicate global definitions.
    excluded = {"uart_tx_offline-am_hal_uart.o",
                "transition_producers_offline-producers.o",
                "timer_wake_providers_offline-port.o",
                "encoder_setup_offline-setup.o",
                "uart_group_power_offline-providers.o",
                "watchdog_callback_offline-watchdog.o",
                "queue_cmsis_offline-blocking.o",
                "freertos_ready-list_subset.o",
                "timer_aux_lifetime_offline-aux.o",
                "float_runtime_offline-math.o",
                "syspll_generator_offline-generator.o",
                "uart_power_config_offline-am_hal_uart.o",
                "timer_queue_wait_offline-wait.o",
                "i2s_power_offline-power.o",
                "i2s_stop_offline-stop.o",
                "timer_daemon_order_offline-daemon.o",
                "timer_wrap_offline-wrap.o",
                "queue_cmsis_offline-queue.o",
                "file_close_offline-close.o",
                "semaphore_take_offline-take.o",
                "transition_snapshot_offline-producers.o",
                "cmsis_memory_pool_offline-heap.o",
                "timer_wake_providers_offline-sorted.o",
                "uart_power_composition_offline-power.o",
                "clock_leaf_providers_offline-providers.o",
                "timer_wake_providers_offline-unlock.o",
                "mutex_disinherit_offline-disinherit.o",
                "resume_ticks_offline-resume.o",
                "uart_rx_notifier_offline-notify.o",
                "info_memory_offline-memory.o",
                "gpio_providers_offline-gpio.o",
                "info_memory_offline-info.o",
                "info_memory_offline-oscillator.o",
                "clock_driver_config_offline-driver.o",
                "early_pcm_dispatch_offline-dispatch.o",
                "early_pcm_gpu_offline-gpu.o",
                "platform_callbacks_offline-planner.o",
                "platform_callbacks_offline-prepare.o",
                "platform_callbacks_offline-route.o",
                "early_pcm_pending_offline-pending.o",
                "pcm21_children_offline-apply.o",
                "pcm21_children_offline-children.o",
                "pcm21_completion_offline-completion.o",
                "platform_callbacks_offline-timer.o",
                "clock_timing_offline-timing.o",
                "transition_timer_offline-transition.o",
                "clock_public_dispatch_offline-dispatch.o"}
    objects = [Path(r["object_path"]) for r in rows
               if Path(r["object_path"]).name.split("-", 1)[1] not in excluded]
    archive.unlink(missing_ok=True)
    subprocess.run(["arm-none-eabi-ar", "rcsD", str(archive), *map(str, objects)],
                   check=True)
    (OUT / "archive-selection.json").write_text(json.dumps({
        "source_compiled": len(SOURCES),
        "provider_sources_compiled": len(PROVIDERS) + len(FOUNDATION_PROVIDERS),
        "archive_members": len(objects),
        "excluded_objects": {
            "uart_tx_offline-am_hal_uart.o": "embedded verbatim in codec_request_offline/hal_bridge.c",
            "transition_producers_offline-producers.o": "superseded by transition_snapshot_offline/producers.c sequence-0 successor",
            "timer_wake_providers_offline-port.o": "rebuilt from the same source via critical_entry_aliases.c to export same-entry audio names",
            "encoder_setup_offline-setup.o": "rebuilt from the same source via encoder_setup_alias.c to export same-entry diagnostic name",
            "uart_group_power_offline-providers.o": "rebuilt from the same source via dispatch_alias.c to export same-entry generic name",
            "watchdog_callback_offline-watchdog.o": "rebuilt from the same source via codec_control_alias.c to export same-entry diagnostic control name",
            "queue_cmsis_offline-blocking.o": "rebuilt from the same source via next_unblock_alias.c to export same-entry pending-resume helper name",
            "freertos_ready-list_subset.o": "rebuilt from the same pinned FreeRTOS source via list_remove_alias.c to export same-entry delayed-block list removal",
            "timer_aux_lifetime_offline-aux.o": "rebuilt from the same timer auxiliary source via timer_delete_alias.c to export same-entry CMSIS delete name",
            "float_runtime_offline-math.o": "rebuilt from same selected source via soft_float_math_aliases.c for soft-float caller names",
            "syspll_generator_offline-generator.o": "rebuilt from same selected source via pll_postdiv_alias.c for clock-driver caller",
            "uart_power_config_offline-am_hal_uart.o": "rebuilt from same pinned SDK source via codec_uart_hal_aliases.c for codec lifecycle power/configure callers",
            "timer_queue_wait_offline-wait.o": "rebuilt from same selected source via restricted_wait_alias.c for same-entry timer daemon caller",
            "i2s_power_offline-power.o": "rebuilt from same selected source via i2s_power_aliases.c for diagnostic caller names",
            "i2s_stop_offline-stop.o": "rebuilt from same selected source via i2s_stop_alias.c for diagnostic caller name",
            "timer_daemon_order_offline-daemon.o": "rebuilt from same selected source via timer_daemon_entry_aliases.c for wrap and daemon caller names",
            "timer_wrap_offline-wrap.o": "rebuilt from same selected source via timer_wrap_aliases.c for switch-lists and auxiliary sampled-time names",
            "queue_cmsis_offline-queue.o": "rebuilt from same selected source via timer_queue_receive_alias.c for timer command receive name",
            "file_close_offline-close.o": "rebuilt from same file-close source via file_close_alias.c for Apollo 0x4745F4 diagnostic caller",
            "semaphore_take_offline-take.o": "rebuilt from same CMSIS mutex source via file_mutex_release_alias.c for Apollo 0x44981C caller",
            "transition_snapshot_offline-producers.o": "rebuilt from same selected transition snapshot source via cache_disable_alias.c for Apollo 0x474EFA caller",
            "cmsis_memory_pool_offline-heap.o": "rebuilt from the same source via heap_free_aliases.c to export two original vPortFree caller entries",
            "timer_wake_providers_offline-sorted.o": "rebuilt from the same source via sorted_insert_alias.c to export same-entry delayed-block list insertion",
            "uart_power_composition_offline-power.o": "rebuilt from the same source via callback_irq_alias.c to export same-entry callback PRIMASK helper",
            "clock_leaf_providers_offline-providers.o": "rebuilt from the same source via clock_leaf_aliases.c to export same-entry power-enabled and HFRC-target getters",
            "timer_wake_providers_offline-unlock.o": "rebuilt from the same source via timer_queue_unlock_alias.c to export same-entry timer queue unlock",
            "mutex_disinherit_offline-disinherit.o": "rebuilt from the same pinned FreeRTOS source via mutex_disinherit_alias.c to export same-entry queue mutex release helper",
            "resume_ticks_offline-resume.o": "rebuilt from the same source via scheduler_resume_alias.c to export same-entry scheduler resume caller name",
            "uart_rx_notifier_offline-notify.o": "rebuilt from the same source via uart_notify_alias.c to export same-entry UART stream task notification",
            "info_memory_offline-memory.o": "rebuilt from the same source via memory_config_aliases.c to export same-entry MCU and SRAM configuration callers",
            "gpio_providers_offline-gpio.o": "rebuilt from the same source via gpio_pin_aliases.c to export same-entry GPIO pin calls",
            "info_memory_offline-info.o": "rebuilt from the same source via info_populate_alias.c to export same-entry INFO1 cache fill",
            "info_memory_offline-oscillator.o": "rebuilt from the same source via oscillator_control_alias.c to export same-entry oscillator control",
            "clock_driver_config_offline-driver.o": "rebuilt from the same source via pll_driver_aliases.c to export six same-entry PLL driver callers",
            "early_pcm_dispatch_offline-dispatch.o": "rebuilt from the same source via ton_update_alias.c to export the same-entry TON callback dispatcher",
            "early_pcm_gpu_offline-gpu.o": "rebuilt from the same source via early_pcm_gpu_aliases.c to export six same-entry callback actions",
            "platform_callbacks_offline-planner.o": "rebuilt from the same source via platform_planner_aliases.c to export planner and state-flag callbacks",
            "platform_callbacks_offline-prepare.o": "rebuilt from the same source via platform_prepare_alias.c to export prepare-state callback",
            "platform_callbacks_offline-route.o": "rebuilt from the same source via platform_step_alias.c to export original step entry under the callback_apply caller name",
            "early_pcm_pending_offline-pending.o": "rebuilt from the same source via temperature_apply_alias.c to export the temperature application entry",
            "pcm21_children_offline-apply.o": "rebuilt from the same source via pcm21_apply_alias.c to export the direct PCM2.1 apply entry",
            "pcm21_children_offline-children.o": "rebuilt from the same source via pcm21_children_aliases.c to export three direct PCM2.1 child entries",
            "pcm21_completion_offline-completion.o": "rebuilt from the same source via pcm21_completion_aliases.c to export four direct PCM2.1 completion entries",
            "platform_callbacks_offline-timer.o": "rebuilt from the same source via spot_timer_aliases.c to export three direct SPOT timer caller entries",
            "clock_timing_offline-timing.o": "rebuilt from the same source via wait4_aliases.c to export the two original status-wait caller names",
            "transition_timer_offline-transition.o": "rebuilt from the same source via timer_stop_alias.c to export original timer-stop caller entry",
            "clock_public_dispatch_offline-dispatch.o": "rebuilt from the same source via clock_public_aliases.c to export HAL public clock caller entries"
        }}, indent=2) + "\n")
    print(f"archive: {len(objects)} source-built objects at {archive}")
