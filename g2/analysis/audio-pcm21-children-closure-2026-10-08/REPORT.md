# PCM2.1 preparation, state-change, planner and apply recovery

Four stock functions now have native reconstructed implementations: [preparation/state-change/planner](../../components/audio/pcm21_children_offline/children.c) and [apply](../../components/audio/pcm21_children_offline/apply.c), with a [shared interface](../../components/audio/pcm21_children_offline/children.h). The exact ELF `c1489e7172d21226ee48bd3dc4921664b2d2dcad3652c89356d2ee985c581517` passes **4,482 comparisons**: 1,336 integrated control cases and 3,146 direct helper cases. [Exact-build validation](exact-build-validation.json), [build](build_offline.py), [direct tests/results](helper-results.json), [annotated original instructions](disassembly-evidence.txt), [function address/hash bindings](function-bindings.json).

|Function|Stock address|Direct cases|Role|
|---|---|---:|---|
|prepare|0x5A0C20|210|Decide whether buck must remain active during deep sleep|
|change_state|0x5A0D44|128|Flag HP-to-deep-sleep and clear HP-to-LP rail overrides|
|plan|0x5A13E8|1160|Determine profile and TON selectors from current request|
|apply|0x5A0FC4|1648|Sequence core and buck trims, timers, cache and CPU power-domain changes|

## Recovered interfaces and behavior

The planner consumes four mask words plus temperature/CPU/GPU bytes, but the memory and SSRAM words do not influence this stock body. Explicit zero/all-ones fixtures confirm unchanged outputs. It builds a packed descriptor with CPU, GPU/peripheral-active, temperature, GPU mode, peripheral-active and special-device nibbles. Profile selection uses mask0xF00FFF; TON selection uses0xFF00F. Ordinary profiles are0..15; selected special-device requests choose16..19. Unknown/unsupported temperature combinations return5 rather than the public SDK's unknown-temperature shortcut to profile20/TON6. On a TON-selector failure the profile may already be written, so callers must check status before consuming outputs. High CPU request is1; sleep requests retain hardware CPU mode from0x40021000 bits0..1.

Preparation stores forced-buck-active byte0x20074F7B. Range3, monitored lower30 device bits, audio mask0x4C4 or SYSPLL bit29 cause an immediate active decision. Otherwise it checks real STIMER availability and clock1/2, then16 enabled timers whose clocks are0..5,19..24 or256..479. STIMER start/stop bits and timer range boundaries are directly exercised. Public source also names unknown/out-of-range temperature causes that this stock preparation does not test. The algorithm resembles the previously recovered PCM2.2 preparation family; this batch validates its separate PCM2.1 address and native integration rather than claiming an entirely new algorithm.

State-change narrows both arguments to bytes. OldHP1 to deep-sleep2 sets0x20074F6B only when switching-to-HP byte0x20074F6D is clear. OldHP1 to LP0 clears three0x4002037C fields in order (bit16,bit3,bit6), then clears switching-to-HP. Direct cases include wide arguments proving byte narrowing, and compare ordered writes rather than final state alone.

Apply reads packed calibration words from0x20056660+4*profile: VDDC bits0..6, core bits7..16, core companion bits17..20 and VDDF bits21..27. Direction comes from two authenticated startup voltage-order tables at0x200001F4 and0x20000244, not numeric profile order. For rising transitions it records target VDDC/VDDF, applies core trim, optionally boosts core by7 capped at1023, and calculates temporary double boosts from old or cached trims. Out-of-range boost sums fall back to target trims. Delay requests are50,200 or2000 through the shared microsecond timer API; passive emulation does not measure physical elapsed time.

A new timer is published/started when disabled; an enabled timer is restarted. Cached profile0x20000298 is updated on the new-timer path. Crossing from profiles0..7 or16..19 into8..15 sets the CPU-domain selector and switching flag, temporarily disables enabled I-cache, delays20 through the shared delay API, then restores cache. Falling transitions update core first, publish or directly apply buck trims depending on timer/boost state, adjust TON for selected profiles, and cancel an active pending timer when its cached voltage ordering no longer requires a rise; cancellation executes the real stop/completion/clear providers.

## Evidence and practical implications

All four helpers replace their old executable children in the integrated control ELF; there are no successful-return stubs or child-entry stops. Common TON, STIMER query, timer, cache, delay and completion providers still execute original instructions. Direct apply cases cover all400 profile pairs with timer disabled/enabled and boost flag states, plus core trim1016/1017/1023 and cache boundaries. Both test suites compare relevant SRAM, ordered MMIO writes and common-provider calls.

This makes offline power-state reasoning more precise for CFW audio/display features: a device/audio-power request can change the selected profile and TON, while changing only memory/SSRAM masks cannot change this particular planner. Timing-sensitive patches must account for pending timer state and the later completion path. A raw SDK substitution is unsafe: its unknown-temperature handling and forced-active conditions differ. No production patch is proposed here.

## Continued source leads and limits

Pinned Ambiq HAL5.1.0 is reused; no new download was necessary. Its `am_hal_spotmgr_pcm2_1.c` identifies concrete next providers: TON0x5A0D9C, timer publication0x5A0AE8, completion0x5A0B9C and boost removal0x5A0B54. [Pinned source files and hashes](source-reference.json). Earlier PCM0.7/2.0 families remain leads; the search is not exhausted.

Calibration words and peripheral/timer fixtures are synthetic; startup SRAM/ITCM are authenticated. MMIO is passive; full M55 instruction support, physical settling, architectural exception delivery and live RTOS/IRQ scheduling are unverified. Original providers remain explicit dependencies, so these four native bodies do not constitute a complete source-built power subsystem or byte-identical OTA. Preserve the earlier whole-system quiescence/trace boundary.

All1,245 prior seals,110 audit inputs,four checkpoints and root Git index were verified before new sealing. No commits, staging, production changes or device writes.
