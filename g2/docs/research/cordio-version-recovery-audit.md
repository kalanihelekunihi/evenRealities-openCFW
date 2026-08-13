# G2 Cordio/Packetcraft source-interval recovery audit

## Result

This audit does **not** identify one exact upstream Cordio tree for the whole
G2 BLE stack.  It does establish a useful, fail-closed source-reuse boundary:

- two independent function-level discriminators require Packetcraft Cordio
  **r20.05-or-later semantics**;
- the relevant public Packetcraft source blobs are identical from `r20.05`
  through `r20.05c`, so that release interval is a defensible source oracle
  for the bounded functions described below;
- the G2 image uses an Ambiq FreeRTOS WSF port and contains local tracing
  changes, so the interval is not an upper bound for the complete vendor tree;
- the focused WSF timer recovery additionally finds mixed lineage: its
  bool-pointer next-expiration ABI matches official Packetcraft r19.02, while
  official AmbiqSuite 2.5.1 archive/source identities pin the exact
  proprietary FreeRTOS implementation family and a saved-tick discriminator
  excludes unmodified AmbiqSuite 2.4.2;
- no authenticated AmbiqSuite 5.1.0 Cordio source archive was available in the
  repository.  The authenticated 5.1.0 snapshot covers the Apollo510 HAL only.

The practical decision is to use Apache-2.0 Packetcraft `r20.05c` as a pinned
candidate source tree, then promote functions one at a time after their ABI,
configuration, data layout, and call closure are proved.  A wholesale Cordio
replacement is not justified by the current evidence.

The machine-readable reproduction is:

```sh
python3 tools/analyze_g2_cordio_version.py
```

It authenticates the official main image before checking paths, pointer xrefs,
function hashes, constants, and instruction shapes.

## Authenticated input

| Item | Identity |
|---|---|
| Firmware | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Size | `3,523,396` bytes |
| SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Raw-image load bias | `0x00437FE0` |

The firmware embeds IAR source paths rooted at
`D:\01_workspace\s200_ap510b_iar_git\third_party\cordio`.  Paths alone are
weak identity evidence, so the analyzer also requires their literal pointer
xrefs and the body/configuration fingerprints below.

Representative path evidence includes:

| Embedded module | String file offset | Runtime address | Pointer-xref file offsets |
|---|---:|---:|---:|
| `atts_csf.c` | `0x2A4954` | `0x6DC934` | `0xF50A8`, `0xF5A4C` |
| `dm_conn_sm.c` | `0x2A5134` | `0x6DD114` | `0xFC56C` |
| `smp_db.c` | `0x2A9A10` | `0x6E19F0` | `0x10A978` |
| FreeRTOS `wsf_buf.c` | `0x2AA0E4` | `0x6E20C4` | `0xF8548` |

The `dm_conn_sm.c` runtime address above is the direct arithmetic result
`0x2A5134 + 0x437FE0 = 0x6DD114`.

## Discriminating firmware bodies and configuration

### ATT client-supported-features write

The core of `AttsCsfWriteFeatures` at `[0x0052D628, 0x0052D674)` has SHA-256
`2e11f9d1dfa9b76ebfd7d92902439df111292ba781151196eca08280184d5bd9`.
The callback tail at `[0x0052D79E, 0x0052D7B6)` has SHA-256
`27aa2fb64353776ed629c906e6c6466d6fdcf0ae9d5f02efa1a5650229afa124`.

The code:

- masks the incoming feature byte with `0x07`;
- rejects a nonzero-to-zero transition with ATT error `0x13`;
- ORs newly enabled bits into the stored feature byte;
- invokes the registered callback, when non-null, with the connection ID,
  change-aware state, and client-features record.

This is the public `r20.05` behavior.  Public `r19.02` instead tests whether
the requested value clears an existing bit and then assigns a differently
masked value.  This is a release-discriminating lower bound, not merely a
symbol or path match.

`AttsCsfSetClientChangeAwareState` at
`[0x0052D090, 0x0052D0DC)` independently pins G2 configuration: connection ID
zero is the none value, `DM_CONN_MAX` is three, each client record is two
bytes, DB-read-pending is state two, and pending-aware is state one.

### DM connection state machine

The event/table core of `dmConnSmExecute` at
`[0x00534024, 0x005340A0)` has SHA-256
`decb00baeedd9291a19c1746fb58d8114c979e3f622c78567143f19b515d89b1`.
The action-dispatch tail at `[0x005344FA, 0x00534532)` has SHA-256
`80294c9e8e8462f412813b8fb7711f795d654d9dd6344b2cda45e8c88e145dd1`.

The implementation masks events with seven, uses eight two-byte entries per
state (a 16-byte row), takes the next state from byte zero and action from byte
one, stores state at CCB offset `0x15`, and selects one of three action sets
using the high action nibble.  Public `r19.02` has thirteen events per state;
public `r20.05` has eight.  This supplies a second independent r20.05-or-later
discriminator.

The G2 trace text is locally expanded to
`dmConnSmExecute event=%d, action = %d, next state = %d`, while public r20.05
has a shorter event/state trace.  That difference is positive evidence of
vendor or product instrumentation and prevents an exact whole-file claim.

### WSF buffer manager

| Function | Runtime range | Bytes | SHA-256 |
|---|---:|---:|---|
| `WsfBufAlloc` | `0x00530446`--`0x005304D4` | 142 | `307ff7ddc2830031087eff4c703949a9974deb2e81efe9cd4334b06c35d57d48` |
| `WsfBufFree` | `0x005304D4`--`0x00530512` | 62 | `6148f827458d86f257dc4ac8eab53f4eeb9372912249d1181fc835861b5a058f` |

The allocation body performs the stock best-fit pool walk.  Its descriptor is
12 bytes, the free-list pointer is at descriptor offset eight, and allocation
zeros the marker at buffer offset four.  Freeing walks descriptors in reverse,
stores `0xFAABD00D`, and pushes the buffer at the free-list head.  These shapes
support the following build configuration:

| Setting | Recovered value | Evidence |
|---|---:|---|
| `WSF_BUF_FREE_CHECK` | enabled | `0xFAABD00D` written by `WsfBufFree` |
| `WSF_BUF_STATS` | disabled | descriptor remains 12 bytes |
| `WSF_BUF_STATS_HIST` | disabled | no histogram update shape |
| `WSF_OS_DIAG` | disabled | simple allocation-failure trace path |

The embedded path is `wsf/sources/port/freertos/wsf_buf.c`, not Packetcraft's
public bare-metal target.  G2 also materializes source line 321 in the
allocation trace; the public AmbiqSuite R4.5 comparison mirror places the
corresponding trace at line 319.  Thus the algorithm and configuration are
recoverable, but exact file text is not.

## Official Packetcraft source identities

Primary repository: [packetcraft-inc/cordio](https://github.com/packetcraft-inc/cordio).

| Release | Commit | Tree |
|---|---|---|
| `r20.05` | `eeb34839755da1c19cc85b8795cc863483c16ef0` | `906eb9beaf5e8c3b39ab445f6522f7febeda38b5` |
| `r20.05a` | `5e21ee596a80a3dc75ae5ef0938712a6042b2ac3` | `5001d075e93220d66ae1340208046c0526b0dc3a` |
| `r20.05b` | `eb4282c7abe78dad8fb3984791b9c193fe904052` | `c8204fcb39847aa6d3cae3ec49772a70f6097765` |
| `r20.05c` | `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` | `0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97` |

The timer-specific older oracle is official Packetcraft `r19.02` commit
`86372d84ef0386d8834ed036e613c8f2ded1ff16`, tree
`b398806b4472aa738b6bfd771b583ad2e9fd179f`. Its
`wsf/sources/port/baremetal/wsf_timer.c` is blob
`d2cced51a06a87f7ca26369b01e4a8b0ec325346`, SHA-256
`1dd5bb6aab28031793227a152686d692b2c04878de4bf6d2d8bef187081a0a4e`.
This pins a two-function public semantic oracle only; it does not supersede
the r20.05-or-later ATT/DM result. The vendor FreeRTOS translation unit is now
separately pinned to the official AmbiqSuite 2.5.1 archive/source family. See the
[focused WSF timer recovery](cordio-wsf-timer-source-recovery.md).

The audited source files below have the same Git blob in all four releases:

| File | Git blob | File SHA-256 |
|---|---|---|
| `ble-host/sources/stack/att/atts_csf.c` | `ed4f051194b77827ec991f0d5c0c38969ea7548a` | `1464bff0dbb063ce0e69c5781b73fd7b95656afcd8f710084449298189f2f747` |
| `ble-host/sources/stack/dm/dm_conn_sm.c` | `58c5c6e1e4df5744c9a41902634cdd23a1aef906` | `cdab18be5711866031487f164d39ea1806bd7f75032992c3050a75bdd0a85de8` |
| `ble-host/sources/stack/smp/smp_db.c` | `cbd056aaab32eab0838b2bd9bbaac872012ca06b` | `d73d33be7c3d64476b8edb763bb0f32f4a49b54e07a65d44cbfbc4b2deb76645` |
| `ble-profiles/sources/af/common/app_db.c` | `789f4c9bac29a5b7eb92c2cb22a221cdd720fe83` | `9d96742d3dcb100f9156bdc339cee04e34a2ef5ca4bc5ee3b9971d1d7876f3df` |
| `wsf/sources/targets/baremetal/wsf_buf.c` | `be2ab9cfc03b65390ba25d8d97321fa2d304fc64` | `d50d374e87b8bed25a0afd50156abac8abad0ae395a7b3db6671decfb50c701d` |

Packetcraft's `LICENSE.md` is Apache-2.0, Git blob
`5fe50d5491f1166292380f46c8beae44ca83cadb`, SHA-256
`682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd`.
The release used as the current source oracle is the official
[`r20.05c` commit](https://github.com/packetcraft-inc/cordio/commit/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6).

These identities prove what would be imported.  They do not prove that every
G2 object originated from those exact files.

## AmbiqSuite comparison and limit

The local authenticated Apollo510 HAL provenance points to the official
[Ambiq HAL repository](https://github.com/AmbiqMicro/ambiqhal_ambiq) at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, tree
`02b79dbf428a8cded053c65c92cc58fa5fdb8e78`.  Its recorded subject is
“Import Apollo510 HAL from AmbiqSuite SDK 5.1.0.”  That closure is useful for
hardware support but contains no Cordio source; it cannot authenticate a 5.1.0
Cordio tree.

A public AmbiqSuite R4.5 mirror was used only as a non-authoritative comparator.
It shares exact r20-era blobs for `dm_conn_sm.c` and `smp_db.c`, while its
FreeRTOS WSF file differs in source-line metadata.  Since it is not Ambiq's
official repository and is not version 5.1.0, it is not a source provenance
anchor for OpenCFW.

## Ownership boundary

The recovered tree must preserve three distinct layers:

1. **Upstream Packetcraft Cordio:** WSF core; BLE-host ATT, DM, L2CAP, and SMP;
   and generic profile/application-framework core.
2. **Ambiq port:** `ble-host/sources/hci/ambiq` and
   `wsf/sources/port/freertos`, including platform scheduling and controller
   transport adaptations.
3. **Even product glue:** `platform/ble`, custom services/profiles, MRAM-backed
   records, application database wrappers/extensions, UI/device policy, and
   product-specific callbacks.

The EM9305 controller firmware is a separate binary boundary and is not
Packetcraft host-stack source.

Notably, the embedded G2 `app_db.c` path is under Ambiq's `apps/app` layout,
whereas public Packetcraft uses `af/common`.  Similar names and interfaces do
not make Even/Ambiq database persistence code upstream Cordio.

## Reuse rules for OpenCFW

- Vendor the pinned Apache-2.0 `r20.05c` source only with its license and
  provenance intact.
- Treat ATT CSF and the DM state-machine logic as bounded source candidates,
  not automatic byte-identical replacements.
- Reconstruct the WSF FreeRTOS configuration and port seam separately; do not
  substitute the public bare-metal file.
- Require a per-function proof of calling convention, structure offsets,
  compile-time constants, callback semantics, and reachable closure before a
  firmware blob range is retired.
- Keep Even platform/database glue and the controller image outside the
  upstream Packetcraft attribution.
- If an authenticated AmbiqSuite 5.1.0 Cordio archive becomes available,
  compare its Git/file identities and the pinned firmware bodies before
  narrowing this conclusion.  Until then, exact whole-tree attribution remains
  unresolved by design.
