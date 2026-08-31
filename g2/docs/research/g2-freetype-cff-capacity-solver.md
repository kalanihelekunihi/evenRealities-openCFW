# G2 FreeType CFF capacity solver

SPDX-License-Identifier: MIT

This software-only audit closes the capacity question for the current CFF
final-link candidate without assigning writable flash or applying the module
class patch.  It consumes the pinned Apple-profile flash plan, its byte-identical
EVENOTA package, every late-Apollo region artifact, the complete CFF map, and
the dual-profile final-link receipt.

## Whole authenticated address space

The pinned flash plan contains 6,120 Apollo-application rows that continuously
tile `[0x00438000,0x007FCEBA)`, including the vector/first region.  Every row's
artifact matches its current package slice.  The plan has no internal
application gap: official blobs, generated source replacements, compiled
source/rodata, generated data/exact replacements, and required alignment are
all treated as occupied.  In particular, no unrelated source-replaced stock
body is promoted to a cave without a component-wide liveness proof.

The separate Apollo bootloader entry has 330 matching rows and occupies
`[0x00410000,0x004368E0)`.  The physically empty 5,920 bytes up to the Apollo
application start belong to that separate package-entry/update domain.  The
application has no authenticated placement authority or cross-component
update-atomicity contract there.  The only legal direct application gap is the
4,422-byte tail at `[0x007FCEBA,0x007FE000)`; secure boot
`[0x00400000,0x00410000)` and the update record
`[0x007FE000,0x007FE010)` are protected.

## Current occupied interval

The nominal append interval is `[0x007ECA44,0x007FE000)`, 71,100 bytes.  The
current package contains one continuous late-Apollo span through `0x007FCEBA`:

- 343 `source_compiled` rows, 66,524 full-row bytes (66,376 bytes inside the
  candidate because the first body begins 148 bytes earlier);
- 134 `generated_alignment` rows, 302 bytes; and
- 4,422 genuinely free bytes before the protected update record.

All 477 planned artifacts are byte-for-byte equal to both their recorded hash
and the corresponding component slice inside the pinned package.  Source
bodies are therefore current package occupants, not caves.  Alignment bytes
can change only as part of a complete tail repack that also regenerates every
later address, relocation, redirect, and receipt; the solver does not count
them as directly writable.

The current contiguous final binary needs 26,794 bytes with Apple clang or
26,726 bytes with Linux clang.  It is short by 22,372 or 22,304 bytes.  The
minimal whole-region suffix that would have to move for either profile starts
at `0x007F7060` with the package-owned 3,662-byte IAR output closure.  It
comprises 171 rows and 24,154 occupied bytes, includes the package-owned
11,520-byte ANCC dispatcher,
and continues through the Cordio security tail.  No alternate placement for
that closed dependency set is authenticated.

Ignoring contiguity gives a separate lower bound: at least four package-owned source
rows would have to move.  The three largest total only 20,686 bytes.  The
smallest count that covers either shortfall adds the 2,128-byte
`hciEvtProcessCmdCmpl` body to the ANCC dispatcher and the IAR input/output
closures, for 22,814 bytes.  These four scattered holes would still not be a
valid placement plan.

## Conditional reclaim upper bound

The complete stock CFF callable/physical envelope contributes 16,924 bytes.
The exact compact tables and 19 independently authenticated callback words
cover 364 bytes, but four callback bytes at `0x005AC5EC` are already inside the
physical envelope.  They therefore add 360 unique bytes.  These bytes become
candidates only after a source-built class owns the module route, every old
root/direct reference is retired, and a reviewed noncontiguous linker owns
every interval.

Even deliberately treating those 17,284 unique conditional bytes, all 302
alignment bytes, and the 4,422-byte tail as available yields only 22,008 bytes.
That remains 4,786 bytes short for Apple clang and 4,718 bytes short for Linux clang.
Consequently the known conditional regions cannot close capacity even before
their noncontiguous layout and liveness conditions are enforced.

## Exact scatter feasibility bound

A scatter layout can legally count only the 16,924-byte authenticated stock
CFF envelope, 360 unique authenticated CFF table/callback bytes outside that
envelope, and the 4,422-byte application tail.  Its deliberately optimistic
upper bound is therefore 21,706 bytes.  The Apple final link has 21,846 bytes
of text, 16 of unwind index, and 4,918 of read-only data (26,780 minimum
loadable bytes), leaving a 5,074-byte minimum shortfall.  Linux has 21,778,
16, and 4,918 bytes respectively (26,712 total), leaving 5,006 bytes.  The
existing flat final binaries remain 5,088 and 5,020 bytes short.

The finalized relocation census is `R_ARM_ABS32`, `R_ARM_PREL31`,
`R_ARM_THM_CALL`, `R_ARM_THM_JUMP24`, `R_ARM_THM_MOVT_ABS`, and
`R_ARM_THM_MOVW_ABS_NC`.  The widest hypothetical binding domain is 3,958,234
bytes, inside the Thumb call/jump range; full-width data-pointer encodings are
also range-compatible.  Range is not the blocker.  An arithmetic layout that
also consumes the unauthorized bootloader headroom would have 462 Apple or
530 Linux text bytes to spare, but it lacks application ownership and
cross-entry atomicity.  Because legal application capacity is already smaller
than the indivisible finalized loadable-section sum, the solver deliberately
does not emit or represent an exact scatter link.

The pinned Ghidra call graph has no direct call edge from outside the stock CFF
envelope to any of its 101 starts.  A halfword-aligned scan finds 62
pointer-like words reaching 58 starts: 40 are in authenticated compact tables,
18 in authenticated callback slots, three inside the envelope, and the lone
remaining word at `0x004CD47E` is instruction bytes inside the pinned
`0x004CD3AA` body.  This supports only conditional retirement after a new
class route owns registration; it does not make the old bytes writable now.

Other source-replaced stock bodies remain excluded.  The repository does not
yet contain a component-wide proof covering alternate entries, literal pools,
callback tables, direct references, and call-graph liveness for those scattered
bodies.  Describing them as writable caves would therefore exceed the evidence.

## Disposition

Production placement and the guarded class-pointer patch remain false.  No
firmware image is emitted.  The update record at `[0x007FE000,0x007FE010)` is
bootloader-owned and never enters the capacity pool.  Font payload identity,
dynamic allocation, task stack, WCET, compiler-byte identity, and physical G2
rendering remain separate unavailable gates; no hardware behavior is claimed.

Run the deterministic audit and hostile tests with:

```sh
cd g2
python3 tools/analyze_g2_freetype_cff_capacity_solver.py --check-manifest
python3 -m unittest -v tests/test_freetype_cff_capacity_solver.py
```
