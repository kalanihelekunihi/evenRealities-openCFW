# G2 bootloader BL-006 cluster 0x00426D2C..0x00427754 source closure

Five retained `official_blob` regions (36 bytes) -- the CLKGEN
register-address literal pool plus four zero-alignment halfwords --
are now produced from reviewed MIT C through the component's
`in_place_data` mechanism. All five payloads compile relocation-free
under the reviewed Apple-clang Cortex-M55 flags and reproduce the
authenticated stock bytes exactly, so `expected.sha256` equals
`stock_sha256` for every placement. The private component build
carries the bytes at their runtime addresses byte-identically.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x00426D2C..0x00426D48` | 28 | `open_cfw_bootloader_bl006_pool_426d2c` |
| `0x00426DB2..0x00426DB4` | 2 | `open_cfw_bootloader_bl006_pad_426db2` |
| `0x00426F6A..0x00426F6C` | 2 | `open_cfw_bootloader_bl006_pad_426f6a` |
| `0x004276BA..0x004276BC` | 2 | `open_cfw_bootloader_bl006_pad_4276ba` |
| `0x00427752..0x00427754` | 2 | `open_cfw_bootloader_bl006_pad_427752` |

Sources: `components/bootloader/core_overlay/runtime_bl006_clkgen_pool_426d2c.c`,
`runtime_bl006_zero_pads_426db2.c`. The pool is one packed struct
with a named field per word (not a byte dump); each field comment
cites its stock loader PCs and its meaning from the already-reviewed
consumer sources. The verifier is
`g2/tests/test_runtime_bootloader_bl006_clkgen_pads.py` (stock-SHA
authentication, byte-exact rebuild, relocation-free check, reviewed
value cross-check, byte-exact-loader exclusion with dead-span
containment, recompiled staleness proof, overlay registration check).

## Method

For each slot the `ldr`/`adr` instructions that read it were mapped
by decoding all routed code spans (`in_place_leaves` plus
entry-redirect stock spans from the live `overlay.json`) with
Capstone, computing Thumb literal targets as `Align(PC,4)+imm`.

## Word table

Pool `0x00426D2C`: `0x00000000` alignment fill (the CLKGEN disable
redirect span ends `0x00426D2C`); `0x40004044` HFADJ control register
(reviewed hfadj-enable source: bit-0 control register; reviewed
dual-switch source: clock-status register); `0x40004020` CLKGEN
control register (reviewed clkgen-config source
`OPEN_CFW_CLKGEN_CONFIG_CONTROL`; reviewed hfadj-config and
hfadj-disable sources); `0x40004030` dual-clock switch status
register (reviewed dual-switch source); `0x4000404C` CLKGEN mode
register (reviewed clkgen-config source
`OPEN_CFW_CLKGEN_CONFIG_MODE`); `0x40004048` CLKGEN divider register
(reviewed clkgen-config source `OPEN_CFW_CLKGEN_CONFIG_DIVIDER`);
`0x40004050` register written by the reviewed CLKGEN disable service.

Stock loader PCs: `0x00426D30` from `0x00426C64` (replaced HFADJ
enable span), `0x00426C94`/`0x00426CBE` (replaced dual-switch span);
`0x00426D38` from `0x00426CB4` (replaced dual-switch span);
`0x00426D34` from `0x00426C76`/`0x00426C7E`, `0x00426D3C` from
`0x00426CD6`, `0x00426D40` from `0x00426CE6`/`0x00426D1E`,
`0x00426D44` from `0x00426CF6` (all inside overwritten redirect
spans).

Pads: `0x00426DB2` pads the replaced floating common-divisor span
before the ratio redirect entry; `0x00426F6A` pads the replaced
floating-multiplier span before the encoding-selector redirect entry;
`0x004276BA` pads the source-owned queue item-get body end before the
memmove redirect; `0x00427752` pads the memmove NOP-fill tail before
the command-queue index-updater redirect. None has a loader in any
routed span.

## Liveness grades

Two grades, pinned per slot by the verifier:

- "pad": zero loaders in any routed span (all four halfwords, plus
  the pool alignment word).
- "dead": no loader in any byte-exact shipped body (all six CLKGEN
  words). Byte-exactness is decided independently per body by
  comparing `expected.sha256` against the stock-image hash (259 of
  291 in-place bodies are byte-exact; neither stale loader is).
  Redirect-span references are dead by construction (containment:
  every `patch_stock` hit lies inside an overwritten span). The two
  `in_place` hits (HFADJ enable, dual-switch) are stale: both bodies
  are functionally replaced, and recompiling each pinned leaf source
  and decoding its `.text` at its runtime address shows no
  PC-relative target on any dead slot (the shipped HFADJ leaf embeds
  `0x40004044` as a body literal; the shipped dual-switch leaf has
  only a `CALL` relocation). Any new byte-exact loader, any new
  loader outside the two proven-stale functions, or any PC-target hit
  from a recompiled stale body fails the test and forces
  re-derivation.

The pool is therefore an authenticated layout reproduction with
reviewed meanings, not address-live traffic; the pads are explicit
zero fills, not claimed data.

## Not established

- Relocated/cave leaves execute at least 30 KB away (`ldr` literal
  range is +/-4 KB), so only `in_place_leaves` spans are scanned for
  live loaders; the verifier does not decode relocated bodies.
- Non-PC-relative references (e.g. computed addressing) are not
  covered by the loader scan.
- Semantics of the register targets beyond the cited consumer
  sources (e.g. hardware behavior at `0x40004044`) are established
  only by the consumer closures, not here.
- Neighboring mixed code/data spans (`0x00424AB2`, `0x00424B88`,
  `0x00425160`, `0x004250E6`, `0x00427308`, `0x00427C72`) and the
  unreachable tails need the still-missing dead-tail fill primitive;
  the `0x00422D7A` datum (`0x20000002`, zero loaders in any routed
  span) has no reviewed meaning; the `0x00420C14` head word
  (`0x000081F6`) likewise stays retained. The 1316-byte
  `0x00427E54` binary32 table and the 98-byte `0x00427588` mixed span
  need per-region reconstruction.
- No hardware, flashing, signing, or transmission operation
  occurred; register behavior and shared-state ownership still
  require authorized hardware evidence, which is unavailable.

## Status

1,158 of the 5,892 BL-006 bytes are now produced from reviewed source
(1,122 prior plus 36 here). The remaining 34 regions (4,734 bytes)
need per-region reconstruction as listed above.

## Addendum 2026-09-11 (BL-006): float/System-PLL pools admitted

Three more retained literal regions (42 bytes) are now produced from
reviewed MIT C (`runtime_bl006_float_syspll_pools_427032.c`) through
`in_place_data`: the 14-byte float-ratio bound pool (`0x00427032`:
alignment pad plus `0x34000000`/`0x34000001`/`0x44700001`), the
20-byte multiplier/select bound pool (`0x0042714C`: `0x427C0001`,
reserved zero, `0x4B800000`, `0x42C00001`, `0x42700000`), and the
8-byte select/PLL pool (`0x00427308`: `240.0f`, `1000000.0f`).

Every value is spelled in hex-float or decimal form by the reviewed
replacement consumer that the stock loader belongs to
(`runtime_float_gcd_426d48.c`, `runtime_float_ratio_426db4.c`,
`runtime_float_multiplier_426eac.c`,
`runtime_float_encoding_select_426f6c.c`,
`runtime_syspll_min_fvco_427040.c`); the verifier checks each spelling
against the stock word independently (`float.fromhex` for `0x`-led
spellings, decimal `float()` otherwise) and checks the spelling text
appears in the named consumer source. All 19 routed loaders of the
ten words live in entry-redirect stock spans (float gcd/ratio/
multiplier/encoding-select at `0x00426D48`/`0x00426DB4`/`0x00426EAC`/
`0x00426F6C`, min-VCO at `0x00427040`), verified by bounded Capstone
decode; no byte-exact shipped body loads any slot, so the pools are
admitted as authenticated layout reproductions with reviewed meanings,
not address-live traffic. The `0x00427032` pad halfword and the
`0x00427150` zero word have no reviewed spelling and are named
reserved slots preserving layout only. Verified by
`g2/tests/test_runtime_bootloader_bl006_float_pools.py` (6 tests pass;
component build records all 5 placements, provider bytes match stock).

This addendum closes `0x00427308` (removed from the mixed-span list
above); the `0x00422D7A` datum and `0x00420C14` head word are closed
by the companion reserved-words file (see the 42086c and 4220b2
cluster docs). BL-006 now stands at 1,208 of 5,892 bytes from
reviewed source (1,158 prior plus 50 here: 42 in this cluster, 8
reserved words). No hardware operation occurred.
