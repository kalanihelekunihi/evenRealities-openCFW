# Variant initialization and original-trim capture

[Reconstructed C](../../components/audio/trim_initialization_offline/initialize.c) and [helper interface](../../components/audio/trim_initialization_offline/initialize.h) pass **1,310 original-instruction comparisons** against the exact compiled ELF: 324 variant/date cases, 984 capture cases (including 12 repeated captures), and two no-op callback cases. [Exact validation](exact-build-validation.json), [tests/results](results.json), [body hashes/disassembly](function-bindings.json).

## Recovered behavior

Variant initializer `0x5A08E4..0x5A09C2` returns zero and writes only bytes `0x20074F6E/6F/70`. Flag6E selects major0x21/revision2. Flag6F selects 0x21/revision2 or3 and0x22/revision0. Flag70 selects0x22/revision1 or unscreened0x23/revision0. The screening date predicate matches public FT1REV low16, day bits16..20, month21..24 and year25..29: year24/month12/day>=20 or year>=25, with FT1REV zero. These are factory-field predicates; no actual device date or revision is inferred. The public SDK also writes analog controls in its initializer; those writes are absent from this stock body.

The original-trim capture is a block of the **common low-power initializer**, `0x47FC14..0x47FDB4`, not this variant initializer. Before this block, stock calls registration `0x480434`, peripheral disables, memory configuration and audio-ADC delay configuration. Those surrounding paths remain original-code dependencies and are not validated by the block comparison.

Capture returns to its parent continuation without changes when stored byte0x20074F63 is nonzero. Otherwise it caches live trim fields at0x2007426C..0x20074290 and six TON fields at0x20074294..0x200742A8, then sets the byte1. The capture reads VDDC/VDDF low7 from0x40020044/4C; memory active/LP fields from0x40020088; core active low10 and temperature bits10..13 from0x40020080. The complete assignments are explicit in the C and original disassembly.

When buck status bits4..5 of0x40021108 equal3 and silicon is eligible, cached core trim gets **+7** for major0x21/revision>=3,0x22/revision1,0x23/revision0; **+6** for0x21/revision1/2 or0x22/revision0. Other eligible revisions retain the captured value. There is no saturation: an initial1023 can cache1030. This adjusts the software baseline, not the live core register. Repeated capture after changing all live registers preserves the first cached values. Consequently later GPU/temperature helpers' baseline comes from startup capture, not necessarily the then-current hardware trims.

The callbacks0x5A0018 and0x5A0A6C are complete zero-return no-ops. They neither capture trims nor reset hardware. They must not be treated as evidence of a reset sequence.

## Validation and remaining boundary

Capture native helper is a reconstruction of a **bounded parent block**, not an independently callable original function. Original execution starts with parent R4=0x4002000C and stops at actual continuation0x47FDB4; native helper returns normally. Tests compare ordered cache/flag writes and resulting RAM, omitting scratch-register state. No external-call stubs are used: these bodies contain no calls. Inputs and MMIO are synthetic; no hardware, authentic calibration, whole-startup timing, M55 exception or live IRQ/scheduler proof is claimed.

All1,328 previous sealed entries,110 audit inputs,four checkpoint images and root index were hash-verified before additive sealing. No staging, commits, production changes or device writes. Exact ELF/source/result identities are bound in receipts; this is not byte-identical firmware.

Pinned source remains actionable. Next specific leads: the enclosing low-power initializer's registration/configuration/retention writes and native LP switching initialization dispatch0x4803AC; PCM2.2 default-reset0x5A4E0C is statically mapped but still needs separate exact-address native validation. Hardware calibration and coherent runtime traces remain external boundaries. Source exhaustion has **not** been reached.
