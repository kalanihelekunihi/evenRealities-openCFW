# G2 bootloader BL-006 retained-seam survey

## Scope

BL-006 names 77 `official_blob` flash-plan regions totalling 5,892 bytes in
`[0x0041F9B6, 0x00428378)` of `apollo_bootloader`. Confirmed against a fresh
read of `g2/build/source/flash-plan.json` (component `apollo_bootloader`,
`address_status == official_blob`, intersecting the item's range): the count
and byte total still match the work item exactly, so no other agent has
routed any of it since the item was generated.

None of these 77 regions is executable code that still runs unmodified.
Every one of them is either:

- a literal pool or alignment/padding gap immediately before, between, or
  after a function whose *code* is already production-routed as reviewed C
  elsewhere in this same address range, or
- the leftover tail of a stock function that a shorter, functionally
  equivalent, reviewed C replacement was compiled in place over (documented
  per-function in the `g2-bootloader-mspi-*-source-closure.md` and
  `g2-bootloader-cmdq-*` family as "the remaining stock bytes ... are
  unreachable after the source-owned function returns").

This survey does not admit any of the 5,892 bytes as source-owned. It
independently corroborates the "unreachable" claims with a whole-image
control-flow scan (rather than trusting the per-function audits' prose), and
catalogs what each region actually contains, so a future BL-006 pass can
spend its effort on reconstruction instead of re-deriving this context.

## Tooling

`g2/tools/analyze_g2_bootloader_bl006_retained_survey.py` (verified by
`g2/tests/test_analyze_g2_bootloader_bl006_retained_survey.py`, 5 passing
cases) pins the SHA-256 of each region's authenticated bytes, disassembles
the entire stock bootloader image once with Capstone, and for each region
checks every branch/call instruction in the raw stock disassembly whose
immediate target lands inside it. A branch only counts as live evidence of
reachability if its *source* address is:

- **not** inside a span the current build already overwrites (read from
  `overlay.json`'s `patch_sites` and `in_place_leaves`, so the check tracks
  the live overlay instead of a hardcoded snapshot), and
- **not** inside one of the 77 BL-006 regions itself (excludes both
  self-referential branches within a region and Capstone occasionally
  misreading literal-pool bytes as branch-shaped opcodes when swept
  linearly through data).

Current result, re-run against the live tree:

```
BL-006 retained-byte survey: 77 regions, 5892 bytes
  corroborated_unreachable_control_flow: 30
  no_control_flow_reference_found: 47
```

Zero regions are flagged `POSSIBLY_REACHABLE_NEEDS_REVIEW`. Separately, the
tool counts how many 4-byte little-endian words anywhere in the *entire*
stock image equal each region's own start address (a cheap, over-approximate
signal that something might still reference the region as a pointer-table
entry rather than a branch target); the count is 0 for all 77 regions.

This is corroboration of "does not execute and is not obviously pointed to,"
not proof that the byte *content* is meaningless. Region content is
catalogued below.

## Region content, by category

### A. Confirmed-dead stock function tails (26 regions, 3,104 bytes)

These sit immediately after a function whose stock prologue/dispatch was
replaced by a shorter, behaviorally-equivalent C body (verified against all
stock cases by that function's own host fixture per its closure doc). The
survey confirms every branch in the raw stock disassembly that still lands
in these ranges originates from bytes inside the *same* tail (the stock
compiler's own case-body chaining) or from another already-dead BL-006
region — never from code the shipped image still executes:

`0x42423C-0x42488E` (1,618 B, mspi_device_configure tail),
`0x4248E2-0x424976` (148 B, mspi_piomixed_configure tail),
`0x424E84-0x425066` (482 B, mspi_device_configure_public tail),
`0x4250E6-0x4250F0` (10 B, mspi enable tail),
`0x425160-0x42516C` (12 B, mspi disable tail + literal),
`0x42612C-0x4262E0` (436 B, mspi control-dispatcher tail),
`0x4263E0-0x426450` (112 B, blocking-transfer tail),
`0x42647C-0x426484` (8 B, interrupt-enable tail),
`0x4264B0-0x4264BA` (10 B, interrupt-disable tail),
`0x4264F6-0x426506` (16 B, interrupt-status tail),
`0x426C22-0x426C24` (2 B, memset wrapper tail),
`0x426C70-0x426C72` (2 B, CLKGEN HFADJ enable tail),
`0x426CC4-0x426CCC` (8 B, CLKGEN dual-clock switch tail),
`0x42784C-0x427878` (44 B, cmdq initializer tail),
`0x4278BC-0x4278C8` (12 B, cmdq enable tail),
`0x4278FC-0x42790A` (14 B, cmdq disable tail),
`0x42799E-0x4279BE` (32 B, cmdq block-allocator tail),
`0x4279EE-0x4279F0` (2 B, cmdq block-release tail),
`0x427A4C-0x427A56` (10 B, cmdq block-post tail),
`0x427ABE-0x427AD6` (24 B, cmdq status tail),
`0x427B2E-0x427B38` (10 B, cmdq termination tail),
`0x427B90-0x427BAA` (26 B, cmdq error-resume tail),
`0x427C02-0x427C12` (16 B, cmdq reset tail),
`0x427C72-0x427C90` (30 B, cmdq suffix + typed gap),
`0x427D84-0x427D98` (20 B, binary32 remainder-core tail).

**Why these are not yet closed**: the build's `in_place_leaves` mechanism
(`g2/tools/apollo_overlay.py:compile_in_place_leaf`) requires the compiled C
to exactly fill the declared `expected.size` byte span; there is no existing
primitive for "compiled leaf occupies the front of a stock span, and the
proven-dead remainder is filled with deterministic bytes." The
`patch_sites`/cave-leaf mechanism *does* support exactly this (a `b.w`
redirect followed by NOP fill, already used for the LittleFS callback family
at `0x421284-0x4212D8`), but only for functions that are *relocated* to the
free tail, not for functions compiled *in place* at their stock address —
switching an already-closed, committed in-place closure (e.g.
`mspi_device_configure_424120`) to a relocated one would be a nontrivial
architecture change to already-landed, cited work, not a same-pass addition.

**Recommended follow-up**: extend `in_place_leaves` (in
`components/bootloader/core_overlay/overlay.json`, built by
`build_component.py`/`apollo_overlay.py`) with an optional trailing
dead-tail-fill field: given `stock.tail_size` and `stock.tail_sha256`, after
verifying the declared tail is not targeted by any branch outside the union
of already-overwritten spans and the BL-006 catalog (exactly the check this
survey's tool already performs generically), fill it with the same
`b"\x00\xbf"` NOP half-word pattern the cave-leaf mechanism already uses, and
account it under the already-accepted `generated_source_data_replacement`
(or a new, equally-reviewed status) rather than `official_blob`. This is a
shared-file change (`apollo_overlay.py`, `build_component.py`, `overlay.json`
provider-region accounting) and needs the integration lock plus a full
`bootloader-component`/`source` rebuild and re-verification; it was judged
out of proportion for a solo BL-006 pass while other agents are concurrently
landing bootloader work in the same files.

### B. Literal pools and alignment gaps (51 regions, 2,788 bytes)

These precede, follow, or sit between already-source-owned code and hold
data the surrounding (already-compiled) code no longer references by
address, plus genuine alignment filler. Selected content, decoded directly
from the authenticated bytes:

- `0x422712-0x422714` (2 B): `00 bf` — the Thumb NOP half-word
  (`0xBF00`), the exact code-alignment idiom the framework's own cave-leaf
  fill already uses (`nop_halfword = b"\x00\xbf"` in `build_component.py`).
- `0x41F9EE-0x41F9F0`, `0x422872-0x422874`, `0x422AD2-0x422AD4`,
  `0x423DCE-0x423DD0` (2 B each): `00 00` — plain zero alignment halfwords
  between odd-length functions and the next word-aligned entry.
- `0x4225AC-0x4225D0` (36 B): a 4-byte pointer (`0x20027190`, an SRAM
  address) followed by the NUL-terminated ASCII string
  `"constraint handler: bad message"` — the IAR CLIB default C11 runtime
  constraint-violation message, referenced by the already-source-owned
  "IAR-compatible constraint dispatcher" at `0x422590`.
- `0x420F0C-0x420F10` (4 B): the 32-bit constant `0x000F4240` (1,000,000
  decimal), preceding the MX25U25643G serial-mode entry — most likely a
  microsecond timeout or Hz constant consumed by that already-compiled
  function.
- The remaining pin-configuration (`0x41FCF6-0x41FD70`, 122 B),
  initializer-table (`0x41FA40-0x41FA50`, 16 B), row-mode literal seams
  (`0x42220E-0x422220`, `0x42228E-0x4222A0`, `0x4222D2-0x4222F0`), debug
  service pools (`0x422430-0x422468`, `0x422574-0x422590`), MSPI/CLKGEN/
  SysPLL literal pools, and the command-queue/binary32 boundary pools decode
  as dense arrays of little-endian 32-bit words. Most fall in the
  `0x00430000-0x00438000` range (pointers elsewhere in this same bootloader
  image, plausibly to functions or globals not yet individually identified)
  or the `0x20000000` range (SRAM addresses). None of these pointer targets
  has been cross-checked against currently-source-owned symbol addresses in
  this pass.

**Recommended follow-up**: for regions B, reconstruction (not fill) is the
right target — these are meaningful data, not dead bytes. The
`relocated_leaves` mechanism already supports declaring an associated
`rodata` closure with named, size/hash-pinned symbols (used today for the
Cordio Secure-Connections state-name tables in `apollo_main`, status
`source_compiled_rodata`); the same mechanism should be extended to
`in_place_leaves`, or the affected functions converted to relocated leaves,
once each literal word's target is identified against a currently-owned
symbol (start by disassembling the immediately adjacent already-compiled
functions for the `ldr`/`ldr.w` pc-relative loads that consume each pool,
and matching the loaded values to source_compiled symbol addresses in
`flash-plan.json`).

## What this survey does not establish

- It does not prove regions in category A are safe to zero/NOP-fill against
  anything other than *control flow* and the cheap literal-word data-pointer
  check; a more exotic reference (e.g. a checksum computed over the whole
  function span, or a debugger/OTA tool that hashes the original bytes) is
  out of scope for a static disassembly sweep.
- It does not identify what any category B literal word points to beyond
  the numeric range it falls in.
- It performs no hardware, signing, flashing, or transmission operation.

## Status

No bytes in `[0x0041F9B6, 0x00428378)` changed classification in this pass;
BL-006 remains open at 5,892 retained bytes. This document and its verifier
are intended to shorten the next BL-006 pass's investigation, not to close
the item.
