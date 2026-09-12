# G2 bootloader BL-006 cluster 0x00427588..0x004275EA source closure

84 of the 98 retained `official_blob` bytes -- the 60-byte
System-PLL literal pool at `0x00427588`, the 4-byte range-error
cell word at `0x004275E4`, the 18-byte range-error setter at
`0x004275D2` (relocated), and the 2-byte divide-by-zero return at
`0x004275E8` (in place, byte-exact) -- are now produced from
reviewed MIT C. The 14-byte setter prologue at
`0x004275C4..0x004275D2` stays retained: its only routed
caller-candidate sits in a survey-corroborated dead tail, and
dead-tail fill is still a missing builder primitive.

| Region | Bytes | Source symbol | Mechanism |
| --- | --- | --- | --- |
| `0x00427588..0x004275C4` | 60 | `open_cfw_bootloader_bl006_pool_427588` | `in_place_data` |
| `0x004275D2..0x004275E4` | 18 | `open_cfw_bootloader_double_range_error_4275d2` | in-place leaf (functionally replaced, exact fill) |
| `0x004275E4..0x004275E8` | 4 | `open_cfw_bootloader_bl006_word_4275e4` | `in_place_data` |
| `0x004275E8..0x004275EA` | 2 | `open_cfw_bootloader_u64_divzero_4275e8` | in-place leaf, byte-exact |

Sources: `components/bootloader/core_overlay/runtime_bl006_syspll_pool_427588.c`
(new, 6,235 bytes), `runtime_double_range_error_4275d2.c` (new,
1,744 bytes), `runtime_u64_divzero_4275e8.c` (new, 814 bytes).
The verifier is
`g2/tests/test_runtime_bootloader_bl006_syspll_pool.py`
(stock-SHA authentication, byte-exact rebuilds, relocation-free
checks, overlay registration checks, pinned loader/caller sets
with reviewed-spelling checks, stale-span zero-data-relocation
checks, host behavior of the relocated setter, and an explicit
retained-remainder assertion); the host fixture is
`g2/tests/fixtures/bootloader_double_range_error_4275d2_host.c`.

## Method

Same loader-mapping refinement as the 0x00424AEA cluster audit,
with one correction made during the pass: a whole-image linear
Capstone sweep desynchronizes before this address (M-profile
instructions without `CS_MODE_MCLASS`, then data regions), so
every span is decoded anchored at its own start -- in-place and
cave stock spans, patch spans, and explicitly listed retained
dead spans from the live `overlay.json` -- using operand-based
literal-target recovery (`ARM_OP_MEM` with PC base,
`Align(PC,4)+disp`). Thumb literal targets are computed as
`Align(PC,4)+imm`; each found loader is classified live (inside
a byte-exact shipped body), stale (inside a named replaced span
whose overlay relocation contract carries only
`R_ARM_THM_CALL` relocations, dead by construction), dead
(inside a survey-corroborated retained dead span), or foreign
(blocks admission).

## Word table

Pool `0x00427588`: `10000000U` (megahertz scaling, reviewed
`runtime_syspll_min_fvco_427040.c`); `0x00431E70` (post-divider
table base, reviewed `OPEN_CFW_SYSPLL_POSTDIV_TABLE` in the same
source); `1000000U` (megahertz scaling, reviewed min-FVCO and
postdiv sources); `0x03938700` (`60000000U` low minimum-VCO
bound, reviewed `runtime_syspll_postdiv_427160.c` -- note
`0x03938700` == 60000000; the stock loader at `0x00427172`
feeds the first min-FVCO call); `240000000U` (high
minimum-VCO bound, same source, stock loader at `0x0042718E`);
`0x00433CC8`/`0x00433CB8` (PTS_B/PTS_A tables, reviewed
`OPEN_CFW_SYSPLL_PTS_B`/`OPEN_CFW_SYSPLL_PTS_A` in the same
source); `0x20027010` (SYSPLL state array, reviewed
`g2-bootloader-syspll-initialize-4272ac-source-closure.md`,
stale loader at `0x004272C2`);
`0x00504C30` (handle magic, same closure, stale loader at
`0x004272EC`); `0x01504C30` (tagged-handle magic, reviewed
`g2-bootloader-syspll-lock-wait-427522-source-closure.md` and
spelled `HANDLE_MAGIC` in the deinitialize/enable/disable/
configure sources; stale loaders at `0x0042752E`,
`0x0042731C`, `0x0042736A`, `0x004273E6`, `0x00427418`);
`0x40020060` (VRCTRL, reviewed
`runtime_syspll_enable_427360.c`, stale loader at
`0x00427386`); `0x400204D8` (PLLCTL0, stale loaders at
`0x0042753A`, `0x004273C4`, `0x004273F4`, `0x0042747E`);
`0x400204DC` (PLLDIV0, reviewed
`runtime_syspll_configure_42740c.c`, stale loader at
`0x004274AC`); `0x400204E0` (PLLDIV1, stale loaders at
`0x00427544`, `0x004274C0`); `0x400204E4` (PLLSTAT, stale
loader at `0x00427580` in the lock-wait tail fill). The
`10000000U`/`0x00431E70`/`1000000U` loaders sit in the
replaced min-FVCO span (`0x0042708A`, `0x004270C8`,
`0x0042711A`, `0x00427120`); the `1000000U`/`60000000U`/
`240000000U`/PTS loaders sit in the replaced postdiv span
(`0x004271CC`, `0x004271FA`, `0x00427226`, `0x0042724C`,
`0x00427172`, `0x0042718E`, `0x004271C8`, `0x004271E6`).
Every owning span's shipped replacement carries only
`R_ARM_THM_CALL` relocations (stale by construction); no
loader sits in any byte-exact shipped body. All PCs are
pinned by the verifier. A whole-image linear sweep misses
the 32-bit `ldr.w` loaders (e.g. min-FVCO at `0x0042708A`)
through desync -- anchored per-span decode is required.

Word `0x004275E4`: `0x20027194`, the range-error status cell
published by the setter tails (stale loaders at `0x004275CC`
in the retained dead A prologue and `0x004275DA` in the
setter-B stock span, which this pass installs source-owned
bytes into, in place).

## Tails

Setter B (`0x004275D2`): the single stock caller is the
tail-branch at `0x00422748` in the byte-exact ldexp scaling
core (overflow/underflow paths set d0 then publish `0x22`).
The compiled 18-byte clean-room body
(`push {r1, r2}; movw r1, #0x7194; movt r1, #0x2002;
movs r2, #0x22; str r2, [r1]; pop {r1, r2}; bx lr`),
SHA-256 `f01e4b7395338750ee33d795cb12293094418adf6965d78e2aaa70e465c62373`,
exactly fills the 18-byte stock span, so it is installed in
place (no redirect, no overlay growth -- the overlay tail
already ends exactly at the partition boundary). The body
preserves r0/r3 untouched and saves/restores its two scratch
registers, matching the observed stock preservation; the
stock `mov r8, r8` alignment no-op is not reproduced. The
pre-existing `R_ARM_THM_JUMP24` relocation in the ldexp core
keeps its reviewed absolute target (`0x004275D2`, now
source-owned bytes), so no caller bytes change. Host
behavior (store `0x22`, neighboring cell preserved) passes
through the fixture.

Div-zero (`0x004275E8`): the single stock caller is the
tail-branch at `0x004228E0` in the byte-exact divmod loader
(zero-divisor path). The 2-byte stock body is a bare shared
`bx lr` returning with the dividend registers undisturbed;
the in-place reconstruction is the identical 2 bytes, so
`expected.sha256` equals `stock_sha256`
(`c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8`).
No patch site is needed. An earlier misreading of the pool
word's high half as `movs r0, #2` is corrected here: the
div-zero entry performs no register write.

A prologue (`0x004275C4..0x004275D2`, SHA-256
`a19e550e2348b6ab72f1f7ef0d2d2afa12d5b6e0944b3df1251c96119706d103`):
the only stock-decode caller (`blo.w` at `0x00427D92`)
sits inside the survey-corroborated dead binary32
remainder-core tail (`g2-bootloader-bl006-retained-seam-survey.md`
category A). It stays `official_blob` until the dead-tail
fill primitive exists.

## Not established

- Every pool word now carries a reviewed spelling; no reserved
  grade remains in this cluster.
- The range-error cell's vendor documentation name is not
  claimed; only its observed store behavior on the ldexp
  range-error paths is reproduced.
- Non-PC-relative references are not covered by the loader scan.
- Relocated bodies execute in the overlay tail, so only
  in-place/cave/patch/dead spans are scanned for loaders;
  relocated sources are grepped for address references instead.
- No hardware, flashing, signing, or transmission operation
  occurred; hardware qualification stays blocked by unavailable
  physical evidence.

## Status

1326 of the 5,892 BL-006 bytes are now produced from reviewed
source (1242 prior plus 84 here). 4,566 bytes remain: 26 fully
uncovered regions (4,420 bytes -- unreachable stock tails
needing the dead-tail fill primitive, the 1,316-byte
binary32/float span at `0x00427E54..0x00428378`, and smaller
mixed/code spans), the 14-byte A prologue retained here, and
the two partial MSPI tails at `0x00424AB2` (56 bytes) and
`0x00424B88` (76 bytes).
