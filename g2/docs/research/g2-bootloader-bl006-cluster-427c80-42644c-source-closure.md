# G2 bootloader BL-006 cluster 0x00427C80/0x0042644C source closure

20 of the retained `official_blob` bytes -- the 16-byte
command-queue suffix literal pool at `0x00427C80..0x00427C90` and
the 4-byte XIP aperture-base mask word at `0x0042644C..0x00426450`
-- are now produced from reviewed MIT C through the component's
`in_place_data` mechanism. Both payloads compile relocation-free
under the reviewed Apple-clang Cortex-M55 flags and reproduce the
authenticated stock bytes exactly, so `expected.sha256` equals
`stock_sha256` for both placements.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x00427C80..0x00427C90` | 16 | `open_cfw_bootloader_bl006_pool_427c80` |
| `0x0042644C..0x00426450` | 4 | `open_cfw_bootloader_bl006_word_42644c` |

Sources:
`components/bootloader/core_overlay/runtime_bl006_cmdq_suffix_pool_427c80.c`
and `runtime_bl006_mspi_aperture_mask_42644c.c` (both new). Each
pool is one packed struct with a named field per slot (not a byte
dump). The verifier is
`g2/tests/test_runtime_bootloader_bl006_cmdq_mspi_literals.py`
(stock-SHA authentication, byte-exact rebuilds, relocation-free
checks, overlay registration checks, encoding-sweep loader-set
pins with per-loader Capstone confirmation and reviewed-spelling
checks, stale-span zero-data-relocation checks, and
pointer-table absence checks).

## Method

Same loader-mapping refinement as the 0x00424AEA cluster audit,
with one correction made during the pass: anchored per-span
Capstone decode desynchronizes inside the error-resume span
(`0x00427B38..0x00427B90`) and the post-loop span
(`0x00427C12..0x00427C72`) and misses two initialized-magic
loaders (`0x00427BB6`, `0x00427C1E`). Loader discovery here is a
sync-independent whole-window encoding sweep for every
literal-load form (`ldr Rt,[pc,#imm]` 0x4800..0x4FFF, `ldr.w`/
`ldrb.w`/`ldrh.w`/`ldrsb.w [pc]`, `adr`/`adr.w`) over
[slot-0x1000, slot+0x1000) -- the forward window covers all
load forms (`ldr`/`adr` immediates only reach forward; the
extended window additionally rules out backward `adr.w`
references, of which there are none). Two intermediate sweep
versions undercounted (16-bit `ldr` top written as 0x48FF, then
0x49FF, instead of 0x4FFF for the 3-bit Rt field); the final
sweep agrees with the routed-span Capstone scan on every other
loader and adds exactly the two desync-missed ones, each locally
confirmed (`ldr r2,[pc,#0xD0]` / `ldr r3,[pc,#0x68]` in the same
`bic #0xFE000000` + `cmp` prefix-check idiom as the other eight).
Capstone is used only to confirm each pinned loader decodes,
anchored at its own address, as a PC-relative load of its slot.

## Word table

Pool `0x00427C80`: `0x200262F0` (OPEN_CFW_CMDQ_STATES queue
state-table base, reviewed `runtime_cmdq_services_427794.c`,
stale loader in the replaced initializer at `0x004277BE`, which
indexes the table: `ldr r0, [r5, r0]` follows);
`0x00430880` (OPEN_CFW_CMDQ_REGISTERS register-table base, same
source, stale loader in the replaced initializer at
`0x00427820`); `0x01CDCDCD`
(OPEN_CFW_CMDQ_INITIALIZED | OPEN_CFW_CMDQ_MAGIC, the
initialized-prefix word the reviewed initializer stores as
`(queue->prefix & 0xFC000000U) | OPEN_CFW_CMDQ_INITIALIZED |
OPEN_CFW_CMDQ_MAGIC`; stale loaders in the ten replaced
command-queue bodies at `0x00427884`/`0x004278D4`/`0x0042791E`/
`0x004279CA`/`0x004279FC`/`0x00427A66`/`0x00427AE6`/`0x00427B44`/
`0x00427BB6`/`0x00427C1E`); `0x20080000`
(OPEN_CFW_CMDQ_SSRAM_BASE shared-RAM base, same source, stale
loaders in the replaced enable/post/post-loop bodies at
`0x004278A0`/`0x00427A38`/`0x00427C64`). Every owning span's
shipped replacement carries only `R_ARM_THM_CALL` relocations
(init/enable/disable/release/post/error-resume/post-loop carry
zero relocations at all); stale by construction. No loader sits
in any byte-exact shipped body, any retained dead span (the
adjoining 14-byte post-loop tail and the whole 436-byte
control-dispatcher tail were decoded for interior loads: none),
or any relocated source, and no image word anywhere equals any
slot address (with or without the Thumb bit).

Word `0x0042644C`: `0x1FFF0000`, the XIP DEV0AXI aperture-base
mask spelled in the reviewed OpenCFW AmbiqSuite adaptation
`runtime_mspi_control_4251c0.c` (`(pXipConfig->ui32APBaseAddr &
(uint32_t)0x1FFF0000)`). Its single stock loader at
`0x004257BC` (`ldr.w r0, [pc, #0xC8C]` then `ands r3, r0;
orrs r1, r3`) performs exactly that mask-and-merge step inside
the replaced 3,824-byte control-upstream span, whose 25
relocations are all `R_ARM_THM_CALL`. Reproduced as a named
layout word, not as claimed live traffic.

## Not established

- Both admissions are grade "stale": reviewed spellings with
  loaders only in functionally replaced (not byte-exact)
  consumers. If a future byte-exact body loads any slot, its
  grade must be re-derived to live.
- The adjoining code tails (14-byte post-loop tail, 108+400-byte
  control-tail remnants, and all other category-A tails) remain
  retained; dead-tail fill is still the missing builder
  primitive described in
  `g2-bootloader-bl006-retained-seam-survey.md`.
- `movw`/`movt` materialization of these constants is not
  covered by the load scan (same boundary as prior cluster
  passes): a live body that constructs a constant in registers
  without reading the pool has no dependency on it, and no live
  (byte-exact) body reads any slot by any means checked here.
- The manifest region re-cut for these two placements (splitting
  `bootloader_mspi_blocking_transfer_unreachable_tail_and_alignment_4263e0_426450_official`
  and `bootloader_cmdq_tail_and_float_math_gap_427c72_427c90`)
  is deferred with all other BL-006 pool re-cuts: `make source`
  is blocked by the unrelated apollo_main littlefs-snapshot
  breakage, and the manifest-regions contract test is already
  red at baseline (61 stale records; this turn adds exactly 4
  builder-generated records, identified in the progress entry).
  The depending analyzers that pin the unsplit records
  (`analyze_g2_bootloader_post_mspi_frontier.py`,
  `analyze_g2_bootloader_mspi_cq_init_423f28.py`) still read the
  unchanged stock bytes and stay green.
- No hardware, flashing, signing, or transmission operation
  occurred; hardware qualification stays blocked by unavailable
  physical evidence.

## Status

1346 of the 5,892 BL-006 bytes are now produced from reviewed
source (1326 prior plus 20 here). Remaining: 26 dead-tail
regions plus the A prologue, the two partial MSPI code tails
(`0x00424AB2` 56 B, `0x00424B88` 76 B, both pure dead code with
no admittable literal word), and the 1,316-byte SPOT span --
all waiting on the dead-tail fill primitive or full
reconstruction. The embedded float-threshold words at
`0x0042805C`/`0x00428060`/`0x00428064` (`-273.0f`/`50.0f`/
`1000.0f`) are loaded by `vldr` from the replaced classifier
head (`0x00427E1A`/`0x00427E4E`/`0x00427E60`/`0x00427E6E`,
found by a VFP-literal encoding sweep since the operand-based
scan does not reliably report `vldr` targets) and from the dead
T0 tail. They carry no reviewed spelling -- the reviewed
classifier spells different thresholds (`0x41A00000U`,
`0x447A0000U`, `0x4FFEE92DU`) -- and stay retained.
