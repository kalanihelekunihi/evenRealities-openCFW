# Bootloader source candidate, 2026-10-10

Run `python3 build.py --output ../../build/bootloader-source-candidate-20261010` from this directory. The script inventories every C unit below `g2/components/bootloader` and nine reviewed, authored assembly units, compiles for Arm Cortex-M55, selects one strong provider for each global symbol, and creates a deterministic source-only archive. The output directory can be elsewhere. It never reads an official firmware image. The formatter DP unit uses its separately evidenced `fpv5-d16` flag; the MSPI queue uses its documented external-clockgen switch.

`g2/analysis/bootloader-source-candidate-20261010/inventory.json` records each unit's includes, compiler command, result, defined/undefined symbols, and exclusion reason. The archive is a relocatable object collection, not a linked firmware image.

The bounded C provider for original `0x4160e8` is in `tick_accessor_4160e8.c`. Its fresh original/source comparison and exact body hash are recorded by `g2/analysis/bootloader-source-candidate-20261010/verify_tick_accessor.py` and `tick-accessor-comparison.json`; the verifier reads the locked image, while `build.py` does not.

`queue_submit_41649a.c` reconstructs the authenticated queue-submit wrapper and leaves its lower queue routine external. `critical_save_adapter.c` names the previously reviewed critical-save assembly provider for one historical alias. Reproducible original/source checks are `verify_queue_submit.py` and `verify_critical_save_adapter.py` in the same analysis directory. The other historical aliases remain a reviewed worklist in `alias-audit.json`.

`delay_alias_adapters.c` names three historical aliases of two reviewed delay assembly wrappers. `verify_delay_alias_adapters.py` checks their original register and lower-call behavior; physical delay timing remains outside that comparison.

`runtime_action_alias.c` names both historical caller APIs for stock `0x416200`. Its register-preserving branch keeps the selected callers' one-argument `void` ABI while reaching the previously validated 64-bit status provider. `verify_runtime_action_alias.py` checks the two aliases' early-return registers against the locked original; the selected provider source also passes its 260-case original/source suite under the current Cortex-M55 compiler flags.

`task_delay_alias.c` names the stock `0x416378` CMSIS tick-delay wrapper for NOR polling callers and restores its incoming R3 in R1. `verify_task_delay_alias.py` reruns the authenticated 270-case delay suite through the selected provider and alias at Cortex-M55/O2, including the public R1 return register.

`coprocessor_enable_alias.c` names historical stock `0x41ac44` and branches to the reviewed assembly CPACR/barrier provider. `verify_coprocessor_enable_alias.py` compares CPACR bits and public registers in 32 locked original/source cases.

`fp_lazy_mode_alias.c` names historical stock `0x41ac5a` and branches to the reviewed assembly FPCCR/PRIMASK provider. `verify_fp_lazy_mode_alias.py` compares the complete 48-byte original wrapper against selected assembly in 80 cases, including both PRIMASK states and low-byte mode truncation.

`mask_interrupts_alias.c` names historical stock `0x41b2f8` and branches to the selected C BASEPRI-mask provider. `verify_mask_interrupts_alias.py` confirms that the provider's compiled 22-byte section is identical to the original body and compares registers/BASEPRI in 40 cases.

`icache_enable_alias.c` names the historical `0x41e1e8` startup entry and branches to selected C cache-enable source. `verify_icache_enable_alias.py` compares 720 original/source cases over guard and cache-control state, ordered barriers/writes, return, stack and callee-saved registers.

`dcache_enable_alias.c` names historical `0x41e266` and branches to selected C data-cache source. `verify_dcache_enable_alias.py` compares 720 original/source cases over guarded configuration, set/way invalidation, optional cleaning, ordered barriers/writes, return, stack and callee-saved registers.

`context_guard_alias.c` names the historical `0x41602a` context guard and branches to selected C source. `verify_context_guard_alias.py` compares 72 original/source register cases over IPSR, scheduler mode, PRIMASK and BASEPRI; its emulator models one M55 CSET instruction unsupported by Unicorn M33 without changing the source ELF.

`kernel_state_alias.c` names historical `0x416088` and calls the selected C kernel-state provider while restoring the original incoming-R7-to-R1 return register. `verify_kernel_state_alias.py` compares 80 original/source cases over scheduler mode and state memory; its emulator models one unsupported M55 CSET opcode without changing the source ELF.

`kernel_initialize_alias.c` names historical `0x416058` for the selected no-argument startup caller. It restores incoming R7 in R1 after the selected C initialization provider; `verify_kernel_initialize_alias.py` compares 108 original/source cases, including state writes and lower-call order.

`kernel_start_alias.c` names historical `0x4160b0` for the selected no-argument startup caller. `verify_kernel_start_alias.py` compares 108 original/source cases over guard/mode/state, including the ordered state write and scheduler-start call.

`control_delay_us_alias.c` names historical Thumb `0x41d1c1` for the selected platform-control `void(uint32_t)` caller. `verify_control_delay_us_alias.py` reruns the authored FP delay assembly through that entry in 780 original/source cases, preserving the resident ROM cycle routine as a recorded callback boundary.

`dfu_panic_alias.c` names historical Thumb `0x41b2f9` for the DFU context's `void(void)` caller. `verify_dfu_panic_alias.py` checks that selected mask-provider instructions are byte-identical to stock and compares the alias entry in 40 original/source cases.

`init_table_default_alias.c` names the startup caller's historical Thumb `0x41f9f9` no-argument entry. `verify_init_table_default_alias.py` compares seven fixed-table callback/sort fixtures through the alias and selected source under the compatible M4 emulator build; the M55 archive contains a direct `R_ARM_THM_JUMP24` branch to the same selected provider.

`runtime_cache_alias.c` names update-core's historical Thumb `0x41e349` two-argument runtime call and branches to selected cache-maintenance source. `verify_runtime_cache_alias.py` compares 270 original/source cases over disabled, set/way and range operations, including SCB writes and barriers.

`queue_create_aliases.c` and `queue_get_aliases.c` name four selected DFU and manager callers of stock queue wrappers `0x416817`/`0x416921`. `verify_queue_alias_batch.py` checks each name separately against original instructions and the selected queue source in 44 cases with controlled kernel queue boundaries.

`queue_put_aliases.c` names the DFU and manager callers of stock queue-put Thumb `0x4168a3`. `verify_queue_put_aliases.py` compares each callable name in 15 stock/source cases, preserving its 32-bit queue/message/priority/timeout ABI.

`fs_mutex_aliases.c` names filesystem/allocator acquire and release callers of stock Thumb `0x4166ab`/`0x416711`. `verify_fs_mutex_aliases.py` checks 288 stock/source cases through the aliases under a compatible M4 emulator build; the M55 archive contains direct branches to the selected mutex providers.

`dfu_flags_aliases.c` names DFU flag-set/wait callers of stock Thumb `0x41623b`/`0x4162c5`. `verify_dfu_flags_aliases.py` checks 11 original/source cases, including the full R0/R1 wait return pair; M55 archive aliases are direct branches.

`platform_configure_alias.c` names startup's historical Thumb `0x41f847` selector entry. `verify_platform_configure_alias.py` compares 44 Cortex-M55 original/source cases across valid, invalid and low-byte-wrapped selectors, visiting the complete 116-byte stock wrapper; lower power/register calls are controlled.

`power_mode_aliases.c` names the post-bringup mode-one and startup mode-two entries at stock Thumb `0x41f8bb`/`0x41ba81`. `verify_power_mode_aliases.py` compares 56 original/source cases through the aliases under compatible M33 emulation; M55 archive objects retain direct branches to selected providers.

`publish_device_mode_alias.c` names NOR commands' historical Thumb `0x41fadd` mode-publisher entry. `verify_publish_device_mode_alias.py` compares 547 original/source cases through the alias and selected C plus assembly ABI wrapper, including the stock saved-R7 return convention.

`clock_request_alias.c` names NOR MSPI queue's stock Thumb `0x4222f1` clock dispatcher. `verify_clock_request_alias.py` compares 121 Cortex-M55 original/source dispatcher cases, including the caller's class 4 path; class-specific clock operations remain controlled.

`mutex_create_alias.c` names the initializer callback's stock Thumb `0x416611` constructor. `verify_mutex_create_alias.py` compares 61 original/source cases for null and four-word attributes under compatible M4 emulation; the M55 archive retains a direct branch to the selected constructor.

`thread_new_aliases.c` names the DFU and manager/event-loop callers of stock Thumb `0x4160ff`. `verify_thread_new_aliases.py` compares each callable name independently against locked original instructions and selected `opencfw_boot_thread_new` in 324 cases each, including the three actual caller attribute records. The M55 archive has one direct branch per alias.

`dfu_send_alias.c` names manager task's stock Thumb `0x42dca3` 40-byte message publisher. `verify_dfu_send_alias.py` compares 36 locked-original/source cases through the alias, while the M55 archive retains a direct branch to selected `opencfw_boot_dfu_send`.

`semaphore_create_alias.c` names the platform initializer's stock Thumb `0x416763` semaphore constructor. `verify_semaphore_create_alias.py` compares 144 locked-original/source cases through the alias, including its actual `(1,0,NULL)` call; the M55 archive has a direct branch to selected `opencfw_boot_semaphore_create`.

`allocator_init_alias.c` names main-init's stock Thumb `0x41fd71` allocator initializer. `verify_allocator_init_alias.py` compares return, logger event, core pointer and full 460800-byte arena SHA through the alias and selected TLSF source; the M55 archive has a direct branch.

`power_callback_alias.c` names the power guards' stock Thumb `0x41cd1b` callback. `verify_power_callback_alias.py` compares 180 locked-original/source cases through the alias, including the guards' ID 5, enabled 0/1 ABI; the M55 archive has a direct branch to selected `opencfw_boot_power_callback`.

`context_nvic_alias.c` names platform-finish's stock Thumb `0x430471` NVIC-enable wrapper. `verify_context_nvic_alias.py` compares 13 locked-original/source issued-write cases through the alias, including the actual IRQ 10 argument. The M55 archive has a direct branch to selected `opencfw_boot_context_nvic_enable`.

`context_interrupt_alias.c` names platform-finish's stock Thumb `0x42c63b` context interrupt-enable wrapper. `verify_context_interrupt_alias.py` compares 49 locked-original/source MMIO cases through the alias, including the caller's `0xff` mask; the M55 archive has a direct branch to selected `opencfw_boot_context_interrupt_enable`.

`context_claim_alias.c` names platform-finish's stock Thumb `0x42c4c7` context-claim body. `verify_context_claim_alias.py` compares 110 locked-original/source cases through the alias, including full eight-slot pool and output state; the M55 archive has a direct branch to selected `opencfw_boot_context_claim`.

`context_transaction_alias.c` names platform-finish's stock Thumb `0x42c989` context-transfer body. `verify_context_transaction_alias.py` compares 270 locked-original/source cases through the alias, including the caller's zero-command/zero-retain path and modeled slot/MMIO state; the M55 archive has a direct branch to selected `opencfw_boot_context_transaction`.

`context_retry_alias.c` names platform-finish's stock Thumb `0x43048f` bounded retry wrapper. `verify_context_retry_alias.py` compares 24 locked-original/source cases through the alias, including the index-4 extra updates and 1,000-attempt failure limit; the M55 archive has a direct branch to selected `opencfw_boot_context_retry`.

`context_configure_alias.c` names platform-finish's stock Thumb `0x42cc35` instance-configure body. `verify_context_configure_alias.py` compares 540 locked-original/source cases through the alias over interface, clock, mode and queue-buffer settings; the M55 archive has a direct branch to selected `opencfw_boot_context_configure`.

`context_enable_alias.c` names platform-finish's stock Thumb `0x42c539` context-enable body. `verify_context_enable_alias.py` compares 288 locked-original/source cases through the alias over interface selection, queue setup and poll outcomes; the M55 archive has a direct branch to selected `opencfw_boot_context_enable`.

`platform_system_init_alias.c` names startup system-entry's stock Thumb `0x41b863` main initializer. `verify_platform_system_init_alias.py` compares 18 locked-original/source dispatcher cases through the alias, including the actual zero argument, error-mode branch and indirect callback; the M55 archive has a direct branch to selected `opencfw_boot_main_init`.

`clear_alias.c` names the NOR timing wrapper's stock Thumb `0x426c11` three-argument fill routine. `verify_clear_alias.py` compares 200 locked-original/source memory and return-pointer cases, including the wrapper's exact six-byte zero fill; the M55 archive has a direct branch to selected source `memset`.

`nor_write_aliases.c` names filesystem NOR page-program and sector-erase callers of stock Thumb `0x420b0d` and `0x420a09`. `verify_nor_write_aliases.py` compares 23 locked-original/source cases through the two aliases, including page boundaries and error cleanup; the M55 archive has two direct branches to the selected NOR write source.

`hal_power_control_alias.c` names NOR initialization's stock Thumb `0x426809` power-control entry. `verify_hal_power_control_alias.py` compares 14 locked-original/source cases through the alias, including the actual operation 0/2 and retain 1 caller shapes, status, callback order, handle bytes and synthetic MMIO. The M55 archive has a direct branch to selected `opencfw_bl_power_control`.

`power_register_read_alias.c` names startup clockmux's stock Thumb `0x41d90f` power-register getter. `verify_power_register_read_alias.py` compares 10 locked-original/source cases through the alias, including its actual ID 15 and valid output pointer call; the M55 archive branches directly to selected `opencfw_bl_power_register_read`.

`power_register_update_alias.c` names startup alternatives' stock Thumb `0x41d92d` power-register setter. `verify_power_register_update_alias.py` compares 24 locked-original/source cases through the alias, including the caller's ID `0x1c`, rejected values and interrupt-mask state; the M55 archive branches directly to selected `opencfw_bl_power_register_update`.

`malloc_failed_alias.c` names the RTOS heap's no-argument stock Thumb `0x41b5f7` failure hook. `verify_malloc_failed_alias.py` compares six locked-original/source entries through the alias, visiting all ten stock body bytes and matching the diagnostic bytes and terminal spin after a controlled formatter call; the M55 archive branches directly to selected `opencfw_malloc_failed_native`.

`stack_overflow_alias.c` names thread selection's stock Thumb `0x41b601` stack-overflow hook. `verify_stack_overflow_alias.py` compares six locked-original/source entries through the alias, matching format bytes, task-name pointer content and the BKPT0 stopping boundary; the M55 archive branches directly to selected `opencfw_stack_overflow_native`.

`dfu_terminal_alias.c` names DFU context's stock Thumb `0x42e1db` terminal loop. `verify_dfu_terminal_alias.py` compares six locked-original/source entries through the alias, including the manager signal and repeated max-delay requests; the M55 archive branches directly to selected `opencfw_dfu_terminal_native`.

`platform_terminal_alias.c` names startup's stock Thumb `0x4329c5` terminal loop. `verify_platform_terminal_alias.py` compares six locked-original/source entries through the alias, including varied incoming status words retained through R7 and repeated controlled exit requests; the M55 archive branches directly to selected `opencfw_platform_terminal_native`.

`task_return_alias.c` names RTOS port startup's stock Thumb `0x41b391` task-return entry. `verify_task_return_alias.py` compares twelve locked-original/source cases through the alias, covering both invalid-store and debugger-release paths with the SP-8 polling slot; the M55 archive branches directly to selected `opencfw_task_return_native`.

`pcm22_icache_disable.c` provides the no-argument PCM2.2 stock `0x41e22f` cache-disable leaf in source-owned C. `verify_pcm22_icache_disable.py` compares 30 locked-original/source cases over guard bits, cache-control state and PRIMASK, visiting all 56 original body bytes. The M55 archive contains this source provider; cache hardware effects remain outside the synthetic-MMIO comparison.

`pcm22_spot_timer.c` provides PCM2.2 timer start/stop leaves from stock Thumb `0x41cc49` and `0x41ccd7`. `verify_pcm22_spot_timer.py` compares 80 locked-original/source cases across both functions, matching ordered clock calls and synthetic MMIO writes with full original body visitation; the M55 archive contains both source providers.

`thread_deinit.c` provides initializer-record DFU and manager thread teardown leaves from stock Thumb `0x42dddb` and `0x42e3cb`. `verify_thread_deinit.py` compares 48 locked-original/source cases across both functions, matching termination requests, handle-slot writes and status with full original body visitation; actual task deletion remains a lower-provider boundary.

`spot_trim.c` provides the PCM2.1 profile trim and trim restore leaves from stock Thumb `0x42ae25` and `0x42ae6d`. `verify_spot_trim.py` compares 90 locked-original/source cases with full body visitation and matching synthetic MMIO writes. The profile entry tests the low R0 byte explicitly, including raw R0=`0x100`; selected callers pass literal `1`.

`power_ton_adjust.c` provides the call-free event-A TON/trim update leaf from stock Thumb `0x42a1bd`. `verify_power_ton_adjust.py` compares 176 locked-original/source cases over all minor branch classes and the major-8 override, matching ordered synthetic MMIO writes with complete 232-byte stock body visitation.

`event_a_sequence24.c` provides the event-A selector-24 callback from stock Thumb `0x42a031`. Its exact two stock bytes are `BX LR`; `verify_event_a_sequence24.py` compares 96 original/source register-state cases with complete body visitation. The source uses an authored instruction in C and is independent of lower providers.

`event_a_transition_children.c` provides the PCM2.2 state selector and ordered temperature transition walker from stock Thumb `0x42a2b5` and `0x42a43b`. It is the exact two-function prefix of the previously authenticated transition source; `verify_event_a_transitions.py` compares all 400 documented state pairs for each function against the locked image, including ordered callback selectors and four-word callback arguments. The indirect callback table is fixture populated for execution; physical callbacks remain separate providers. `power_trims_update.c` is byte identical to the previously compared analysis candidate, whose 54 stock/source cases visit all 138 dispatcher body bytes. Selecting the three functions together reduces the archive's unresolved census by one.

`idle_cleanup_entry.c` adds the `cleanup` callable entry used by the selected idle loop. Original idle instruction `0x4189c0` branches to stock `0x418a98`; historical link scripts bind that address to the selected `opencfw_boot_idle_cleanup`, whose 60-byte body has 24 stock/source comparisons with full visitation. The adapter compiles to a direct tail branch with no register changes.

`scheduler_suspend_entry.c` binds idle's no-argument stock `0x4181d8` scheduler-depth increment to selected `opencfw_bl_scheduler_suspend`. `verify_scheduler_suspend_entry.py` compares 16 locked-original/source cases, including wraparound and both PRIMASK states, with full 12-byte body visitation.

`reschedule_entry.c` binds the idle loop's no-argument stock `0x41b3d0` PendSV-request body to selected `opencfw_bl_kernel_reschedule`. `verify_reschedule_entry.py` compares 16 original/source MMIO and caller-register cases with full 18-byte executable-body visitation; target scheduling behavior is outside the synthetic comparison.

`buck_override_entry.c` maps the two stock deep-sleep calls to selected `opencfw_boot_ton_gate_write`. `verify_buck_override_entry.py` compares 112 locked-original/source cases and all 40 stock body bytes. The callers pass R0=0; the verifier covers wider raw inputs. Synthetic MMIO does not prove physical buck or TON behavior.

`boost_service_entry.c` maps the deep-sleep stock `0x41cdb8` nullable callback wrapper to selected `boost_service_wrapper`. `verify_boost_service_entry.py` compares 16 locked-original/source cases with full 18-byte body visitation; the installed callback is observed at entry only.

`power_state_entry.c` maps deep-sleep's stock `0x41cd1a` nullable callback wrapper to selected `power_state_wrapper`. `verify_power_state_entry.py` compares 32 original/source cases and all 26 stock bytes, including callback argument and return ABI; the callback body itself remains controlled.

`hal_delay_us_entry.c` and `delay_one_entry.c` map current source callers and the deep-sleep R0=1 stock calls to selected authored `delay_math.S` at original `0x41d1c0`. Each owned verifier passes 780 original/source cases with 80/80 body bytes visited. Resident ROM delay execution and elapsed time remain lower boundaries.

`mspi_status_transfer.c` is the source-owned stock `0x4205f4` status/command PIO wrapper. The copied current source passes 13 original/source cases with all 170 stock instruction bytes visited. Its transfer child is selected; its error-report call retains unresolved `opencfw_provider_415fae`, whose formatter ABI is still open.

`mspi_status_transfer_entry.c` supplies the second exact-address NOR name for stock `0x4205f4`. Two original mode-switch calls use its five-word ABI. The entry tail-branches to the selected status-transfer body and passes 13 original/source cases with all 170 stock bytes visited. Formatter `0x415fae` and physical MSPI remain open.

`event_a_sequences_0_2.c` is an exact copy of the previously authenticated source for root-reachable PCM2.2 selectors 0 and 2. The locked/source comparison passes 22 root-vector cases; measured body visitation is 444/470 and 282/312 bytes respectively. The remaining branches, timer service, resident ROM timing and physical power effects remain explicit limits.

`pcm22_timer_service.c` extracts the source-owned timer service and state-2/state-7 children from the authenticated native PCM2.2 source. The active timer selector-8 comparison passes 24 original/source fixtures with full 46-byte timer-service body visitation. Resident ROM delay and physical timer timing remain open.

`event_a_sequence8_timer.c` is the verified source-owned PCM2.2 selector-8 body for stock `0x428bb0`. Twenty-four locked-original/source timer-ready and timeout cases pass with full 212-byte selector and 46-byte timer-service visitation. Resident ROM delay timing and physical timer behavior remain outside the comparison.

`pcm22_transition14_18.c` supplies the authenticated source bodies for PCM2.2 indirect transitions 14 and 18. The historical byte-identical source passes 56 locked-original/source cases with complete original-body visitation (210/210 and 464/464 bytes), including timer-enabled paths. The selected M55 archive compiles and links; resident ROM delay, physical timing, and hardware effects remain lower boundaries.

`pcm22_transition15.c` and `pcm22_transition16.c` preserve the authenticated four-input, two-return-register ABI. Their historical source ELFs pass 14 direct locked-original/source cases each with 256/256 and 212/212 original-body visitation; the relocated selector-16 walker path passes two further cases. The current M55 archive compiles and links, but the M55 combined runtime and physical ROM timing are outside this receipt. The historical `handler16-17` folder does not contain a verified selector-17 implementation.

`event_mutex_entries.c` binds the event timer callback's stock `0x4166aa` and `0x416710` mutex calls to already selected source bodies, preserving R0/R1. Its owned verifier passes 288 original/source cases with controlled kernel lower calls. Selector 17 was already selected from `initializer_callbacks/startup_pcm22_sequence17.c`; a rerun of its integrated receipt passes 14 direct cases plus the natural walker path, without adding a duplicate provider.

`queue_submit_raw_41937c.c` is the stock 98-byte queue envelope wrapper sourced from the original instruction body. Its owned verifier passes 216 returning original/source cases plus 24 null-event prefix cases and visits 88/98 stock bytes, comparing envelope and lower-call ABI while controlling blocking/ISR queue operations. The null-event prefix is compared through interrupt masking; its invalid-address write/nonreturn tail, scheduler delivery and physical ISR behavior remain unverified.

`cache_invalidate_entry.c` supplies clock-mux's exact stock `0x41e348` cache call name, tail-branching to already selected cache-maintenance source. Its original/source verifier passes 270 cases with 250/250 stock-body bytes visited and compared SCB write/barrier order. Physical cache effects remain unverified.

`formatter_415fae_entry.c` supplies the exact wrapper's variadic register and R1 return contract through an authored source entry, calling selected `opencfw_boot_plain_vsprintf`. Its owned verifier passes 20 original/source cases with 44/44 wrapper bytes visited, including the mode-error and MSPI-error format strings. Broader format grammar, original string-address layout, callback output and floating runtime helpers remain open. Other historical formatter names still require their own caller ABI checks.

`nor_printf_entry.c` maps verified NOR sector-erase and page-program original `BL 0x415fae` calls to the selected formatter wrapper. It preserves variadic registers and stack words; 20 NOR/literal locked-original/source cases pass with all 44 wrapper bytes visited. Full formatting domain and production string layout remain open.

`nor_transfer_error_entry.c` maps NOR write's exact stock transfer-error call to selected formatter code and replaces its one original-address format pointer with a source-owned string. Six locked-original/source cases pass with all 44 formatter-wrapper bytes visited; broader formats and hardware output remain open.

Round 83 audit: `opencfw_boot_fs_error` remains unselected because littlefs callbacks target `0x415fae` while boot-mount callbacks target `0x4176ce` under the same historical source name. The generic log alias includes floating formats outside the bounded formatter proof. No source or archive membership changed; see the round-83 analysis report.

Round 84 alias audit: the remaining `opencfw_bl_logger_output` calls mix source parameter order across initializer/platform-finish and EasyLogger setters; no broad logger alias was selected. The pinned native logger test ELF is absent here, so exact `0x4176ce` needs a fresh current-source fixture and caller-specific comparison. The unchanged round-82 archives hash identically; see the round-84 analysis report.

Round 85 audit: the selected timer fresh-queue source is narrower than the generic static queue constructor used by message queues and semaphores. The selected post-configure guard delegates accepted objects to an unresolved lower source. Startup power still installs several original executable addresses in dispatch slots. No new provider was selected; see the round-85 report.

`queue_create_static.c` now source-defines the generic five-argument static queue constructor and local initializer at stock `0x419c9c`/`0x419d68`. The scalar original/source oracle passes 240 valid and bounded assertion-stop cases; Cortex-M55 archive compilation and whole-archive relocatable link pass separately. The selected queue-reset source remains lower, including its independent reuse/wakeup contract. The deterministic archive has 300 selected members and 18 unresolved names; `g2/analysis/bootloader-source-candidate-20261010/REPORT.md` records the round-86 receipt and remaining categories.

`allocator_log_alias.c` maps the sole allocator-init line-19 call to the already selected source metadata adapter. Four locked-original/source Cortex-M4 entry fixtures compare the six EasyLogger arguments by value, stopping before the logger body. The M55 archive now selects 301 members and has 17 unresolved names; the production alias contains no stock address.

`control_log_alias.c` binds the sole bootloader error transaction call `(level=1,line=505)` to the selected fixed EasyLogger metadata adapter. Four authenticated stock/source entry fixtures compare the six logger arguments; no formatter alias or mixed tag order is assumed. The deterministic M55 archive selects 302 members and has 16 unresolved names.

`nor_log_alias.c` binds `opencfw_bl_log` to the selected EasyLogger source entry in the NOR modules' common `(level,tag,file,function,line,format,...)` ABI. A current original/source public-entry oracle covers the NOR mutex-acquire diagnostic in 18 cases and corrected its source-owned text to the authenticated stock literal. Other NOR logger callsites retain their own behavior coverage limits. The deterministic archive selects 303 members and has 15 unresolved names.

`elog_entry_alias.c` binds the historical `opencfw_provider_4176ce` name to the selected canonical EasyLogger source ABI. An 18-case public-entry original/source oracle covers NOR mutex initialization and compares queue attribute bytes plus all six logger arguments. The alias itself contains no stock-address literal; the lower NOR mutex attribute still has an independently unresolved stock data-name pointer. The deterministic M55 archive selects 304 members and leaves 14 names unresolved.

`update_log_alias.c` binds update-core's canonical EasyLogger variadic ABI to the selected source logger. Six authenticated stock/source `verify` open-failure cases compare open arguments, all logger arguments and return/handle state. The update-core caller still has original-image data pointers; the alias itself does not contain any stock address, and product data placement remains open. The deterministic M55 archive selects 305 members and has 13 unresolved names.

`dfu_log_alias.c` routes DFU fixed-line calls to the selected source metadata adapter. The selected DFU task's read-error call now passes its actual `got` byte count to the already source-owned detail adapter. Ten authenticated stock/source call-prefix cases cover fixed line 356 and read-error line 532 with nonzero detail values; full DFU task/output is not claimed. The deterministic M55 archive selects 306 members and leaves 12 unresolved names.

`initializer_log_alias.c` binds the initializer callback logger name to the selected canonical EasyLogger source. The older declaration labels R1 as `function`, but its actual stock-address value is tag `redirect`; R2 is file and R3 function. An 18-case authenticated redirect-initializer public-entry comparison covers both mutex-return branches and all logger arguments. The alias has no stock-address literal; initializer product string placement remains open. The deterministic M55 archive selects 307 members and has 11 unresolved names.

`format_engine_alias.c` binds the bounded `snprintf` wrapper's five-word engine call to the selected source IAR formatter. A fresh stock `snprintf` versus complete source wrapper/engine oracle passes 24 scalar format and truncation cases. Floating behavior retains the separate M55 QEMU formatter receipt; this alias does not claim a new float oracle. The deterministic archive selects 308 members and has 10 unresolved names.

The selected `initializer_callbacks/startup_runtime.c` now installs a source-defined BL009 slot-8 zero-return callback in place of original executable target `0x42d849`. Forty authenticated dispatcher-plus-callback stock/source cases compare the stored target's behavior and caller-visible state. Seventeen distinct original executable target addresses remain in the startup dispatch source; top-level startup power remains unresolved.

The BL009 dispatch slot `0x34` now installs source `bl009_slot34_enable`, replacing original executable target `0x42d693`. Forty authenticated dispatcher-plus-callback cases compare bit setting at `0x400211a0`, the ready byte at `0x200271b8`, return and preserved state. The selected dispatch retains 16 original executable target literals and the top startup root is unresolved.

BL009 slot `0x38` now installs source `bl009_slot38_disable` in place of original target `0x42d6a7`. An 80-case authenticated dispatch-and-callback oracle covers ready clear/set and control bits clear/set. The selected dispatch has 15 original executable target literals; top-level startup power remains open.

The selected startup dispatch now also source-binds both non-special and special BL009 timing/configuration slot pairs and three short PCM2.1 callbacks. Authenticated dispatch-plus-callback oracles pass 64, 80, 40, 32 and 48 cases respectively; prior BL009 slot oracles remain passing. Eight distinct original executable target literals remain: six have selected source bodies but still require installed-table callback-effect proof, one has an isolated GX reconstruction outside this archive, and one is a larger ROM/VFP callback without selected source. The deterministic M55 archive remains 308 members, 846 providers and 10 unresolved names; two builds hash identically at `a0996f41a28643acd76dced9a70b716f74dd2436636a6e7cdd67e4c5bb2b166d`, and whole-archive relocatable linking passes. Startup power root and product state placement remain open; see rounds 99–101 of the analysis report.

Four more selected source callbacks now replace startup table literals: PCM2.2 profile, post-low-power and timer services, plus PCM2.1 boost. Authenticated installed-pointer/callback receipts pass 144, 48, 64 and 64 fixtures. The timer and boost oracle treats unsupported PRIMASK restoration as an explicit symmetric instrumentation cut; production C retains the ARM restoration instruction. Four original target literals remain: two selected but unverified large/VFP bodies, one isolated GX candidate, and one unsourced ROM/VFP callback. The current deterministic archive has 308 members, 846 providers and 10 unresolved names, hash `88a3648a3ddb81b98aefbf5d2bf038f42d83cce34374aabf4a73f6e3cfcbe14f`; relocatable linking passes. Startup power root and product data remain open.

The PCM2.2 temperature slot now installs its selected source body. A Cortex-M33 M-class/VFP authenticated stock/source oracle passes 256 installed-table and callback cases, including hard-float `S0=-40.0f`, lower call arguments, PRIMASK and FPSCR. Three original target literals remain: selected event graph, isolated GX callback and unsourced ROM/VFP callback. The deterministic archive remains 308 members, 846 providers and 10 unresolved names; two builds hash identically at `8847b8b775967b2e99be964b0078297c0dc58473cba0cb816119af15a03b48dc`, and relocatable linking passes. Startup power root and product state placement remain open.

The selected PCM2.2 event callback now owns startup slot `+4`. The combined current-source dispatcher/event ELF passes 16 installed-pointer and guard-effect cases; a separate strict original/source event oracle passes 150 fixtures against that same ELF and visits 740/758 callback bytes. Selector children and 18 unvisited bytes remain bounded limits. Two original executable target literals remain: isolated GX `0x42ba01` and unsourced ROM/VFP `0x42bf55`. The deterministic M55 archive remains 308 members, 846 providers and 10 unresolved names; two builds hash identically at `fb48a37309123eebd38eeb71a067d8d661b883375ff99f7a96e1fad0d7868e7e`, with relocatable linking passing. Startup power root and product state placement remain open.

The PCM2.1 VFP slot `+8` now reuses the selected temperature source after 256 authenticated installed-pointer and callback cases established stock target `0x42bf55` has the same bounded contract. One original executable target literal remains: GX `0x42ba01`. Its isolated callback and children have passing original/source evidence, but their current objects are not selected; the child object duplicates two providers already in the archive. A source-owned split and current selected-archive installed-table oracle are required before substitution. The M55 archive remains 308 members, 846 providers and 10 unresolved names, deterministic SHA `9ac7432efd77c368427adfd452ae10acf78e65ef1881b5e1cb042ced86d90b44`; relocatable linking passes. Startup root, product state and image/hardware proof remain open.

An analysis-only GX split excludes those two duplicate leaves and compiles/relocates for M55, but a current source callback oracle still needs the selected clock request/release and delay graph plus coherent clock state. The direct trial with synthetic clock destinations cannot validate its accepted transition path. The final stock executable literal remains `0x42ba01`, and the 10 unresolved names are unchanged. Round 106 of the analysis report lists the exact dependency and ABI gates; no production GX pointer was substituted.
The GX callback is now selected as `gx_event.c`, `gx_adapters.c`, and `gx_children.c`, with selected SPOT trim and clock-manager providers supplying its lower graph. A Cortex-M33 hard-float stock/source oracle passes 44 direct cases (798/908 bytes visited, 110 unvisited), and 8 installed-table cases pass on the same production-source ELF. The selected startup dispatch has **zero original executable target literals**; its top startup-power root and product layout remain unresolved. Independent M55 builds produce identical archive SHA-256 `8844de064e272b9d4c83711d1a39e966c52e99f15c2b2d505edce0b86b676bfe`: 311 members, 860 providers, 10 unresolved; relocatable link passes. M33 execution and M55 compile/link are separate evidence, and neither proves hardware or full-image equality. See round 107 of the analysis report.
