# G2 bootloader BL-006 cluster 0x00423D9A..0x00426C10 source closure

Four retained `official_blob` regions (36 bytes) -- the
hardware-control register literal plus alignment, and the MSPI
interrupt-service and power-control literal pools -- are now produced
from reviewed MIT C through the component's `in_place_data`
mechanism. All four payloads compile relocation-free under the
reviewed Apple-clang Cortex-M55 flags and reproduce the authenticated
stock bytes exactly, so `expected.sha256` equals `stock_sha256` for
every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x00423D9A..0x00423DA0` | 6 | `open_cfw_bootloader_bl006_pool_423d9a` |
| `0x00423DCE..0x00423DD0` | 2 | `open_cfw_bootloader_bl006_align_423dce` |
| `0x004267FE..0x00426808` | 10 | `open_cfw_bootloader_bl006_pool_4267fe` |
| `0x00426BFE..0x00426C10` | 18 | `open_cfw_bootloader_bl006_pool_426bfe` |

Sources: `components/bootloader/core_overlay/runtime_bl006_hw_control_pool_423d9a.c`,
`runtime_bl006_mspi_isr_pools_4267fe.c`. Each pool is one packed
struct with a named field per literal word (not a byte dump); each
field comment cites its loader PCs and its meaning from the
already-reviewed consumer sources. The verifier is
`g2/tests/test_runtime_bootloader_bl006_ctrl_pools.py` (stock-SHA
authentication, byte-exact rebuild, relocation-free check,
live-consumer coverage with exact/valuelive grades, overlay
registration check, dead-span containment for stale stock hits).

## Method

For each region every 4-byte slot was mapped to the `ldr`/`adr`
instructions that read it by decoding all routed code spans
(`in_place_leaves` plus entry-redirect stock spans from the live
`overlay.json`) with Capstone, computing Thumb literal targets as
`Align(PC,4)+imm`. A decisive refinement over decoding alone: the
overlay's relocation contracts were inspected. Every functional
(non-exact) consumer leaf carries only `R_ARM_THM_CALL` relocations
(zero data relocations), so its shipped bytes materialize constants
internally and cannot load a stock pool slot; stock-decode loaders
found inside functionally replaced spans are therefore stale, not
live. Only loaders inside byte-exact shipped bodies count as live
evidence. Word meanings come from the already-reviewed consumer
sources and their closure audits.

## Word table

Pool `0x00423D9A`: `0x0000` alignment fill (the register-query body
ends at `0x00423D9A`); `0xE0000E80` hardware-control register
address, loaded by the exact register query (`0x00423D82`) and the
exact global service (`0x00423D28`/`0x00423D3E`) as the register
argument of `open_cfw_hwcs_host_register_call(1000U, 0xE0000E80U,
...)` (query passes mask `0x00800000U`, global service passes `0U`).

Alignment `0x00423DCE`: `0x0000` pads the zero-index test wrapper
(ends `0x00423DCE`) so the interrupt-atomic control-service entry at
`0x00423DD0` is word-aligned.

Pool `0x004267FE`: `0x0000` alignment fill; `0x00424979` Thumb
pointer to the exact source-owned `mspi_seq_loopback` callback body
at `[0x00424978,0x0042499C)` (valuelive grade: the shipped control
body stores this value into `pfnCallback[]` on the loop path, but no
byte-exact shipped body loads this slot); `0x40060000` MSPI register
base, loaded by the exact interrupt-service body
(`0x0042656E`/`0x00426762`/`0x004267CC`) as `base + module << 12`.

Pool `0x00426BFE`: `0x0000` alignment fill; `0x00424977` Thumb
pointer to the exact source-owned `mspi_dummy_callback` (`bx lr`)
body at `[0x00424976,0x00424978)` (valuelive grade, same rationale);
`0x01BEBEBE` initialized-handle prefix sentinel, low 25 bits,
compared by the exact interrupt-service body (`0x00426548`) and the
exact power-control body (`0x0042681A`) as
`(handle & ~0xFE000000U)`; `0x2001CAA0` MSPI init state-table base,
used by the exact interrupt-service body (`0x0042667E`) as
`base + module * 0x8D0U + 0x828U`; `0x40060000` MSPI register base,
loaded by the exact power-control body
(`0x0042688A`/`0x00426A40`/`0x00426BBC`) as `base + module << 12`.

Two stock-decode loaders of `0x00426804` sit inside the
`replace_ambiq_mspi_interrupt_clear` entry-redirect span
(`0x00426520`/`0x00426512`); that span is overwritten by a redirect
plus NOP fill in the shipped image, so both hits are dead by
construction. The verifier pins this containment generically: every
`patch_stock` hit must lie inside a `patch_site` span.

## Not established

- The two callback-pointer slots (`0x00426800`, `0x00426C00`) have
  no loader in any byte-exact shipped body. Their values are live
  (stored by shipped code, targets exact), but the slots themselves
  are layout-preserving, not proven-live data. If a future exact
  body loads either slot, the field comment and the verifier's
  `valuelive` contract must be re-derived, not silently kept.
- Non-PC-relative references (e.g. computed addressing) are not
  covered by the consumer scan.
- Relocated/cave leaves cannot reach these pools by PC-relative
  literal load (they execute at least 30 KB away; `ldr` literal
  range is +/-4 KB), so only `in_place_leaves` spans are scanned
  for live loaders.
- Semantics of the pointer targets beyond the cited consumer
  sources (e.g. register behavior at `0xE0000E80`) are established
  only by the consumer closures, not here.
- The neighboring `0x00422D7A` datum (one word, no routed loader
  found anywhere in the image) and the mixed code/literal spans at
  `0x00424AB2`, `0x00424B88`, `0x00425160` (dead tails needing the
  still-missing dead-tail fill primitive) were examined and left
  retained; see the survey.
- No hardware, flashing, signing, or transmission operation
  occurred; interrupt timing, register behavior, and shared-state
  ownership still require authorized hardware evidence, which is
  unavailable.

## Status

580 of the 5,892 BL-006 bytes are now produced from reviewed source
(544 prior plus 36 here). The remaining 50 regions (5,312 bytes)
need per-region reconstruction: dead stock tails after short
in-place leaves (no fill primitive exists yet), pools whose
consumers live in not-yet-routed stock spans (early boot, MX25,
LittleFS frontiers), and scattered small pools. The survey in
`g2-bootloader-bl006-retained-seam-survey.md` still describes those.
