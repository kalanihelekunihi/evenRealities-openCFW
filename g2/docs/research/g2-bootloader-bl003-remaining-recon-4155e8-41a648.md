# G2 bootloader BL-003 remaining-region reconnaissance

Work item `BL-003` covers 11,158 retained bootloader bytes across the
eleven official regions in `[0x004155E8,0x0041A648)`. This session closed
two of them (30 bytes total):

- `docs/research/g2-bootloader-bounded-sink-415672-source-closure.md` --
  `[0x00415672,0x0041568C)`, 26 bytes.
- `docs/research/g2-bootloader-trap-stubs-416026-416030-source-closure.md` --
  `[0x00416026,0x0041602A)`, 4 bytes.

This document records what was established about the other nine regions
(11,128 bytes) so a follow-up agent does not have to redo the reconnaissance.
Nothing below is claimed as source-owned; `report_transparent_coverage.py`
and the flash plan still show these bytes as `official_blob`.

## `[0x004155E8,0x0041560C)` -- 36-byte address table (undetermined consumer)

Decodes cleanly as nine little-endian words, not instructions:

```
0x20026878  0x2002712c  0x20027130  0x2002718c   (SRAM addresses)
0x00432808  0x00433e68  0x00431258  0x00433fd4  0x00432bdc   (flash addresses)
```

The four SRAM words are plausible object addresses (compare
`0x2002712C`/`0x20027130`, the two mutex-handle SRAM slots documented in
`docs/research/g2-bootloader-redirect-init-source-closure.md`, immediately
adjacent -- `redirect_init` itself occupies `[0x00415590,0x004155E8)`, right
before this table). The five flash words all land in `[0x00431000,0x00434000)`,
well past this work item's `0x0041A648` upper bound and past anything
currently registered in `overlay.json` (`grep`-checked against every
`isolated_leaves`/`relocated_leaves`/`in_place_leaves`/`cave_leaves`
`runtime_address`: no match). Nothing in the currently-admitted source
reads this table via absolute or PC-relative load, so which code consumes
it -- and therefore what each slot means -- is not established. Do not
encode this as an `in_place_data` array of unexplained pointers; that would
be exactly the "binary bytes encoded as C arrays" the source-only goal
excludes. Establishing meaning requires finding and admitting the (still
opaque) consumer first.

## `[0x00415732,0x00415758)` -- 38-byte semihosting-shaped cave (candidate, not closed)

Sits between the generated forward-copy (`memcpy`) redirect and the
generated bounded byte-comparison (`memcmp`) redirect. Disassembles as:
2 bytes of alignment padding, then a 30-byte function, then 2 bytes of
alignment padding, then a 4-byte PC-relative literal:

```
415732: 2e00            (alignment filler, decodes as lsls r6,r5,#0 but is dead)
415734: b500            push {lr}
415736: b083            sub  sp, #0xc
415738: 9100            str  r1, [sp]
41573a: 9201            str  r2, [sp, #4]
41573c: 9002            str  r0, [sp, #8]
41573e: 466a            mov  r2, sp
415740: 4904            ldr  r1, [pc, #0x10]   ; -> 0x00415754 == 0x00021010
415742: 2018            movs r0, #0x18
415744: beab            bkpt #0xab
415746: 2800            cmp  r0, #0
415748: d101            bne  #0x41574e
41574a: f0026dfa? -> bl  #0x00417c28
41574e: b003            add  sp, #0xc
415750: bd00            pop  {pc}
415752: bf00            nop
415754: 1010 0200        (literal word 0x00021010, consumed by the ldr above)
```

`bkpt #0xab` with `r0 = 0x18` and `r1` pointing at a 3-word block built from
the function's own three arguments is shaped exactly like the open ARM
semihosting `SYS_EXIT_EXTENDED` (operation `0x18`) call convention (ARM
semihosting is a published Arm Ltd. specification, not vendor IP): on
return, `r0 == 0` on unsupported/no debugger, falling through to
`bl 0x00417C28` as a fallback. This reading is **plausible but not
verified** -- the literal `0x00021010` doesn't independently confirm an
ADP-style reason/subcode block, and no differential oracle can exercise a
real semihosting trap on this host. Do not admit this as source without
either (a) corroborating what `0x00417C28` does (still unrouted) or (b) a
stronger identification of the literal's role. Treat this write-up as a
lead, not a closure.

## `[0x00415FDA,0x00415FFA)` -- 32-byte mixed literal (undetermined)

```
0000 cc700220 c4710220 302e3000 232e2300 3f2e3f00 d04c0220 00220 1f01bbe
```

Two clear SRAM-address words (`0x200270cc`, `0x200271c4`) plus a run of
printable bytes (`0.0#.#?.?`-shaped, NUL-separated) that looks like several
short null-terminated fragments rather than one string, plus a trailing
`0xbe1bf001`-shaped tail that does not resolve to a clean address. Not
decoded with enough confidence to represent as meaningful C; left for a
follow-up with the actual logging-format call site in hand.

## `[0x0041658C,0x00416590)` and `[0x00417AD0,0x00417AD4)` -- candidate literals (verified, not routed)

Both fully decoded and verified byte-identical against
`apollo_overlay.compile_in_place_data_group` (the mechanism
`components/apollo_main/core_overlay/overlay.json` already uses for its
Cordio SMP state tables):

- `[0x0041658C,0x00416590)`: the single word `0x200270D4`, the SRAM address
  of the shared event-flags object used by the neighboring
  (already-admitted) CMSIS-RTOS2 event-flags set/wait wrappers. Candidate
  source: `components/bootloader/core_overlay/runtime_event_flags_literal_41658c.c`.
- `[0x00417AD0,0x00417AD4)`: bytes `1B 5B 00 00` -- the ANSI CSI-start escape
  (`ESC '['`) EasyLogger uses to open a terminal color sequence, plus two
  alignment bytes. Candidate source:
  `components/bootloader/core_overlay/runtime_easylogger_csi_literal_417ad0.c`.

Both compile to their exact stock bytes (verified interactively with
`apollo_overlay.compile_in_place_data_group`, `record=True`, against the
component's canonical Apple clang 21 Cortex-M55 flags). Neither is
registered in `overlay.json` and neither contributes to source-owned
accounting, because **`components/bootloader/core_overlay/build_component.py`
does not read an `in_place_data` key at all** -- unlike
`components/apollo_main/core_overlay/build_component.py`, which already
loops over `config.get("in_place_data", [])` (that builder's line ~270) and
calls the shared `compile_in_place_data_group`/`append_relocated...` helpers
in `tools/apollo_overlay.py`. The shared compile/validate logic already
exists and already works for this component's data; only the bootloader
component's own build-orchestration script needs the same few lines of
wiring the apollo_main builder already has. That wiring was deliberately
left out of this session's changes: it touches a shared script that other
concurrent agents may be editing, and the two literals above are a small
enough return to justify a dedicated, reviewed follow-up rather than a
same-session addition to shared build infrastructure.

## `[0x0041699A,0x004169A4)` -- 10-byte literal (partially identified, not routed)

Two-byte pad, then two words: `0xE000ED04` (the Cortex-M SCB->ICSR register
address -- an ARMv7-M/v8-M architecture-defined address, not vendor IP) and
`0x0041639B` (Thumb-bit-set pointer to `0x0041639A`, which is
`open_cfw_bootloader_runtime_callback_41639a`, an **already-admitted**
in-place leaf; see
`docs/research/g2-bootloader-runtime-callback-41639a-source-closure.md`).
This is the strongest remaining data candidate: both words have identified,
named meaning, and the second literally points at existing source. Not
closed this session for the same reason as the two literals above (no
`in_place_data` wiring in this component's builder yet); recommended as the
first follow-up once that wiring lands.

## `[0x004172DA,0x0041733C)` -- 98-byte table of 24 flash addresses (undetermined)

Two-byte pad, then 24 words, all in `[0x00430000,0x00434000)`:

```
0x004341b8 0x00431a40 0x00432860 0x00432598 0x00431a7c 0x0043288c
0x00430d3c 0x00430cc8 0x004318cc 0x0043138c 0x00431d90 0x004341b0
0x004328b8 0x004314f8 0x004328e4 0x00431dc8 0x004325c8 0x00433738
0x00433420 0x004320e0 0x0043190c 0x00431a04 0x00432114 0x00431e00
```

None match a `runtime_address` currently registered anywhere in
`overlay.json`'s leaf tables -- they point into a part of the bootloader
this work item's range does not cover and no other landed work has named
yet. Same guidance as the 36-byte table above: do not admit as an opaque
pointer array; find and name the consumer/targets first.

## `[0x00417B3E,0x00417B48)` -- 10-byte literal (identified, not routed)

Two-byte pad, then two words: `0x20` (ASCII space) and `0x5B` (ASCII `[`).
Small integer/character constants, consistent with "alignment and
punctuation bytes between source-replaced EasyLogger helpers". Same
`in_place_data`-wiring blocker as the SRAM/CSI literals above; not routed
this session.

## `[0x00417BB8,0x0041A648)` -- 10,896-byte compatibility tail (unanalyzed)

No `docs/research/g2-bootloader-*` audit currently names any address inside
this span; it is the single largest unaddressed piece of `BL-003` by far
(97.6% of the item's bytes). A rough linear Thumb-2 sweep (Capstone,
`CS_MODE_THUMB`, no attempt to separate embedded data from code, so this is
an upper-bound heuristic and will overcount where data is misread as
instructions) over the raw stock bytes finds roughly 66 `push {..., lr}`
prologues, 64 `pop {..., pc}` epilogues, and 19 bare `bx lr` leaf returns in
4,546 decoded instruction slots -- on the order of 80-130 distinct
functions/leaves. This is well beyond one work item's scope to close; it
needs its own manifest/analyzer/audit series (following the
`g2-bootloader-<closure>-source-closure.md` + `tools/analyze_g2_bootloader_*.py`
pattern already used for the rest of this component) rather than a single
pass. No hardware operation occurred while producing this reconnaissance.

## Summary for the next BL-003 pass

| Region | Bytes | Status |
|---|---:|---|
| `0x4155E8-0x41560C` address table | 36 | undetermined consumer |
| `0x415732-0x415758` semihosting-shaped cave | 38 | plausible lead, not verified |
| `0x415FDA-0x415FFA` mixed literal | 32 | undetermined |
| `0x41658C-0x416590` SRAM literal | 4 | verified candidate, needs `in_place_data` wiring |
| `0x41699A-0x4169A4` ICSR + callback-ptr literal | 10 | identified, needs `in_place_data` wiring |
| `0x4172DA-0x41733C` 24-entry address table | 98 | undetermined consumer |
| `0x417AD0-0x417AD4` CSI-start literal | 4 | verified candidate, needs `in_place_data` wiring |
| `0x417B3E-0x417B48` punctuation literal | 10 | identified, needs `in_place_data` wiring |
| `0x417BB8-0x41A648` compatibility tail | 10,896 | unanalyzed, needs its own audit series |

11,128 bytes remain open after this session's two closures.
