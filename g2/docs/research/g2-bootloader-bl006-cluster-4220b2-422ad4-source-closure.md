# G2 bootloader BL-006 cluster 0x0042220E..0x00422AD4 source closure

Nine retained `official_blob` regions (192 bytes) between the exact
source-owned bitmap/mode bodies and the double/atomic leaves are now
produced from reviewed MIT C through the component's `in_place_data`
mechanism. All nine payloads compile relocation-free under the reviewed
Apple-clang Cortex-M55 flags and reproduce the authenticated stock bytes
exactly, so `expected.sha256` equals `stock_sha256` for every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x0042220E..0x00422220` | 18 | `open_cfw_bootloader_bl006_seam_42220e` |
| `0x0042228E..0x004222A0` | 18 | `open_cfw_bootloader_bl006_seam_42228e` |
| `0x004222D2..0x004222F0` | 30 | `open_cfw_bootloader_bl006_seam_4222d2` |
| `0x00422430..0x00422468` | 56 | `open_cfw_bootloader_bl006_pool_422430` |
| `0x00422574..0x00422590` | 28 | `open_cfw_bootloader_bl006_pool_422574` |
| `0x004225AC..0x004225D0` | 36 | `open_cfw_bootloader_bl006_island_4225ac` |
| `0x00422712..0x00422714` | 2 | `open_cfw_bootloader_bl006_align_422712` |
| `0x00422872..0x00422874` | 2 | `open_cfw_bootloader_bl006_align_422872` |
| `0x00422AD2..0x00422AD4` | 2 | `open_cfw_bootloader_bl006_align_422ad2` |

Sources: `components/bootloader/core_overlay/runtime_bl006_mode_seams_42220e.c`,
`runtime_bl006_debug_pool_422430.c`, `runtime_bl006_align_fill_422712.c`.
Each pool is one packed struct with a named field per literal word (not a
byte dump); each field comment cites its consumers and its meaning. The
verifier is `g2/tests/test_runtime_bootloader_bl006_cluster.py` (stock-SHA
authentication, byte-exact rebuild, relocation-free check, live-consumer
coverage, overlay registration check).

## Method

The neighbors are exact in-place leaves, so they keep stock PC-relative
literal addressing and these pools stay live in the shipped image. For
each region every 4-byte slot was mapped to the `ldr`/`adr` instructions
that read it by decoding the exact spans of all 514 routed code spans
(`in_place_leaves` plus entry-redirect stock spans from the live
`overlay.json`) with Capstone, computing Thumb literal targets as
`Align(PC,4)+imm`. Word meanings come from the already-reviewed consumer
sources and their closure audits (host-model variable names are quoted
below). No consumer was found in any entry-redirect stock span: every
observed reference is live.

Fill slots (two-byte pads, one reserved zero word) have no routed
consumer. For each, the +/-4KB literal window was checked against the
flash plan: it holds no retained code, only routed bodies (all decoded)
and data pools, so no shipped instruction can address the slot. They are
reproduced as named pad constants preserving layout, not as claimed data.

## Word table

Seam A `0x0042220E` (2-byte zero fill, then):
`0x20026E74` bitmap table root (`bitmap-helpers` closure; `bitmap_any`,
`bitmap_test`, `bitmap_count`, `bitmap_update`); `0x00433F08` mode
fallback template table pointer (prologue `ldm`/`stm`; target holds
`{0x0025B800,0,0}`, cf. `mode-service` closure and host `local[3]`;
target bytes stay BL-012 retained); `48000000` fixed mode instance
`OPEN_CFW_MODE_SPECIAL` (`runtime_mode_service_4216d4.c:35`);
`0x2000007C` controller seam cell (`mode-service` closure, host
`controller`; also read by dual, bitmap-client, row-one, mode enables,
and the mode copy helper).

Seam B `0x0042228E` (2-byte zero fill, then): `0x20027030` mode
current-instance word (host `current`; `mode_service`, `row4_enable`);
`0x20026FEC` mode fallback array base (host `fallback[3]`; `[base]` is
applied by `mode_service` and `row4_enable`); `0x2002719C` mode-zero
polled byte (`mode0-disable` closure; host aux flag; `mode_service`,
`mode0_poll_cleanup`, `row4_enable`); `0x20027044` mode-zero state
pointer (`mode0-disable` closure; host aux word; same consumers).

Seam C `0x004222D2` (2-byte zero fill, then): `0x20000550`
instance-comparison cell (word view on the mode busy path, byte view in
`row4_enable`; no host-variable mapping established, see below);
`250000000` / `196608000` accepted dual instances (`dual-mode`
closure); `0x20027034` dual current-instance publication (dual, row5
leaves); `0x00433F14` dual query-template pointer (target holds
`{0x00020000,0x000C49BA,0}`; target bytes stay BL-012 retained);
`0x20026FF8` dual 12-byte configuration publication base (dual, row5
leaves); `0x20000551` dual readiness byte (dual, `row5_enable`).

Pool D `0x00422430`: `0x20027004` 12-byte configuration publication
(`bitmap-clients` closure; row6 leaves read its first byte for selector
ordering); `0x20027038` current instance (same closure);
`0x2002719A` readiness byte (same closure; row6 ready gate, host
`ready`); `0x0043414C` mode-one enable control word base (low nibble
overwritten with `0xA` at runtime, request 15; host `enable_word`);
`0x00434150` mode-one disable control word (host `disable_word`);
`0x2002719B` mode active byte and `0x20027040` mode state word/pointer
(`mode1` closure; shared by mode-zero leaves); `0x2002719E`
mode-zero completion byte (`mode0-disable` closure; set by
`row4_enable`); `0x2002719D` row-four active byte and `0x20027048`
row-four state pointer (`row4-disable` closure; row5 leaves);
`0x2002719F` row-five active byte (`row5` closure active/state cells;
set/cleared by the row-five leaves); `0x200271A0` row-six pending byte
(host `pending`); `0x2002703C` row-six service handle word (host
`handle`); `0x2000007C` controller seam cell again (mode copy helper).

Pool E `0x00422574`: zero reserved word (no routed consumer; see
method); `0x200271A1` debug user count, `0x40020250` debug control
register (low four enable/clock bits cleared for the last user),
`0x200271A2` power count, `0x200271A4` power entry state,
`0x200271A3` trace count (host `enable_count`, `dbgctrl`,
`power_count`, `power_entry_state`, `trace_count`; debug-disable,
debug-power consumers); `0xE000EDFC` architectural DCB DEMCR, TRCENA
cleared and polled (host `demcr`; trace-disable consumer).

Island F `0x004225AC`: `0x20027190` registered C11 handler pointer
cell (null selects the retained default handler at `0x00417C28`,
else `(message, NULL, 0x22)`); `constraint handler: bad message\0`,
the IAR CLIB default violation message (host `bad_message`;
`constraint-memchr` closure records this pool's SHA-256 as
`6a1c3b3c...a5b25`, matched exactly by the compiled payload).

Aligns: `0xBF00` NOP pads the ldexp wrapper (ends `0x00422712`) to the
word-aligned core entry `0x00422714`; `0x0000` pads the multiply leaf
(ends `0x00422872`) to the thread-pointer entry `0x00422874`;
`0x0000` pads the query wrapper (ends `0x00422AD2`) to the instance
initializer entry `0x00422AD4`.

## Not established

- The `0x20000550` cell's host-variable mapping (both access shapes are
  cited; behavior beyond the two consumer sites is not claimed).
- Semantics of the pointer targets `0x00433F08`/`0x00433F14` beyond
  their observed template contents; both stay BL-012 retained.
- The reserved zero word at `0x00422574` is layout-preserving fill, not
  understood data; if a future consumer is found the field must be
  re-derived, not silently kept.
- No hardware, flashing, signing, or transmission operation occurred;
  interrupt timing, register behavior, and shared-state ownership still
  require authorized hardware evidence, which is unavailable.

## Status

192 of the 5,892 BL-006 bytes are now produced from reviewed source.
The remaining 68 regions (5,700 bytes) need per-region reconstruction:
dead stock tails after short in-place leaves (no fill primitive exists
yet) and the other literal pools. The survey in
`g2-bootloader-bl006-retained-seam-survey.md` still describes those.

## Addendum 2026-09-11 (BL-006): 0x00422D7A datum admitted

The retained datum between the secondary register-clear leaf and the
per-instance status mapper (`0x00422D7A`, `0x20000002`) is now
produced from reviewed MIT C
(`runtime_bl006_reserved_words_420c14.c`) through `in_place_data`.
Bounded Capstone decode of every routed span finds no loader
targeting it and no reviewed consumer source names the value, so it
is a named reserved word preserving layout, not claimed data; if a
future consumer is found the field must be re-derived. Verified by
`g2/tests/test_runtime_bootloader_bl006_float_pools.py`. No hardware
operation occurred.
