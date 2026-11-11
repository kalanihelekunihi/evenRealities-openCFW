# Software-TWI delay source closure

`software-twi/sdk_delay_busy.c` now participates in normal composition and
resolves `r1_twi_delay_busy`. Application imports fall from 211 to 210;
bootloader imports remain 34. All 562 R1 units compile, with zero failures
or duplicate strong symbols and no added imports. The other 561 source units
are unchanged. The application now composes 456 objects.

The wrapper retains a small native CMP/BEQ condition primitive because a C
zero test compiled to CBZ, which does not produce stock's zero-path flags.
C supplies the wrapping left shift and typed call to the existing source-built
subtract-three delay primitive. Clang's `musttail` enforces the native tail
handoff, while an empty register constraint retains the target in R1. There
is no handwritten executable word array or hardcoded code-address call.
The recorded `-Oz` setting produces the native literal-load instruction form.

Official qualification accepts both complete 16-byte wrappers at `0x7a6dc`
and `0x7a6ec`: 12 instruction bytes and four literal bytes each. Their literal
bindings select `0x9a641` and `0x9a651`; both underlying six-byte source
primitives were already selected in the canonical plan. The frontier's two
existing candidate-source paths were corrected from the old GPIO source to
the current delay source; native entry addresses/instruction sizes did not
change. Earlier REA observations and current raw execution are bound below.

The qualifier now uses its existing anchored matcher when a named source
entry has unresolved direct relocation bindings and `--match-functions` is
requested. It recovers only permitted relocation scalars, links the compiled
body at that exact independently named entry, and still requires full byte
equality. This handles repeated wrappers without treating a globally
ambiguous byte pattern as a unique function. No executable reference bytes
are copied into the provider.

All 41 qualifier checks pass: ambiguous unanchored duplicates are rejected;
both anchored full links match; all 24 single-byte instruction perturbations,
unnamed entries, unsupported relocation types, instruction-misclassified
literals and the C-only CBZ candidate are rejected. The existing 19 build-tool
unit tests also pass.

All 1,608 stock/source cases pass against both native wrapper locations,
for 6,432 executions. There are 566 bounded complete-loop cases and 1,042
handoff-only cases for large countdowns. Both the wrapper and primitive are
compiled source installed at their native addresses. Checks include literal
reads, shifted arguments, R0/R1 and flags, zero behavior, LR/SP, R2-R12,
interrupt masks, unchanged stack and absence of data writes. Nonzero inputs
whose shift wraps to zero still enter the primitive.

Only the two official qualifier selections were appended to the canonical
source plan; existing selections remain unchanged. The candidate-plan hybrid
application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Source-built content increases by 32 bytes to 3,649 bytes, with 642,511 retained
bytes and 248 resource bytes. That is hybrid byte identity, not a complete
source rebuild. Physical bus/electrical timing remains unverified. Source
checks pass and the G2 interrupted pseudocode gates remain unchanged. Exact
source, tool, qualification, plan, build and probe bindings are in the
[machine-readable review](twi-delay-tail-closure-review.json).

## C-only optimization probe, 2026-11-11

An ignored `build/r1-twi-pure-c-20261111/` probe compiles an ordinary C
zero test, wrapping shift and tail call under the current Arm Clang target.
Clang `-Oz` and Arm GNU C `-Os` emit `CBZ`, leaving zero-path flags unchanged.
At Clang `-Os` (and `-O1` through `-O3`), the entry uses `CMP` and an
`ITE` block: the zero return gets the expected compare flags, but the
nonzero `LSLNE` does not update APSR before the delay primitive. The
existing stock/source handoff checks include those primitive-entry flags,
so this C-only shape is not a replacement for the selected exact wrapper.
