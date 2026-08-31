# openCFW

Open, source-controlled firmware for Even Realities hardware.

`openCFW` covers two independent devices, each with its own silicon, toolchain,
and reconstruction strategy:

| | [`g2`](g2) | [`r1`](r1) |
| --- | --- | --- |
| Device | G2 smart glasses | R1 smart ring |
| Application MCU | Ambiq Apollo510 (Cortex-M55) | Nordic nRF52840 (Cortex-M4F) |
| Approach | byte-exact reconstruction of the stock image, then incremental source replacement | clean-room reimplementation of the observable firmware contract |
| Reference version | `s200_v2.2.6.10` | `2.2.6.0009` |
| Output | locally buildable hybrid `.evenota`; public stock-bearing binary release remains fail-closed, while hardware qualification is deferred by project direction | portable host build, freestanding Cortex-M4 objects, linked nRF52840 image |

They share a dependency registry, a verification philosophy, and a single build
entry point. They do not share code.

## What this is, and is not

**G2** is not yet a clean-room replacement firmware. It is a build boundary that
reproduces the official image byte-for-byte, then replaces reconstructed regions
with compiled source one closure at a time. The checked-in completion assessment
is the authoritative live classification of source-owned, retained, unresolved,
and container-only bytes; prose milestone lists are historical context rather
than a substitute for that machine-checked boundary. Coverage is measured, not
estimated — see [`g2/docs/source-coverage.md`](g2/docs/source-coverage.md).

**R1** is a clean-room C implementation derived from recovered protocol,
behavioral, memory, and security-audit evidence. It is not reconstructed vendor
source and is not byte-identical to the stock image. Vendor-attributable
functionality comes from pinned upstream sources; clean-room code is limited to
R1-specific behavior, configuration, ports, and safety corrections.

Neither target fabricates behavior it cannot attribute. Where a licensed
provider is missing — Goodix biometrics, GoMore health algorithms, the YHM power
path — the boundary returns an explicit "unsupported" rather than inventing
plausible data.

## Layout

```
openCFW/
├── Makefile              unified entry point; dispatches to each target
├── make.sh               run the above from any directory
├── docs/                 cross-target documentation
│   ├── repository-layout.md
│   ├── build.md
│   └── methodology.md
├── g2/                   G2 firmware: reconstruction + source overlays
│   ├── Makefile          profiles, snapshot verifiers, closure audits
│   ├── blobs/            official OTA provenance (payloads not redistributed)
│   ├── components/       compiled overlay sources, per component
│   ├── docs/             reference documents + per-closure audits
│   ├── manifests/        region/flash layout pins per build profile
│   ├── research/         evidence corpus: candidates, readiness, decompilation
│   ├── tests/            regression modules gating the above
│   ├── third_party/      vendored upstream snapshots (see third-party/README.md)
│   └── tools/            build/release entry points + analyzers
├── r1/                   R1 firmware: clean-room implementation
│   ├── Makefile          host, sanitizer, freestanding, verify, SDK-image
│   ├── docs/             correlation/ boundaries/ closures/ reference/
│   ├── include/openr1/   public headers
│   ├── src/              portable implementation
│   ├── platform/         nRF52840 platform layer and Nordic SDK integration
│   ├── port/             R1-owned FlashDB/FAL port and configuration
│   ├── research/         decompilation corpus, image reconstruction, BSim runs
│   ├── tests/            host, storage, and crypto tests
│   └── tools/            verifiers + evidence/ probes/ ghidra_scripts/
└── third-party/          shared dependency registry
    ├── README.md         full inventory: pin, license, consuming target
    └── fetched/          non-redistributable upstreams: manifest, fetch, verify
```

Every directory large enough to need one carries a `README.md` index —
[`g2/tools/`](g2/tools/README.md), [`g2/docs/`](g2/docs/README.md),
[`g2/research/`](g2/research/README.md), [`r1/docs/`](r1/docs/README.md),
[`r1/tools/`](r1/tools/README.md), [`r1/research/`](r1/research/README.md),
[`third-party/`](third-party/README.md).

The repository carries the source-audit evidence and tooling without depending
on another project checkout. Inputs deliberately excluded for licensing remain
external: stock-bearing G2 builds require locally authorized official payloads,
and R1 SDK-image workflows require their separately fetched, pinned vendor roots.

## Quick start

```sh
./make.sh help
```

The R1 portable target needs only a C11 compiler and builds immediately:

```sh
./make.sh r1-test
./make.sh r1-sanitize
```

The G2 target additionally needs Python 3.9+, GNU `make`, and the reviewed
Clang release family. Stock-bearing build, local hydration, and extracted-tree
smoke targets also need the official OTA payloads, which are vendor-proprietary
and excluded from the verified community source ZIP; source-bundle creation and
other source-only audits do not.

> **Release warning:** The verified official-payload-free ZIP is the
> history-free public artifact. The existing Git history retains 52
> `g2/.tmp-*` paths and descendants totaling 108,601,986 bytes, including
> official-derived firmware variants. That set contains the now-deleted exact
> official-payload copies `g2/.tmp-pt-working-base.bin` and
> `g2/.tmp-pt-working-base-linux.bin` (SHA-256
> `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`). Do
> not publish or mirror that history as-is. Use the verified ZIP or a separately
> audited clean-history export; rewriting the private history requires separate
> authorization.

Put locally authorized inputs where
[`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](g2/blobs/official/g2-2.2.6.10/PROVENANCE.md)
says, then:

```sh
./make.sh g2-build
```

To create the public, official-payload-free G2 community source archive instead:

```sh
./make.sh g2-community-source
```

The archive contains source, build recipes, manifests, and applicable license
texts, but no official firmware or raw stock patch guards. A recipient supplies
their own authenticated `s200_v2.2.6.10` package locally; the preparation tool
validates all six payload identities before the software-only build. Run
`./make.sh g2-community-smoke` to repeat that workflow in a fresh extracted
tree without signing, flashing, or hardware access. See the
[community distribution guide](g2/docs/community-source-distribution.md) and
[release licensing inventory](g2/docs/release-licensing-and-redistribution.md).
Public distribution of a generated stock-bearing firmware binary remains
fail-closed until redistribution authority for all six payloads is documented.

Full details, including the R1 vendor SDK fetch, are in
[`docs/build.md`](docs/build.md).

## Documentation

| Document | Covers |
| --- | --- |
| [`docs/repository-layout.md`](docs/repository-layout.md) | why the tree is shaped this way; where to add things |
| [`docs/build.md`](docs/build.md) | prerequisites, every target, verification model |
| [`docs/methodology.md`](docs/methodology.md) | evidence, attribution, and what "verified" means here |
| [`third-party/README.md`](third-party/README.md) | dependency inventory and pinning policy |
| [`g2/README.md`](g2/README.md) | G2 status, current source coverage, build profiles |
| [`g2/docs/community-source-distribution.md`](g2/docs/community-source-distribution.md) | create, verify, hydrate, and smoke-test the official-payload-free G2 source archive |
| [`g2/docs/release-licensing-and-redistribution.md`](g2/docs/release-licensing-and-redistribution.md) | live mixed-license source inventory and fail-closed binary authority boundary |
| [`r1/README.md`](r1/README.md) | R1 status, implemented contract, open gaps |
| [`r1/docs/README.md`](r1/docs/README.md) | R1 evidence provenance and remaining hardware work |
| [`g2/tools/README.md`](g2/tools/README.md) | which G2 script to run, and how the G2 analyzers are organized |
| [`g2/docs/README.md`](g2/docs/README.md) | which G2 document answers which question |
| [`g2/research/README.md`](g2/research/README.md) | the G2 evidence corpus and how it is authenticated |
| [`r1/tools/README.md`](r1/tools/README.md) | the R1 evidence toolchain and how to reproduce any claim |
| [`r1/research/README.md`](r1/research/README.md) | the R1 decompilation corpus and image reconstruction |

## Community

Contributions must preserve the clean-room, provenance, and mixed-license
boundaries described in [CONTRIBUTING.md](CONTRIBUTING.md). Community behavior,
private vulnerability reporting, and support expectations are documented in
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [SECURITY.md](SECURITY.md), and
[SUPPORT.md](SUPPORT.md).

## Licensing

openCFW-authored software and documentation without a more specific license are
available under the [MIT License](LICENSE). The repository-wide
[licensing boundary](NOTICE) also grants an MIT option for original
openCFW-owned contributions that were previously marked GPL solely because they
were aggregated with a GPL component. The current project-owned normalization
census is complete; upstream-derived files retain their applicable terms.

Vendored and adapted upstream code retains its upstream license; each dependency
under `g2/third_party/` carries its applicable license text and a provenance
record identifying its source. Files with an SPDX identifier or a component
license remain under those stated terms. Per-component attribution for compiled
overlays is in the `NOTICE.md` and `LICENSE-*` files under
[`g2/components`](g2/components).

Official Even Realities firmware payloads, retained proprietary compatibility
bytes, and captured vendor artifacts are not covered by the root MIT grant.
They are excluded from the verified community source ZIP; the existing private
development history contains tracked donor/build artifacts and must not be
published or mirrored as the community distribution.

The g2flash-derived gesture and patch sources and the upstream QP/C sources
remain GPL-covered. Firmware binaries combining them with MIT components must
be distributed in compliance with the applicable GPL terms.
