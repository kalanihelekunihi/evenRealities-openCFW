# Earlier PCM temperature application, pending work and TON recovery

Twelve additional native bodies have [readable C](../../components/audio/early_pcm_pending_offline/pending.c) and [interfaces](../../components/audio/early_pcm_pending_offline/pending.h). Exact ELF `3ca2ac60ed5e045cfed2612188472c6cbede1912649092e6826575d7250425f1` passes **6,888 comparisons**: 1,266 new-family fixtures plus all5,622 earlier GPU/temperature/wrapper regressions. [Exact validation](exact-build-validation.json), [build](build_offline.py), [direct results](pending-results.json), [annotated stock instructions](disassembly-evidence.txt), [body/data hashes](function-bindings.json).

## Temperature hardware-application and pending contract

Application0x5A001C writes **VDDF trim only**, gated by cached-original-trims flag0x20074F63 and active buck status0x40021108 bits4..5. Cached VDDF0x20074270 is the base. Range0/1 subtract10, while range2/other byte values subtract0. An enabled GPU (0x40021004 bit18) plus variant flag0x20074F6F adds15. The final calculation floors reductions at0 or caps increases at127, preserving the rest of0x4002004C. Repeating the same request uses the cached base rather than compounding the current hardware-register value. Native and stock tests include wide-range narrowing and malformed cache values; those are synthetic arithmetic fixtures, not normal-device claims.

Postpone0x5A07E6 sets0x20074F71 without clearing existing pending0x20074F72. Publication from the preceding batch updates cached range0x20074F74 and pending flag. Pending handler0x5A07F0 saves PRIMASK, applies the **latest cached range** if pending, clears pending, unblocks publication and restores PRIMASK. Two postponed reports therefore coalesce; there is no FIFO in these bodies. Repeated postpone preserves pending work; repeated drain has no further application call.

A drain clears its pending state even when the application's buck/cache gate prevents any MMIO trim write. Software completion therefore does not prove that hardware compensation was applied, and the cleared pending flag will not automatically replay when that gate later becomes eligible. Direct synthetic inactive-gate fixtures and last-range/repeated-drain sequences establish this bounded behavior, not a live scheduling defect. No separate cancellation primitive is invented.

## Earlier TON configuration

TON initialization0x59FDC2 snapshots six current hardware TON fields when major byte is≥0x22 or major0x21 has nonzero revision. Otherwise it uses VDDC low/high14/31, VDDF21/31 and low-voltage11/11. The six cache bytes are0x2000453A..0x2000453F. Initialization fixtures cover default/snapshot branches and field widths.

TON update0x59FE5A uses authenticated **configuration data** at0x789FE0 (`01 01 02 / 01 01 02 / 01 02 02`). Rows are GPU OFF/LP/HP; used columns1/2 are **CPU LP/HP**, not sleep. GPU-off or GPU-LP chooses cached low TON for CPU-LP and high for CPU-HP; GPU-HP chooses high for both. Public field names corroborate these CPU mode semantics.

If buck-enable bit0x40021100.0 was set, update disables the real buck-register controls, delays5 through the shared microsecond API and clears enable. It sets high-trim-enable0x40020340 bit31, writes six TON fields, then re-enables/delays/restores the real controls only if originally enabled. Repeating identical requests still performs the sequence; it is not an optimized no-op. Arguments narrow to bytes. Direct/repeated fixtures compare ordered writes and cached fields under both initial enable states. Physical rail behavior remains unmeasured.

## LP automatic switching and variant lifecycle

LP-switch initialization0x5A085E programs clock divider0, FCNT1000, hysteresis0 and raw threshold-register values800/450/600/250, then clears two enable/override bits. These are register values; no milliseconds or physical load-current conversion is claimed. Enable0x5A08B6 sets both bits and software flag0x20074F73. Disable0x5A08CA clears hardware bits only if that software flag is set, then clears the flag. With a clear software flag it leaves even externally set hardware bits untouched. Repeated enable→disable→disable and malformed flags are tested. Initialization does not independently clear the software flag in this stock body.

Four before/after-enable callbacks are also native. Earlier before-enable0x59FD82 installs cached core trim minus6 with floor0; middle0x5A081C uses minus7. Both are gated by original-trims flag. Earlier after-enable0x59FDA8 installs memory trim0/control1; middle0x5A0842 installs trim1/control2. These distinct variant settings must not be collapsed into a universal sequence.

## Source comparison, next leads and limits

Pinned SDK5.1.0 `am_hal_pwrctrl.h` defaults VDDC compensation=false, VDDF=true and SDIO boost=false; selected stock body shape is consistent with those paths. The public TON table's non-high-efficiency branch matches the recovered data. That is source-backed interpretation, not proof of historical compile definitions or full-module equivalence. [Exact source paths/pin/hashes](source-reference.json). No new download was needed; earlier bounded public search returned no additional version. Concrete remaining work includes earlier initialization0x5A08E4/original-trim capture and callback/default-reset/suspend behavior. Source exhaustion has not been reached.

This batch replaces earlier temperature-application/registered-TON executable dependencies with native bodies in the integrated test ELF. Common IRQ-save, delay, STIMER and buck-register helpers still execute original instructions; no successful-return stubs are used. Deterministic trims/variant flags and passive MMIO do not prove authentic calibration, fullM55, physical settling, live scheduling or architectural IRQ delivery. Those earlier external-state boundaries remain.

All1,312 prior seals,110 inputs,four checkpoints and root Git index were verified before new sealing. No commits, staging, production changes or device writes.
