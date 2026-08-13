# FlashDB 2.1.1 G2 read-only port source-candidate audit

Status: production-excluded source candidate. No overlay, manifest, Makefile,
release pin, firmware artifact, or hardware state was changed. In particular,
this tranche does not call `fdb_kvdb_init`, mount either database, inspect
magic values, load defaults, format storage, sign, flash, or connect to a G2.

## Result

`components/shared/flashdb/runtime_flashdb_readonly_port_candidate.c` is a
freestanding, fail-closed read-only implementation of the recovered G2 FAL
boundary. It provides:

- fixed-width representations of the released 32-bit `fal_flash_dev` and
  `fal_partition` records;
- the exact `kvdb` and `NVdb` partition records and authenticated stock
  `norflash` record as non-operational ABI evidence;
- an overflow-safe partition-read adapter for `kvdb` at
  `0x01FC0000..0x01FF7FFF` and `NVdb` at
  `0x01FF8000..0x01FFFFFF`;
- the recovered MX25 read seam at Thumb entry `0x004709C9`;
- the shared CMSIS mutex-ID slot at `0x20074944`, acquire entry
  `0x004497B7`, release entry `0x0044981D`, and wait-forever value
  `0xFFFFFFFF`; and
- unconditional write/erase callbacks that return `-1`, have six-byte target
  bodies, contain no relocation, and have no mutation transport declaration or
  dispatch.

The implementation deliberately corrects the released first-party error
mapping. The official MX25 seam returns zero only after a complete transfer.
Every nonzero result—including a positive value that might otherwise be
mistaken for a short byte count—is mapped to `-1`. This matters because
FlashDB 2.1.1's `_fdb_flash_read` reports `FDB_READ_ERR` only when the FAL
return value is negative. The stock G2 adapter returned zero on transport
failure and could therefore report success.

## ABI and bounds

The source header asserts these released layouts independently of host pointer
width:

| Record/field | G2 value |
|---|---:|
| `sizeof(fal_flash_dev)` | `0x38` |
| device read/write/erase callback offsets | `0x28/0x2C/0x30` |
| `sizeof(fal_partition)` | `0x40` |
| partition offset/length offsets | `0x34/0x38` |
| device address/length/block size | `0x01FC0000/0x02000000/0x1000` |
| device write granularity | 1 bit |

The candidate accepts only pointers returned for its two immutable partition
records. It validates `address <= length` and
`size <= length - address` before adding the partition offset. This is
equivalent to upstream FAL for valid values while closing its 32-bit
`address + size` wraparound case. It also checks the resulting read against
the recovered NOR window. A zero-byte read returns zero without touching the
mutex or transport.

The public transaction entry acquires the shared CMSIS mutex, performs the
unlocked FAL read, and releases on both success and transport failure. A lock
failure suppresses the transport call; a release failure makes the operation
fail closed. The separate unlocked entry preserves the exact low-level FAL
layering for a future integration whose upstream DB operation already owns the
same mutex, avoiding double-locking.

## Authenticated source oracle

The candidate is derived from the exact Apache-2.0 FlashDB `2.1.1` snapshot:

- lightweight tag `2.1.1`;
- commit `714d6159e7e6afb267a3953756abca445c350e61`;
- selected tree `3410ae8111e4dbf6ae22d995bfcf37274abf89ea`; and
- offline commit-to-tree-to-path-to-blob proof in
  `third_party/flashdb/verify_snapshot.py`.

The host oracle fixture compiles the authenticated upstream
`port/fal/src/fal_partition.c` itself with only the recovered two-record FAL
table and a negative-error read-only device seam. The test pins that upstream
file (14,574 bytes, SHA-256
`25b7ade441576561e5ebee1ef43c92c9e03c494e0a459588d82a1ebccc7c498c`),
`fal_def.h`, and the `_fdb_flash_read` consumer in `fdb_utils.c`. Randomized
differential vectors cover both partitions, edge addresses, out-of-bounds
requests, successful reads, negative errors, and positive nonzero/short-like
driver results. Additional tests authenticate the candidate's two ABI records
directly against the official G2 image.

The local candidate boundary is pinned as:

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_flashdb_readonly_port_candidate.c` | 8,019 | `b711c22c470cbf09245b8e29946a63be7d4710c96bc7409dd402c61899bf5f14` |
| `runtime_flashdb_readonly_port_candidate.h` | 5,296 | `d9e72e7e70adfef60e330abed6f49a3863896284ac003e78101b2c70123a9d19` |
| candidate host fixture | 4,360 | `2aca0dfacf1fa0beae0167dbc2222861854aea91a0b8b2fce9fb6b717c353285` |
| upstream-oracle host fixture | 4,470 | `62306986bfc9429c9bec2f9c8c5ea65f59be680d6b49d74e32f179a80177c1fe` |

## Dual target authentication

Both compiler profiles use the normal openCFW Thumb-v7E-M, freestanding,
ROPI, per-function/data-section flags. The complete objects are:

| Profile | Compiler | Bytes | Object SHA-256 |
|---|---|---:|---|
| Apple | Apple clang 21.0.0 (`clang-2100.3.27.1`) | 3,800 | `3c05501e866c7d1defd8504bcb3f13551e8287cae3177d8e7c9e5f30d8490429` |
| Linux | Homebrew clang 22.1.8, image `sha256:ab76…36805` | 3,780 | `4559b527367faeced0109a91924dc949fbfb73fa596f02b31417aeb8077dd85b` |

Both emit identical candidate text and read-only data sections. The normalized
18-record relocation graph has SHA-256
`2065e910c013ad5424e02807f1f9820fd93b5a9994e88fe049ec61642a9000ed`.
There are no undefined symbols. The write-denied and erase-denied sections are
each exactly `4ff0ff307047` (`mov.w r0, #-1; bx lr`) and have no code
relocations. The only inter-function call relocations in the public read path
target the source-owned lock, unlocked-read, and unlock functions. Direct
recovered read/CMSIS seams are literal Thumb addresses; no program or erase
seam exists.

`tests/test_runtime_flashdb_readonly_port_candidate.py` exercises the host
differential, records, bounds, transport-error conversion, lock lifecycle,
compile-time mutation rejection, production exclusion, Apple object, Linux
object, per-section hashes/alignment, relocation graph, and mutation-stub
instruction bytes.

## Explicit blockers

This candidate is not a mount-ready database port. Promotion remains blocked
on all of the following:

1. There is no authenticated, non-mutating golden capture of the G2 `kvdb`
   and `NVdb` external-flash contents against which to establish on-disk
   header, status-bit, CRC, enumeration, and corruption behavior.
2. The Even application schemas and factory calibration semantics are not
   supplied by upstream FlashDB.
3. Upstream `fdb_kvdb_init` can reach corruption/magic-driven formatting and
   `fdb_kv_set_default`; a source-owned non-destructive mount policy is not yet
   implemented or proven.

The former `kvbooCount` blocker is closed: reset's authenticated IAR zero
scatter initializes `0x20074988` to zero, and the closed system-KVDB service
proves the persisted read/increment/write lifecycle plus the eleven migration
callbacks.

Until those blockers are closed, this source remains a compile- and host-test
candidate only. Its safe next use is against an authenticated disposable copy
or read-only golden capture, never live hardware storage.
