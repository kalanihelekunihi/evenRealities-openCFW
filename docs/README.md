# Documentation

Documentation is split the same way the code is: cross-target material lives
here, and everything specific to a device lives with that device.

## Cross-target (this directory)

| Document | Read it when |
| --- | --- |
| [`repository-layout.md`](repository-layout.md) | you need to find something, or decide where new work belongs |
| [`build.md`](build.md) | you are building, or a build failed and you want to know which gate fired |
| [`methodology.md`](methodology.md) | you want to know what "verified" means here, and what the project refuses to claim |

## G2 — [`../g2/docs`](../g2/docs)

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
| [`../r1/docs/correlation`](../r1/docs/correlation) | one record per subsystem, pinning recovered behavior to the stock image: exact addresses, byte counts, record layouts, and how the reimplementation corresponds | 75 |
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
