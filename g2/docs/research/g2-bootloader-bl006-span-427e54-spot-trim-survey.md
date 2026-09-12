# G2 bootloader BL-006 span 0x00427E54..0x00428378 structural survey

Date: 2026-09-12. Work item BL-006 (partial; 0 new source-owned bytes).

## Result

The last unexamined BL-006 region -- 1,316 bytes, flash-plan text
"Authenticated retained literal, table, and alignment bytes between
the binary32 runtime and SPOT-man[agement]" -- is four single-exit
Thumb-2 code subspans, not a literal pool. Nothing is admitted as
source-owned here: the named-field `in_place_data` route cannot
represent code, and no reviewed clean-room C reproduces these bodies.
What this pass contributes is a pinned decomposition (byte hashes,
prologue/epilogue encodings, exact callee and literal-target sets)
plus the two properties a future fill or reconstruction pass needs:
no word anywhere in the image equals any subspan entry, and the
whole-image survey still finds no surviving external branch into
the region. The verifier is
`g2/tests/test_runtime_bootloader_bl006_span_427e54.py` (8 tests).

## Structure

All spans are decoded anchored at their own prologues. A whole-span
linear sweep is untrustworthy here: it sails through the embedded
`50.0f`/`1000.0f` pool words at `0x00428060`/`0x00428064` and reports
phantom `bl` targets (including a SPOT timer ISR that no float code
would call). Byte-level facts first: exactly one `bx lr` (`7047`)
exists in the span, at `0x00427E82`; no `pop {...,pc}`; three
`push.w` prologues (`0x00427E84`, `0x00428068`, `0x00428240`); three
`pop.w {...,pc}` epilogues (`0x00428056`, `0x0042823C`,
`0x00428374`); no 16-bit push. Prologue/epilogue register lists
balance in all three functions.

| Subspan | Range | Bytes | SHA-256 | Shape |
| --- | --- | --- | --- | --- |
| T0 classifier tail | `0x00427E54..0x00427E84` | 48 | `609d289f...f791ab2c` | `vcmp.f32` vs pool, returns 2/3/4, `bx lr` |
| F1 | `0x00427E84..0x00428068` | 484 | `b5072ed7...63cd021fa` | `push.w {r3-r11,lr}` / `pop.w {r0,r4-r11,pc}` |
| F2 | `0x00428068..0x00428240` | 472 | `7828372b...5e284388ad` | `push.w {r1-r11,lr}` / `pop.w {r0-r2,r4-r11,pc}` |
| F3 | `0x00428240..0x00428378` | 312 | `aed159d1...7cbf41289` | `push.w {r3-r11,lr}` / `pop.w {r0,r4-r11,pc}` |

Span SHA-256 `0ce1f663...58821` matches the survey pin. No function
carves local stack (`sub sp` absent; scratch stores reuse the
register-save area, the usual IAR pattern). The `push {r7,lr}` at
`0x00428378` belongs to the source-owned SPOT-manager transition
sequence that starts the next region, confirming the F3 boundary.

T0 is the documented suffix tail of the stock
`float_range_classify_427e0c` body: the reviewed replacement covers
72 of the 120 stock bytes
(`g2-bootloader-float-math-427c90-427e84-source-closure.md`, "68
bytes of authenticated suffix typed as unreachable", and "No direct
interior call or stored Thumb pointer reaches either suffix"). The
`vldr` pair resolves under the standard Thumb `Align(PC,4)+imm`
rule to `0x00428060` = `50.0f` (`0x42480000`) and `0x00428064` =
`1000.0f` (`0x447A0000`), confirmed with `struct.unpack`.

## Callees (exact sets, all out-of-span, all named by reviewed sources)

- T0: none.
- F1: `0x0041CCD6` trim finalize, `0x0041D1C0` delay cycles,
  `0x0041E1E8` IRQ resume, `0x0041E22E` IRQ pause, `0x0042A04A`
  SPOT timer service, `0x0042A1BC` VDDC/VDDF Ton-trim selector.
- F2: same minus trim finalize.
- F3: delay cycles, SPOT timer service, trim selector, plus
  `0x0041CC48` transition start (no IRQ pause/resume, no finalize).

Symbol names come from the reviewed SPOT sources
(`runtime_spotmgr_state_transition_42b294.c`,
`runtime_spotmgr_timer_irq_service_42a04a.c`,
`runtime_control_services_42bf54.c`, which names `0x0041D1C0` the
delay-cycles helper). No call targets the inside of the span, so
there are no internal entries beyond the four prologues.

## Literal pools (all outside BL-006, other items' territory)

Every PC-relative data target lies in retained SPOT-table gaps:

- `0x00428A78..0x00428A90`: SRAM state words (`0x20026BA0`,
  `0x20000154`, `0x200270B0/B4/C0/C4`) and power registers
  (`0x400083E0`, `0x40008064`).
- `0x00428BA8`: `0x4002004C`, `0xE000ED14`.
- `0x00428C84..0x00428CA0`: power registers (`0x40020044`,
  `0x4002037C`, `0x40020080`), SRAM words, and `0x3F666666`
  (`0.9f`).

F1 loads 16 of these slots, F2 loads 14, F3 loads 13 (exact sets
in the verifier). These pools sit in the `0x004283E2..` retained
regions between the source-owned SPOT-manager transition
sequences -- closing them belongs to the SPOT work items, not
BL-006, and is recorded here only so a future pass knows what this
span's code reads.

## Deadness evidence (stronger than the survey's region-start check)

- Whole-image word scan: no 4-byte little-endian word anywhere in
  the stock image equals `0x00427E54`, `0x00427E84`,
  `0x00428068`, or `0x00428240`, with or without the Thumb bit
  set (the survey only checked the region start).
- Whole-image branch scan (reused via the survey module, not
  reimplemented): the region's verdict is not
  `POSSIBLY_REACHABLE_NEEDS_REVIEW`, and the report-wide
  `needs_review_count` stays 0.
- No internal calls; no stored pointers; single exits.

Functional reading (hypothesis, not a claim): F1/F2/F3 are three
SPOT trim-search/measure variants (pause IRQs, delay, select trim,
resume/finalize) for different rails or corners, with T0's
classifier tail selecting a trim index from a float reading. The
callee sets and pool contents support this; the exact measured
quantities and rail assignment are not established.

## Why this span stays retained

- As code it cannot go through `in_place_data` (that mechanism is
  for data with named, loader-evidenced fields; byte dumps do not
  count as completion).
- As dead bytes it needs the still-missing dead-tail fill
  primitive (`g2-bootloader-bl006-retained-seam-survey.md`
  category A follow-up): the builder must verify unreachability
  and emit deterministic fill accounted as generated data. This
  span is now the best-characterized candidate for that
  primitive's first use -- entries, exits, callees, pools, and
  deadness are all pinned -- but the primitive itself is a shared
  `apollo_overlay.py`/`build_component.py` change, out of scope
  for this pass.
- As live code it would need full clean-room reconstruction with
  behavioral qualification; the deadness evidence above points
  the other way, and the SPOT tables it reads are themselves
  retained under other items.

The 2-byte `bx lr`/`pop` stubs elsewhere in the
retained set (`0x00426C22`, `0x00426C70`, `0x004279EE`) were
explicitly considered for the `u64_divzero_4275e8` in-place-leaf
precedent and rejected: unlike that 2-byte function, which keeps
its live caller in the byte-exact divmod loader, these stubs have
no caller in any shipped body -- they are dead tails, not shared
returns, and admitting them as leaves would mislabel dead bytes
as functions.

## Status

BL-006 stands at 1,326 of 5,892 bytes from reviewed source
(unchanged this turn). Remaining: the 26 category-A dead tails
(3,104 B) plus adjoining dead heads (`0x00424AB2` 56 B,
`0x00424B88` 76 B) and the `0x004275C4` prologue (14 B), all
waiting on the dead-tail fill primitive; and this 1,316-byte
span, now structurally surveyed with deadness pinned. No
hardware, flashing, signing, or transmission operation occurred;
hardware qualification stays blocked by unavailable physical
evidence.
