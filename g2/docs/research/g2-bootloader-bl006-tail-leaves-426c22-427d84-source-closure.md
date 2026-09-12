# G2 bootloader BL-006 tails 0x00426C22/0x00426C70/0x00427ABE/0x00427D84/0x004275C4/0x00425160/0x004264B0 source closure

84 more of the retained `official_blob` bytes -- seven dead tails
as byte-exact `in_place_leaves` plus four no-loader fragment /
pad / literal slots as `in_place_data` -- are now produced from
reviewed MIT C. Seven official regions close; BL-006 moves from
62 to 69 of 77 regions (1,554 to 1,722 closed-region bytes of
5,892 by overlay-placement coverage against the flash-plan
official regions; the +168 counts the whole 98-byte System-PLL
region closed by its last 14 bytes).

| Span | Bytes | Entry |
| --- | --- | --- |
| `0x00426C22..0x00426C24` | 2 | `open_cfw_bootloader_memset_term_tail_426c22` (`pop {r4, pc}`) |
| `0x00426C70..0x00426C72` | 2 | `open_cfw_bootloader_clkgen_hfadj_term_426c70` (bare `bx lr`) |
| `0x00427ABE..0x00427AD6` | 24 | `open_cfw_bootloader_cmdq_status_rem_tail_427abe` |
| `0x00427D84..0x00427D98` | 20 | `open_cfw_bootloader_binary32_rem_tail_427d84` |
| `0x004275C4..0x004275D2` | 14 | `open_cfw_bootloader_syspll_alt_entry_4275c4` |
| `0x00425162..0x00425166` | 4 | `open_cfw_bootloader_mspi_disable_tail_425162` |
| `0x00425160/.66/.68` | 2+2+4 | frag / pad / lifecycle word (data) |
| `0x004264B0` / `0x004264B2` | 2+8 | frag (data) / publish tail (leaf) |

New sources (all MIT, all with portable C twins for host tests):

- `components/bootloader/core_overlay/runtime_bl006_terminal_returns_426c22.c`
  (both 2-byte terminal returns).
- `components/bootloader/core_overlay/runtime_bl006_cmdq_status_binary32_tails_427abe.c`
  (status remainder with internal branches via local labels;
  remainder-code tail with IT blocks, `pop.w`, and the out-of-span
  `blo.w` to `0x004275C4`).
- `components/bootloader/core_overlay/runtime_bl006_syspll_alt_entry_4275c4.c`
  (alternate setter entry loading the `0x004275E4` cell pointer
  and joining the shared body at `0x004275DE`).
- `components/bootloader/core_overlay/runtime_bl006_disable_tail_425162.c`
  (disable mini-tail).
- `components/bootloader/core_overlay/runtime_bl006_tail_fragments_425160.c`
  (four data slots).
- `components/bootloader/core_overlay/runtime_bl006_irq_disable_tail_4264b2.c`
  (`str.w` publish tail).

The verifier is
`g2/tests/test_runtime_bootloader_bl006_tail7_fragments.py`
(14 tests: stock-SHA authentication, byte-exact leaf and data
rebuilds with zero relocations, overlay registration, exact
survey-verdict pins, a whole-image `bl`-caller sweep, a
no-routed-loader sweep for the fragment slots, and ctypes
host-behavior cases against inline oracles).

## Why leaves, and why two reviewed encodings

Same precedent as the 424AB2/4250E6, 42647C/4278BC, and
4264F6/4279EE tail clusters: executable tails with behavior to
reconstruct go through `in_place_leaves`; loader-free slots go
through `in_place_data` as named layout preservation (the
reserved-word precedent). Two tails branch out of span, and the
relocatable object assembles at address 0, so far-absolute
mnemonic operands are rejected (`blo.w 0x4275c4`) or widened
(`b 0x4275de` assembled 4 bytes instead of 2). Those two
instructions -- and only those -- are spelled with reviewed
explicit encodings (`.inst.w 0xF4FFAC17`, `.inst.n 0xE005`):
each names its instruction, PC, target, and offset in the
comment, and each encoding was cross-checked by assembling the
identical branch at the identical offset with the same toolchain
(`blo.w` 2002 back emits `ff f4 17 ac`; `b` 10 ahead emits
`05 e0`; a first attempt at the wrong offset emitted `16 ac`,
which is how the true -2002 offset was confirmed against the
branch at `0x00427D92`, PC `0x00427D96`). The byte-exact rebuild
test pins both emissions.

## Tail semantics (from anchored stock decode)

- A `0x00426C22` (`pop {r4, pc}`): restore the head-owned r4
  slot, return to the head-owned link slot.
- B `0x00426C70` (`bx lr`): bare return, r0 pass-through.
- C `0x00427ABE` (r0 = status, r4/r5 head-owned): clear
  `*(r4 + 0x0D)`, hit-test the status against the
  `*(r5 + 0x24) -> *(... + 0x20)` mask thread, publish the
  boolean at `r4 + 0x0E`, return 0 via `pop {r1, r4, r5, pc}`.
- D `0x00427D84` (r0..r3 operands, r4 head-owned): under the
  incoming carry flag, `r0 = ~r3` (HS, flags untouched) or
  `apsr = r1 + r2; if (!Z) r0 = ~r3` (LO, stock CMN); restore
  r4; carry-clear transfers to `0x004275C4`, else return. The
  host twin takes the incoming APSR explicitly.
- E `0x004275C4`: `push {r0-r3, lr}; sub sp, #4; r0 = 0;
  r1 = *(0x004275E4); r2 = 0x21; goto 0x004275DE`, joining the
  already-routed range-error publish span (identical bytes in
  the built image). This is the 0x21 sibling of the routed
  `0x004275D2` (0x22) entry.
- F `0x00425162`: `r0 = 0; pop {r1, r4, r5, pc}`. The halfword
  before it is the orphaned second half of the replaced disable
  head's `bl #0x0041D1C0` at `0x0042515E` (authentic stream
  decoded anchored at `0x00425140`); the halfword after the tail
  is alignment NOP and `0x00425168` holds the `0x0007FFFF`
  lifecycle word. Neither fragment nor word has a loader in any
  routed span.
- G `0x004264B2`: `*(r2 + 0x200) = r1; r0 = 0; bx lr`. The
  halfword before it is the orphaned second half of the
  replaced head's `adds.w` at `0x004264AE`; this resolves the
  prior turn's deliberate exclusion (mid-instruction slice via
  the data route, executable suffix via a leaf).

Every span's stock SHA-256 matches the pin already recorded in
the whole-image retained survey.

## Deadness evidence

The `0x00425160`, `0x004264B0`, and `0x00427ABE` regions grade
`corroborated_unreachable_control_flow`; the `0x00426C22`,
`0x00426C70`, and `0x00427D84` regions grade
`no_control_flow_reference_found` (zero inbound references --
the weaker verdict is asserted as-is, never upgraded). A
whole-image Capstone `bl` sweep finds no caller of any new
entry. The stock-internal branches into these tails originate
in replaced head spans whose source-owned bodies return/jump
away in the built image. No live traffic is claimed: the
reconstructions document dead bytes from reviewed source and
pin the behavior the replaced heads must cover.

## Re-derivation forced by this turn

Routing the `0x004275C4` prologue and the `0x00427D84` caller
changed two pins owned by the System-PLL pool verifier, which
anticipated exactly this ("a prologue was routed; audit must be
re-derived"):

- `test_runtime_bootloader_bl006_syspll_pool.py`: the
  "prologue stays retained" pin became
  `test_a_prologue_now_routed` (prologue covered only by the
  new leaf; sole caller `0x00427D92` now in the byte-exact
  binary32 leaf); the two routed spans left `DEAD_SPANS` (the
  setter-B span entry was equally stale -- its body is the
  earlier exact-fill range-error leaf -- so it left too); the
  `0x004275E4` cell contract is now "mixed" (byte-exact loader
  `0x004275CC` in the new leaf, stale loader `0x004275DA` in
  the exact-fill body). All 8 tests pass.

## Deliberately excluded

- `0x0042799E` (32 B block-acquire fragment): branches out to
  the replaced head with no in-span exit -- not a leaf entry.
- `0x00427B90` (26 B error fragment): entry branches back into
  the replaced head -- not a single-entry tail.
- `0x004263E0` (108 B blocking-transfer tail): single
  entry/exit but three `bl` calls to live helpers with
  head-owned registers -- needs heavier callee modeling.
- `0x0042423C` (1,618 B), `0x004248E2` (148 B), `0x00424E84`
  (482 B), `0x0042612C` (436 B) unreachable tails and the
  `0x00427E54` (1,316 B) literal/table span: bulk dead
  code/data needing fill primitives or larger reconstruction.
  Follow-ups for later BL-006 turns.

## License and toolchain

All six sources are MIT (new openCFW code, no vendor text).
Leaves pin the reviewed Apple-clang Cortex-M55 flags (`-Oz
-fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fropi`, `strict_relocation_contract`,
zero relocations) plus the standard linux-clang profile; data
slots use the pool flags. The two `.inst` emissions are covered
above and by the rebuild test.

## Build and gate standing

- New verifier: 14/14 pass (stock pins, byte-exact leaf/data
  rebuilds, registration, survey verdicts, no-`bl`-caller
  sweep, no-loader sweep, seven ctypes behavior groups).
- Neighbor suites green: retained survey (5), mspi-clkgen-cmdq
  tails (9), cmdq-irq tails (11), syspll pool as re-derived
  (8).
- `build_component.py` for the bootloader overlay succeeds
  with the 11 entries (15,240 overlay bytes at `0x00434478`).
- `make -C g2 bootloader-component` remains blocked at its
  `littlefs-snapshot` prerequisite by another lane's
  uncommitted `apollo_main` overlay change (untouched).
- `test_bootloader_core_overlay`
  `test_provider_contract_is_manifest_ready_and_hardware_free`
  was already red before this turn (pinned canonical-manifest
  contract predates uncommitted admissions across lanes; the
  checked-in flash plan still grades routed spans
  `official_blob`); this turn extends the same drift and leaves
  the manifest lane untouched.

## Score

BL-006 moves from 62 to 69 of 77 regions (1,554 to 1,722 of
5,892 closed-region bytes; +84 newly source-owned bytes this
turn). Eight regions (4,170 bytes) remain, listed above.
Hardware qualification stays blocked by unavailable physical
evidence; no hardware operation occurred.
