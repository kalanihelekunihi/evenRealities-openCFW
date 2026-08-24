# G2 factory NV service recovery

## Result

The authenticated `platform\service\flashDB\NV\service_nvdb.c` object is closed as
five functions at `[0x005105F0, 0x00510A0C)`. The physical object is 1,052
bytes with SHA-256
`89b3755f401952cd93615b007fdcdade3c203c60f2dccdd7c9a587c12b8e761e`:
930 executable bytes and 122 bytes of alignment/literal data. The path directly
anchors the default validator and initializer; adjacency, shared configuration
data, internal calls, and whole-image ingress restore the read wrapper, write
wrapper, and default-table descriptor.

The object now has an independently authored production implementation. It
contains first-party factory-NV policy over an already authenticated
FlashDB dependency. It embeds no FlashDB definition. Four direct calls reach
`fdb_kv_set_default`, `fdb_kvdb_control`, and `fdb_kvdb_init` from FlashDB
2.1.1 commit `714d6159e7e6afb267a3953756abca445c350e61`. Nine calls reach
G2 database-object adapters, two reach first-party serial-number policy, two
reach bounded IAR `memcpy`/`strcmp`, and forty reach the admitted logging
seams. No new version discriminator or recoverable private generating commit
is present.

This closure intentionally reuses the complete existing FlashDB configuration
audit. That audit already authenticates the exact upstream snapshot, object
ABI, short enums, cache sizes, default SRAM tables, FAL partitions, callbacks,
and called FlashDB bodies. The retained path can therefore be classified
without re-reversing those same bytes.

## Reproduction

Run:

```sh
make service-nvdb-closure
```

The analyzer authenticates the official image, invokes the fail-closed full
FlashDB 2.1.1 configuration audit, pins all five local bodies and both object
boundaries, recovers every instruction and call, scans whole-image ingress,
checks all eight path references and retained configuration/diagnostic strings,
and verifies the object is production-routed under the non-destructive media
policy described below.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered functions | 5 / 5 |
| Restored / path-anchored functions | 3 / 2 |
| Raw path references / referencing functions | 8 / 2 |
| Body / alignment-pool / physical bytes | 930 / 122 / 1,052 |
| Reachable instructions | 379 |
| Direct calls | 60 |
| Internal / external direct calls | 3 / 57 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 20 |
| Stored / strict-interior entries | 0 / 0 |

The executable-body SHA-256 is
`69a92529d34123e3cd0e04272754940e699a0c6323215ceff1d0f7c88f47a9bd`.
The instruction topology digest is
`d716e7b623620fd7365c60d95a149a71e47f28a37c16ba6f350c5cc7f1476f7f`,
and the direct-call digest is
`d97b1798aef49da4f4578969e2a5e33a283c5361a803cf6994c84500cd41a2c3`.

## Recovered factory database contract

Database object index 1 is initialized as database `factory` on FAL partition
`NVdb`. The partition begins at external-flash offset `0x01FF8000` and is
`0x8000` bytes. The object installs the shared lock and unlock callbacks with
`FDB_KVDB_CTRL_SET_LOCK` (2) and `FDB_KVDB_CTRL_SET_UNLOCK` (3); it does not set
a sector-size override. It then calls `fdb_kvdb_init` with the nine-node default
table at `0x20003868`.

The factory defaults are explicit-length blobs:

| Key | Bytes |
|---|---:|
| `nvString` | 9 |
| `nvMagic` | 4 |
| `nvProdMode` | 4 |
| `nvSysDt` | 172 |
| `nvAdvMagic` | 4 |
| `nvMAC` | 10 |
| `nvSCald` | 92 |
| `nvSCaldAG` | 68 |
| `nvBuzzer` | 12 |

After initialization, the service reads four bytes from `nvMagic`. The expected
little-endian value is `0x55550022`. A missing or mismatched value triggers
wholesale `fdb_kv_set_default`, writes the expected magic, and then validates
the default records. This is reset policy, not an upstream migration facility;
FlashDB automatic KV version migration is not enabled. The validator also
performs G2-specific production serial-number reconciliation for the system
data record.

The two 18-byte public wrappers bind reads and writes to database index 1 and
preserve the caller's explicit 16-bit blob length. They do not add a second
storage library or schema layer.

## OpenCFW implication and safety gate

The exact dependency shortcut is now explicit: source reconstruction can use
the vendored FlashDB 2.1.1 API and the already recovered nine-node table,
partition, callback, magic, and reset policy. Remaining work is first-party
schema/reconciliation implementation and a production choice about destructive
default reset.

The stock FAL adapter returns zero on lower-driver failure, while FlashDB 2.1.1
recognizes negative FAL values as errors. That unsafe seam can hide read, write,
or erase failures and is already corrected by the production-excluded
read-only port candidate. OpenCFW must not admit the stock magic-mismatch reset
or any write/erase path before obtaining a read-only golden `NVdb` capture and
choosing a non-destructive mount policy.

No device, signing, flashing, erase, or runtime operation was performed.

## Production source closure

`components/apollo_main/core_overlay/service_nvdb.c` implements the two blob
wrappers, nine-node default-table descriptor, default validator/PSN
reconciliation path, and factory database initializer. Five selector-isolated
Cortex-M55 leaves total 514 text bytes with four generated alignment bytes and
eleven strict relocations. Five guarded redirects replace all 930 callable
stock bytes; the authenticated 122-byte pool remains official.

The source changes the unsafe stock magic-mismatch behavior deliberately. A
valid `nvMagic=0x55550022` database mounts and validates normally. Missing or
mismatched magic returns a schema error without calling
`fdb_kv_set_default`; destructive reset is compile-time disabled. Enabling it
requires a read-only golden `NVdb` capture and explicit policy review.

The canonical overlay/component/package sizes are 239,330 / 3,762,726 /
4,541,220 bytes. Live external-flash persistence, corruption recovery,
power-loss behavior, and schema compatibility remain blocked because no
authorized responsive G2 target and golden writable-media evidence are
available.
