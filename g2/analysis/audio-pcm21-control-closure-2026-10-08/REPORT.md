# PCM2.1 outer control recovery

Stock **0x5A1738..0x5A1BB6** now has readable [C reconstruction](../../components/audio/pcm21_control_offline/control.c) and [request interface](../../components/audio/pcm21_control_offline/control.h). The exact current ELF passes **1,336 original-instruction comparisons**, including 39 additional profile/flag/unchanged-plan fixtures. [Build receipt](reproduction-receipt.json), [validation](exact-build-validation.json), [complete results](results.json), [byte/source provenance](provenance.json).

## Recovered behavior

The function checks SIMObuck state from bits4..5 of MMIO0x40021108 before the calibration signature or metadata. If inactive, it returns success without changing temperature classification, range outputs or flags. This differs from pinned public SDK5.1.0 `am_hal_spotmgr_pcm2_1_power_state_update` (line1451 onward), which records temperature even while inactive. All three inactive gate fixtures assert untouched outputs and cached state.

Action and enable narrow to bytes. Actions0/1 accept CPU/GPU byte values; action2 accepts float temperature and writes lower/upper float bounds at offsets4/8. Actions3/4 OR device/audio masks when enabled; action5 assigns memory mask; action6 assigns SSRAM mask when enabled. Missing required arguments or unsupported actions return6; calibration signature mismatch returns1. The internal planner request is19 meaningful bytes (four little-endian uint32 masks then temperature-range/CPU/GPU bytes; C struct has trailing alignment padding).

CPU state byte0x20074F76 values2..4 to0/1 updates the byte without preparing, planning or applying. Six explicit stock fixtures confirm no child calls. Names LP/HP/sleep are corroborated by public source; these integer values are internal power states, not a BLE interface.

HP-to-LP (old1,new0) defers its state-change helper and cached CPU byte until a changed profile/TON operation has completed. A fixture derived from the actual planner output sets the prior profile and TON to the selected pair: stock then skips apply and leaves the CPU byte1. The corresponding changed-plan fixture executes real apply and ends with byte0. This is observed original-instruction behavior, not proof of a hardware bug or naturally reachable unchanged-plan state.

Sleep preparation records flag0x20074F6A according to current profile neither8 nor12; targeted fixtures cover both exceptional profiles. The peripheral/power flag cases also exercise0x20074F6C handling. Temperature ranges and hysteresis bounds are preserved in the C switch; invalid/NaN/infinite temperatures produce range4, zero bounds and return6.

## Continued dependency lead

Pinned Ambiq source directly identifies the remaining common children: preparation0x5A0C20, state-change0x5A0D44, planner0x5A13E8 and application0x5A0FC4. They execute original bytes in this batch, so this is outer-control reconstruction rather than native closure of the whole PCM2.1 family. Public code additionally accepts INIT_STATE and BACK_TO_DEFAULT_STATE stimuli that this stock dispatcher rejects, and reads CPU state differently. It cannot be substituted wholesale. Earlier PCM0.7/2.0 families and PCM2.1 planner/application remain concrete source leads, not missing tools or an exhausted search.

## Validation limits

No success-return stubs, child-entry stops or firmware modifications are used. Startup SRAM and ITCM come from authenticated OTA initializer records. Calibration words, peripheral state and callback availability are synthetic; MMIO is passive. Stock profiling NOP probes read four metadata bytes, even for byte enums; caller storage therefore needs four readable bytes (temperature requires12). Stack-only profiling records are omitted. Cortex-M33-compatible Unicorn/FPU execution does not prove full M55, physical timing, exception delivery, coherent scheduler state or actual device calibration. This is offline reconstructed behavior, not byte-identical firmware or a safe hardware patch.

All1,233 prior sealed entries,110 audit inputs,four checkpoints and root index were preserved before sealing. No commits, staging, production changes or device writes.
