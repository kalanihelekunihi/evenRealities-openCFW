# Final bounded source-reference constraints

This extends STATIC-COMPARISON.md using authenticated payload bytes and already available disassembly, without running downloaded code, a compiler, an emulator or Docker. `branch-constraint-evidence.json` retains target slices, addresses, offsets and hashes; `consumed-disassembly.json` hashes existing disassembly consumed as secondary evidence. No canonical recovery or source ledger was changed.

## GX8002B clock: supported lineage discriminator

Existing SRAM disassembly at 0x10025AA8 loads copy length 20, copies the table at 0x10025CE0, indexes it at 0x10025ABA, and compares attempt count to 5 at 0x10025AD0. Raw authenticated codec bytes at the table decode as five signed little-endian integers **{0, 10, 15, -10, -15}**. These correspond to KWS `boards/nationalchip/grus_gx8002b_dev_1v/clock_board.c:118`, versus AIoT same path:137 **{0, 10, -10}**.

This is inconsistent with the unmodified AIoT three-attempt source branch as the explanation for this particular target initialization sequence; it does not exclude a modified AIoT checkout or a separately linked KWS-like object. It supports KWS-like code or a common/privately patched predecessor retaining five offsets. It does not identify the exact commit or GCC release. AIoT's extra 60M configuration is not established by absence of its constant in this branch; configuration selection and dead-code elimination can remove it. No complete original Kconfig has been inferred.

## VAD: strings are referenced by executable call sites

Previously raw strings alone supported only retention. Existing XIP disassembly now supplies three explicit string-load/call pairs:

| Target | Loaded diagnostic | Direct call |
|---|---|---|
| 0x1020744A / 0x1020744C | 0x1020AE2F, level 3 | 0x10206C24 |
| 0x10207510 / 0x10207512 | 0x1020AE4A, level 2 | 0x10206C24 |
| 0x1020752E / 0x10207530 | 0x1020AE65, level 1 | 0x10206C24 |

These occur in conditional level-selection control flow, followed by state/curve updates. KWS `lvp/common/lvp_audio_in.c:668,699,730` actively prints these exact formats; AIoT `:653,684,715` comments them out. This supplies a stronger active-diagnostic source-branch constraint than mere string retention. The six string-load/call instructions were separately checked byte-for-byte against the locked codec payload in `vad-callsite-byte-checks.json`; all six match. The existing callee label is `gx8002_printf` (Inferred). These checks do not establish reachability from a live image entry point, completion of the surrounding CFG, execution on a physical device, or that the instructions cannot reside in an unused linked archive member. A private patch or other public revision can also retain these calls, so exact producing-source attribution remains open.

## Audio callback: LOGFBANK, not an FFT-branch discriminator

At target 0x10026218 the callback masks channel bit **4**; at 0x10026222 it passes **sdc_addr + 8**, equivalent to **&sdc_addr[2]**, to the VAD query at 0x10207404. KWS `lvp/common/lvp_audio_in.c:210–219` selects CONFIG_ENABLE_HARDWARE_LOGFBANK and uses exactly that channel/index combination. AIoT retains this LOGFBANK branch; its removed FFT branch is therefore irrelevant to this selected callback.

The target's invalid-VAD counter increments at 0x100262BA, compares against **25** at 0x100262BC and stores delayed state at control offset 0xC. This is compatible with CONFIG_LVP_FFT_VAD_ENABLE and CONFIG_LVP_FFT_INVALID_VAD_NUM=25 in the shared LOGFBANK logic (KWS lines 254–264). The macro spelling is a source-derived interpretation, not a proven complete original configuration. The code family could implement that value under different names or patches.

## Board/audio fields: preserve mapping uncertainty

The target audio-board getter at 0x10203004 returns **0x200269A4**, whereas storage candidates are historically named at **0x100269A4**. The initializer at 0x10203024 prints the DMIC diagnostic with argument **2**, then reads halfword offset 0x20 and extracts bits 6–9 for gain. This is consistent with the board audio configuration lineage already documented, but the SRAM/data alias and precise structure/enum/packing layout must remain image-profile-bound.

The acquired AIoT I2S-output initializer forces SADC source at audio_board.c:202–203; KWS can select PDM/I2SIN based on CONFIG_TYPE_* at lines 202–210. No unambiguous target left/right field binding was established here without assuming the exact structure layout and alias profile. Thus no additional supported source/configuration restriction is claimed from those fields. Raw 240-byte candidate configuration is retained for owner review.

## embARC: architecture comparator only

Authenticated BLE record 3 begins at payload offset **1060**, mapped to **0x00302400**. Its first 64 little-endian words include slot 0 **0x001003D0**, slot 16 **0x00305B1C**, and slot 17 **0x00305BE0**. The first word lies outside the application's `[0x00302400,0x00335BC8)` range. It must not be interpreted as the spurious branch to 0x003027D0 produced by a linear code disassembly of vector data. FHDR's separately documented entry point is **0x00302028**, not a demonstrated embARC `_arc_reset` body. No producing startup source is available for the external first-slot target.

The target IRQ0 handler at 0x00305B1C allocates **88 bytes**, stores r0–r12, r30, blink, r58/r59, LP_COUNT, LP_START/END and auxiliary registers 1411/1409, then calls an optional callback loaded from **0x00801904**. This is a fixed vendor IRQ entry, not embARC's `arc/arc_exc_asm.s:112–127` generic IRQ_CAUSE-indexed handler-table dispatcher. embARC's configuration-dependent save/restore macros illustrate architecture semantics but do not prove target stack layout, FIRQ configuration, compiler register allocation or linkage.

Existing QK port and vendor IRQ SDK attribution outrank architecture analogy. embARC's GNU-vs-MetaWare GP and startup alternatives cannot constrain the external startup body absent its authenticated bytes. The already documented MetaWare T-2022.09 SDK archive identity remains the producing-toolchain evidence; no new compiler claim follows from embARC.

## Static stopping boundary

For the acquired pins and selected branches, supported new restrictions are: five-offset PLL initialization, active level 1–3 VAD diagnostic calls, LOGFBANK channel/index selection, and a threshold compatible with 25. UART/startup/trap common sources add no pin discrimination; AIoT FFT deletions do not discriminate the selected LOGFBANK body. Board field binding and external ARC startup cannot be established from these references without additional image-bound layout/ROM evidence or further owner pseudocode recovery. More semantic analogy would not supply new supported constraints.

No exact producing checkout, complete original configuration, compiler release, source completeness, runtime behavior or byte-identical build is proven. Submodule proposals and exact revision receipts remain unchanged. No Docker or denied-path access was attempted.

## Independent-audit caveat incorporated

The parent relayed an independent audit confirming 13 target-slice hashes, 3550 acquired working-tree file hashes and commit/origin provenance. That validates acquisition and target identity, not attribution. Raw VAD strings alone cannot exclude dead retention, a separately linked archive member or modified AIoT. The follow-up supplies byte-valid executable string-load/call pairs, narrowing the evidence to actual instructions rather than only retained data. It still does not prove entry-point reachability or producing source lineage. The LOGFBANK bit/index and threshold observations likewise remain local function constraints, not complete original configuration evidence. No further reachability proof or source-version exclusion is available within this bounded reference comparison without owner CFG/indirect-root recovery.
