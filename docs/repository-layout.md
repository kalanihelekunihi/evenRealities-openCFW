# Repository layout

The tree is organized around one rule: **each firmware target owns everything
that is specific to it, and nothing that is not.** Two devices, two directories,
one shared dependency registry, one build entry point.

```
openCFW/
├── Makefile  make.sh        unified build entry point
├── docs/                    cross-target documentation (this directory)
├── g2/                      everything G2-specific
├── r1/                      everything R1-specific
└── third-party/             shared dependency registry
```

Every directory that holds more than a handful of files carries a `README.md`
that says what is in it and how to navigate it — `g2/tools/`, `g2/docs/`,
`g2/research/`, `r1/docs/`, `r1/tools/`, `r1/research/`, `third-party/`, and
this directory. Where the filesystem cannot be reorganized (see below), that
index *is* the organization.

The repository is self-contained: each target carries its own evidence and the
tooling that produced it, and every claim is checkable with `make verify`.

## Why targets are separated

G2 and R1 share no code, and their reconstruction strategies are not comparable:

- **G2** starts from the official image and works inward. Its build is a
  *packaging* operation — reconstruct the flash layout byte-for-byte, then swap
  reconstructed regions for compiled overlays and prove the result still matches
  the reviewed layout. Correctness means *identical bytes*.
- **R1** starts from recovered behavior and works outward. Its build is an
  ordinary C build. Correctness means *the observable contract holds*, verified
  by host tests and against function-level correlation records.

Putting them in one flat tree, as the previous layout did, forced a reader to
know which of `components/`, `manifests/`, `platform/`, `src/`, and `vendor/`
belonged to which device. The split removes that question entirely.

## `g2/` — Even Realities G2

A verbatim, self-contained G2 tree. Everything resolves relative to `g2/`, so
the directory can be entered and built directly:

```sh
make -C g2 build
```

| Path | Contents |
| --- | --- |
| `blobs/` | provenance for the official OTA payloads; the payloads themselves are vendor-proprietary and untracked |
| `components/` | overlay sources compiled into the image, split by image (`apollo_main`, `bootloader`) and by shared upstream (`shared/`) |
| `docs/` | G2 memory map, source coverage, upstream inventory, reproducible-build notes, and per-closure research audits |
| `manifests/` | per-profile region and flash-layout pins |
| `releases/` | published release definitions |
| `research/` | reverse-engineering evidence: source candidates, per-module readiness matrices, and the decompilation corpus — see [`../g2/research/README.md`](../g2/research/README.md) |
| `tests/` | 736 modules gating every claim the build makes |
| `third_party/` | vendored upstream snapshots — see [below](#third-party-shared-dependency-registry) |
| `tools/` | image analyzers, evidence manifests, overlay builder, packager |

`g2/README.md` and `g2/docs/*.md` are **SHA-256 pinned** by the test suite
(`tests/test_runtime_nanopb_decode_svarint_production.py` and
`tests/test_runtime_nanopb_decode_varint32_production.py`). Editing them without
re-pinning turns those tests red. This is intentional: those documents are part
of the evidence record, not free-form prose. One consequence is that
`g2/README.md` still spells the build directory `openCFW`; read it as `g2`.

## `r1/` — Even Realities R1

| Path | Contents |
| --- | --- |
| `docs/` | orientation: status, security posture, provenance, source-admission policy |
| `docs/correlation/` | one record per subsystem, pinning recovered behavior to the stock image |
| `docs/boundaries/` | one record per licensed-provider seam, stating what stays gated |
| `docs/closures/` | Nordic SDK closure proofs |
| `docs/reference/` | function ownership, coverage, remaining frontier, BSim run summaries |
| `include/openr1/` | public headers |
| `src/` | portable, platform-independent implementation |
| `platform/nrf52840/` | platform layer, linker script, and the Nordic SDK application under `sdk/` |
| `port/` | R1-owned FlashDB/FAL port and its configuration headers |
| `tests/` | host protocol tests plus vendor storage and crypto tests |
| `research/` | the decompilation corpus, bootloader reconstruction, and BSim runs — see [`../r1/research/README.md`](../r1/research/README.md) |
| `tools/` | the evidence toolchain: ~220 pinning scripts, simulator, and verifiers — see [`../r1/tools/README.md`](../r1/tools/README.md) |

`port/` was previously `vendor/`, which mixed two unrelated things: R1-authored
adapter code, and bookkeeping for external dependencies. The adapter code is
R1's own and stayed; the dependency bookkeeping moved to
`third-party/fetched/`.

## `third-party/` — shared dependency registry

The inventory of every upstream either target depends on, with its pin, license,
and consuming target: [`../third-party/README.md`](../third-party/README.md).

Dependencies arrive two ways. **Fetched** dependencies — the Nordic SDK, the
sensor-vendor SensorAPIs — are not redistributable; `third-party/fetched/` holds
their manifest, fetch script, and authenticator. **Vendored** snapshots are
committed, and live at `g2/third_party/`.

That last point is the one asymmetry in this layout, and it is load-bearing
rather than incidental. Each vendored snapshot authenticates its own
repository-relative path: `PROVENANCE.json` files name `third_party/<name>/...`
paths, several verifiers scan the G2 `Makefile` and `manifests/` for the literal
string `third_party/<name>` as a production-exclusion gate, and 61 test modules
verify the verifiers — some by pinning the verifier script's exact byte size and
SHA-256. Moving the directory means editing those paths and then re-pinning the
hashes whose entire purpose is to detect such edits. The snapshots stay where
their own provenance says they are; `third-party/` indexes them.

The sharing is not hypothetical: `r1/platform/nrf52840/sdk/Makefile` compiles
CMSIS-FreeRTOS, FreeRTOS-Kernel, and CmBacktrace straight out of
`../g2/third_party/`, and `third-party/fetched/verify_vendor.py` authenticates
those same three snapshots as part of the R1 vendor audit.

## Where to put new things

| You are adding | It goes in |
| --- | --- |
| a G2 overlay source file | `g2/components/apollo_main/` or `.../bootloader/`, plus a test in `g2/tests/` |
| a G2 image analyzer | `g2/tools/`, plus its evidence maps in `g2/tools/manifests/` |
| G2 evidence a new analyzer reads | `g2/research/` — unpacked, filed by subject, then `make -C g2 research-corpus` to re-index |
| an R1 subsystem | `r1/src/` with its header in `r1/include/openr1/`, plus a record in `r1/docs/correlation/` |
| an R1 licensed-provider seam | the adapter in `r1/src/`, the gate description in `r1/docs/boundaries/` |
| R1 nRF52840 glue | `r1/platform/nrf52840/sdk/` |
| a new vendored upstream | `g2/third_party/<name>/` with `PROVENANCE.json` and `verify_snapshot.py`; add a row to `third-party/README.md` |
| a new fetched upstream | a component entry in `third-party/fetched/manifest.json`, a block in `fetch.sh`, and a check in `verify_vendor.py` |
| documentation about one target | that target's `docs/` |
| documentation about the repository | this directory |

## What is deliberately absent

- **Build output.** No `build/`, `_build/`, `build-*/`, object files, or
  `__pycache__`. Everything is regenerable by `make`.
- **Vendor firmware payloads.** The official G2 OTA binaries are
  vendor-proprietary. Their provenance and hashes are tracked; the bytes are not.
- **Recorded manifest and overlay variants.** `*-record*.json` files under
  `g2/manifests/` and `g2/components/` are compiler-profile replay artifacts,
  explicitly documented in the verifiers as non-canonical build inputs.
- **Compiled binaries inside evidence.** `emit_image`, `rebuilt-*.bin`, and the
  Nordic bootloader build tree are regenerated by their own makefiles and
  authenticated on the way out.
- **Vendor firmware byte arrays.** The R1 reconstruction under
  `r1/research/decompilation/rebuild/` embeds the stock images as C arrays.
  Those are the vendor firmware in another encoding, so the same policy applies
  as for the G2 payloads: the reconstruction, manifest and verifier are tracked;
  the arrays are supplied locally.
- **Large rebuildable trees.** The 108 MB Nordic bootloader build tree under
  `r1/research/bootloader-reconstruction/` is not tracked; its project is.

### What looks removable but is not

`g2/research/` is 100 MB of Ghidra logs, compiler-matrix object files, and SDK
comparison reports. It looks like archived tool output. It is not: the Cordio
and EM9305 analyzers hash-check it, so roughly two dozen tests fail closed
without it. Its files share extensions with build output (`.log`, `.o`, `.elf`),
which is why `.gitignore` carries an explicit `!/g2/research/**` un-ignore.

Two rules follow, and both have already caught real mistakes:

1. **Grep before deleting.** Much of this repository's evidence is stored as
   data files rather than code. Check `g2/tools/` and `g2/tests/` for a filename
   before assuming it is leftover.
2. **Never run a text transform across `g2/research/corpus/` or
   `g2/research/readiness/`.** Those bytes are the delivered evidence, and their
   digests are pinned. A repo-wide "fix all the markdown links" pass will
   silently corrupt the `final.md` lane transcripts. Exclude the evidence tree
   from any bulk edit; `make -C g2 research-corpus` is what catches it.
