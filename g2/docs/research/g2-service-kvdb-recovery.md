# G2 system KVDB service recovery

## Result

The retained `platform\service\flashDB\kv\service_kvdb.c` object is closed as
seven functions at `[0x004D9530, 0x004D9B34)`. It occupies 1,540 physical
bytes with SHA-256
`373fb5e4f07d20e74c238fe6fe5922064d28e398b19696459167432fdbbc83c0`:
1,384 executable bytes plus 156 bytes of alignment and shared literals.

Only `SVC_KvdbReadAll` and `SVC_KvdbInit` carry retained-path anchors. Five
adjacent helpers are restored to the object by source order, shared pool,
internal calls, exact database signatures, the migration table, and complete
whole-image ingress. All seven were independently discovered by Ghidra. The
object has one bounded indirect call site: it copies and invokes an exact
eleven-entry ROM table of already object-closed first-party KV migration
callbacks.

This closes a previously unresolved FlashDB configuration detail. The
`kvbooCount` value at `0x20074988` lies inside the authenticated reset-called
IAR zero range `[0x20004558, 0x20075048)`, so its startup/default bytes are
provably `00000000`. Initialization reads the persisted word, increments it,
and writes it back. The initial default and runtime lifecycle are no longer an
open provenance/configuration gap.

## Reproduction

Run:

```sh
make service-kvdb-closure
```

The analyzer authenticates the official image, all seven bodies, physical
boundaries and pool, every instruction and direct call, whole-image ingress,
the bounded indirect migration dispatch, exact path and configuration strings,
the FlashDB 2.1.1 audit, and the reset/scatter proof for `kvbooCount`.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered / non-anchor restored functions | 7 / 7 / 5 |
| Path-anchored functions | 2 |
| Raw path references / referencing functions | 13 / 2 |
| Body / alignment-pool / physical bytes | 1,384 / 156 / 1,540 |
| Reachable instructions | 550 |
| Direct calls | 88 |
| Internal / external direct calls | 4 / 84 |
| Indirect call sites / bounded targets | 1 / 11 |
| Whole-image direct `BL` entries | 32 |
| Stored exact entries / strict-interior entries | 0 / 0 |

The executable-body SHA-256 is
`2c07e82aa841a5f3a6cd0cdefc14f91a357fd9f8f6fa2e341cbd9a3ca0ea1665`.
The instruction topology digest is
`921ef30a8be2b109603d722ccfccc84a2956e6b5bd53c356dc07c1156a20e348`,
and the direct-call digest is
`a556efd6d2a9a46c504f06860fc378f21588c759e4504fd69b8221f391702a2c`.

## Recovered initialization contract

Database index zero binds `sysenv@kvdb` to the `norflash` partition at offset
`0x01FC0000`, length `0x38000`. Its default descriptor contains twelve
explicit-length nodes at `0x2000372C`, with magic
`kvMagic=0x5A000020`. Non-null lock and unlock callbacks are installed with
FlashDB control commands two and three. A missing or mismatched magic value
triggers wholesale `fdb_kv_set_default`.

The reset path then preserves/reloads the separately closed onboarding byte,
reads `kvbooCount`, increments and persists it, runs the eleven migration
callbacks, and reloads all nonempty default nodes. The callback table SHA-256
is `bd1d3336c4e37373945074a222e8bc34f71269373b0cf16ffe7fbd7bc779b112`
and covers ALS scale, menu/dashboard/language configuration, ring, settings,
temperature unit, terminal mode, time, time format, and universal settings.

The final helper writes zero to `kvMagic`, deliberately scheduling wholesale
default reset for the next initialization. Together with the FlashDB
corruption fallback, this remains a destructive production-policy gate.

## Dependency result

Four calls reach the authenticated FlashDB 2.1.1 core at commit
`714d6159e7e6afb267a3953756abca445c350e61`. Twelve reach the already closed
G2 database adapters, two reach the closed onboarding record, and the bounded
indirect table reaches eleven closed first-party migration bodies. The only
other reusable seams are 65 admitted logging calls and one IAR `memcpy`. No
third-party implementation or new version discriminator is embedded.

OpenCFW can now remove `kvbooCount` from the FlashDB residual list. Production
mount remains blocked by golden-media validation, application schema semantics,
non-destructive reset policy, and hardware behavior; the stock zero-on-driver-
failure FAL hazard also remains explicit.

No device, signing, flashing, erase, or runtime operation was performed.
