# OpenCFW shortcut-theory fourth frontier, 2026-10-09

This goal used three GPT-6.1 Sol low-reasoning tracks to reopen only concrete
branches left by the third frontier: complete provider-archive traversal,
authenticated package/body discrimination, and a full registered-corpus
similarity index. It remained private P2 evidence. No canonical ledger,
firmware source, installed analysis tool, authenticated input, submodule pin,
or workflow gate changed.

## Net new knowledge

### Complete NationalChip archive traversal

- The prior pass inspected eleven of 41 members. The corrected closure compares
  all 585 sized functions in all 41 members against authenticated XIP and SRAM.
  It resolves provider candidates for 23 of the former 40 unresolved call sites.
- New correlations include analog setters, `reg_get_val`, `reg_set_val`, flash
  OTP read, IRQ save/restore/request, delay/time, and PMU oscillator control.
  Literal-pool normalization also closes the earlier `gx_snpu_init` and
  `gx_snpu_get_state` layout gap and binds the SNPU and audio ISR pointers.
- The IRQ provider establishes an eight-byte callback table rooted at
  `0x20026ef4`: registration stores callback and argument; dispatch supplies
  `(active_irq_index, saved_argument)`. This is an ABI boundary, not hardware
  routing proof.
- A predecessor metadata weakness was corrected. The archive uses `SHT_RELA`,
  so explicit addends—not raw pool contents—must drive relocation reasoning,
  and local section symbols must be scoped per archive object. The corrected
  method still rejects the earlier `npu_dis_interrupt` false positive.
- The 17 remaining sites reduce to five symbols already represented by public
  C. Stock `printf_` agrees with the tinyprintf three-argument wrapper and
  contradicts the alternate five-argument wrapper. Stock `memset` realigns and
  enters word fills, contradicting the registered public implementation's
  initially-unaligned byte-only path. The board clock table is exactly
  `[28, 0, 18, 1]`, but shared public variants prevent unique configuration
  attribution.

### Package/body discrimination

- The authenticated Apollo main reset vector is `0x005E4233`, with Thumb entry
  `0x005E4232`. Consolidated wording that treated `0x005E4294` as reset was
  conflating it with the downstream IAR runtime entry.
- The real chain sets MSPLIM/PSPLIM, creates the stack seal, sets PSP, enables
  CP10/CP11, writes FPSCR, and enters IAR runtime/scatter initialization.
- Instruction ordering excludes direct reuse of the acquired Apollo_DFP 1.5.2
  Reset_Handler/SystemInit pair: the pack source performs SSRAM power and
  unconditional cache/SystemCoreClock operations absent from the bounded stock
  helpers. Shared CPACR bits alone are not source identity.
- Existing STM32, Infineon, CMSIS, Ambiq, and IAR-visible source families add no
  further release-specific identity without a new authenticated discriminator
  or the exact producing inputs.

### Registered cross-corpus index

- The replayed unified scanner authenticated all six payloads and 32 distinct
  registered image contents, then visited 2,557 binary artifacts and 34,282
  source files. It examined 287,285 ELF members and 570,457 sized ARM,
  older-ARC, ARCv2, and C-SKY functions.
- It retained 545 exact occurrences, 462 explicitly unaccepted relocation-mask
  candidates, and 247 lexical source anchors. Native archive/member extraction,
  mutation controls, and shifted-placement controls validated 168 unique exact
  provider functions.
- New high-value review discriminators include IAR `_GetN`, `_UngetN`, and
  `ranmatch` in Apollo main, eleven exact C-SKY DSP leaves in
  `binh_b_stage2`, and exact NationalChip VUI and EM9305 ARCv2 leaves. Ten IAR
  exact occurrences overlap historical body records without their own scoped
  review and are preserved as the next bounded-review shortlist.
- Exact bytes identify provider bodies; they do not establish a complete
  producing package, accepted pseudocode, or additive coverage. Relocation
  candidates remain candidates until destination and data-relocation contracts
  are validated. String matches remain lineage anchors only.

## Tool and acquisition decision

Ghidra-MCP, Ablation, and REA helped locate and organize bounded candidates in
the earlier passes. For this frontier, native ELF/archive metadata, GNU decoding,
authenticated byte comparison, and controlled execution supplied the stronger
independent oracles. Running another query-transport layer would not strengthen
the source identities above.

All positive providers come from already registered NationalChip, IAR, C-SKY,
Ambiq, and EM9305 material. No new public Git repository supplied a missing
producing input or warranted another submodule. No existing pin was moved.

## Reasonable exhaustion boundary

The complete registered binary/source corpus has now been enumerated, all four
represented ELF machine families scanned, all NationalChip driver members
visited, exact positives independently extracted, and available official
package sources compared where authenticated body discriminators exist. There
is no remaining untried third-party/dependency operation in the current corpus
that can defensibly add source identity without changing the evidence class.

Remaining progress requires one of:

- bounded semantic review and independent canonical admission of the saved
  exact-provider shortlist and other private P2 candidates;
- first-party protocol, state-machine, callback, and indirect-target recovery;
- a genuinely new authentic input such as historical `lvp_tws`, EM9305 v4.2,
  producer-version IAR DLIB sources, the exact MetaWare project, or target
  CapSense configuration/generator;
- proprietary/unsized-object support tied to a concrete target discriminator;
- resident-ROM or live hardware evidence; or
- later gated corpus freeze, implementation, and byte-identical rebuilding.

This is a reasonable finite exhaustion claim for the currently available
third-party and dependency approach, not a claim that unavailable private
sources or firmware semantics do not exist. A new authenticated input or body
can reopen a narrowly scoped branch. No cybersecurity classifier rejected a
phase, so Daybreak Blue was not needed. G2 remains in P2 and later gates remain
closed.

## Evidence

- `../shortcut-provider-closure-20261009-agent1/REPORT.md`
- `../shortcut-provider-closure-20261009-agent1/closure.json`
- `../shortcut-package-discrimination-20261009-agent2/REPORT.md`
- `../shortcut-package-discrimination-20261009-agent2/receipt.json`
- `../shortcut-cross-corpus-20261009-agent3/REPORT.md`
- `../shortcut-cross-corpus-20261009-agent3/final-summary.json`
- `../shortcut-cross-corpus-20261009-agent3/validation.json`
- `../shortcut-cross-corpus-20261009-agent3/previously-unreviewed-shortlist.json`
