# G2 bootloader BL-006 cluster 0x00424AEA..0x00424BE4 source closure

Five retained `official_blob` placements (34 bytes) -- the MSPI
state-literal island at `0x00424AEA`, the MSPI state-literal pool at
`0x00424BD4`, and three trailing boot-island reserved words at
`0x0041F9CC..0x0041F9D8` -- are now produced from reviewed MIT C
through the component's `in_place_data` mechanism. All five payloads
compile relocation-free under the reviewed Apple-clang Cortex-M55
flags and reproduce the authenticated stock bytes exactly, so
`expected.sha256` equals `stock_sha256` for every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x00424AEA..0x00424AF0` | 6 | `open_cfw_bootloader_bl006_island_424aea` |
| `0x00424BD4..0x00424BE4` | 16 | `open_cfw_bootloader_bl006_pool_424bd4` |
| `0x0041F9CC..0x0041F9D0` | 4 | `open_cfw_bootloader_bl006_word_41f9cc` |
| `0x0041F9D0..0x0041F9D4` | 4 | `open_cfw_bootloader_bl006_word_41f9d0` |
| `0x0041F9D4..0x0041F9D8` | 4 | `open_cfw_bootloader_bl006_word_41f9d4` |

Sources:
`components/bootloader/core_overlay/runtime_bl006_mspi_state_pools_424aea.c`
(new) and `runtime_bl006_reserved_words_420c14.c` (extended; the two
pre-existing entries' `source.size`/`source.sha256` pins were updated
to the extended file). Each pool is one packed struct with a named
field per slot (not a byte dump). The verifier is
`g2/tests/test_runtime_bootloader_bl006_mspi_state_pools.py`
(stock-SHA authentication, byte-exact rebuild, relocation-free
check, overlay registration check, pinned live/stale loader sets
with reviewed-spelling checks, reserved/pad unload checks, and a
stale-span zero-data-relocation check).

## Method

Same loader-mapping refinement as the 0x00423D9A cluster audit:
every slot was mapped to the `ldr`/`adr` instructions that read it by
decoding all routed spans (`in_place_leaves` plus entry-redirect
patch spans from the live `overlay.json`) with Capstone, computing
Thumb literal targets as `Align(PC,4)+imm`. Each found loader was
classified: inside a byte-exact shipped body (live), inside a named
functionally-replaced span whose overlay relocation contract carries
only `R_ARM_THM_CALL` relocations (stale, dead by construction --
the shipped bytes materialize constants internally), or anything
else (foreign, blocks admission). One correction made during the
pass: the stock configure-body load at `0x00424B1A` targets
`0x00424BD8`, not `0x00424BD4` (16-bit `ldr` literal offset
`#0xbc` from the aligned PC `0x00424B1C`); the pool's timeout slot
therefore has exactly one loader, the byte-exact pause body.

## Word table

Island `0x00424AEA`: `0x0000` alignment fill (the replaced MSPI
initialize tail ends at `0x00424AEA`, so the state-base word is
word-aligned; no loader); `0x2001CAA0` MSPI init state-table base,
loaded by the byte-exact command-queue initializer (`0x00423F36`)
and terminator (`0x00423F5C`, whose source names the load as
"Fixed literal load from 0x00423F5C to 0x00424AEC") as
`base + module * 0x8D0U + 0x828U` (reviewed
`runtime_mspi_cq_init_423f28.c`).

Pool `0x00424BD4`: `0x000186A0` (100000U pause poll timeout,
reviewed `runtime_mspi_cq_pause_423fb8.c` `remaining = 100000U`,
live loader in the byte-exact pause body at `0x00423FBE`);
`0x40060000` MSPI0_BASE (vendored CMSIS `apollo510.h`
`MSPI0_BASE 0x40060000UL`; reviewed `base = 0x40060000U +
instance->module * 0x1000U` in `runtime_mspi_cq_pause_423fb8.c`;
live loaders in the byte-exact pause/DMA-program/schedule bodies at
`0x00423FC4`/`0x00424070`/`0x004240DE`, plus one stale loader in
the replaced configure span at `0x00424B1A`); `0x80000013`
pad-configuration word spelled in the replaced
`runtime_mspi_device_configure_424120.c`, whose only stock-decode
loaders (`0x004241E0`/`0x00424228`) sit inside that replaced span
(zero data relocations pinned by the verifier) -- layout only;
`0x8000001F` pad-configuration word spelled in the same replaced
source with no loader in any routed span -- layout only.

Reserved words `0x0041F9CC/0x0041F9D0/0x0041F9D4`
(`0x0043419C`/`0x00434158`/`0x0043415C`): pointers into the
retained `0x004341xx` read-only tables (`0x0043419C` heads a small
"dfu" descriptor); no loader in any routed span and no reviewed
consumer names them, so they close the `0x0041F9B6` boot island as
layout-preserving reserved words, extending the `0x00420C14` /
`0x00422D7A` precedent. The boot-init pool file's header note that
these words "stay retained for the owning item" is now superseded
for these three slots.

## Not established

- The `0x00424BDC`/`0x00424BE0` pad words' live meaning is not
  claimed: their reviewed spellings come from a functionally
  replaced (not byte-exact) consumer, so the slots are admitted as
  layout-preserving constants. If a future byte-exact body loads
  either slot, its grade must be re-derived to live.
- The code tails adjoining both pools (replaced initialize/configure
  bodies) remain retained; dead-tail fill is still the missing
  primitive described in `g2-bootloader-bl006-retained-seam-survey.md`
  and is out of scope here.
- Non-PC-relative references are not covered by the consumer scan.
- No hardware, flashing, signing, or transmission operation
  occurred; hardware qualification stays blocked by unavailable
  physical evidence.

## Status

1242 of the 5,892 BL-006 bytes are now produced from reviewed
source (1208 prior plus 34 here). The remaining 29 official regions
(4,650 bytes) are dominated by unreachable stock tails needing the
dead-tail fill primitive, the 98-byte System-PLL lock-wait body at
`0x00427588`, and the 1,316-byte binary32/float helper span at
`0x00427E54..0x00428378`.
