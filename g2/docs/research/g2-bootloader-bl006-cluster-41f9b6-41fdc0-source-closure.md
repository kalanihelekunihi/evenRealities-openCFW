# G2 bootloader BL-006 cluster 0x0041F9B6..0x0041FDC0 source closure

Six retained `official_blob` regions (198 bytes) across the
boot-initialization literal pools are now produced from reviewed MIT C
through the component's `in_place_data` mechanism. All six payloads
compile relocation-free under the reviewed Apple-clang Cortex-M55
flags and reproduce the authenticated stock bytes exactly, so
`expected.sha256` equals `stock_sha256` for every placement.

| Region | Bytes | Source symbol |
| --- | --- | --- |
| `0x0041F9B6..0x0041F9CC` | 22 | `open_cfw_bootloader_bl006_pool_41f9b6` |
| `0x0041F9EE..0x0041F9F0` | 2 | `open_cfw_bootloader_bl006_align_41f9ee` |
| `0x0041FA40..0x0041FA50` | 16 | `open_cfw_bootloader_bl006_pool_41fa40` |
| `0x0041FAD0..0x0041FADC` | 12 | `open_cfw_bootloader_bl006_pool_41fad0` |
| `0x0041FCF6..0x0041FD70` | 122 | `open_cfw_bootloader_bl006_pool_41fcf6` |
| `0x0041FDA8..0x0041FDC0` | 24 | `open_cfw_bootloader_bl006_pool_41fda8` |

Sources: one file,
`components/bootloader/core_overlay/runtime_bl006_boot_init_pools_41f9b6.c`.
Each pool is one packed struct with a named field per literal word
(not a byte dump); each field comment cites its stock loader PCs and
its meaning from the already-reviewed consumer host models. The
verifier is
`g2/tests/test_runtime_bootloader_bl006_boot_pools.py` (stock-SHA
authentication, byte-exact rebuild, relocation-free check, stock
loader-PC coverage, reviewed-source value association, overlay
registration check).

## Method

Unlike the two prior BL-006 clusters (whose neighbors are exact
in-place leaves that keep stock PC-relative addressing), every loader
of these pools lives in an entry-redirect stock span: the consumers
(run-initializers, platform setup, guarded teardown, pin-group
dispatcher, TLSF initializer, EasyLogger channel-write) are relocated
leaves that carry their own copies of these constants. These pools
are therefore NOT address-live in the final image. They are admitted
as authenticated layout reproductions with reviewed meanings: for
each slot, the stock loader PCs were mapped by decoding each
loader's stock function span from its exact entry with Capstone
(`Align(PC,4)+imm` literal targets; per-span decode keeps Thumb
sync across the interleaved pools), and each value was matched to a
named constant in the already-reviewed consumer source.

The one slot class with no stock loader is the SCS quartet at
`0x0041F9B8..0x0041F9C4` (orphaned literals): three words match
reviewed IRQ-service host constants exactly (`0xE000E100`,
`0xE000E400`, `0xE000ED18`), and the fourth (`0xE000E280`) is the
architectural NVIC clear-pending register 0 (CMSIS `NVIC->ICPR[0]`,
offset `0x180` from the NVIC base; `core_cm55.h` names the
`Interrupt Clear Pending Register` at that offset). It is
reproduced as a named layout constant, not as claimed data.
Intra-island branches (`0x0041F9BA->0x0041F9BE->0x0041F9C2->...`)
are chained `b next` padding; no branch from outside the island
targets `0x0041F9B6..0x0041F9C7`, and no `adr` in the image targets
the island, so the SCS-word reading (not code) stands.

The trailing island words at `0x0041F9CC..0x0041F9D8`
(`0x0043419C`, `0x00434158`, `0x0043415C`) point into the
unidentified retained globals region `0x004329D2..0x00434477` and
stay retained for the owning item; only `0x0041F9B6..0x0041F9CC`
is admitted.

## Word table

Pool `0x0041F9B6` (22 B: fill + 5 words): `0x0000` alignment fill
(`0x0041F9B8` is word-aligned); `0xE000E100` NVIC set-enable
register 0, `0xE000E280` NVIC clear-pending register 0,
`0xE000E400` NVIC priority register 0, `0xE000ED18` SCB
handler-priority register 2 (reviewed irq_services host
`OPEN_CFW_NVIC_ISER` / `OPEN_CFW_NVIC_IPR` / `OPEN_CFW_SCB_SHP`;
ICPR from CMSIS architecture); `0x20000454` EasyLogger transport
table base (reviewed transport host
`OPEN_CFW_BOOTLOADER_ELOG_TRANSPORT_TABLE_ADDRESS`; stock loader
`0x0041F93A`).

Pool `0x0041F9EE` (2 B): `0x0000` alignment fill before the
initializer-priority comparator entry.

Pool `0x0041FA40` (4 words): `0x00433440` initializer-table begin
(loader `0x0041F9FA`), `0x00433460` table end (loader `0x0041F9FC`),
`0x20022E00` sort scratch cell (loader `0x0041FA10`),
`0x0041F9F1` comparator Thumb entry (loader `0x0041FA1A`) --
reviewed boot-services host `OPEN_CFW_BOOT_SERVICE_INITIALIZER_BEGIN`
/ `_END` / `_SCRATCH` / `_COMPARATOR_THUMB`; the stock loads of
both bounds confirm the reviewed count derivation.

Pool `0x0041FAD0` (3 words): `0x20027198` teardown guard cell
(loader `0x0041FA9A`; reviewed teardown host
`OPEN_CFW_TEARDOWN_GUARD`), `0x00433A9C` 20-byte platform
configuration base (loader `0x0041FA70`; reviewed platform host
`OPEN_CFW_PLATFORM_CONFIG`), `0x00434154` pin-configuration word
(loader `0x0041FABE`; reviewed teardown host
`OPEN_CFW_TEARDOWN_PIN_CONFIG`).

Pool `0x0041FCF6` (122 B: fill + 30 words): `0x0000` alignment fill,
then `0x20000000+offset` pin-configuration SRAM addresses, i.e.
reviewed dispatcher host `OPEN_CFW_PIN_CONFIG_BASE + offset`.
Every (pin, offset) call site matches the reviewed
two-bank/subtype paths exactly -- bank-zero nine
(pins `0x25-0x2D`, offsets `0x28-0x48`, loaders
`0x0041FB38-0x0041FB98`), bank-zero quad (pins `0x44-0x47`,
offsets `0x14-0x20`, loaders `0x0041FBA4-0x0041FBC8`),
bank-zero pair (pins `0x42-0x43`, offsets `0x0C/0x10`, loaders
`0x0041FBD4/0x0041FBE0`), bank-zero common (pins
`0xC7/0x40/0x41/0x48`, offsets `0x00/0x04/0x08/0x24`, loaders
`0x0041FBEC/0x0041FBF8/0x0041FC04/0x0041FC10`), bank-one quad
(pins `0x63-0x66`, offsets `0x60-0x6C`, loaders
`0x0041FC66-0x0041FC8A`), bank-one pair (pins `0x61-0x62`,
offsets `0x58/0x5C`, loaders `0x0041FC96/0x0041FCA2`), bank-one
common (pins `0x31/0x5F/0x60/0x67/0x68`, offsets
`0x4C/0x50/0x54/0x70/0x74`, loaders
`0x0041FCAE/0x0041FCBA/0x0041FCC6/0x0041FCD2/0x0041FCDE`).

Pool `0x0041FDA8` (6 words): `0x20081000` TLSF pool base (loader
`0x0041FD78`), `0x2002718C` allocator handle cell (loader
`0x0041FD8C`), `0x00434010` log file string (loader `0x0041FD90`),
`0x00433CA4` log argument string (loader `0x0041FD98`),
`0x004315C8` log format string (loader `0x0041FD9A`),
`0x00434144` log tag string (loader `0x0041FD9C`) -- reviewed
allocator host `OPEN_CFW_ALLOC_POOL` / `_HANDLE` / `_LOG_FILE` /
`_LOG_ARGUMENT` / `_LOG_FORMAT` / `_LOG_TAG`.

## Status

This brings BL-006 to 544 of 5,892 bytes from reviewed source (346
prior plus 198 here). The remaining 54 regions (5,348 bytes) --
MX25 flash-driver literal gaps, LittleFS/mapped-memory pools,
control/MSPI pools, unreachable tails, and scattered small pools --
remain retained stock. Hardware qualification stays blocked by
unavailable physical evidence; no hardware operation occurred, and
firmware-wide completeness is not claimed.
