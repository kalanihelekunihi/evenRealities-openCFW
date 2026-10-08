# PCM2.2 deferred completion and failure rollback — validated222 checkpoint

Isolated candidate SHA-256 e5c70f86f09717487f2e85f76b507ed9d79a374f1baa90eda9d4b7f40a4bd143. All seven exact-image integration cases PASS:2 normal/update,3 malformed-input,2 interrupted-update.222 frozen object hashes and five immutable creation-source hashes reconcile; frozen-object relink is exact. Five delivered C variants reproduce their frozen objects exactly. These are isolated component alternatives; do not compile them alongside conflicting existing variants.

Preserved220-object e5972f99 checkpoint and shared129a6b2f ELF hashes are unchanged. Intermediate221-object44b51b73 remains diagnostic evidence: its failed HP scenarios stopped at unsupported selector22;222 closes that actual dependency. No official artifact repin, commit, index/shared campaign or hardware writes.

## Newly closed functions

|Body|Locked range|Bytes|Behavior|
|---|---|---:|---|
|completion21b|429da4..429df6|82|Reads published major/profile separately for temperature coefficient, CORE trim and VDDC trim; writes fields then clears continuation byte.|
|post callback|42a036..42a04a|20|If continuation byte is nonzero, executes completion; always returns0.|
|rollback selector22|429e00..429f68|360|Waits bounded timer expiry and invokes native timer handler, publishes cached target/trims, boosts VDDC by twice the positive increase capped127, waits50, restores target trim, loads CORE fields, waits5, clears two power-switch bits, loads VDDF and adjusts TON last.|

462 newly reconstructed original body bytes. Existing hook28 wrapper22 bytes and mode controller300 bytes are reused dependencies, not new reconstruction counts. Disassembly and exact byte hashes are in function-provenance.json. Private interfaces and readable reconstruction are in g2/components/bootloader/initializer_callbacks/pcm22_deferred21_native/.

## Actual lifecycle and ownership

Call chain: mode controller41b954 → config wrapper41cd1a → updater42a878 → selector21 → publish major8 → hardware readiness/switch polls → hook41cdfa → post42a036 → completion429da4 → on HP failure config wrapper/updater → selector22 → publish rollback major0 → restore saved PRIMASK.

The tested controller enters with critical-save and invokes post completion unconditionally on HP success, not-ready status1 and switch-timeout status4. Failure rollback happens after completion clears the pending byte. Four installed native chain fixtures execute through return with0 boundaries; readiness is synthetic, resident ROM delay40 is stubbed. No queue, task-owned message, allocator or epoch object exists in this examined completion path. The global flag is a continuation indication, not an atomic ownership claim or cancellation API.

|Phase|Storage/ownership|Observed or proven consequence|
|---|---|---|
|selector21 publication|Shared continuation byte200271bc|Sets pending while transition work proceeds; current major is published after the updater’s callback.|
|post guard|Single nonzero byte test|Zero skips completion; no generation token or claim-before-write.|
|hook dispatch|Shared pointer20026e60|Existing wrapper guards then reloads pointer. Null hook returns0 and leaves pending untouched.|
|completion reads|Current major20000150; profile word20026ba4+4*major|Three independent rereads; cached target200270c4 is not the source.|
|completion writes|CORE40020080 twice; VDDC40020044 once|Clearing pending after entry does not abort those writes. Synthetic between-read retarget yields mixed-profile fields.|
|completion release|Byte store0 after all trims|Synthetic republish during completion is cleared; nested entry may repeat writes. No memory free/copy involved.|
|failure rollback|Native selector22 after completion|VDDC boost/restore and final major0 publication occur after flag clear.|
|duplicate post|Same guest machine, flag already0|Second call does no trim writes.|
|rearm or restored hook|Synthetic between-call publication/registration|Rearmed flag executes again; null-hook pending state executes once hook restored.|

115 original/source comparisons cover all82/20/22 bytes including synthetic cancellation, retarget, republish and nested entry.10 additional sequential comparisons reuse the same guest memory across duplicate, rearm and null→restored-hook calls.145 selector22 comparisons cover all360 bytes, timer/timeout, trim saturation, TON and mask cases. RawR0, SP, callee-saved registers, PRIMASK, ordered selected MMIO/SRAM writes and resident-ROM delay inputs are compared. Host flag changes are fixtures, not recovered firmware cancellation functions.

Ordinary maskable reentry is deferred by the explicit model under PRIMASK1; forced nested mask1 case is counterfactual/nonmaskable stimulus only. Nested guest calls use separate stack and restore outer context/PC while memory persists. These tests establish matched modeled behavior, not physical race occurrence. The controller’s config hook still caches its pointer once whereas the stock wrapper reloads after guard; canonical0/0 inputs are tested, concurrent mutation of that slot is not claimed equivalent. Whole-system scheduling, NMI/debugger/other-core writers and all registration mutations remain outside the bounded proof.

## Validation and retained diagnostics

44 broad effective regressions,11 focused,5 extra,3 closure jobs pass. The first broad binding test failed on the new native post-hook address. broad-first-failures.json retains it; adding only the logical native-pointer→original42a036 identity alias yields832 passing comparisons in broad-pin-repairs.json. Candidate bytes and behavior assertions did not change. broad-effective-results.json preserves the composed successful set; the original broad-run-results.json retains its failure.

796 hot-transition,579 selector5,192 selector20 direct comparisons pass.151 completed native updater frontier plus17 targeted installed-updater cases pass; normal combined coverage remains756/758 bytes. Three above-four temperature-global mutation tests remain separate prefix stimuli, not counted as full normal coverage.290 QEMU tests compare bucket and full raw FPSCR using exact frozen object:0 differences. Preserved217 negative control retains8 bucket and290 FPSCR differences. No result mask/FPSCR repair.

Frozen relink emits existing enum-width, executable-stack and absolute-Thumb-branch linker warnings; exact equality here is to the isolated candidate, not the official vendor image. No clean rebuild of all222 sources, source-complete firmware, byte-identical OTA or deployable Apollo memory map is claimed.

## Next bounded source hypotheses

Pinned official Apollo510 HAL commit5efc0228528a8adce5eae0d226fac85d2551eb3b already provides this family; locally authenticated acquisition.json and family sources under ../idle-native-integrated/upstream/ are the provenance. Stock instructions govern, not SDK source substitution.

1. Highest confidence family identification: am_hal_spotmgr.c:593/700 registration and pcm2_2.c:1631/1647/1772 continuation21b, rollback22 and post-handler names. Newly tested locked bodies support this relationship; compiler/version and whole-library byte identity remain unproved.
2. Next low-dependency unresolved candidate: selector23 at429f68, matching SDK:1674 timer/global/TON-only sequence. Selector10 at428d90, SDK:1378, has a similar family shape. Neither has been compiler-bound or validated here; compare locked instructions and native timer/TON calls before reuse. No fabricated result fallback.
3. Selector9 at428ca4, SDK:1357, adds VDDF trim. Selector4 at428506, SDK:1143, adds CORE/VDDC/VDDF and override clears. These have more ordering risk; prioritize when a grounded transition fixture reaches them.
4. Selector7 at428920 (SDK has conditional variants1231/1263), selector13 at4291ec and19 at429a30 need branch/configuration identification before selecting an upstream implementation. Their table entries remain guarded unsupported. Seven unsupported slots remain4/7/9/10/13/19/23.

Do not expand a shutdown/scheduler model to claim a patch safe. Hardware-scheduling claims require an instruction/interrupt trace showing actual callers, flag/pointer writers and readiness timing with known processor/mask state. In the meantime the directly actionable offline step is locked selector23 disassembly against the pinned family, followed by original/source tests and native caller evidence.
