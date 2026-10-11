# Bounded audio source composition (2026-10-10)

`build_arm_inventory.py` recompiles all 113 existing audio C translation units and 94 provider units as Cortex-M55 Thumb objects, one source at a time. It archives 160 selected objects after excluding superseded or duplicate implementations. This source-only archive is an inventory/composition artifact with unresolved providers, not a linked firmware claim. Objects are freshly rebuilt from source; no retained executable objects or stock bytes are inputs.

Run `python3 build_arm_inventory.py /tmp/g2-audio-arm-inventory`. The generated `compile-results.json` records all 113 audio and fifty provider source hashes, full dependency hashes from `-MD`, compile commands, results, and object hashes; `archive-selection.json` explains the duplicate exclusions and same-source alias replacements. `build.py` retains the narrower three-file host check and experimental C-SKY cross-compile route; it must not be interpreted as a C-SKY codec implementation.

The ARM UART bridge is included in the ARM inventory; its `msr primask` and `mrs primask` assembly is ARM specific and excludes it from the C-SKY experiment. These audio sources target Apollo MAIN ARM stock addresses, not a proven GX8002 codec firmware. Genuine C-SKY DSP source and authenticated GCC 6.3 execution receipts are separately in `third-party/upstream/nationalchip-lvp-kws/utility/libdsp/Source/` and `g2/analysis/nationalchip-dsp-c-compiler-successor-20261009T195245Z/`.

The new `irq_provider.c` implements the authenticated MAIN helper at `0x473940`; its complete eight-byte compiled text matches the pinned original (see `g2/analysis/audio-source-candidate-20261010/irq-provider-byte-proof.json`). Six existing source providers are selected from foundation modules with their own evidence reports. Two additional C sources adapt seventeen imports through source contracts bound in prior original/source receipts. No simulator provider stubs are linked.

`kernel_read_providers.c` adds source reads for the original tick word and current-task pointer. The OTA literal pools and current compiled objects are compared in `kernel-read-provider-proof.json`; the address and load semantics agree, while the instruction bytes differ. `irq_provider.c` also exports `audio_clock_save_disable_irq` as the same source entry, matching its original 0x473940 binding.

`simple_ram_getters.c` adds source-backed log-mask and role byte getters. Their complete original Thumb bodies, literal-pool addresses, and 10/10 original/source synthetic RAM comparisons are in `simple-ram-getter-proof.json` and `simple-ram-getter-execution.json` under the analysis directory.

`scheduler_suspend_provider.c` adds the original 0x454D7C suspension-counter increment and two same-entry aliases; 5/5 original/source comparisons and the literal-pool proof are in the analysis directory.

`irq_mask_pair.c` implements the complete original BASEPRI save and restore bodies, with 22-byte and 14-byte exact function-text matches to the pinned OTA (`irq-mask-pair-byte-proof.json`).

`yield_provider.c` provides the original 0x4420BC PendSV request for three audio import names and the foundation source alias; its 4/4 original/source synthetic ICSR comparisons are in the analysis directory.

`daemon_static_memory.c` supplies the timer daemon TCB, stack, and 4096-word depth outputs from original 0x4D3610; 4/4 source/original write comparisons cover distinct and overlapping caller cells.

`ack_event_provider.c`, `itcm_copy_provider.c`, and `codec_tick_provider.c` add respectively the manager acknowledgment, authenticated ITCM word-copy contract, and zero-extended tick snapshot. Source/original comparisons are 18/18, 8/8, and 20/20; the ack retains named unresolved `osEventFlagsSet` rather than substituting a stub.

`watchdog_stop_provider.c` reproduces the original watchdog handle-cell read and conditional timer stop. Four original/source comparisons execute through the real original `osTimerStop`, timer-active check, queue initializer, and timer-command producer for null, active, inactive, and ISR cases. `audio_timer_stop` remains a named unresolved source provider; enqueue is not daemon completion. See `watchdog-stop-proof.json` and `watchdog-stop-execution.json`.

`critical_entry_aliases.c` recompiles the existing port source as an included, hashed dependency and exports both audio critical-entry names at the same entry as `stock_enter_critical`. The old port object is excluded from the archive. Its `.text` matches the original selected port object exactly, and 28/28 original/source execution cases preserve the observed BASEPRI transition before the nesting write when the initial mask differs from 0x30. See `critical-entry-alias-proof.json` and `critical-entry-alias-execution.json`.

`encoder_setup_alias.c` and `dispatch_alias.c` export the existing encoder reset and generic callback dispatcher entries under their audio import names. The rebuilt Clang `.text` matches the previously selected source objects exactly; 8/8 fresh GCC Cortex-M4 original/source cases cover config setup and callback argument/null paths. See `encoder-dispatch-alias-proof.json` and `encoder-dispatch-alias-execution.json`.

`codec_control_alias.c` exports the already proven watchdog type-0 emitter as `audio_codec_control` at the same object entry. Fifteen original/source comparisons pass through the real original publisher/queue; the Clang `.text` is identical to the replaced source object. `audio_delay` remains unresolved because its nonzero task path calls a kernel delay body without admitted Apollo source.

`critical_entry_aliases.c` also exports `audio_resume_enter`, `audio_timer_wait_enter`, `audio_resume_exit`, and `audio_timer_wait_exit` at the same existing port entries. The grouped audit keeps all 64 historical alias leads and admits only these four after 49/49 original/source enter/exit comparisons. Apollo `osDelay` still needs an integrated kernel-delay scheduler fixture.

`next_unblock_alias.c` exports the existing queue/CMSIS next-unblock helper at its same original entry for pending resume. The replaced source object `.text` is identical and 15/15 original/source delayed-list cases pass.

`list_remove_alias.c` exports pinned FreeRTOS `uxListRemove` as `audio_block_remove` at the same entry. The old foundation list object is replaced with identical `.text`; 8/8 original/source one- and two-item list cases pass.

`sorted_insert_alias.c` exports the already authenticated sorted-list source entry as `audio_block_sorted_insert`; the old sorted-list object is replaced with identical `.text`, and 8/8 fresh original/source list cases pass.

`callback_irq_alias.c` exports the UART saved-PRIMASK entry as `callback_save_disable_irq`; the old object and rebuilt `.text` match, and the isolated eight-byte entry equals stock exactly.

`clock_leaf_aliases.c` exports the existing PLL power-state getter and HFRC target, force, and disable functions under caller names at the same entries. The rebuilt clock leaf `.text` equals the selected source object, and 16/16 fresh original/source MMIO and division cases pass.

`timer_queue_unlock_alias.c` exports the pinned queue unlock source at the same entry for the timer wait caller. The rebuilt `.text` matches the old selected object, and the prior independent suite passed 675 stock/source unlock cases.

`mutex_disinherit_alias.c` exports the pinned FreeRTOS priority-disinherit source at the queue caller name and same entry. Its rebuilt `.text` matches the old object, and the prior independent stock/source suite passed 195 cases.

`scheduler_resume_alias.c` exports the pending-tick/list scheduler resume source under queue and daemon caller name at the same entry. Rebuilt `.text` matches the prior selected object, and the independent stock/source suite passed 432 coherent scheduler cases.

`uart_notify_alias.c` exports the valid-call ISR notifier under the UART stream caller name. Rebuilt `.text` matches the prior selected object, and the independent stock/source suite passed 1,440 valid task/index-zero notifier cases.

`memory_config_aliases.c` exports the source MCU and SRAM configuration functions at their original caller names and entries. Rebuilt `.text` matches the prior object; independent stock/source suites passed 184 MCU and 480 SRAM cases.

`gpio_pin_aliases.c` exports the GPIO get/set source bodies under clock-recovery caller names at their original entries. Rebuilt `.text` matches the prior object; independent stock/source suites passed 60 getter and 1,300 setter cases.

`info_populate_alias.c` and `oscillator_control_alias.c` export the source INFO1 and oscillator entries under clock-reset caller names. Their rebuilt `.text` matches prior selected objects; independent stock/source suites passed 96 and 384 cases.

`clock_leaf_aliases.c` additionally exports the direct PLL enable/disable and HFRC2 force entries. Prior original/source clock leaf suites passed 20 cases each; `stock_delay` now resolves through the selected same-object delay alias; hardware timing remains open.

`pll_driver_aliases.c` exports six direct PLL driver entries under caller names. Rebuilt `.text` matches the prior selected object; independent stock/source driver cases total 1,407 across init, configuration, enable, disable, deinit, and wait.

`ton_update_alias.c` exports the original early PCM TON callback dispatcher under its caller name at the same object entry. The independent original/source suite passed 240 TON cases; no fresh cases were added in this alias round.

`early_pcm_gpu_aliases.c` exports six original early and middle PCM callback entries from the selected source object; 5,454 prior original/source comparisons support those bodies.

`platform_planner_aliases.c` exports the original planner and state-flag callback entries; 2,928 prior original/source cases support them.

`platform_prepare_alias.c` exports the original prepare-state callback entry, supported by 336 prior original/source cases.

`platform_step_alias.c` corrects `callback_apply` to the original step entry at 0x5A44BA, backed by 1,600 prior bounded route comparisons.

`temperature_apply_alias.c` exports the original hardware-temperature entry under the early PCM caller name, supported by 784 prior original/source cases.

`pcm21_children_aliases.c` and `pcm21_apply_alias.c` export four original PCM2.1 caller entries, supported by 3,146 prior original/source helper cases.

`pcm21_completion_aliases.c` exports four original completion, timer, and TON entries, supported by 2,960 prior original/source function cases.

Eleven previously uncataloged caller names now alias five selected original entries after caller ABI review. Their source objects remain text-identical; see `same-entry-eleven-alias-proof.json`.

`platform_prepare_alias.c` now exports `stock_stimer_running` at the original auxiliary-active getter entry, backed by 27 prior original/source cases.

`spot_timer_aliases.c` exports the original timer initialize/start/restart entries, supported by 120 prior original/source comparisons.

`wait4_aliases.c` exports two original four-argument status-wait names at 0x4807FC; 720 prior bounded original/source cases support the read/return behavior.

`timer_stop_alias.c` exports the original timer-stop entry; 54 prior and 4 fresh bounded original/source comparisons support it.

`clock_public_aliases.c` exports the HAL public clock request/release entries; 816 prior original/source dispatcher cases support them.

`clock_public_aliases.c` additionally exports four I2S/SPOT caller names at the verified request/release entries; the prior 816 comparisons are reused.
# Apollo INFO reader provider

`info_space_reader_provider.c` reconstructs the six-space `infoX_read` body from the pinned Apollo510 Ambiq HAL source and exports the audio archive name `audio_info_space_read`. `g2/analysis/audio-source-candidate-20261010/info-space-reader-integration-proof.json` records the source pin, full Cortex-M55 dependencies, archive hash and 498-case stock/source public-entry receipt. Positive word copies execute the authenticated original ITCM copy child; zero-word copying is retained as a lower call boundary. The INFO and power windows in the oracle are synthetic memory, not device observations.
