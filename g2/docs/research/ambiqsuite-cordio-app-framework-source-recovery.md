# AmbiqSuite Cordio application-framework source recovery

## Result

All nine retained stock paths under
`third_party\cordio\ble-profiles\sources\apps\app` now have a concrete,
redistribution-safe source lineage. They descend from Packetcraft Cordio's
Apache-2.0 application framework through AmbiqSuite. The selected rebuild
oracle is the public SparkFun AmbiqSuiteSDK 2.5.1 import at commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` (tree
`3a06dca6e2222fdc2058e9587596e22325a6f024`, subject `bump to sdk release
2.5.1`). The public ancestor comparison point is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`.

This closes the third-party source-identification gap; it does **not** identify
Even's private producing checkout. Stock contains substantial downstream
database, privacy, pairing, connection, diagnostic, and UI changes, so exact
source-text identity is false. Production routing is complete for the bounded
framework: the 22 anchored `common/app_db.c` functions are source-owned by the
G2 MRAM database implementation, while 14 legacy master/slave functions and
all 25 remaining anchored UI/core/master/server/slave/discovery functions are
source-routed by the five maintained `runtime_cordio_app_*.c` modules.

The exact nine-file source snapshot, Apache license, blob IDs, sizes, hashes,
release history, and negative historical-commit claim are authenticated under
`third_party/ambiqsuite-cordio-app-framework`. Four files (`app_disc.c`,
`app_master_leg.c`, `app_server.c`, and `common/app_ui.c`) are blob-identical
across authenticated AmbiqSuite 2.3.2, 2.4.2, and 2.5.1 imports. The remaining
five change at 2.5.1, making that release the narrowest coherent selected
baseline available from the public imports.

## Why AmbiqSuite, not pristine Packetcraft

AmbiqSuite 2.5.1 contains application-framework changes beyond public
Packetcraft r20.05c. A direct source-tree comparison gives these per-file
deltas (Ambiq relative to Packetcraft):

| File | Added | Removed |
|---|---:|---:|
| `app_disc.c` | 59 | 43 |
| `app_main.c` | 6 | 69 |
| `app_master.c` | 114 | 54 |
| `app_master_leg.c` | 4 | 4 |
| `app_server.c` | 12 | 9 |
| `app_slave.c` | 109 | 28 |
| `app_slave_leg.c` | 6 | 4 |
| `common/app_db.c` | 149 | 444 |
| `common/app_ui.c` | 7 | 22 |

Distinctive selected-source features provide practical reconstruction
shortcuts: `appExtConnCb[DM_CONN_MAX]`; the three-argument, role-aware
`AppDbNewRecord(..., TRUE/FALSE)` calls; `AM_BLE_USE_NVM`; and the default
legacy advertising-state assignment in `AppSetAdvType`. These make the Ambiq
fork a better semantic base for OpenCFW than pristine Packetcraft.

Stock is later and larger still. Its `app_db.c` diagnostics extend beyond line
2200 and describe a ten-record role-aware MRAM database rather than the sample
NVM model. That local delta must be reconstructed as G2 behavior; it must not
be attributed to the selected public commit.

## Authenticated stock boundary

The 64-shard source-path map anchors 50 functions and 29,110 body bytes across
the nine retained paths:

| Retained source | Anchored functions | Anchored bytes | Highest diagnostic line |
|---|---:|---:|---:|
| `common/app_db.c` | 22 | 14,996 | 2,256 |
| `app_master_leg.c` | 2 | 376 | 124 |
| `app_slave_leg.c` | 1 | 270 | 322 |
| `common/app_ui.c` | 3 | 2,512 | 202 |
| `app_master.c` | 4 | 1,522 | 933 |
| `app_server.c` | 1 | 296 | — |
| `app_slave.c` | 3 | 1,944 | 1,396 |
| `app_disc.c` | 11 | 6,186 | 1,130 |
| `app_main.c` | 3 | 1,008 | 556 |

The concatenated anchored stock bytes have SHA-256
`d00e4ff2b560f970cf23e00d80bf6701581574d14939f5d69843fe13310839e9`.
Each path also has an independent concatenated-body hash in the analyzer.
These are lower bounds: retained source paths attach only where diagnostics or
assertions leave ownership witnesses.

The focused audit therefore recovers the adjacent legacy master/slave objects
separately. `app_master_leg.c` has four linked functions / 454 bytes, and
`app_slave_leg.c` has ten linked functions / 952 bytes. That adds eleven
functions beyond the three path-anchored bodies in those two files. In the
slave object, stock cells `0x004B2DDC` and `0x004B2DE0` contain Thumb pointers
to `appSlaveLegAdvStop` and `appSlaveLegAdvRestart`. Three selected-source
definitions (`AppAdvSetAdValue`, `AppSetAdvPeerAddr`, and `AppConnAccept`) do
not appear in the linked stock cluster and are classified as source-only, not
missing OpenCFW behavior.

## Application-framework production closure

The complete 1,406-byte linked legacy cluster is now guarded at its 14 stock
entries and replaced by 14 isolated Cortex-M55 leaves. The maintained source
preserves the recovered fixed G2 ABI: master state `0x20071670`, slave state
`0x200719C8`, advertising/master configuration cells `0x2007434C` and
`0x20074354`, and the stored callback entries `0x004B2AFF` / `0x004B2B91`.
It also implements G2's extension beyond public AmbiqSuite: when controller
advertising mode is extended, legacy state transitions are retried through the
WSF timer at `0x20073DF4` with the pending flag at `0x20074F94`, using the
recovered 200 ms start/state delay and 100 ms stop retry.

The 14 leaves compile to 948 bytes with 29 strict relocations. Host tests cover
legacy/invalid scan mode, scan start/stop, connection open, callback identity,
advertising-data truncation, state sequencing, advertising type, directed
restart, successful extended-set termination, and every retry/timer branch.
All 14 selector-isolated builds pass with `-Werror`.

Four additional runtime modules close the remaining 25 anchors:

| Runtime module | Entries | Compiled bytes | Relocations | Replaced stock bytes |
|---|---:|---:|---:|---:|
| `runtime_cordio_app_core.c` | 7 | 488 | 10 | 3,816 |
| `runtime_cordio_app_master.c` | 4 | 262 | 6 | 1,522 |
| `runtime_cordio_app_slave.c` | 3 | 698 | 25 | 1,944 |
| `runtime_cordio_app_discovery.c` | 11 | 2,064 | 38 | 6,186 |

The core module owns UI action/passkey/confirmation, bond lookup, resolving-list
admission, connection-update timer start, and database-hash update behavior.
The master and slave modules own scan/address resolution, connection/security,
and DM-event processing. The discovery module owns configuration, service
search, ATT response parsing, handle-list state, completion, and database-hash
read progression. The two large stock discovery response parsers contain only
diagnostic expansion beyond their bounded state effects; the maintained source
implements the stateful behavior and bounded response validation without
reproducing diagnostics.

Together with the 22-function MRAM database closure, the five application
runtime modules production-own 61 distinct functions / 29,870 stock body bytes.
All 50 source-path anchors / 29,110 anchored bytes are routed, leaving zero
bounded framework anchors. The five runtime modules compile to 4,460 bytes
under 108 strict relocations. Host behavior tests and every selector-isolated
Cortex-M55 build pass with `-Werror`.

Canonical overlay/component/package identities are 424,732 / 3,948,128 /
4,726,622 bytes with SHA-256
`9f0dd0742bac903da275993e19c135a2508070a8baf4c462fb3d170a0a1272d9`,
`e3cfa30e77a5053d302aa3bc569cad39937d57c524c8e2e681923b70ad60b3a7`,
and `ecc49cd5b184fce9a6a25f71532eba7d1ee33ee566b131ec1b97b0a9536287d9`.
The source package rebuild is byte-identical. No image was signed or flashed.
This is bounded application-framework software closure, not firmware
functional-completeness evidence.

## OpenCFW disposition

The source family, public origin, selected release, selected commit, and
Packetcraft ancestor are closed. The historical private G2 commit remains
binary-unobservable. Every bounded source-path anchor is production-routed.
Live scanning, advertising, connection, controller transition, concurrency,
and paired-temple validation is explicitly blocked: the authorized right G2 is
nonresponsive and the left temple must remain stock. Hardware-dependent
functional completeness is therefore not claimed.

Reproduce the audit with:

```sh
make cordio-app-framework-lineage
```
