# Building openCFW

Both targets are driven from the repository root:

```sh
./make.sh help
```

`make.sh` is a thin wrapper that runs `make` against the repository root from
any working directory. Everything it exposes can also be run per target with
`make -C g2 <target>` or `make -C r1 <target>`.

Every build in this repository **fails closed**. A mismatched hash, checksum,
vector table, region partition, protected boundary, or commit pin aborts the
build. There is no flag that downgrades a verification failure to a warning; if
you need to inspect a mismatch, inspect the failing artifact, not the gate.

## Prerequisites

| | G2 | R1 (portable) | R1 (nRF52840 image) |
| --- | :-: | :-: | :-: |
| Python 3.9+ | required | — | for `sdk-verify` |
| POSIX `make` + shell | required | required | required |
| C compiler (`cc`) | — | required | — |
| Clang, reviewed release family | required | for `sanitize` / `arm-objects` | — |
| Arm GNU toolchain | — | — | required |
| Official G2 OTA payloads | for stock-bearing build, hydration, and smoke targets | — | — |
| Fetched Nordic SDK + sensor SDKs | — | — | required |

G2 pins compiled overlays byte-for-byte per reviewed toolchain profile. On macOS
that resolves to Apple Clang and the `apple-clang` profile; on Linux it resolves
to a present Clang and that Clang's recorded reproducible profile. Check what
was selected:

```sh
make -C g2 toolchain
```

Override only with a compiler in the same release family — the reviewed builds
use Apple Clang 21.0.0, including the compiler shipped with Xcode 26.6.0:

```sh
make -C g2 build OPENCFW_CLANG=/path/to/clang OPENCFW_TOOLCHAIN_PROFILE=<id>
```

Linux specifics are in
[`../g2/docs/linux-reproducible-build.md`](../g2/docs/linux-reproducible-build.md).

## Supplying the inputs that are not redistributed

### G2 firmware payloads

The official Even Realities OTA payloads are vendor-proprietary. Their origin
and SHA-256 digests are recorded in
[`../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md`](../g2/blobs/official/g2-2.2.6.10/PROVENANCE.md).
For a stock-bearing checkout build or the extracted-tree smoke target, place
your own copies at the paths that file names —
`g2/blobs/official/g2-2.2.6.10/`. The local hydration command instead accepts
the exact official outer package at a caller-selected path and installs its six
authenticated payloads into the extracted workspace. Source-bundle creation,
toolchain inspection, and source-only audits do not require these payloads.
Every target that uses a package or payload verifies its hash first.

### R1 vendor SDKs

```sh
third-party/fetched/fetch.sh /absolute/path/to/vendor-cache
```

This downloads the fetchable dependencies, checks each archive's SHA-256 before
unpacking, and finishes by authenticating the whole set. The per-dependency root
variables the R1 build expects are listed in
[`../third-party/fetched/README.md`](../third-party/fetched/README.md).

## Building G2

```sh
./make.sh g2-build          # all three profiles
```

Three profiles are produced, each verified byte-identical to its own reviewed
profile identity:

| Profile | Target | What it is |
| --- | --- | --- |
| reference | `make -C g2 reference` | blob-only reconstruction of the stock image; compiler-independent |
| ring-source | `make -C g2 ring-source` | the preserved first ring-source milestone |
| source | `make -C g2 source` | the current source-divergent build, with the compiled Apollo overlay |

Each prints the package size, its SHA-256, `reference: byte-identical`, and the
placed/unresolved flash-region counts. The `source` profile additionally reports
the overlay and component digests.

Other useful G2 targets:

```sh
./make.sh g2-community-source # official-payload-free deterministic source archive
./make.sh g2-community-smoke  # hydrate/build in a fresh extracted archive
make -C g2 vendor-snapshots   # authenticate every vendored upstream, offline
make -C g2 upstream-audits    # read-only closure audits over the stock image
make -C g2 verify             # build + upstream audits
make -C g2 test               # the full test suite
make -C g2 inspect            # inspect the built source package
make -C g2 clean
```

The community targets do not redistribute the required official payload. The
bundle contains source, recipes, manifests, and license texts; its local
preparation step authenticates a recipient-supplied `s200_v2.2.6.10` package.
The smoke target performs only filesystem/compiler work and never signs,
flashes, resets, or contacts hardware. See
[`../g2/docs/community-source-distribution.md`](../g2/docs/community-source-distribution.md).

The Makefile also exposes roughly two hundred per-closure targets — one per
subsystem under analysis (`make -C g2 lvgl-snapshot`,
`make -C g2 cordio-aggregate-closure`, `make -C g2 service-audio-closure`, and
so on). `make -C g2 -pn | grep '^[a-z].*:'` lists them.

## Building R1

The portable implementation needs nothing beyond a C11 compiler:

```sh
./make.sh r1-test           # host protocol/device tests
./make.sh r1-sanitize       # the same under ASan + UBSan
./make.sh r1-arm            # freestanding Cortex-M4 objects
./make.sh r1-sim            # host simulator
```

The simulator answers EUS requests as BLE values:

```sh
r1/build/openr1_sim 01 get
```

Mutating requests require a final `authorized` argument.

With the fetched vendor roots present, the linked nRF52840 application builds
and verifies:

```sh
make -C r1 sdk-image  SDK_ROOT=... FLASHDB_ROOT=... BMA456_ROOT=... \
                      LIS2DW12_ROOT=... ST25DVXXKC_ROOT=... TINY_AES_ROOT=...
make -C r1 sdk-verify
make -C r1 vendor-audit        # + IQS7211E_ROOT, AZOTEQ_SETTINGS_ROOT
make -C r1 vendor-storage-test # FlashDB/FAL port against pinned upstream
make -C r1 vendor-crypto-test  # AES-128 adapter against pinned tiny-AES-c
```

The SDK target compiles CMSIS-FreeRTOS, FreeRTOS-Kernel, and CmBacktrace
directly from the vendored snapshots under `g2/third_party/`.

## Verifying dependencies

```sh
./make.sh third-party                # every vendored snapshot, offline
./make.sh third-party-fetched SDK_ROOT=... FLASHDB_ROOT=... ...
```

Snapshot verification is fully offline. Each verifier reconstructs the
applicable Git commit, tree, and blob closure from the committed objects and
checks it against the recorded pin, so it proves the snapshot's upstream
identity without network access. Several also authenticate recovered G2
ABI/configuration evidence, and several enforce a production-exclusion gate that
fails closed if the snapshot has been wired into a shipped image without review.

## Cross-target

```sh
./make.sh build      # g2-build + r1-build
./make.sh test       # both test suites
./make.sh verify     # G2 build + upstream audits + all snapshots + R1 tests
./make.sh clean      # both trees
```

## When a build fails

The failure message names the gate. In rough order of frequency:

- **missing blob** — the official payloads are not in `g2/blobs/official/`; see
  above.
- **toolchain profile mismatch** — your Clang is outside the reviewed release
  family. `make -C g2 toolchain` shows what was detected.
- **snapshot verification failed** — a vendored dependency was modified. The
  message names the file and expected digest.
- **`snapshot is production-configured by <path>`** — a production-excluded
  dependency was referenced from the Makefile, a manifest, or a component. This
  gate is intentional; promoting a dependency to production is a reviewed change
  to its `README.openCFW.md` and its verifier, not a build flag.
- **package not byte-identical** — a generated overlay changed. Compare the
  reported overlay SHA-256 against the manifest pin; the packager reports which
  regions moved.
