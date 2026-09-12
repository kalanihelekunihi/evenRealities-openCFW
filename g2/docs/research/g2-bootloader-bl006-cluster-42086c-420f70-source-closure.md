# G2 bootloader BL-006 cluster 0x0042086C..0x00420F70 source closure

Nine retained `official_blob` regions (208 bytes) -- the MX25
event-state, log-file, event-release, NVIC/timing, log-tag/timing,
low-init/driver, log-format, timeout, and QE-text pools -- are now
produced from reviewed MIT C through the component's `in_place_data`
mechanism. All nine payloads compile relocation-free under the
reviewed Apple-clang Cortex-M55 flags and reproduce the authenticated
stock bytes exactly, so `expected.sha256` equals `stock_sha256` for
every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x0042086C..0x00420890` | 36 | `open_cfw_bootloader_bl006_pool_42086c` |
| `0x00420978..0x00420984` | 12 | `open_cfw_bootloader_bl006_pool_420978` |
| `0x004209BE..0x004209C4` | 6 | `open_cfw_bootloader_bl006_island_4209be` |
| `0x004209FC..0x00420A08` | 12 | `open_cfw_bootloader_bl006_pool_4209fc` |
| `0x00420ADA..0x00420B0C` | 50 | `open_cfw_bootloader_bl006_pool_420ada` |
| `0x00420C18..0x00420C5C` | 68 | `open_cfw_bootloader_bl006_pool_420c18` |
| `0x00420DFA..0x00420E08` | 14 | `open_cfw_bootloader_bl006_pool_420dfa` |
| `0x00420F0C..0x00420F10` | 4 | `open_cfw_bootloader_bl006_word_420f0c` |
| `0x00420F6A..0x00420F70` | 6 | `open_cfw_bootloader_bl006_text_420f6a` |

Source: `components/bootloader/core_overlay/runtime_bl006_mx25_pools_42086c.c`.
Each pool is one packed struct (plus two scalar islands) with a named
field per literal word; each field comment cites its loader PCs and
its meaning from the already-reviewed consumer sources. The verifier
is `g2/tests/test_runtime_bootloader_bl006_mx25_pools.py`
(stock-SHA authentication, byte-exact rebuild, relocation-free
check, overlay registration check, per-slot loader resolution by
exact-entry decode, per-slot reviewed-source naming, and the
ADR-selected text case).

## Method

For each region every 4-byte slot was mapped to the `ldr`/`ldr.w`
instructions that read it by decoding every consuming stock span from
its exact function entry with Capstone (one span per function, so
Thumb decode stays in sync across the interleaved literal pools),
computing Thumb literal targets as `Align(PC,4)+imm`. The QE "set"
text at `0x00420F6C` is selected by `adr r0` at stock loader
`0x00420DD2` (falling through to the clear text), verified the same
way. As in the prior boot-init cluster, every consumer lives in an
entry-redirect span the shipped image overwrites, so the relocated
leaves carry their own copies and these pools are admitted as
authenticated layout reproductions with reviewed meanings, not as
live traffic.

## Word table

Pool `0x0042086C`: `0x00000000` alignment fill; `0xE000E400` NVIC
IPR base (irq_services `OPEN_CFW_NVIC_IPR`, loader `0x41FDE8`);
`0x200270DC` MSPI handle (control `OPEN_CFW_MSPI_HANDLE_WORD`,
loaders `0x41FE38/0x41FE4E/0x41FF54/0x420030/0x420292/0x42060A/0x4206AA`);
`0x200271C6` active flag (control `OPEN_CFW_MSPI_ACTIVE`, loaders
`0x41FE2A/0x41FE5A`); `0x200270E0` event handle, `0x00433CF8` event
config, `0x004329FC` init format, `0x0043376C` init function,
`0x00432CA0` acquire format (event-flags host names, loaders
`0x41FE64/0x41FE9E/0x41FED6`, `0x41FE6E`, `0x41FE7E`, `0x41FE88`,
`0x41FEB6`).

Pool `0x00420978`: `0x00431540` log-file path (4byte-mode
`OPEN_CFW_4BYTE_MODE_LOG_FILE`, 26 loaders from the event, timing,
init, driver, transfer, busy, and 4byte-mode bodies);
`0x00433784` acquire function and `0x00432A24` release format
(event-flags host names, loaders `0x41FEC0`/`0x41FEEA`).

Island `0x004209BE`: `0x0000` fill; `0x0043379C` release function
(event-flags `OPEN_CFW_EVENT_RELEASE_FUNCTION`, loader `0x41FEF4`).

Pool `0x004209FC`: `0xE000E100` NVIC ISER (irq_services
`OPEN_CFW_NVIC_ISER`, loader `0x41FDD0`); `0xE000ED18` SCB SHPR
(`OPEN_CFW_SCB_SHP`, loader `0x41FDF4`); `0x2000023C`
timing-active/XIP address (timing-auto
`OPEN_CFW_TIMING_AUTO_ACTIVE_ADDRESS`, loaders `0x41FF3E/0x41FF48/`
`0x41FF4E/0x4201D2/0x420216`).

Pool `0x00420ADA`: `0x0000` fill; `0x00433CD8` "drv.norflash" tag
(write-latch `OPEN_CFW_WRITE_LATCH_LOG_TAG`, 28 loaders);
`0x200271C5` guard bypass (guard
`OPEN_CFW_MSPI_GUARD_BYPASS_ADDRESS`, loaders
`0x41FF0E/0x41FF20`); `0x002539C2` expected ID, `0x20000244` table,
`0x00433AB0` log function, `0x0043160C` summary format,
`0x004313D8` row format (timing-scan host names, loaders
`0x420046`, `0x420070/0x4200FC`, `0x4200DA`, `0x4200E2`,
`0x42013A`); `0x00430BD0` success format, `0x004337B4` log
function, `0x00430C4C` failure format (timing-auto host names,
loaders `0x4201F6`, `0x420202/0x42023E`, `0x420232`);
`0x20026FD0` state and `0x00432CC4` power format (low-init host
names, loaders `0x420278/0x42041C`, `0x4202B4`).

Pool `0x00420C18`: `0x004334B4` center format (timing-scan,
loader `0x420162`); `0x00433180` log function (six low-init
loaders), `0x200F4C00` TCB, `0x00432CE8` configure format,
`0x20000224` default config, `0x00432624` device format,
`0x004331A0` enable format, `0x00432A4C` interrupt format,
`0x2000020C` serial template (serial-mode
`OPEN_CFW_SERIAL_TEMPLATE_ADDRESS`, loader `0x42042C`),
`0x00432A74` success format (low-init host names, loaders per
slot); `0x200270D8` state, `0x004337E4` fail format,
`0x004337CC` log function, `0x00433AC4` ID-fail format,
`0x00433AD8` ID format (driver-init host names, loaders per
slot); `0x004334EC` enable format, `0x004334D0` log function
(soft-reset host names, loaders `0x420540`,
`0x42054C/0x420584`).

Pool `0x00420DFA`: `0x0000` fill; `0x00432650` shared log format
(write-latch `OPEN_CFW_WRITE_LATCH_LOG_FORMAT`, loaders
`0x42099C/0x4209DC/0x420578`); `0x00433AEC` fail format and
`0x004337FC` log function (read-ID host names, loaders
`0x4205B8/0x4205C4`).

Word `0x00420F0C`: `1000000` transfer timeout (read/write-transfer
`OPEN_CFW_READ_TRANSFER_TIMEOUT` /
`OPEN_CFW_WRITE_TRANSFER_TIMEOUT`, loaders `0x420672/0x420720`).

Text `0x00420F6A`: `0x0000` fill plus `"set\0"` (QE
`OPEN_CFW_QUAD_SET_TEXT = 0x00420F6C`, selected by `adr` at
`0x00420DD2`).

## Duplicate-word split

The log-file (`0x00431540`) and log-tag (`0x00433CD8`) values each
appear twice in stock: at `0x00420978`/`0x00420ADC` (loaded by the
early IRQ/event/timing/init/transfer/4byte bodies pinned here) and
at `0x00421030`/`0x00421034` inside the 214-byte shared pool
(loaded by the later sector-erase/program/QE/reconfigure/read
bodies). During verification two transcription slips initially
claimed `0x4209AC`/`0x4209EC`/`0x420A2E` (and a later batch of
file-word loaders) against `0x00420978`; exact-entry re-decode
showed they target `0x00421030`, and the verifier now pins only
exact-verified targets, so any future re-derivation must repeat
that check. The `0x00420FF2` pool itself stays retained.

## Not established

- The leading word at `0x00420C14` (`0x000081F6`) has no loader in
  any exactly-decoded routed span and is named in no reviewed
  source; only `0x00420C18..0x00420C5C` is admitted, leaving a
  4-byte retained head. A follow-up should identify it (or prove
  it orphaned) before claiming it.
- Relocated/cave leaves cannot reach these pools by PC-relative
  literal load (they execute more than 4 KB away for `ldr.w`, and
  the `adr` range check covers only the text island); only stock
  spans decoded from exact entries are scanned for loaders.
- Non-PC-relative references (e.g. computed addressing) are not
  covered by the loader scan.
- Semantics of the pointer targets beyond the cited consumer
  sources are established only by those consumer closures, not
  here.
- No hardware, flashing, signing, or transmission operation
  occurred; register behavior and shared-state ownership still
  require authorized hardware evidence, which is unavailable.

## Status

788 of the 5,892 BL-006 bytes are now produced from reviewed source
(580 prior plus 208 here). The remaining 42 regions (5,104 bytes)
need per-region reconstruction: dead stock tails after short
in-place leaves (no fill primitive exists yet), the 214-byte shared
log-pointer pool at `0x00420FF2`, the LittleFS/mapped-memory pools,
the retained `0x00420C14` head word, and scattered small pools.

## Addendum 2026-09-11 (BL-006): 0x00420C14 head word admitted

The retained leading word of the QE literal gap (`0x00420C14`,
`0x000081F6`) is now produced from reviewed MIT C
(`runtime_bl006_reserved_words_420c14.c`) through `in_place_data`.
Bounded Capstone decode of every routed span finds no loader
targeting it and no reviewed consumer source names the value, so it
is a named reserved word preserving layout, not claimed data; if a
future consumer is found the field must be re-derived. Verified by
`g2/tests/test_runtime_bootloader_bl006_float_pools.py`. This closes
the `0x00420C14..0x00420C5C` region fully (68 bytes prior plus 4
here). No hardware operation occurred.
