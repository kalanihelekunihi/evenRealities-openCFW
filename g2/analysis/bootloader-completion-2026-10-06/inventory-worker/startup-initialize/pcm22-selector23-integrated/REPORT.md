# Native selector23 and bounded selector10 reuse evidence

Validated223-object offline checkpoint SHA-2568aca98ea30439829915d54c00ee6f1e66487aa9251691a70591ea3b66294d307. All seven exact-image cases PASS:2 normal/update,3 malformed-input,2 interrupted-update.223 frozen input hashes and five immutable creation-source hashes reconcile; frozen-object relink produces exactly this ELF. Two delivered C files reproduce their frozen objects exactly. The validated222 e5c70f86,220 e5972f99 and shared129a6b2f ELF hashes are unchanged. No commits/index/shared campaign/hardware writes.

## Newly installed body and real callers

Locked selector23 is429f68..42a030,200 bytes. Pinned Apollo510 HAL commit5efc0228528a8adce5eae0d226fac85d2551eb3b, am_hal_spotmgr_pcm2_2.c:1669/1674 describes power-state8↔12 and matches its qualitative timer/global/TON flow. Local acquisition.json authenticates source provenance; original instructions/literals govern the C. Full hashes and original disassembly are local, not inferred from SDK comments.

Natural call chain: installed revision35/variant2 SPOT dispatcher41ce52 → power wrapper41cd1a → updater42a878 → trim dispatcher42a4bc → state-transition selector lookup → table slot23 →429f68 → optional timer-service42a04a and delay41d1c0 → TON42a1bc → updater publishes major/minor. Four cases cover8→12 and12→8 with initial PRIMASK0/1. Eight separate return-chain cases cover the same paths with zero/nonzero profile control and capture actual guest callback returns. No new opaque dependency was reached: timer service, ISR/stop, delay conversion and TON providers are existing native source. Only absent resident ROM delay40 is stubbed. No opaque callback return replacement.

## Readable behavior and layouts

```
packed = pack_7bit_fields_into_four_bytes(profile_word_at_20026c04);
read current and target profile fields;
if (timer_control_at_400083e0 & 1) {
    poll timer_status_at_40008064 bit30, at most60 one-us delay calls;
    timer_service();                // executes even after timeout
}
cached_ton = ton; cached_target = target;
cached_core = target_word[16:7]; cached_tempco = target_word[20:17];
cached_vddc = target_word[27:21]; cached_vddf = target_byte[6:0];
ton_adjust(ton, target);
return packed;                     // locked POP restores stack word intoR0
```

Target/current profile address is20026ba4+4*state. Cache addresses:TON200270c0,target200270c4,CORE200270b8,TEMPCO200270bc,VDDC200270b0,VDDF200270b4. Explicit dead volatile profile reads are retained. No direct CORE/VDDC/VDDF register loads, boost or switch instruction exists in selector23 itself. Its called timer service can finish earlier pending trim work, and TON adjustment can write power registers; this is not a no-op callback.

Common-header packed word is four7-bit chunks from20026c04, each placed into one byte. For control0x0dabc123, raw returnedR0 is0x6d2f0223. Eight native guest chains prove the updater still returns0 and publishes the new state while ignoring that raw callback value. Do not turn it into a success/failure API contract. The SDK's source-level status variable is not sufficient evidence for the locked optimized ABI.

This body has no allocation, copy, release, epoch or cancellation token. It publishes shared cached values and synchronously calls existing timer/TON providers. The prior completion lifecycle115 synthetic comparisons and10 same-guest duplicate/rearm/restored-hook comparisons remain passing and separately preserved; selector23 adds no claim that asynchronous races occur on hardware.

## Original-instruction validation

241 direct comparisons exercise all200 original body bytes (145 baseline plus96 additional8↔12 timer/timeout, service-state, TON and mask combinations).145 rollback22,796 hot-transition,579 selector5 and192 selector20 cases pass.115 deferred and10 sequential lifecycle cases pass.151 completed native updater frontier plus17 targeted installed-updater cases pass; normal updater coverage remains756/758 bytes. Three above-four temperature mutations remain separate prefix tests.44 broad,11 focused,5 extra,3 closure driver jobs and nine affected jobs return0.290 QEMU full-FPSCR/bucket comparisons have0 differences; preserved217 negative control retains8 bucket and290 FPSCR differences.

First candidate18fee7ce is retained as diagnostic evidence: compiler-installed slot23 was missing from the source capability mask. Binding regressions detected actual0x777d96f vs required0x7f7d96f. Corrected initialized_data.c produces a new frozen8aca98ea identity; no assertions were weakened. Own outdated test processes were stopped, recorded, and all final checks rerun on corrected bytes. Earlier missing output-directory and linker KEEP syntax errors are also recorded; first-candidate-diagnostics retains attempted receipts. No completion claim applies to that first image.

## Next ranked source hypothesis actually tested

Selector10 at428d90..428e6a is218 original bytes. Locked disassembly has the same profile packing, timer service, cache publication and TON operations as23, with wider/different PC-relative literal loads. The existing compiled23 C body matches original10 in241 direct comparisons visiting all218 bytes. Two natural16→12 guest chains also match after explicitly substituting only source guest table slot10 with the compiled23 address. No candidate image or hardware is patched by that synthetic fixture.

These are reuse-hypothesis receipts, not native compiler-installed10 coverage. Slot10 remains unbound in8aca98ea; its capability bit is still absent. pcm22_sequence10-proposed.c and verify_selector10_reuse*.py expose the proposed source and test transport. The next concrete integration is an independently compiled10 binding and capability bit, followed by its exact-image regressions and seven cases. Six unsupported slots remain4/7/9/10/13/19. Selector9 adds a direct VDDF trim and should not be aliased to23; selector4 adds trim sequencing and override clears; selector7 has SDK conditional alternatives requiring configuration discrimination.

## Limits and navigation

Timer status, readiness and clock/SCS accesses are synthetic. Resident ROM delay implementation, physical W1C semantics, task/NMI/debugger/other-core races, config-hook concurrent pointer mutation and hardware timing remain unproved. No whole-source/official byte-identical OTA/deployable Apollo image claim. Frozen equality is to this isolated three-slot candidate, not to vendor bytes. Existing enum-width, executable-stack and absolute-Thumb-branch linker warnings are retained in relink logs.

Owned predecessor navigation:pcm22-hot-transitions-integrated/220;pcm22-deferred21-rollback-integrated/222 with ownership table and counterexamples;this directory223 with selector23;all are siblings under startup-initialize. Canonical delivered alternative is g2/components/bootloader/initializer_callbacks/pcm22_selector23_native/. Use one initialized-data variant; do not link conflicting component alternatives together.
