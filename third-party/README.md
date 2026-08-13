# Shared third-party dependencies

This directory is the single registry for every upstream dependency used by
either firmware target. It records what is depended on, at exactly which
revision, under which license, and which target consumes it.

Dependencies reach the build in one of two ways:

| Class | Where the source lives | How it is authenticated |
| --- | --- | --- |
| **Vendored snapshot** | [`../g2/third_party/<name>/`](../g2/third_party) | `verify_snapshot.py` per dependency, offline |
| **Fetched at build time** | a local cache directory you choose | [`fetched/verify_vendor.py`](fetched/verify_vendor.py) against [`fetched/manifest.json`](fetched/manifest.json) |

Nothing here is fetched implicitly. Both classes fail closed: a hash, commit,
tree, or file-set mismatch aborts the build rather than downgrading to a
warning.

## Why the vendored snapshots live under `g2/`

The vendored snapshots are physically stored at `g2/third_party/` rather than
in this directory. That is deliberate, not an oversight.

Each snapshot carries a self-referential integrity net that names its own
repository-relative path:

- `g2/third_party/*/PROVENANCE.json` records `third_party/<name>/...` paths that
  the verifiers resolve against the G2 tree root;
- several verifiers implement a *production-exclusion gate* that scans the G2
  `Makefile`, `manifests/`, and `components/` for the literal token
  `third_party/<name>` and fails closed unless the only matches are an exact
  allow-listed pair of lines (for example `NANOPB_DIR := third_party/nanopb`);
- 62 test modules verify the verifiers, and several pin the verifier script's
  exact byte size and SHA-256.

Relocating the directory would mean editing those paths and then re-pinning the
hashes that exist precisely to detect such edits — which would quietly retire
the byte-exactness guarantee that the G2 reconstruction rests on. The snapshots
stay put; this directory is the shared index over them.

The sharing is real rather than nominal: the R1 nRF52840 target already compiles
three of the G2 snapshots directly, via `../g2/third_party/...` in
[`../r1/platform/nrf52840/sdk/Makefile`](../r1/platform/nrf52840/sdk/Makefile).

## Vendored snapshots

Verified by `make third-party` from the repository root. All are pinned to an
exact upstream commit and reconstructed offline from the Git object closure.

| Dependency | Upstream pin | License | G2 | R1 |
| --- | --- | --- | :-: | :-: |
| `ambiqsuite-amota-profile` | `de5c6ba3` | BSD-3-Clause (Ambiq per-file) | • | |
| `ambiqsuite-ancc-profile` | `de5c6ba3` | BSD-3-Clause (Ambiq per-file) | • | |
| `ambiqsuite-apollo510` | `5efc0228` | BSD-3-Clause | • | |
| `ambiqsuite-cordio-app-framework` | `de5c6ba3` | Apache-2.0 | • | |
| `cmbacktrace` | `73714489` | MIT | • | • |
| `cmsis-core` | `d23a6949` | Apache-2.0 | • | |
| `cmsis-freertos` | v10.5.1 | Apache-2.0 | • | • |
| `cordio` | `3656312d` (r20.05c) | Apache-2.0 | • | |
| `cordio-profile-gatt` | see `SNAPSHOT.sha256` | Apache-2.0 | • | |
| `cJSON` | `3c893567` (v1.7.12; proven interval v1.7.9–v1.7.12) | MIT | • | |
| `easylogger` | `a596b264` | MIT | • | |
| `flashdb` | `714d6159` (2.1.1) | Apache-2.0 | • | |
| `freertos-kernel` | `def7d2df` (V10.5.1) | MIT | • | • |
| `freertos-plus-cli` | `43defa56` | MIT | • | |
| `freetype` | 2.9.1 | FTL | • | |
| `goodix-gr551x-app-error` | see `PROVENANCE.json` | BSD-3-Clause (Goodix per-file) | • | |
| `liblc3` | `96a3af0b` | Apache-2.0 | • | |
| `littlefs` | `0494ce71` (v2.10.1) | BSD-3-Clause | • | |
| `lvgl` | `344c7c31` (9.3-dev) | MIT | • | |
| `lz4` | `ebb370ca` (1.10.0) | BSD-2-Clause | • | |
| `nanopb` | `98bf4db6` (0.4.9) | Zlib | • | |
| `npmx` | `e1aaec53` | BSD-3-Clause | • | |
| `packetcraft-gatt-profile` | `3656312d` | Apache-2.0 | • | |
| `ring-buffer` | `190e30be` | MIT | • | |
| `tinyframe` | `eb75483e` | MIT | • | |
| `tlsf` | see `SNAPSHOT.sha256` | BSD-3-Clause | • | |

A `•` in the R1 column means the R1 nRF52840 target compiles that snapshot
directly out of `g2/third_party/` — currently CMSIS-FreeRTOS, FreeRTOS-Kernel,
and CmBacktrace, which `verify_vendor.py` also re-authenticates during the R1
vendor audit. Everything else is G2-only today. Note that R1 uses FlashDB too,
but takes it from the fetched set rather than from this snapshot.

Many snapshots are **production-excluded**: authenticated and retained as
attribution evidence, but not linked into any shipped image. Each dependency's
`README.openCFW.md` states its own status. Do not infer from this table that a
dependency is compiled in.

## Fetched dependencies

[`fetched`](fetched) covers upstreams that are not redistributable here —
principally the Nordic nRF5 SDK and the sensor-vendor SensorAPIs. They are
downloaded into a cache directory of your choosing, checked against pinned
archive hashes, and then authenticated file-by-file.

```sh
third-party/fetched/fetch.sh /absolute/path/to/vendor-cache
```

The script refuses relative paths, verifies each archive's SHA-256 before
unpacking, skips anything already present, and finishes by running
`verify_vendor.py` over the whole set. See [`fetched/README.md`](fetched/README.md)
for the per-dependency roots and the environment variables the R1 build expects.

## Vendor firmware blobs

The official Even Realities OTA payloads that the G2 reconstruction is verified
against are vendor-proprietary and are **not** in this repository.
[`../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md)
records their origin and SHA-256 digests so a local copy can be reproduced and
checked. Place them at the path that file names before running any G2 target
beyond `make reference`'s prerequisites.
