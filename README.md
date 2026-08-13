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
| Output | flashable `.evenota` package, byte-identical to reference | portable host build, freestanding Cortex-M4 objects, linked nRF52840 image |

They share a dependency registry, a verification philosophy, and a single build
entry point. They do not share code.

## What this is, and is not

**G2** is not yet a clean-room replacement firmware. It is a build boundary that
reproduces the official image byte-for-byte, then replaces reconstructed regions
with compiled source one closure at a time. Five non-Apollo components and most
of the Apollo application remain opaque. Coverage is measured, not estimated —
see [`g2/docs/source-coverage.md`](g2/docs/source-coverage.md).

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
│   ├── docs/             reference documents + 502 per-closure audits
│   ├── manifests/        region/flash layout pins per build profile
│   ├── research/         evidence corpus: candidates, readiness, decompilation
│   ├── tests/            736 test modules gating the above
│   ├── third_party/      vendored upstream snapshots (see third-party/README.md)
│   └── tools/            4 entry points + 355 read-only analyzers
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

The repository is self-contained. Each target carries its own evidence and the
tooling that produced it, so every claim in the documentation can be regenerated
here — nothing points at another checkout.

## Quick start

```sh
./make.sh help
```

The R1 portable target needs only a C11 compiler and builds immediately:

```sh
./make.sh r1-test
./make.sh r1-sanitize
```

The G2 target additionally needs Python 3.9+, POSIX `make`, and the reviewed
Clang release family; it also needs the official OTA payloads, which are
vendor-proprietary and not distributed here. Put them where
[`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](g2/blobs/official/g2-2.2.6.10/PROVENANCE.md)
says, then:

```sh
./make.sh g2-build
```

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
| [`r1/README.md`](r1/README.md) | R1 status, implemented contract, open gaps |
| [`r1/docs/README.md`](r1/docs/README.md) | R1 evidence provenance and remaining hardware work |
| [`g2/tools/README.md`](g2/tools/README.md) | which G2 script to run, and what the 355 analyzers are |
| [`g2/docs/README.md`](g2/docs/README.md) | which G2 document answers which question |
| [`g2/research/README.md`](g2/research/README.md) | the G2 evidence corpus and how it is authenticated |
| [`r1/tools/README.md`](r1/tools/README.md) | the R1 evidence toolchain and how to reproduce any claim |
| [`r1/research/README.md`](r1/research/README.md) | the R1 decompilation corpus and image reconstruction |

## Licensing

Vendored upstream code retains its own license; each dependency under
`g2/third_party/` carries its upstream license text and a `PROVENANCE.json`
recording the exact commit it was taken from. Per-component attribution for
compiled overlays is in the `NOTICE.md` and `LICENSE-*` files under
[`g2/components`](g2/components). Official Even Realities firmware payloads are
vendor-proprietary and are not redistributed.
