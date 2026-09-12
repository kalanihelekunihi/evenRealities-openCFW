# G2 bootloader BL-006 cluster 0x00420FF2..0x00421584 source closure

Three retained `official_blob` regions (334 bytes) -- the MX25/LittleFS
shared literal pool, the directory-bootstrap/format/init/callback pool,
and the mapped-memory control/security/window pool -- are now produced
from reviewed MIT C through the component's `in_place_data` mechanism.
All three payloads compile relocation-free under the reviewed
Apple-clang Cortex-M55 flags and reproduce the authenticated stock
bytes exactly, so `expected.sha256` equals `stock_sha256` for every
placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x00420FF2..0x004210C8` | 214 | `open_cfw_bootloader_bl006_pool_420ff2` |
| `0x00421372..0x004213D4` | 98 | `open_cfw_bootloader_bl006_pool_421372` |
| `0x0042156E..0x00421584` | 22 | `open_cfw_bootloader_bl006_pool_42156e` |

Source: `components/bootloader/core_overlay/runtime_bl006_littlefs_pools_420ff2.c`.
Each pool is one packed struct with a named field per literal word;
each field comment cites its loader PCs and its meaning from the
already-reviewed consumer sources. The verifier is
`g2/tests/test_runtime_bootloader_bl006_littlefs_pools.py`
(stock-SHA authentication, byte-exact rebuild, relocation-free
check, overlay registration check, per-slot loader resolution by
exact-entry decode, and per-slot reviewed-source naming).

## Method

For each region every 4-byte slot (after the 2-byte alignment fill)
was mapped to the `ldr`/`ldr.w` instructions that read it by decoding
every consuming stock span from its exact function entry with Capstone
(one span per function, so Thumb decode stays in sync across the
interleaved literal pools), computing Thumb literal targets as
`Align(PC,4)+imm`. Span coverage is complete by range arithmetic:
every code span in `[slot-4099, slot]` for every slot is decoded
(46 spans for the mapped-memory pool check; the merged stock-init
span `0x00421210..0x004212D8` decoded from its exact entry resolves
the identical loader set as the sub-span decode). The result is 163
loaders across 82 slots with no slot left without a loader.

As in the prior clusters, the MX25/LittleFS consumers live in
entry-redirect stock spans, so the relocated leaves carry their own
copies and those two pools are admitted as authenticated layout
reproductions with reviewed meanings, not as live traffic. The
mapped-memory pool at `0x0042156E` is different: its 8 loaders sit in
the in-place `source_compiled` selector and odd-selector wrapper
spans (`0x004213EC..0x00421548`), so it is live traffic read by
shipped code -- and every word is named in the reviewed selector
source (`OPEN_CFW_MEMORY_SELECT_CONTROL/SECURITY/BASE_ONE/TWO/THREE`).

## Word table

Pool `0x00420FF2` (53 words): read/write-transfer log formats
(`OPEN_CFW_READ_TRANSFER_LOG_FORMAT`, loader `0x42068E`;
`OPEN_CFW_WRITE_TRANSFER_LOG_FORMAT`, loader `0x42073E`);
busy-status fail format and log function; address-mode read-fail,
log-function, and three-byte words; the MSPI state-handle word
(`0x200270DC`, consumed as a bare literal by the enter-4byte
availability check plus erase/program/QE/reconfigure/quad-mode/
serial-mode/read hosts, 8 loaders); six enter-4byte words; the
write-enable log function and the shared log-file path
(`OPEN_CFW_QUAD_LOG_FILE`, 16 loaders) and log tag
(`OPEN_CFW_QUAD_LOG_TAG`, 14 loaders -- the same duplicates the MX25
cluster documented at `0x00420978`/`0x00420ADA`); the write-disable
function; seven sector-erase words; seven page-program words; eight
QE words including the "clear" text pointer
(`OPEN_CFW_QUAD_CLEAR_TEXT = 0x00434034`, loader `0x420DD6`,
complement of the "set" text admitted last turn); three reconfigure
words plus the state slot; four quad-mode words; four serial-mode
words; and the one-microsecond read timeout
(`OPEN_CFW_MSPI_READ_TIMEOUT = 1000000`, loader `0x420FDC`,
decimal-written like the prior timeout word).

Pool `0x00421372` (24 words): the directory paths table and
`0x20026878` LittleFS object (`OPEN_CFW_FS_DIRECTORIES_PATHS_ADDRESS/
LFS_ADDRESS`); the shared directory log function, log file
(`0x00430E60`, 10 loaders), log tag (`0x00433FBC`, 10 loaders), and
five per-outcome formats; the format config address
(`OPEN_CFW_LITTLEFS_FORMAT_CONFIG_ADDRESS`) plus mount-failed,
function, and failed words; seven init words read by the stock init
body (`0x00421210..0x004212D8`), including the ready flag and file
object (`OPEN_CFW_LITTLEFS_INIT_READY/FILE_ADDRESS`); and the
block-read/program/erase log formats consumed by the three callback
spans.

Pool `0x0042156E` (5 words): `0x400201BC` control, `0x40021008`
security, `0x42004000`/`0x42006000`/`0x42002000` window bases, all
named in the reviewed selector source (loaders `0x4213F2`,
`0x421408`, `0x4214B6/0x421502`, `0x4214E0/0x421518`,
`0x4214EC/0x42152A` -- the second loader of each window word sits in
the stock odd-wrapper tail the shorter C replacement leaves
unreachable).

## Status

BL-006 stands at 1,122 of 5,892 bytes from reviewed source (788
prior plus 334 here); 39 regions (4,770 bytes) remain retained stock:
the category-A dead tails (which need the trailing-dead-tail-fill
mechanism the survey scoped out), the MSPI/clock pools
(`0x0042499C`, `0x00424AB2`, `0x00424B88`), and the clock/cmdq/binary32
tail pools. No hardware operation occurred. Hardware qualification
stays blocked by unavailable physical evidence.
