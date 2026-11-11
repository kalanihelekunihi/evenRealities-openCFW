# R1 sensor-flag qualification and ownership

The pinned driver's `GH3X2X_GetCapEnableFlag` at `0x2a54c` and `GH3X2X_GetTempEnableFlag` at `0x2a610` now supply eight more exact C-built bytes in the canonical application. Both stock bodies return zero with `MOVS` followed by return through LR. This proves their disabled-getter behavior, not physical sensor capability.

Two earlier generic copies, `goodix_primitives_zero_a` and `goodix_primitives_zero_b`, and their declarations are retired. Their existing inventory rows are merged into the pinned-driver mapping, keeping one implementation and one entry row per stock function. The normal manifest and pinned upstream source are unchanged.

The native configuration-stop call chain identifies these getters and `GH3X2X_AlgoSensorEnable` at `0x2a0e4`. The setter has ten instruction bytes, followed by two alignment bytes and a four-byte literal; its entry supplement does not count those adjacent bytes as instructions. These identities are linked to the preceding REA instruction/byte evidence and native registration/execution fixture in [configuration-stop validation](goodix-config-stop-order-review.md).

Validation:

- Clang and GCC9 each pass 384 paired stock/C getter cases. They compare all registers, interrupt masks, and flags, including R0 zero and the native MOVS N/Z effect. Only the two expected instructions execute and there are no data accesses.
- All 576 R1 units compile; both relocatable compositions succeed without failures or duplicate strong symbols. Imports remain 165 application and 34 bootloader. All 575 unrelated objects are unchanged.
- The generic unit loses only the two retired functions. Among its 318 retained functions, the sole changed body contains two local BL instructions retargeted to the same unchanged `goodix_primitives_hr_extrema_refine`, shifted by eight bytes. All other retained function bytes and relocations are unchanged.
- `make sources-check` and `git diff --check` pass.

Twenty-four GCC9 qualification candidates compile across optimization and data-section/anchor variants. Only the two zero getters qualify, and the selected qualifier unit is admitted without modification. The state setter and gsensor getter do not qualify. A separate two-candidate probe combining section anchors with disabled top-level reordering fails dependency discovery because GCC rejects that flag combination; those failed candidates are retained as diagnostic evidence and are not admitted.

The setter remains a compiler/data-layout boundary: a tested no-data-sections GCC body uses anchor offsets +1/+2/+3 while native uses +2/+3/+4. Literal/alignment placement also remains unmatched. No native padding or opcode patches are used to manufacture equality. The existing setter's void-return register difference remains outside the bounded integration contract, as recorded in the earlier review.

The complete canonical hybrid matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: **3,961 source-built bytes**, 642,199 fallback bytes and 248 resource bytes. Full source-only linking, physical operation and source completeness remain unproven. No global pseudocode/freeze coverage or G2 gate advances.

[Machine-readable evidence](goodix-sensor-flags-review.json) binds source/retirement hashes, native disassembly, compiler tests, ownership consolidation, qualification and full hybrid output. Probes remain under ignored `build/goal-r1-goodix-sensor-flags/`.
