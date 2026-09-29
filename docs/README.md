# Documentation

Documentation is split the same way the code is: cross-target material lives
here, and everything specific to a device lives with that device.

For new G2 work, start with the [active pseudocode-first workflow](../g2/workflow/README.md).
The consolidated reference documents listed below replace the scattered
campaign records as the place to look up facts. The older G2 coverage and build
documents describe historical hybrid-overlay evidence. They do not override the
requirement to freeze the whole pseudocode corpus first.

## Cross-target (this directory)

| Document | Read it when |
| --- | --- |
| [`repository-layout.md`](repository-layout.md) | you need to find something, or decide where new work belongs |
| [`build.md`](build.md) | you are building, or a build failed and you want to know which gate fired |
| [`methodology.md`](methodology.md) | you want to know what "verified" means here, and what the project refuses to claim |
| [`tooling.md`](tooling.md) | you are setting up decompilation, byte-matching, emulation or debug tools |
| [`hardware/README.md`](hardware/README.md) | you need a part number, bus, pin, data rate, protocol, FCC record or datasheet |

## Hardware — [`hardware/`](hardware)

| Document | Contents |
| --- | --- |
| [`hardware/g2-glasses.md`](hardware/g2-glasses.md) | G2 system overview, IC table, buses and pads, inter-processor links, display/audio/power |
| [`hardware/g2-case.md`](hardware/g2-case.md) | charging case MCU, power parts, UART framing, dual-bank update |
| [`hardware/r1-ring.md`](hardware/r1-ring.md) | R1 pin and bus map, sensors, PMIC single-wire link, NFC charging |
| [`hardware/regulatory.md`](hardware/regulatory.md) | FCC IDs (grantee 2BFKR), exhibits, RF test data, ISED/Japan numbers |
| [`hardware/components/`](hardware/components) | one page per identified IC: datasheet links, key specs, SVD source |
| [`hardware/sources.md`](hardware/sources.md) | bibliography of every external source |

## G2 — [`../g2/docs`](../g2/docs)

Index: [`../g2/docs/README.md`](../g2/docs/README.md). Tools: [`../g2/tools/README.md`](../g2/tools/README.md).

Active procedure and prompts: [`../g2/workflow/README.md`](../g2/workflow/README.md).

Consolidated reference (start here for facts):

| Document | Contents |
| --- | --- |
| [`../g2/docs/reference/firmware-formats.md`](../g2/docs/reference/firmware-formats.md) | EVENOTA, component headers, CRC variants, per-payload wrappers |
| [`../g2/docs/reference/memory-map.md`](../g2/docs/reference/memory-map.md) | per-processor memory maps and load addresses |
| [`../g2/docs/reference/toolchains.md`](../g2/docs/reference/toolchains.md) | original compilers and runtimes; open questions blocking byte equality |
| [`../g2/docs/reference/libraries.md`](../g2/docs/reference/libraries.md) | identified upstream libraries, versions, recovered configuration |
| [`../g2/docs/reference/protocols.md`](../g2/docs/reference/protocols.md) | phone, inter-processor, case, touch, codec and ring protocols |
| [`../g2/docs/reference/capabilities.md`](../g2/docs/reference/capabilities.md) | capability checklist for pseudocode review coverage |
| [`../g2/docs/reference/hardware-validation-notes.md`](../g2/docs/reference/hardware-validation-notes.md) | on-device observations and safety cautions |
| [`../g2/symbols/README.md`](../g2/symbols/README.md) | naming seeds per payload |
| [`../g2/config-recovered/README.md`](../g2/config-recovered/README.md) | recovered upstream configuration headers and patches |

Historical campaign records:

| Document | Contents |
| --- | --- |
| [`../g2/README.md`](../g2/README.md) | current status, build profiles, per-dependency snapshot posture |
| [`../g2/docs/source-coverage.md`](../g2/docs/source-coverage.md) | exactly which functions are compiled from source |
| [`../g2/docs/memory-map.md`](../g2/docs/memory-map.md) | recovered flash and RAM layout |
| [`../g2/docs/upstream-inventory.md`](../g2/docs/upstream-inventory.md) | upstream-first attribution queue and configuration gaps |
| [`../g2/docs/linux-reproducible-build.md`](../g2/docs/linux-reproducible-build.md) | reproducing the pinned builds on Linux |
| [`../g2/docs/research`](../g2/docs/research) | per-closure source-boundary and candidate audits |
| [`../g2/research/README.md`](../g2/research/README.md) | the raw evidence those audits are built on |

`../g2/README.md` and the four `../g2/docs/*.md` documents above are SHA-256
pinned by the G2 test suite. They are evidence records; edit them only with the
matching re-pin. One visible consequence: `../g2/README.md` still refers to the
build directory as `openCFW`, which is now `g2`.

## R1 — [`../r1/docs`](../r1/docs)

Consolidated reference (start here for facts):

| Document | Contents |
| --- | --- |
| [`../r1/docs/memory-map.md`](../r1/docs/memory-map.md) | flash/RAM/UICR layout, partitions, image hashes, rebuild oracle |
| [`../r1/docs/toolchain-and-dependencies.md`](../r1/docs/toolchain-and-dependencies.md) | stock SDK/library identities, Arm Compiler evidence, byte-equality blockers |
| [`../r1/docs/protocol.md`](../r1/docs/protocol.md) | BLE services, framing, CRCs, command dispatch |
| [`../r1/docs/storage-formats.md`](../r1/docs/storage-formats.md) | persistent record formats |
| [`../r1/docs/hardware-pinout.md`](../r1/docs/hardware-pinout.md) | pins, buses, ADC channels, peripheral addresses |
| [`../r1/docs/security-and-bootloader.md`](../r1/docs/security-and-bootloader.md) | DFU trust model and stock defects a faithful build must keep |
| [`../r1/docs/hardware-observations.md`](../r1/docs/hardware-observations.md) | field versions and physical measurements |
| [`../r1/config-recovered/README.md`](../r1/config-recovered/README.md) | configuration seeds, stock-proven vs. openR1 choices |

Clean-room openR1 records (historical; not byte-identical):

| Document | Contents |
| --- | --- |
| [`../r1/README.md`](../r1/README.md) | implemented contract, provider gates, remaining hardware work |
| [`../r1/docs/README.md`](../r1/docs/README.md) | evidence provenance, coverage, safety differences, analysis-tooling note |
| [`../r1/docs/SOURCE-ADMISSION.md`](../r1/docs/SOURCE-ADMISSION.md) | what may be admitted as vendor source, and on what evidence |
| [`../r1/docs/SECURITY.md`](../r1/docs/SECURITY.md) | security posture and intentional differences from stock |
| [`../r1/docs/PROVENANCE.md`](../r1/docs/PROVENANCE.md) | where the recovered evidence came from |

Those four orient a reader. Everything below them is filed by document kind:

| Directory | Kind | Count |
| --- | --- | ---: |
| [`../r1/docs/correlation`](../r1/docs/correlation) | one record per subsystem, pinning recovered behavior to the stock image: exact addresses, byte counts, record layouts, and how the reimplementation corresponds | 80 |
| [`../r1/docs/boundaries`](../r1/docs/boundaries) | one record per licensed-provider seam — what the R1-owned adapter implements, and what stays disabled until that provider is supplied | 29 |
| [`../r1/docs/closures`](../r1/docs/closures) | Nordic SDK closure proofs | 5 |
| [`../r1/docs/reference`](../r1/docs/reference) | function ownership, coverage, remaining frontier, and BSim run summaries under `reference/bsim/` | 9 |

Start with `correlation/` to understand what the firmware does, and
`boundaries/` to understand what it deliberately refuses to do.

## Dependencies — [`../third-party`](../third-party)

| Document | Contents |
| --- | --- |
| [`../third-party/README.md`](../third-party/README.md) | every upstream: pin, license, consuming target, vendored vs fetched |
| [`../third-party/fetched/README.md`](../third-party/fetched/README.md) | fetching and authenticating the non-redistributable upstreams |

Each vendored dependency additionally carries its own `README.openCFW.md` under
`../g2/third_party/<name>/`, stating where the upstream boundary sits and
whether the snapshot is production-excluded.
