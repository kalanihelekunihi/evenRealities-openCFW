# Native SPOT PCM2.1 startup candidate — 2026-10-07

Candidate **5797d0992aeb4f3bcfbe0610dcf53a5158ca5b79347bcefdaf7fa9918c79cfe6** is source-linked and tested, **not promoted**. Main129a is unchanged. [Reconciled candidate](candidate-validation.json) records191 actual linked objects,220 newly frozen inputs and902 verified frozen prerequisite/evidence copies. No full Makefile reproduction claim. No index changes, commits or hardware access.

## Why544 cases were excluded

These are Apollo510 silicon/trim SPOT variants, despite historical worker labels “EM/GX”. They are not EM9305 ARC or GX8002 C-SKY firmware functions. Revision34/variant2 and35/variant1 install callback42ba01; revision35/variant>=2 and>=36 install42a879. Root clock switching invokes callback selector4; shared-SRAM configuration can invoke selector6 even when switching is skipped. Prior4de9 deliberately rejected source execution at both opaque original addresses.

[Native callback](startup_gx_event.c), [children](startup_gx_children.c) and [adapters](startup_gx_adapters.c) now replace42ba00 and its local dependency family in a separate root image. No `test_event_providers.c`, success-return provider or locked executable fallback is linked. The replacement runtime binds the native callback only for its stock silicon routes. Configuration word434164 is source-defined zero, authenticated against stock; it is data, not opcodes.

## Same-candidate execution evidence

| Receipt | Result | Meaning/limit |
|---|---:|---|
|[Root/clock](root-comparison.json)|1032 PASS|176 formerly excluded cases reopened;368 PCM2.2 cases still explicitly excluded.810/810 root and922/922 clock bytes visited; original/source integer register/stack/PRIMASK, writes, ROM calls and selected state compared.|
|[Initialized rank root](root-initialized-ranks.json)|1032 PASS|Same matrix using actual initialized voltage ranks and current index20. Synthetic acknowledgements/readiness and absent resident ROM40/48 remain controlled.|
|[Callback](event-comparison.json)|44 PASS|798/908 original callback bytes visited; return, argument updates, selected SRAM, ordered MMIO and PRIMASK match without instrumentation providers. Does not separately compare child arguments or floating register state.|
|[Descendants](children-comparison.json)|4834 PASS|Temperature120/120,effect84/84,scanner288/288 bytes; decoder740/770,30 unvisited bytes explicitly recorded.|
|[Transition](transition-initialized-ranks.json)|51 PASS|Prior30 plus21 transitions from state20 using recovered ranks;880/1032 bytes visited,152 still unvisited.|
|[Scatter decoder](scatter-selector-table.json)|PASS|Original415326 versus reconstructed C produces identical1371 initialized bytes from625 authenticated compressed DATA bytes, including27 callback pointers. Does not generate this compressed stream from source.|
|[Alignment](alignment.json)|542 PASS|All checked Thumb mapping symbols aligned.|

A success-only callback mutant fails on a revision35/variant1 clock case: [counterexample](mutant-comparison.failure.json). Main seven-profile integration and38 regressions were not rerun on this separate candidate, so neither the main root alias nor its broader readiness claim changed.

## A real bug exposed and corrected

The51-case transition expansion failed on `initialized-state20-to-1`. At stock42b618 the literal42b9c4 resolves to **200270ac**;42b61c stores the target low-seven-bit trim there. The initial reconstruction wrote **200270a4**, corrupting the delta cache and leaving saved trim stale. [Before-fix failure](transition-before-fix.failure.json) is preserved. The prior168aa ELF and its narrower passing receipts are frozen separately; they do not imply correctness on the new case. Corrected candidate5797 passes every suite above. The worker original is being corrected separately; no firmware patch is applied.

## New pinned source and useful negative matches

Downloaded official **PCM2.1 andPCM2.2 C translation units** at existing Ambiq gitlink5efc0228528a8adce5eae0d226fac85d2551eb3b. BSD3-Clause notices preserved; exact URLs/hashes/release markers are in [source probes](dependency-source-probes.json). Existing `.gitmodules` already references this repository; no second submodule or index mutation is needed. The local downloads extend the earlier header-only SPOT evidence.

Both publicPCM2.1 rank arrays agree on20/21 words. At index20, stockVDDC/VDDF ranks are1/7, public source3/6. The public inactive-SIMOBUCK temperature handling also differs from stock42ba00's early return. Therefore source-family agreement is useful; wholesale substitution/exact producing-checkout identity is rejected. The corrected reconstruction continues to consume actual runtime rank inputs.

## Recovered PCM2.2 dispatch boundary and next supported lead

The initialized table at**20000158** has27 pointers to actual original handlers427e84..42a034, not unknown external state. Five targets were absent as keys in the old Ghidra function index; their addresses are still authenticated from decoder output. Do not invent extents from neighboring indexed functions. IDs24-26 are separate `BX LR` leaves; the instruction preserves incomingR0, not fabricated status0.

The independent [event-A work](../../startup-events-a/REPORT.md) now has native selector/walker comparisons over400+400 documented state pairs. Hardware sequence handlers0..23 remain explicit cuts there. Immediate next experiments: integrate those helpers into the event-A direct suite, then port one actual reachable sequence8 handler428bb0 with its precise timer-active branch boundary42a04a→428378/428a94. PCM2.2 C is available to guide those ports. No missing-hardware/table-input blocker or dependency-exhaustion claim is justified yet.

## Reproduction and limits

`run-regressions.py` runs affected comparisons against the prepared candidate. `module.ld` and source files are reviewable here; compile/link commands and actual inputs are frozen in `g2/build/bootloader-completion/startup-root-gx-native/5797d0992aeb4f3bcfbe0610dcf53a5158ca5b79347bcefdaf7fa9918c79cfe6/`. The absolute/tmp paths are prepared execution inputs, not a portable full build recipe.

Offline CortexM33 models use the accepted CortexM55 instruction subset. ROM40/48, acknowledgement/readiness, INFO contents and runtime profile inputs are controlled. Physical scheduling, IRQ/cache/coherence/drain and full FPU state are unverified. Full payload source, original compiler settings, all variant/branch closure and byte equality remain separate goals.
