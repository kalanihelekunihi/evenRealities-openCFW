# G2 bootloader BL-006 cluster 0x004233E0..0x004251C0 source closure

Eight retained `official_blob` regions (154 bytes) across the
hardware-service register pools, the control-service SRAM cells, and
the MSPI state pool are now produced from reviewed MIT C through the
component's `in_place_data` mechanism. All eight payloads compile
relocation-free under the reviewed Apple-clang Cortex-M55 flags and
reproduce the authenticated stock bytes exactly, so `expected.sha256`
equals `stock_sha256` for every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x004233E0..0x004233E8` | 8 | `open_cfw_bootloader_bl006_pool_4233e0` |
| `0x00423430..0x00423444` | 20 | `open_cfw_bootloader_bl006_pool_423430` |
| `0x004236FA..0x00423700` | 6 | `open_cfw_bootloader_bl006_pool_4236fa` |
| `0x00423764..0x0042377C` | 24 | `open_cfw_bootloader_bl006_pool_423764` |
| `0x0042382C..0x00423864` | 56 | `open_cfw_bootloader_bl006_pool_42382c` |
| `0x00423E0C..0x00423E14` | 8 | `open_cfw_bootloader_bl006_pool_423e0c` |
| `0x0042499C..0x004249A0` | 4 | `open_cfw_bootloader_bl006_word_42499c` |
| `0x004251A4..0x004251C0` | 28 | `open_cfw_bootloader_bl006_pool_4251a4` |

Sources: `components/bootloader/core_overlay/runtime_bl006_hw_service_pools_4233e0.c`,
`runtime_bl006_hw_register_pools_4236fa.c`,
`runtime_bl006_mspi_pools_423e0c.c`. Each pool is one packed struct
with a named field per literal word (not a byte dump); each field
comment cites its loader PCs and its meaning from the
already-reviewed consumer host models. The verifier is
`g2/tests/test_runtime_bootloader_bl006_hw_pools.py` (stock-SHA
authentication, byte-exact rebuild, relocation-free check,
live-consumer coverage, overlay registration check).

## Method

The neighbors are exact in-place leaves, so they keep stock
PC-relative literal addressing and these pools stay live in the
shipped image. For each region every 4-byte slot was mapped to the
`ldr`/`adr` instructions that read it by decoding the exact spans of
all routed code spans (`in_place_leaves` plus entry-redirect stock
spans from the live `overlay.json`) with Capstone, computing Thumb
literal targets as `Align(PC,4)+imm`. Zero references were found in
any entry-redirect stock span: every observed reference is live.
Word meanings come from the already-reviewed consumer sources and
their closure audits (host-model variable names are quoted below).

The one slot with no routed consumer (`0x004251B8`, `0xFC001F03`)
is reproduced as a named reserved constant preserving layout, not
as claimed data. The 2-byte fill at `0x004236FA` likewise has no
routed consumer and is reproduced as a named pad constant.

## Word table

Pool `0x004233E0`: `0x01EA9E06` instance-header match word, low 25
bits (hardware initializer `0x0042309E`, four-instance initializer
`0x00422AF4`, instance service `0x00422BB8`; host
`(header & ~0xFE000000U) == magic`); `0x20024400`
instance-descriptor table base, 0x11C-byte entries (instance init;
host `open_cfw_hw_host_instances[index]`).

Pool `0x00423430`: `0x00EA9E06` fresh-header low word ORed into the
preserved top byte on claim (instance init `0x00422B24`; host
`(header & 0xFF000000U) | 0x00EA9E06U`); `0x0016E361` (1500001)
requested-frequency threshold for the high-speed init path
(initializer `0x004230F4`, instance service `0x00422BF8`/
`0x00422CC8`; host `requested >= 0x0016E361U`); `0x4002000C`
chip-revision register, low byte against 0x21/0x22 (initializer,
instance service; host `open_cfw_hwinit_host_chip_revision`);
`0x400201B0` global-control register, bit `0x00400000 << index`
(initializer, instance service; host
`open_cfw_hwinit_host_global_control`); `0x40039000` peripheral
register-bank base, 0x1000 stride (clock divider, initializer,
instance service, register clear, status mapper; host
`open_cfw_hw*_host_registers[index]`).

Pool `0x004236FA`: `0x0000` alignment fill; `3000000` mode-4 clock
reference Hz (clock divider `0x00422EB0`; host `references[4]`).
The stock compiler spilled this one reference here because the
remaining six references already filled the later pool; the five
reference loads there use identical `#0x9a0`/`#0x99c` encodings
from different PCs (modes 5/1 share `#0x9a0`, modes 2/3 share
`#0x99c`), confirmed per-loader in the table above.

Pool `0x00423764`: `0x40039000` bank base (FIFO pump/read/write,
register clear/OR/query/write, shutdown); `0x08000006` through
`0x0800000A` bit-6/7/8/9/10 fault codes (status mapper
`0x00422D8E`..`0x00422DB6`; host per-bit returns).

Pool `0x0042382C`: `0x0800000B` bit-12 fault code (status mapper
`0x00422DC0`); `0x01EA9E06` descriptor-header magic, low 25 bits
(descriptor init, mode dispatch, register OR/query/write, service
dispatch; host `(x & 0x01FFFFFFU) != magic` guard); `49152000`
mode-6 reference (clock divider `0x00422E58`; host
`references[6]`); `0x08000003` divider zero/overflow status
(`0x00422E92`; host `divisor == 0` / `integer == 0`);
`48000000`/`24000000`/`12000000`/`6000000` mode-5/1/2/3
references (`0x00422E98`/`0x00422E9E`/`0x00422EA4`/`0x00422EAA`;
host `references[5]/[1]/[2]/[3]`); `0x08000002` idle-mode status
(`0x00422EBC`; host `mode == 0 || mode == 7`); `0x08000004` /
`0x08000005` latch / secondary-latch statuses (config latch
`0x00422F3E`, secondary `0x00422F94`); `10000000` shutdown delay
reference Hz (shutdown `0x0042303A`; host
`host_delay(10000000U / divisor + 1)`); `0x08000001` snapshot
status (FIFO snapshot `0x00423380`); `0x40039000` dispatch bank
base (service dispatch `0x004237AE`).

Pool `0x00423E0C`: `0x200271C2` retry-countdown cell (control
critical `0x00423DF2`; host `open_cfw_hwcs_host_countdown`,
decremented under primask); `0x200271C3` completion-latch cell
(`0x00423DD8`; host `open_cfw_hwcs_host_latch`, cleared on
expiry).

Word `0x0042499C`: `0x40060000` MSPI0 register base, 0x1000
module stride (device configure `0x004241AA`/`0x004241F2`, FIFO
read `0x00423EC2`/`0x00423EE6`, FIFO write `0x00423E5A`;
AmbiqSuite-equivalent sources spell
`0x40060000U + module * 0x1000U`).

Pool `0x004251A4`: `0x40060000` MSPI register base again
(device-configure-public, disable, enable, PIO-mixed configure,
sequence loopback); `0x40004110` clock-gate register
read-modified-written by the clock-generator control service
(`0x004249BC`/`0x004249DE`/`0x004249FA`); `0x2001CAA0` init
state-table base (configure `0x00424B42`, initialize `0x00424A70`;
host `0x2001CAA0U + module * STATE_BYTES`); `0x01BEBEBE`
initialized-handle prefix sentinel, low 25 bits (configure,
deinitialize, device-configure-public, disable, enable; host
`(prefix & 0x01FFFFFFU) == 0x01BEBEBEU`); `0x20080000`
transfer-block SSRAM limit (configure `0x00424B68`; host
`end < 0x20080000U ? 1U : 0U`); `0xFC001F03` reserved word, no
routed consumer (layout-preserving fill, see below);
`0x00400080` command-queue set/clear word (enable `0x004250A0`;
host `store32(registers + 0x2B4U, 0x00400080U)` and
`trace->cq_setclear`).

## Not established

- The `0xFC001F03` reserved word at `0x004251B8` has no
  PC-relative loader in any routed span (live or stock). It is
  reproduced to preserve layout, not as understood data; if a
  future consumer is found the field must be re-derived, not
  silently kept. Non-PC-relative references (e.g. computed
  addressing) are not covered by the consumer scan.
- The `0x0000` fill at `0x004236FA` is layout-preserving
  alignment, not understood data.
- Semantics of the pointer targets beyond the cited host-model
  cells (e.g. the descriptor-table contents at `0x20024400`)
  are established only by the consumer closures, not here.
- Several apparent pools elsewhere in the BL-006 range
  (`0x00420FF2`, `0x00420ADA`, `0x00421372`, `0x0042156E`)
  disassemble as coherent Thumb code with zero leftover bytes
  and no live data consumers; they are unreachable stock bodies
  in the sense of the seam survey, not literal pools, and need
  the still-missing dead-tail fill primitive (see the survey).
- No hardware, flashing, signing, or transmission operation
  occurred; interrupt timing, register behavior, and
  shared-state ownership still require authorized hardware
  evidence, which is unavailable.

## Status

346 of the 5,892 BL-006 bytes are now produced from reviewed
source (192 from the prior `4220b2-422ad4` cluster plus 154
here). The remaining 60 regions (5,546 bytes) need per-region
reconstruction: dead stock tails after short in-place leaves
(no fill primitive exists yet), pools whose consumers live in
not-yet-routed stock spans (early boot, MX25, LittleFS
frontiers), and scattered small pools. The survey in
`g2-bootloader-bl006-retained-seam-survey.md` still describes
those.
