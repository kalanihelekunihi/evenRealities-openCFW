# Linux-reproducible builds (dual-toolchain profiles)

openCFW pins every compiled overlay byte-for-byte. Historically those pins
assumed one reviewed compiler — Apple clang 21.0.0 from Xcode 26.6.0 — which
cannot run on Linux. This document describes the additive **toolchain-profile**
layer that lets the compiled source profiles build and verify reproducibly on a
non-Apple host (today a Linux Homebrew clang) without disturbing the reviewed
Apple reference.

## Policy

Reproducibility is defined **per reviewed toolchain**, not as one universal
byte string:

- The canonical `apple-clang` profile is unchanged. Its pins are each config's
  own top-level `toolchain`/`expected` and each manifest's own
  `package.expected_*` / `provider.size`/`provider.sha256`. The blob-only
  `reference` reconstruction stays byte-identical to the official bundle
  (`f4dfb0b4…`) and is compiler-independent, so it reproduces under any
  profile.
- Every alternate profile (e.g. `linux-clang`) carries its **own**
  independently recorded, fail-closed pins under a `toolchain_profiles` map
  (overlay configs) and a `profiles` map (manifest package + source-build
  providers). Its artifacts are byte-identical **to that toolchain's recorded
  output**, and deterministic across rebuilds — but they are *not* identical to
  the Apple-built firmware.

The Apple-clang profile therefore remains the provenance/reference anchor.
Alternate profiles are for reproducible independent builds and CI on hosts
without Apple clang. Choosing a profile never mutates another profile's pins.

## Using it

Toolchain selection is automatic. The Makefile picks the first present clang
(preferring `/usr/bin/clang`, then the Homebrew LLVM path) and asks
`tools/detect_toolchain.py` which reviewed profile that compiler matches:

```sh
cd openCFW
./make.sh toolchain      # show the resolved OPENCFW_CLANG + profile
./make.sh reference      # byte-identical reconstruction (any profile)
./make.sh ring-source    # compiles + verifies under the detected profile
```

Override either axis explicitly:

```sh
./make.sh ring-source \
  OPENCFW_CLANG=/path/to/clang \
  OPENCFW_TOOLCHAIN_PROFILE=linux-clang
```

Detection fails closed: a compiler that matches no reviewed profile's
`reviewed_version_prefix` is rejected rather than silently guessed, because its
bytes cannot reproduce any recorded pin.

## Recording a new profile

When a new reviewed compiler is introduced, record its pins once and commit
them. Recording never touches the canonical Apple pins.

```sh
# 1) Overlay/component pins for each compiled component:
python3 tools/apollo_overlay.py \
  --config components/apollo_main/ring_gesture/overlay.json \
  --output-dir components/apollo_main/ring_gesture/build \
  --clang "$OPENCFW_CLANG" \
  --toolchain-profile <id> --record-profile

# 2) Package + source-build provider pins for the profile:
python3 tools/open_cfw.py build \
  --manifest manifests/g2-2.2.6.10-ring-source.json \
  --output-dir build/ring-source \
  --toolchain-profile <id> --record-profile
```

`--record-profile` compiles with the current compiler, skips the reviewed pin
check, writes the observed pins into `toolchain_profiles[<id>]` /
`profiles[<id>]` (using the compiler's exact `--version` string as the reviewed
family), and preserves the hand-authored key order so the diff is a clean
append. Review the diff, then a normal build under `<id>` must reproduce those
pins exactly and fails closed on any drift.

## What reproduces on Linux today

| Target | Status on Linux (`linux-clang`, Homebrew clang) |
|---|---|
| `reference` | ✅ byte-identical to the official bundle (compiler-independent) |
| `ring-source` | ✅ reproducible + fail-closed against recorded `linux-clang` pins |
| `source` (core_overlay + bootloader) | ✅ full build + verify reproduces the complete profile-pinned Apollo overlay and bootloader |
| `verify` (all three profiles) | ✅ passes fail-closed on Linux |
| `test` (full suite) | ✅ green on Linux — all 221 modules pass; byte-exact Apple-clang assertions self-skip under an alternate profile |

### Running the test suite on Linux

The suite honors `OPENCFW_CLANG` (no longer hard-codes `/usr/bin/clang`) and
the active `OPENCFW_TOOLCHAIN_PROFILE`. Host-behavior, structural, and
source-hash tests run under any compiler. Two classes of assertion are
Apple-toolchain-specific and self-skip under a non-`apple-clang` profile:

- the two complete-component byte-exact reference suites
  (`test_core_overlay`, `test_bootloader_core_overlay`); and
- individual `*_are_exact` / `*_pinned` / `test_target_*` methods across the
  `test_runtime_*` leaf suites that pin exact Apple-clang compiled bytes,
  relocation-table layout, or `llvm-objdump` type names.

These are guarded by a `@_APPLE_ONLY` skip that points back here. Skipping loses
no Linux coverage: `tests/test_toolchain_profiles.py` rebuilds the entire
`source` package under `linux-clang`, which transitively pins every compiled
overlay, leaf, function, and package byte fail-closed — a strict superset of the
per-leaf exact assertions. On macOS with Apple clang the skips do not trigger
and the full byte-exact corpus runs.

The `linux-clang` pins were produced with Homebrew clang 22.1.8 targeting
`thumbv7em-none-eabi` with the reviewed overlay flags. The current profile
pins a 127,082-byte Apollo-main overlay, 3,650,478-byte component, and
4,428,972-byte package with SHA-256 values
`f24cf0e060530429679df9389571ffee397819dfa2c3abc00d26deb75a3e47ad`,
`5fe58e3af2a0b7fed55c6b7c33afbd1ac5c887860721b04859e2d49d81be828c`,
and
`22117e0cd7d0b827a8c31d22eb509edb30651fef6a6308838a8220ff80f6c702`.
Determinism is covered by `tests/test_toolchain_profiles.py`, including an
end-to-end rebuild of the full `source` package.

### Recorded source-root qualification

The core-overlay config records a reviewed source root for each toolchain
profile. When the build runs from a linked worktree, the compiler maps that
worktree's actual `openCFW` root to the selected profile's reviewed root. This
keeps vendored TLSF diagnostics that embed `__FILE__` byte-identical to the
reviewed aggregate.

The current reviewed roots are:

```text
apple-clang: /Users/kalani/Repo/SybilSight/openCFW
linux-clang: /Users/kalani/Repo/SybilSightABCD/openCFW
```

This is a per-profile normalization to explicitly reviewed roots; it does not
claim global path independence across arbitrary users or source layouts. The
bounded FreeRTOS leaves (`vTaskMissedYield`,
`uxTaskResetEventItemValue`, and `pvTaskIncrementMutexHeldCount`) retain their
reviewed cross-profile contracts.

### Per-leaf and flash-plan pins under a profile

The compiled Apollo overlay changes size and internal layout across compilers,
so a profile records more than the overlay/component hashes:

- **Overlay / component / package** — size + SHA-256, as for `ring-source`.
- **Isolated / in-place / relocated leaves** — each leaf's `toolchain_profiles`
  entry. Assembly (`.S`) and other byte-identical leaves record only the
  reviewed compiler family; leaves whose bytes, placement, or relocation
  offsets shift record their own `expected` (and, for relocated leaves, the
  observed relocation offsets — the call targets and order are unchanged).
- **Bootloader function ABI** — the bootloader pins each function's
  offset/size; those are recorded under `function_profiles[<id>]`.
- **Flash-plan regions** — the manifest's detailed per-function regions above a
  component's `source_appended_boundary` describe the Apple layout. Under an
  alternate profile the compiled tail is mapped as a **single coarse
  source-compiled region** sized to the actual component; the compiler-
  independent base map (opaque spans, fixed-address in-place leaves, fixed-size
  redirects) stays exact. The canonical `apple-clang` profile keeps the full
  per-function breakdown.

Relocation-table order is compared as a set ordered by offset (assemblers emit
entries in different orders); the full `(offset, type, symbol)` identity is
still verified.

## Preceding cross-profile FreeRTOS missed-yield leaf

Unlike the Linux-only replacements below, `vTaskMissedYield` is enabled in
both profiles. FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` identifies the operation as
`xYieldPending = pdTRUE`; focused G2 disassembly binds `xYieldPending` to
`0x20074A44`.

Both compilers emit bytes
`44f64420c2f20700012101607047`, SHA-256
`2b028e0c4aa84ce41bfe4b4164a397ae4d5ba9f177900cefb3b71c5d5d339ba9`.
Apple places the leaf at `[0x007B0800,0x007B080E)`. Linux places it at
`[0x007B0F38,0x007B0F46)` after two generated alignment bytes because its
earlier profile-gated leaves make the pre-existing overlay longer. Each
profile authenticates the same ten-byte stock span
`[0x004555E6,0x004555F0)` and emits its own displacement-correct `B.W`
redirect. See
[`research/freertos-missed-yield-source-boundary-audit.md`](research/freertos-missed-yield-source-boundary-audit.md).

## Prior cross-profile FreeRTOS task leaves

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` also supplies exact
`uxTaskResetEventItemValue` and `pvTaskIncrementMutexHeldCount` bodies. The
former preserves three volatile `pxCurrentTCB` evaluations while resetting
event-list item value `+0x18` from priority `+0x2C` and 56 priorities. The
latter preserves its volatile current-TCB evaluations while incrementing
held-mutex field `+0x64` under `configUSE_MUTEXES=1`. Both bind
`pxCurrentTCB` at `0x20074A20`.

| Function | Stock span / SHA-256 | Canonical target / SHA-256 | Linux target |
|---|---|---|---|
| `uxTaskResetEventItemValue` | `[0x00455ACA,0x00455AE0)` / `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` | `[0x007B0810,0x007B082A)` / `04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6` | `[0x007B0F48,0x007B0F62)` |
| `pvTaskIncrementMutexHeldCount` | `[0x00455AE0,0x00455AF6)` / `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f` | `[0x007B082C,0x007B0844)` / `494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf` | `[0x007B0F64,0x007B0F7C)` |
| `vTaskSuspendAll` | `[0x00454D7C,0x00454D88)` / `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` | `[0x007B0844,0x007B0854)` / `0928ce291a4a96b18baf7304bc7f87fb828ac06902619f1f42500e04c73883be` | `[0x007B0F7C,0x007B0F8C)` |
| `vTaskInternalSetTimeOutState` | `[0x00455556,0x00455566)` / `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` | `[0x007B0854,0x007B0866)` / `8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a` | `[0x007B0F8C,0x007B0F9E)` |

Reset and mutex-held each retain their two preceding alignment bytes;
suspend and timeout are consecutive and add none. Suspend binds
`uxSchedulerSuspended=0x20074A58`; timeout capture binds
`xNumOfOverflows=0x20074A48`, `xTickCount=0x20074A34`, and the two-word
`TimeOut_t` layout. The canonical overlay, component, and package are
116,034, 3,639,430, and 4,417,884 bytes with SHA-256 values
`d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd`,
`8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`,
and
`e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7`.
Those Linux aggregate pins were the values for that prior release and retain
the reviewed source-root qualification
`/Users/kalani/Repo/SybilSightABCD`. See the
[reset audit](research/freertos-reset-event-item-value-source-boundary-audit.md)
and [mutex-held audit](research/freertos-mutex-held-source-boundary-audit.md),
plus the
[suspend audit](research/freertos-suspend-all-source-boundary-audit.md).

## Profile-gated source replacements

A leaf or patch site may carry a `"profiles": ["<id>"]` allow-list. Items so
gated are compiled and placed only under a listed profile and are *absent*
under every other profile, which leaves those profiles' overlays byte-identical.
This lets an alternate toolchain source-replace functions that the reviewed
apple-clang reference has not yet taken on, without perturbing the canonical
pins.

The first such replacement is the **TinyFrame `TF_CksumAdd`** checksum step
(stock at run `0x00491730`). Under `linux-clang` the core overlay appends a
source-owned, table-free CRC-16/ARC leaf
(`components/apollo_main/core_overlay/runtime_tinyframe_cksum_add.c`,
behaviourally identical to the recovered stock table lookup) and redirects the
stock function to it with a `B.W` tail-branch; callers return through the
preserved `LR`. Under `apple-clang` the leaf, its patch site, and its function
are filtered out, so the apple overlay/component/package pins are unchanged.
`tests/test_tinyframe_cksum_leaf_integration.py` guards the gating and the
leaf's checksum equivalence, and the end-to-end firmware reproduction (with the
live redirect) is covered by the `source` package rebuild in
`tests/test_toolchain_profiles.py`.

The second such replacement is the **first-party transport CRC-32** finaliser
(stock at run `0x0058FCF0`), the standard reflected CRC-32 (polynomial
`0xEDB88320`) used by transport-protocol packet framing, OTA external-flash
verification, and the box-UART manager. Under `linux-clang` the core overlay
appends a source-owned update leaf
(`components/apollo_main/core_overlay/runtime_transport_crc32.c`) and redirects
the stock 40-byte body to it with a `B.W` tail-branch; the leaf reproduces the
recovered ABI (`r0` seed CRC, `r1` length, `r2` data; returns the table-updated
CRC `^ 0xFFFFFFFF`) and references the pinned canonical table at `0x006987A8` as
fixed-address data, exactly as the stock body loads it. Under `apple-clang` the
leaf, patch site, and function are filtered out, so the apple pins are
unchanged. `tests/test_first_party_transport_crc32_leaf.py` guards the gating
and proves the leaf source computes the canonical CRC-32 (check value
`0xCBF43926`) against the firmware's own pinned table. Evidence is in
[`research/first-party-transport-crc32-source-boundary-audit.md`](research/first-party-transport-crc32-source-boundary-audit.md).

The third replacement is the **first-party CRC-16/CCITT** computation (poly
`0x1021`, MSB-first), source-owned as two `linux-clang` leaves in
`components/apollo_main/core_overlay/runtime_crc16_ccitt.c`: the XMODEM variant
(seed `0x0000`, stock at run `0x0059D350`) and the resumable CCITT-FALSE variant
(seed `*ptr`/`0xFFFF`, stock at run `0x0049ACD4`, 48 callers). Each redirects its
40+-byte stock body with a `B.W` tail-branch and references its pinned canonical
`0x1021` table as fixed-address data. Under `apple-clang` both are filtered out.
`tests/test_first_party_crc16_ccitt_leaf.py` proves the check values (`0x31C3`
and `0x29B1`) against the firmware's own table; evidence is in
[`research/first-party-crc16-ccitt-source-boundary-audit.md`](research/first-party-crc16-ccitt-source-boundary-audit.md).

## Safety

Nothing here flashes, signs, or connects to hardware. Alternate-profile
artifacts are independent reproducible builds; they are not vendor-reviewed and
are not byte-identical to the Apple-built firmware. Do not treat an
alternate-profile package as the reviewed reference, and never translate
EVENOTA package offsets into controller flash addresses.

## Scheduler-cluster profile qualification

The scheduler-cluster release was rebuilt at the reviewed exact source-root
spelling `/Users/kalani/Repo/SybilSightABCD/openCFW` with Homebrew clang
22.1.8. Two component builds were byte-identical. The resulting overlay is
118,660 bytes with SHA-256
`77ae17c20117c476596c76544c397516ee561219296db4b7f5dc2d80d0907024`;
the Apollo-main component is 3,642,056 bytes with SHA-256
`2c9076f817e28b776bb34538915c18097b1ea24ee1b4cdcfa22aab075797e32f`.

Combining that component with the authenticated Linux bootloader and the four
unchanged official peripheral payloads produces the all-Linux 4,420,510-byte
package with SHA-256
`2692cc62f39793c3111004bc2d55b65450903b8f6164f9206c43509b7de8462b`.
The noncanonical coarse-region flash plan is 558,796 bytes with SHA-256
`5c3629f259af83752a28e7da1e776fec80d5257f888303ae3effb52b6f00e013`
and records 783 placed, two unresolved, and five container-only regions.
The scheduler-cluster verifier passes 9/9 under this exact-root profile.

## Prior LZ4 profile qualification

Both production profiles now compile the authenticated upstream LZ4 v1.10.0
snapshot at commit `ebb370ca83af193212df4dcbadcc5d87bc0de2f0`. This is the
maintained openCFW replacement source; the stock point release remains
unclaimed. Section selection retains only `LZ4_decompress_safe`, its 64-byte
read-only table closure, and the two source adapters.

| Closure item | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Decoder text | 1,660 bytes at `[0x007B0B74,0x007B11F0)`, relocated SHA `a7e5690af5e74e5395a51a716c9ebde2ee692dcf38decbf92141a3be261d358e` | 1,690 bytes at `[0x007B12A8,0x007B1942)`, relocated SHA `632ad34cdf299a714e4d81b7f2ba55e4edb1ac897ff65744622ab29b914bc542` |
| Table alignment | none | two bytes at `[0x007B1942,0x007B1944)` |
| Tables | 64 bytes at `[0x007B11F0,0x007B1230)` | 64 bytes at `[0x007B1944,0x007B1984)` |
| Safe adapter | four bytes at `[0x007B1230,0x007B1234)` | four bytes at `[0x007B1984,0x007B1988)` |
| Mode-2 adapter | 30 bytes at `[0x007B1234,0x007B1252)` | 30 bytes at `[0x007B1988,0x007B19A6)` |

The common table SHA-256 is
`361b3c2a85717050294fd9e3c6440690de35c0a9455d50e487ea8f0881c40f03`.
The Apple/Linux relocated safe-adapter hashes are
`589f67fc5b672f2be0809e999e8168708b11b90452088fb401a8d76d604959f5`
and
`b30709dd4480368a7662bc4ec880846e7d74cb1da1386d4bbad8240d447894c2`;
the relocated mode-2 hash is identically
`577501eac08ce8028c0262f19c84864439e11378314bc9f2874bd8acc77729b6`.
The old profile-specific primary sections remain under `_legacy` names and
unreachable; Apple retains 30/696 bytes and Linux 30/650 bytes.

The compiler-specific relocations differ but resolve the same closure. Apple
uses `R_ARM_REL32` table references, while Linux uses MOVW/MOVT PREL pairs.
Both call the authenticated fixed-address void-EABI providers
`__aeabi_memcpy=0x00439BE4` and `__aeabi_memmove=0x00439710`. The complete
provider spans and memmove tail behavior are pinned by the production audit.

The final profile artifacts are:

| Artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Overlay | 118,574 / `1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9` | 120,450 / `2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7` |
| Apollo-main component | 3,641,970 / `6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d` | 3,643,846 / `140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d` |
| Core-source package | 4,420,424 / `d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294` | 4,422,300 / `cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8` |

Linux component accounting is 120,632 source-owned, 82,644 generated patch,
82,826 replaced-stock, 3,440,538 opaque-base, and 32 wrapper bytes; its package
is 121,291 source, 84,232 generated, and 4,216,777 opaque bytes. The canonical
Apple accounting is documented in `source-coverage.md`. Reproduction and
validation are offline operations. Nothing here flashes, signs, or executes
firmware on G2 hardware.

## Prior FreeRTOS queue/task closure qualification

The authenticated `xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace` production tranche was qualified at the reviewed
source root `/Users/kalani/Repo/SybilSightABCD/openCFW` with Homebrew clang
22.1.8. A profile-recording pass and two ordinary fail-closed `source` builds
produced identical output:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 120,942 | `8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905` |
| Apollo-main component | 3,644,338 | `9532d9051a424453fda38d383aa303e4783c9832430d816554e2c861ea7afac0` |
| Apollo-main component report | 1,025,177 | `db953c59a91adecf2eaf7c5c030d12a50c61971b7ad3a33dd0cb1870e3decdaf` |
| Core-source package | 4,422,792 | `b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea` |
| Flash plan | 563,117 | `9ba2fe6f12dd487cb07ae8e1fa38cabf8320d8bd399283acb7e0bf125c0c03bb` |
| Package build report | 2,322 | `11f9dc769de125c578ecb0121d3838b32ef5313f3453adce796933484fcdd27d` |
| `SHA256SUMS` | 105,615 | `16297b9a989f5d8a951ca4e8295e13f5a8219c19ce59cf0faba2e28453c8412b` |

The component accounts for 121,124 source-owned bytes (182 in place),
83,112 generated patch bytes, 83,294 replaced-stock bytes, 3,440,070 opaque
bytes, and 32 wrapper bytes. The package owns 121,781 source, 84,702
generated, and 4,216,309 opaque bytes. The alternate-profile coarse flash
plan records 789 placed, two unresolved, five container-only, and six
protected regions. These were compile/package checks only; no firmware was
signed, flashed, reset, or executed on physical hardware.

## Preceding FreeRTOS timeout-check qualification

The authenticated FreeRTOS V10.5.1 `xTaskCheckForTimeOut` promotion was
qualified with Homebrew clang 22.1.8 at the reviewed exact source-root
spelling. The compiler emits one relocation-free 136-byte leaf with SHA-256
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.
It follows two alignment bytes at `[0x007B1B92,0x007B1B94)` and occupies
`[0x007B1B94,0x007B1C1C)`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 121,080 | `75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324` |
| Apollo-main component | 3,644,476 | `29c48306a2f8fab7b87af6c90b38786e4ee36d19f9eb68122614df4b355472ce` |
| Apollo-main component report | 1,029,223 | `f978bdbda751dc21252d213c717b6df344ae5fce482c1bddacc8b7fc130db9ad` |
| Core-source package | 4,422,930 | `22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab` |
| Flash plan | 563,135 | `7128a3311f0a0ded53394dbf49a1a1f71d5d559b891aba080cd41de2c5cf9066` |
| Package build report | 2,322 | `b00099ecb6b6dc5e9c49dd046cf59c2bfb30220f653b4214308cfd72b22eef06` |
| `SHA256SUMS` | 105,648 | `463541d197174f263bd0bd86e0be733ac7797d755b3752b207381161cf5da78b` |

The component accounts for 121,262 source-owned bytes (182 in place), 83,240
generated patch bytes, 83,422 replaced-stock bytes, 3,439,942 opaque bytes,
and 32 wrapper bytes. The package partitions into 121,917 source, 84,832
generated, and 4,216,181 opaque bytes. The coarse plan records 789 placed,
two unresolved, five container-only, and six protected regions. A recording
pass followed by two ordinary fail-closed builds reproduced the overlay,
component, component report, package, flash plan, package report, and checksum
index byte-for-byte.

The qualification is compile, assembly, packaging, and offline-analysis
evidence only. No firmware was signed, flashed, reset, booted, or executed on
physical hardware.

## Preceding EasyLogger output/async qualification

At the reviewed exact source-root spelling, Homebrew clang 22.1.8 produces a
123,170-byte overlay, a 3,646,566-byte Apollo-main component, and a
4,425,020-byte package. Their SHA-256 values are respectively
`36479ef84126bc0075a2bcfa93c86591376eb4f18eb32983f84865f9d51e72e9`,
`43d02017caa63a2bbe96e7dda056fa61009abcdb2913a12b2298dde131eb0a9c`,
and `12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Two ordinary fail-closed builds produced identical artifacts.

The three production leaves contain 33 paired MOVW/MOVT `R_ARM_PREL31`
references (66 pairs across Apple and Linux; 132 encoded relocations). An
independent checker linked every pair at the planned placement and matched
all 132 final encodings against LLD. The closure extractor also authenticates
the exact selected-function 8-byte `.ARM.exidx` CANTUNWIND companion and its
local-section `R_ARM_PREL31` binding, then deliberately discards that metadata
rather than appending it as executable bytes. Personality/data/non-CANTUNWIND
and cross-function companions fail closed.

This is compile, relocation, packaging, and offline-analysis evidence only.
No firmware was signed, flashed, reset, booted, or executed on physical G2
hardware.

## Preceding FreeRTOS semaphore-take exact-root result

The authenticated V10.5.1 semaphore-take/helper pair was built at
`/Users/kalani/Repo/SybilSightABCD/openCFW` with
`/home/linuxbrew/.linuxbrew/bin/clang` 22.1.8. The helper occupies overlay
offset 122,564 (18 bytes); the semaphore leaf occupies offset 122,584 (600
bytes) and resolves its sole `R_ARM_THM_CALL` to the helper. Final pins are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 123,184 | `2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63` |
| Apollo-main component | 3,646,580 | `0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9` |
| Core-source package | 4,425,034 | `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1` |
| Coarse flash plan | 566,643 | `cdf6345ab2e71209025e06f17165fcf8d8f87715820c3821b1bad450e48f83e2` |

The package partitions into 124,025 source, 86,010 generated, and 4,214,999
opaque bytes. This was an offline compile/package result; no hardware was
operated.

## Preceding FreeRTOS queue-reset/unordered-removal exact-root result

At exact source-root spelling `/Users/kalani/Repo/SybilSightABCD/openCFW`,
Homebrew clang 22.1.8 emits a 174-byte relocation-free
`xQueueGenericReset` leaf at overlay offset 123,184, two generated alignment
bytes at 123,358, and a 210-byte relocation-free
`vTaskRemoveFromUnorderedEventList` leaf at 123,360. Their SHA-256 values are
`18f27b60f944abbc4a8c703e4aa6e4fba0bac243a4010ea32474e9f8d9fe31ff`
and `b2e29e859cae0b43dadddf1dad7f44f9740ae5b6ed93a3febf3a28a7128331e4`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 123,570 | `6885adb2da4019a5595fd14fefe7e6682e6d32e63b45c47b3436828a1238d288` |
| Apollo-main component | 3,646,966 | `657140490b0bd0b1f5aeb44505cc24b01377d16254f91c30e31893d1890731ca` |
| Core-source package | 4,425,420 | `d7870c13b9417f8a9866ad6b87858e712c1c6c005b0b534bdd1d4ba540b64d60` |
| Coarse flash plan | 568,157 | `de304382e1757f54525eb64a579b92b7db5fb63f7d45d6003a0c25afb3bbcff0` |

The component accounts for 123,752 source-owned bytes (182 in place), 84,820
generated patch bytes, 85,002 replaced-stock bytes, 3,438,362 opaque bytes,
and 32 wrapper bytes. The package partitions into 124,409 source, 86,410
generated, and 4,214,601 opaque bytes. The focused qualification suite passes
9/9 under this exact-root profile. This was an offline compile/package result;
no hardware was operated.

## Preceding corrected EasyLogger single-owner exact-root result

At exact source-root spelling `/Users/kalani/Repo/SybilSightABCD/openCFW`,
Homebrew clang 22.1.8 emits the corrected builder as 210 text bytes plus a
54-byte read-only-data closure. Its nine relocations resolve the ready and
metadata globals, allocator, consuming enqueue seam, local data, and
diagnostic output; there is no recycler symbol or relocation. The submit
wrapper still targets the builder's official entry and the stock caller
topology is unchanged.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 123,558 | `f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc` |
| Apollo-main component | 3,646,954 | `5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9` |
| Core-source package | 4,425,408 | `fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75` |
| Coarse flash plan | 568,151 | `57161e24c9d4c5867558481415af0087e93c6315b01b3e049175b949fdd0aeac` |
| Build report | 2,322 | `ba2d31a4ac14c556bdc0f1a6796a0657d9eaedfb3a12cabf22e428e616d3fe30` |
| Checksum inventory | 106,656 | `f5b95a8deb504264016195991fe8eabd269770b192764782bc291ca281438504` |

The component accounts for 123,740 source-owned bytes (182 in place), 84,820
generated patch bytes, 85,002 replaced-stock bytes, 3,438,362 opaque bytes,
and 32 wrapper bytes. The package partitions into 124,397 source, 86,410
generated, and 4,214,601 opaque bytes. This was an offline compile/package
result; no hardware was operated.
## Preceding EasyLogger hexdump exact-root result

The production hexdump tranche was recorded and rebuilt at the reviewed source
root `/Users/kalani/Repo/SybilSightABCD/openCFW` with Homebrew clang 22.1.8.
This spelling is mandatory because existing source embeds `__FILE__`; a
temporary `/work/openCFW` build shortened linked rodata by 28 bytes and was
discarded without retaining any of its pre-existing leaf pins.

The exact-root build preserves every earlier Linux object/pin and appends ten
strict hexdump/formatter/level-less transport leaves beginning at overlay
offset 123,560. The level-less builder is offset 124,252 with nine
relocations, raw submit is 124,508 with one, and the main hexdump is 124,516
with 23. The overlay ends at 125,023.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 125,023 | `47f588845f4bd202d1d184282996cf45dd2cb514b4795ac9cdd5a7835da90d02` |
| Apollo-main component | 3,648,419 | `df9a1b00038d07ea0137258cc879547ecc86a11a737d1954bd1f4babd259c8e3` |
| Core-source package | 4,426,873 | `2eef6375f1ac218701f438afd8f5b5752b789a20db1e73f6dfd71486acc94423` |

The record build and two normal exact-root overlay builds reproduce these
pins. The package was assembled from the pinned exact-root component and the
existing reviewed Linux bootloader. No signing, flashing, reset, or hardware
operation was performed.

## Preceding FreeRTOS+CLI accessor-only exact-root result

The accessor and then-current collector-capacity fragment were recorded at the
reviewed source spelling `/Users/kalani/Repo/SybilSightABCD/openCFW` with
Homebrew clang 22.1.8. A structural comparison against the preceding
EasyLogger-hexdump configuration found changes only in the four aggregate
Linux expected fields; every earlier relocated-leaf profile remained
byte-for-byte identical.

The accessor raw object is 1,120 bytes with SHA-256
`76a9d2f7de4d6c98902b84e1ad535f6bc643ae45a4676794e8e3345f41f5b263`;
its extracted 252-byte leaf hashes to
`7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914`
and begins at overlay offset 125,024. The two-byte capacity fragment begins
at offset 125,276. Its 540-byte object hashes to
`e2b931288aa86668af5e8b87288bc041ec8c0c96dc9f730891433f9fafcf2380`,
and its extracted bytes hash to
`dbf2d8a1ffb886d7964cf470133c8a289aff606c14e6d75fd258678de0f47495`.
Both objects reproduced twice and both extracted leaves have zero text
relocations.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 125,278 | `a0a520069e497613b397af1d7327752201ced44c876d6925a7561ae45c91fa7c` |
| Apollo-main component | 3,648,674 | `8c477d28a9f58feaf722bd1e00b9767a8ca745ba618515d46339271cd0288c1a` |
| Core-source package | 4,427,128 | `5598cb1f2a3b9a8b6101f61afcc5e24de54b01c3d5aa45396bf161344b3618bb` |

One record build and two ordinary fail-closed component builds reproduced the
overlay and component. The package record and two ordinary package builds
also reproduced the package exactly. Exact manifest ownership for the Linux
package is 126,117 source, 87,248 generated, and 4,213,763 opaque bytes.
Cross-profile overlay configuration registers 631 functions and 587 patches;
Linux emits all 631/587, while the Apple-effective report emits 627/583 because
four CRC/TinyFrame leaves are Linux-profile-only. The focused production suite
checks upstream/candidate/production equivalence, strict extraction,
manifest tiling, exact patch bytes, package identities, and whole-component
branch/pointer ingress. All work was offline; no firmware was signed or
flashed and no hardware was operated.

## Prior phase-local nanopb varint exact-root result

The bounded production nanopb `pb_decode_varint` leaf was recorded at the
reviewed source spelling `/Users/kalani/Repo/SybilSightABCD/openCFW` with
Homebrew Clang 22.1.8. Its 1,220-byte raw object hashes to
`0f19f9419ddc74d50e58f5e63737fe7224de35fdf7a0395267e987748e5064ed`;
the 124-byte unrelocated text hashes to
`e820aa1b54f20ec1454462d356562177f8d03d98f21dff4bba77fa39fe282fa5`.
The relocated text at overlay offset 125,280 hashes to
`ca6cab5c48508184b30bedf534d094e867e0369564e9e039ff4813bbba40001d`;
its 140-byte text-plus-rodata closure hashes to
`c8d549db76abf789f897a87aff567331cf81e7732870404ba1ed3602d4c10bcc`.

The record output and two ordinary fail-closed core builds reproduced the
same 125,420-byte overlay and 3,648,816-byte component byte-for-byte. Their
SHA-256 values are
`dfc052f153f99c1fb153dd06cfcbd5380733d47d6e376ce902dbc2dc63413692`
and `24a02cdaf64fb9d761fb896a4d09d72cfbe48f08b799cb49a95e0a61ad69892f`.
All 62 pre-existing relocated-leaf records were structurally identical across
record and normal runs. The package record and two ordinary builds reproduced
4,427,270 bytes with SHA-256
`81729530e02fc666dfdef831933b44ec74e45bc3412c81d7c1161e03a5055152`.

Linux emits all 632 registered functions and 588 patches. Coarse profile
ownership is 126,259 source, 87,360 generated, and 4,213,651 opaque bytes.
This exact-root work was offline; no firmware was signed or flashed and no G2
hardware was operated.

## Preceding littlefs `lfs_tag_id` exact-root result

The atomic production promotion replaces the byte-identical private
`lfs_tag_id` leaves at `[0x004CAEB0,0x004CAEB8)` in Apollo main and
`[0x00410BB8,0x00410BC0)` in the bootloader. Their bytes
`800a8005800d7047` hash to
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`.
Complete-image scans close 50 main and 41 boot direct callers and find no
reviewed alternate or interior ingress, stored pointer, or outgoing call.

The altered BSD-3-Clause source is selected from authenticated littlefs
v2.10.1 commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`; the exact
`lfs.c[10702:10793]` definition hashes to
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`.
The 845-byte production source and 872-byte header hash to
`5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638`
and `5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e`.
Homebrew Clang 22.1.8 and Apple Clang 21.0.0 emit the same relocation- and
provider-free six-byte text `c0f389207047`, SHA-256
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`.

The exact-root Linux replay pins its build-dependent contract independently
rather than silently inheriting Apple values:

| Item | Final Linux value |
|---|---|
| Main leaf | offset `126,416`, address `0x007B30F4`, patch `e8f220b900bf00bf` |
| Boot leaf | offset `650`, address `0x00434702`, patch `23f0a3bd00bf00bf` |
| Main overlay | `126,422` / `fcf2783a5a73474fb87cdd22cc592a12056b6a4d4080e7f8ca6120b88d82ebaa` |
| Main component | `3,649,818` / `40d16ee5833eae6ae3229d82fcd583fd2c3ba9fe6234978d503a57c0d88ffeff` |
| Boot overlay | `656` / `4cadbf422b57b1905b38df77ab0d24932839aa28f883f57e56a09183d577edb8` |
| Boot component | `149,256` / `a3ca91bb744c777d7d98d8b34a044e613ad251a972d6e6d54a8a48b959795ad2` |
| Package | `4,428,306` / `727354ce585843f11fabec93884640fdf58c71b251f5b7067ee4c0703cb53fcd` |
| Flash plan | `597,634` / `165e5cb41e271e2b55e4330aa2872504bce55d98dd3c0c6e3c099788f0ad42c1`; `837 placed / two unresolved / five container-only` |
| Exact ownership | `127,291 source / 87,882 generated / 4,213,133 opaque bytes` |

The cross-profile config censuses are `654/603/85`
main and `33/31/14` boot. The selected release is a
source-equivalent compatibility baseline rather than proof of the vendor's
exact checkout. Reproducibility does not source-own the broader littlefs
implementation or a G2 block-device port. The replay is offline and
authorizes no signing, flashing, filesystem mutation, reset, boot, or hardware
operation.

## Preceding atomic dual-image littlefs tag-validity/type1 exact-root result

Homebrew Clang 22.1.8 reproduces the Apple six-byte
`open_cfw_littlefs_tag_isvalid` text and ten-byte
`open_cfw_littlefs_tag_type1` text exactly. They hash to
`65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e`
and `079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf`
and have no providers or relocations.

Linux places the Apollo-main validity/type1 leaves at offsets 126,388 /
`0x007B30D8` and 126,396 / `0x007B30E0`, after two alignment bytes apiece.
Complete stock patches are `e8f235b900bf00bf00bf` and
`e8f22abd00bf00bf`. Boot uses the cross-profile offsets 628 /
`0x004346EC` and 634 / `0x004346F2`, with patches
`23f0bbbd00bf00bf00bf` and `23f0afbd00bf00bf`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,406 | `7196c0d0d456b46e125b793d7ab4c6175768067589f4153d9b3ee997011c0314` |
| Apollo-main component | 3,649,802 | `a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef` |
| Bootloader overlay | 644 | `078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794` |
| Bootloader component | 149,244 | `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593` |
| Core-source package | 4,428,278 | `07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc` |
| Flash plan | 594,109 | `f59945999bdff46a4d86cc0d886adafae75ba23d136b7de448adbb1f7c12f3a4` |

The package build report is 2,322 bytes, SHA-256
`a6c0df56d505e665d122740792797905111f4d6d988c791c6f4efaa568ec8457`.
The plan reports 832 placed, two unresolved, and five container-only records,
839 total. Its coarse source/generated/opaque view is 127,263 / 87,850 /
4,213,165; exact manifest ownership is 127,265 / 87,848 / 4,213,165. Linux
main builder accounting is 126,588 source, 86,232 patch, 32 wrapper,
3,436,950 opaque, 86,414 replaced, and 182 in-place bytes; boot is 642 source,
838 patch, three alignment, and 147,761 opaque bytes.

The littlefs commit is an authenticated source-equivalent baseline, not proof
of the vendor's exact checkout. The exact-root result is offline assembly GO;
signing, flashing, filesystem mutation, reset, boot, and hardware operation
remain NO-GO.

## Preceding atomic dual-image littlefs tag-type3 exact-root result

Homebrew Clang 22.1.8 reproduces the Apple six-byte
`open_cfw_littlefs_tag_type3` text exactly. It hashes to
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`
and has no providers or relocations.

Linux places the Apollo-main leaf at offset 126,408 / `0x007B30EC`, after two
alignment bytes, and redirects the complete stock body with
`e8f228b900bf00bf`. Boot remains cross-profile identical at offset 644 /
`0x004346FC`, with patch `23f0acbd00bf00bf`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,414 | `df3b885d5a5c952144fd50324f556e1fdf9435728bb2db8aa015183eb0f4cd4f` |
| Apollo-main component | 3,649,810 | `478877ed8ac940d208216d4950a423f70728571fa9f18795c1ee01d521ee858c` |
| Bootloader overlay | 650 | `968dbeac7adef3acc5151cd15189bba3528de295147ecca60832f1cf87b425e3` |
| Bootloader component | 149,250 | `bb3d7eef87a59529f67de9996324a91575d6e1218471a5330b153eb28950742a` |
| Core-source package | 4,428,292 | `e56f78421dd83283e3d4e3f4a6b61a3400260c2618719cc6051453dd9e249bc1` |

The exact-root plan reports 833 placed, two unresolved, and five
container-only records. Linux exact ownership is 127,279 source, 87,864
generated, and 4,213,149 opaque bytes. Main builder accounting is 126,596
source, 86,240 patch, 32 wrapper, 3,436,942 opaque, 86,422 replaced, and 182
in-place bytes; boot is 648 source, 846 patch, three alignment, and 147,753
opaque bytes.

Focused production qualification passes five tests. The authenticated
littlefs commit is a source-equivalent compatibility baseline, not proof of
the vendor's exact checkout. This exact-root result is offline assembly GO;
signing, flashing, filesystem mutation, reset, boot, and hardware operation
remain NO-GO.

## Preceding dual-image littlefs `lfs_tag_chunk` replay

The exact-root Linux Clang 22.1.8 profile now compiles the shared, bounded
BSD-3-Clause `open_cfw_littlefs_tag_chunk` leaf into both Apollo images. Its
six-byte text hashes to
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`
under both reviewed compilers and has no relocation or undefined provider.
Linux places it at main overlay offset 126,380 / `0x007B30D0` and boot offset
622 / `0x004346E6`; each complete six-byte stock body becomes a
profile-specific non-linking `B.W` plus one NOP.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,386 | `5ebdb04c602ff59241f9d376caa474180f1e9c90ba2ea05581e2b247528b814a` |
| Apollo-main component | 3,649,782 | `3ad0a8692694132ce30b266ae8ec4ffb66617de173cb1e3d96ee90335945c70d` |
| Bootloader overlay | 628 | `e7619c604912ded4b5ac4513287bb68560bba2a09f84cda42dd9f1cf2d080a63` |
| Bootloader component | 149,228 | `64d87f89085988da184b7cf3b9758e702093e35f0e4b2afb6da22971b8532f1b` |
| Core-source package | 4,428,242 | `8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba` |
| Flash plan | 589,115 | `745b6dfe55e08fd6ad5d860e76b0d97c844368ef69ac0af396d887dc9a4ed6f5` |

The Apollo-main config now registers 650 functions, 599 patch sites, and 81
relocated leaves; boot registers 29/27/10. The plan records 825 placed, two
unresolved, and five container-only records, 832 total; its coarse ownership
is 127,231 source, 87,810 generated, and 4,213,201 opaque bytes. Main builder
accounting is 126,568 source-owned, including 182 in-place; 86,214 generated
patch, 32 wrapper, 3,436,968 opaque, and 86,396 replaced-stock bytes. Boot
builder accounting is 626 source, 820 patch, three alignment, and 147,779
opaque bytes. The littlefs v2.10.1 commit is an
authenticated source-equivalent compatibility baseline, not proof of the
vendor's precise checkout. This replay did not sign or flash an image, mount
or mutate a filesystem, or operate G2 hardware.

## Preceding CmBacktrace exact-root result

The CmBacktrace current-thread-name source pair was qualified with Homebrew
Clang 22.1.8 at the reviewed exact-root
`/Users/kalani/Repo/SybilSightABCD/openCFW`. Linux places the 14-byte recovered
adapter at `0x007B2D10`, two alignment bytes at `0x007B2D1E`, and the 4-byte
MIT compatibility helper at `0x007B2D20`. The resulting overlay is 125,440
bytes / `d577a1faefb80857c9cf1aba83e3ae59cf90ee9747b208b8a187cd7a11bdb4ae`;
the component is 3,648,836 bytes /
`c1c6c563167c2451cb896e482dfaa58da075d6fea8ebc147dcb68dd74247da51`;
the package is 4,427,290 bytes /
`03d082df4a74448bcdfed86f4fea7d09454a03e87c9deb8ab178b444a3546222`.

Linux emits all 634 registered functions and 589 patches. Its coarse flash
ownership is 126,279 source, 87,368 generated, and 4,213,643 opaque bytes.
The two-leaf target closure and resolved `fff7f6bf` tail branch are identical
to Apple. Qualification was offline with no signing, flashing, or hardware.

## Prior phase-local complete FreeRTOS+CLI console-task exact-root result

The seven-leaf production console closure was rebuilt at the reviewed exact
source spelling `/Users/kalani/Repo/SybilSightABCD/openCFW` with Homebrew
Clang 22.1.8. Linux places fill at `0x007B2D20`, state initialization at
`0x007B2DF0`, 22-group registration at `0x007B2E0C`, command processing at
`0x007B2E6C`, byte consumption at `0x007B2EB0`, polling at `0x007B2F10`, and
the task entry at `0x007B2F4C`. The 3-byte prompt closure is at `0x007B2EAC`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,032 | `bdc8bf69d75b7ff8354e12aa392416956a2afa04442488e7653e79b89ce62f1f` |
| Apollo-main component | 3,649,428 | `d90824df529385ae5fba464c88b0c1e4e7d145a939024632c0806c4462d68d00` |
| Core-source package | 4,427,882 | `3aa279193bf67b50a75ad5490a8cd2e22ffb32d36f6de1e5befe0a11368fe743` |

The recorded component and two ordinary fail-closed component builds are
byte-identical. Package A/B builds also match the independent in-memory
assembly pin. The 576,923-byte flash plan hashes to
`c7514451fc0447118aee048688e9d4e328ada948698c917dae747fc442d647a2`
and contains 808 placed, two unresolved, and five container-only records. Its
coarse ownership is 126,873 source, 87,496 generated, and 4,213,513 opaque
bytes.

Exact manifest/package ownership is separately 126,868 source, 87,653
generated, and 4,213,361 opaque bytes. The distinction is intentional: the
flash plan coarsens some ownership records, while the package census resolves
them byte-for-byte.

The compact repin moves nanopb text to `0x007B2C80`, the CmBacktrace adapter
to `0x007B2D0C`, and its helper to `0x007B2D1C` without changing their source
or provenance boundary. The old capacity leaf is absent. Qualification was
offline; no firmware was signed or flashed and no G2 hardware was operated.

## Prior phase-local FreeRTOS queue-message-count exact-root result

Homebrew Clang 22.1.8 produces the same production object pins as Apple Clang
21.0.0 when both use the reviewed flags including `-fno-ident`: the task
object is 852 bytes /
`24c8d8a8311ad6a094b0e92e048b0324320002d9d850441887b05ececbcc0453`,
and the ISR object is 856 bytes /
`a69c13094a7f4afcc65f48e660ccd09293a5409b6ec94f278eab9635c31139a7`.
Two compiles reproduce each object. Their extracted 50-byte and 34-byte text
sections are byte-identical across profiles and have zero text relocations.

Linux places the task leaf at overlay offset 126,032 / address `0x007B2F74`,
two alignment bytes at `[0x007B2FA6,0x007B2FA8)`, and the ISR leaf at offset
126,084 / address `0x007B2FA8`. The generated stock replacements hash to
`0dd88ba663317edbf9a515397f3369d4221f25889551189ff70a5b8bb68067d6`
and
`2ef6ffe002ec6b197643da1304921bbc422dc9beb124b23343f16bf187e303a1`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,118 | `db4f80dd7caa313de96580ce10050cba2ad07bc0b7495bbc3f122a29bf9dfefa` |
| Apollo-main component | 3,649,514 | `45ee630ef534a524d8f8dab01af2c38412f0fa9394e7a94d0ff4f781730465c2` |
| Core-source package | 4,427,968 | `44a43f3cb4d9e36acb9ab7c1064403a9786f6657f7f6a629dfd639db7e1aacc3` |

Exact Linux package ownership is 126,952 source, 87,715 generated, and
4,213,301 opaque bytes. Its coarser flash-plan classification is 126,957
source, 87,558 generated, and 4,213,453 opaque bytes. The cross-profile config
contains 642 functions, 591 patch sites, and 73 relocated leaves. The
preceding console values remain phase-local history. Qualification was
offline; no firmware was signed or flashed and no G2 hardware was operated.

## Prior phase-local nanopb `pb_skip_varint` exact-root result

Homebrew Clang 22.1.8 and Apple Clang 21.0.0 both reproduce the same 932-byte
production object with SHA-256
`651b45c3291a106f6e930129db85af7bbcba416f9ccc260f87b4d5a417eb53d4`.
The selected 36-byte text is byte-identical before relocation and hashes to
`7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b`.
Its only executable relocation is one `R_ARM_THM_CALL` at offset 18 to stock
`pb_read` at `0x0048F3BE`.

Linux appends two alignment bytes at `[0x007B2FCA,0x007B2FCC)` and places the
leaf at `[0x007B2FCC,0x007B2FF0)`. Relocated text hashes to
`09b1b218b4b222b284b44d433b5ae257e70c13b9cab13e7d53ca9168e7bcf27c`;
the generated `B.W` plus sixteen-NOP stock replacement hashes to
`f54c433a31f74f74b34709901da696d850b4dd2d0fb743b8166d49256c287303`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,156 | `e7f3d94e8a7253f761c5d535dba918b765c9f3f2aba82a5cdc5372bd0ebf9d62` |
| Apollo-main component | 3,649,552 | `160c431d1ff7ea9bd941583705fd2ebfb9cb6b7037298bf3d0bd8f2bd72dbd71` |
| Core-source package | 4,428,006 | `44adc5125db5e459bc0e32f258a02fbf2f564f8f4f739b542d7406741c046ab1` |

Exact package ownership is 126,988 source, 87,753 generated, and 4,213,265
opaque bytes. The 579,136-byte Linux flash plan hashes to
`b8b604173230837fddf9553eaf6307c47677404987ce8eec772bc2f815f0f986`
and contains 811 placed, two unresolved, five container-only, and 818 total
records. Its coarser package-envelope view is 126,997 source, 87,592
generated, and 4,213,417 opaque bytes.

The cross-profile config contains 643 functions, 592 patch sites, and 74
relocated leaves. nanopb 0.4.9 remains a compatibility selection within the
authenticated pristine 0.4.7–0.4.9 range, not proof of the vendor revision.
The preceding queue values are phase-local. Qualification was offline; no
firmware was signed or flashed and no G2 hardware was operated.

## Preceding littlefs `lfs_file_size_` exact-root result

Homebrew Clang 22.1.8 emits the same 20-byte unrelocated
`open_cfw_littlefs_file_size_private` text as Apple Clang, SHA-256
`1edf2a8aae0009f5fca77cb8ba1430c2bfa7e52181c4620841450cbc2cbb3683`.
Linux places it without additional alignment at
`[0x007B2FF0,0x007B3004)`. After its sole `R_ARM_THM_JUMP24` relocation binds
directly to the existing source-owned `open_cfw_littlefs_util_max`, the leaf
hashes to
`74544bcbc851e0164d33575a42b8fe3d9270ff4fc25b056fd7dc743a7410fc72`.
The generated replacement of `[0x004CE472,0x004CE48A)` is `e4f2bdbd` plus ten
Thumb NOPs, SHA-256
`faa50b6a896129aef410f74f4f4c333bc32f2e0d5604ed939d3cc6bd7519ae3a`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,176 | `45ddc376dc3943a1b2aaff981566cbd55a89197ddfe65ac368cedd6f607b4fd3` |
| Apollo-main component | 3,649,572 | `d8ae148bbb44df20a66fef2815ed2276d7bf1608a11ed833c44260e4178da4fb` |
| Core-source package | 4,428,026 | `dba4d48dccef97ad4b1559f239553b467632f6a546e0ec908977ea395b13f9b7` |

The 580,508-byte Linux flash plan hashes to
`a052ade1c8d9153a6f9fb14db33ba14dab1c42c5eca84b67c4446c7efaad1da6`
and contains 813 placed, two unresolved, and five container-only records. Its
coarse package-envelope accounting is 127,017 source, 87,616 generated, and
4,213,393 opaque bytes. The shared config now contains 644 functions, 593
patch sites, and 75 relocated leaves; the canonical Apple manifest contains
901 regions, including 579/85,686 generated entry-replacement,
178/3,437,320 official, and 94/124,492 source regions.

The preceding nanopb and queue results remain phase-local. The reused
BSD-3-Clause body comes from the authenticated littlefs v2.10.1
source-equivalent snapshot and adds no G2 block-device, format, or erase
authorization. Qualification was offline; no firmware was signed or flashed
and no G2 hardware was operated.

## Preceding FreeRTOS task-list initializer exact-root result

Homebrew Clang 22.1.8 and Apple Clang 21.0.0 emit identical 88-byte
unrelocated text for `open_cfw_freertos_task_lists_initialize`, SHA-256
`6710533445c9aac3904152a43147d0e9ba9bec7eff8e7c5c6b72007c4c301fdb`.
The exact-root Linux leaf is placed without new alignment at overlay offset
126,176 / `[0x007B3004,0x007B305C)`. Its six `R_ARM_THM_CALL` relocations at
offsets 14, 36, 46, 54, 62, and 70 all resolve to
`open_cfw_freertos_list_initialise`; relocated text hashes to
`dd4a36cadf6346d513ec039724a2a58309f443d31aad4e50858c5a64d95c04f6`.

The complete stock `[0x0045568C,0x004556E0)` replacement is `5df3babc`
followed by forty Thumb NOPs, SHA-256
`52fb57ebe49286360f1258cb2855a3b95abee1ed0a247e0cd3a3d6f6fc7d5e33`.
The sole original caller at `0x00454A20` is unchanged.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,264 | `62d8e21bec02a7505a39296f2e474e703b6a3989c252c6cda3fda43e12e7d236` |
| Apollo-main component | 3,649,660 | `5a098690012093defe0573e7f5c4cfb20ae79f77ff3aa88ce6adda3279c73764` |
| Core-source package | 4,428,114 | `0c446de88f84b8b81049b54efc94e0c40b411bfc9b2c8655cbf5b762bb846068` |
| Flash plan | 581,929 | `a13a7ffc624804bcc91484bf601e775cd14d081ca840715753af27fef2a633ad` |

The Linux plan reports 815 placed, two unresolved, and five container-only
records and classifies 127,105 source, 87,700 generated, and 4,213,309 opaque
package-envelope bytes. The cross-profile config is 645 functions, 594 patch
sites, and 76 relocated leaves. The preceding littlefs, nanopb, and queue
values remain phase-local. This was built and checked offline; no firmware was
signed or flashed and no hardware was operated.

## Preceding nanopb `pb_close_string_substream` exact-root result

Homebrew Clang 22.1.8 reproduces the same 968-byte target object and 36-byte
unrelocated text as Apple Clang. The common object SHA-256 is
`864cf56e2148b53a0938de80a05e25a81951adbb8ca147a0ddf6297968c126fc`;
the unrelocated text SHA-256 is
`5e6ee5f441e5ba91e0e0147b8453a31186f3ce4bd0efc114edda60f00093a51e`.
The sole relocation is an `R_ARM_THM_CALL` at offset 16 to
`open_cfw_nanopb_read`, resolved to reviewed stock `pb_read` at `0x0048F3BE`.

Linux places the leaf at overlay offset 126,264 / address `0x007B305C`.
Relocated text hashes to
`a90a09f0f98c5b4cf7d885af34c914ae5d492ac7352b5e359ba68ad482cb3044`.
The generated replacement for `[0x0048F7CA,0x0048F7F4)` begins `23f347bc`,
continues with nineteen Thumb NOPs, and hashes to
`bcffd3e5e32492e5c32143eac31bec47f2fabb91c8411a274eebd29e99f203f3`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,300 | `3a565aa2dd24d197e04a669bb11a1b12f39b4c8cc70344c55520c922df4964d9` |
| Apollo-main component | 3,649,696 | `1aa883832df0a09e0c540d4c31e93331053f05048baf149c3d5dba7725d19158` |
| Core-source package | 4,428,150 | `31a7850ca003235912a32e66a31397ccabcc3486b96e7acfde1086acfba3a1f1` |
| Flash plan | 583,414 | `b8654efdc30ec77fec4fff795d58782eb8fa853e5f1010989570388e2b02bdec` |

The exact-root plan contains 817 placed, two deliberately unresolved, and
five container-only/skipped regions, 824 total. Its coarse ownership is
127,141 source, 87,742 generated, and 4,213,267 opaque bytes. Linux builder
accounting is 126,482 source-owned bytes, 86,154 generated patch bytes, 32
wrapper bytes, and 3,437,028 opaque bytes. The cross-profile config contains
646 functions, 595 patch sites, and 77 relocated leaves.

The selected authenticated nanopb 0.4.9 snapshot is compatible with the exact
semantics present in pristine 0.4.7–0.4.9; it is not evidence of the vendor's
historical point release. Qualification was offline and does not establish
source provenance for retained opaque firmware.

## Preceding littlefs private rewind exact-root result

Homebrew Clang 22.1.8 emits the same 960-byte object and 16-byte unrelocated
text as the reviewed Apple compiler. The object and text SHA-256 values are
`c7398babd0a9adba9ea4a81c8221d8826f1aac166bebbee4307280778a1443bf`
and `46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b`.
The sole relocation is an `R_ARM_THM_CALL` at offset six to private seek at
`0x004CE3BC`.

Linux places the leaf at offset 126,300 / `0x007B3080`; relocated text hashes
to `9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1`.
The complete 18-byte stock replacement hashes to
`f014878435e10f6bf1feba6c78781bee5e0a8f15a9b47aa4cfd596cffb7d984b`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,316 | `eea387bf745530cb810166a4779e5b32de9578cdeb41643440a096334113995e` |
| Apollo-main component | 3,649,712 | `535f1d7117d36073b8153fea3334cc53c692671da91baca443e3bd82db35851d` |
| Core-source package | 4,428,166 | `6a08107f4bf3fbfcfa959056f121230488352ab5f1b89a3d2bfb07526c16776a` |
| Flash plan | 583,448 | `60bdc9a9bff4b70df9b88dcb3964ed13ccd0c77a91c48c9a6ad1c0077c8f46a9` |

The plan reports 817 placed, two unresolved, and five container-only records;
coarse ownership is 127,157 source, 87,760 generated, and 4,213,249 opaque
bytes. This is an exact-root offline replay, not a flashing or hardware claim.

## Preceding nanopb `pb_decode_fixed32` exact-root result

Homebrew Clang 22.1.8 reproduces the same 960-byte target object and 50-byte
unrelocated text as Apple Clang 21.0.0. Their SHA-256 values are
`499f6ec335b62a6af9a4f2370aaa5ef831a5ec2b3e8da99bcb6f7b8a4e83fedd`
and
`798f8f7cbed57f6ba11dad46a6de9d25cb1f1710eb4fa904d79b6fe449952a04`.
The only executable relocation is `R_ARM_THM_CALL` at text offset 10, bound to
stock `pb_read` at `0x0048F3BE`.

Linux places the leaf at overlay offset 126,316 / `0x007B3090`. Relocated
text hashes to
`53a1961d2df94674da6890611087ab865498084ced6a6f0c6850dcee23c7bf60`.
The complete 28-byte stock replacement is `22f37ebf` followed by twelve Thumb
NOPs and hashes to
`d6c11f5f1a5b6f89f12e30c476f27daf0301a2d17d7ad9bafd5039d0aa970085`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,366 | `4e9a1384d9e0de525b5c0cfda765d2dc01fe7e397058cda3a261907446b04ec3` |
| Apollo-main component | 3,649,762 | `2469216749e322db7dcaf5e7d0c34c0441f544226771dcc0024442945dc1ca9e` |
| Core-source package | 4,428,216 | `e09df2c48feea00a281e5a874eb06fc4381403f9d38cafd9f2efff04a8ef6476` |
| Flash plan | 584,883 | `96e3339d6740ad96ef15fb0888afb18ddfba958e2324f910e5d6be3f0b5fb633` |

The plan reports 819 placed, two unresolved, and five container-only records,
826 total. Its coarse ownership is 127,207 source, 87,788 generated, and
4,213,221 opaque bytes. Linux builder accounting is 126,548 source-owned,
86,200 generated patch, 32 wrapper, and 3,436,982 opaque bytes; 86,382 stock
bytes are replaced. The shared config contains 648 functions, 597 patches,
and 79 relocated leaves.

Exact-root reproducibility does not remove the stock read seam or prove the
vendor's nanopb point release: the source baseline remains authenticated
0.4.9 within the compatible 0.4.7–0.4.9 range. The replay was offline; no
image was signed or flashed and no G2 hardware was operated.

## Preceding littlefs `lfs_tag_type2` exact-root result

Homebrew Clang 22.1.8 reproduces the same 788-byte target object and ten-byte
relocation-free text as Apple Clang 21.0.0. Their SHA-256 values are
`8114a6a47e5e5f65517bc62afdfca88bae1c38961643a12940d62554a077887e`
and
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.
There are no undefined runtime symbols or executable relocations.

Linux places the leaf at offset 126,368 /
`[0x007B30C4,0x007B30CE)`, after two alignment bytes. The complete replacement
of stock `[0x004CAE90,0x004CAE98)` is `e8f218b900bf00bf` and hashes to
`84c933a2887b7027c2904be21d89be5ef671b3ec83f7f7160974aa8fe17dbd4d`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Apollo-main overlay | 126,378 | `12ebf0aef9e1ce61c6f5f151515a8c4245b1b353ca921dcddfc6b521cf8f870a` |
| Apollo-main component | 3,649,774 | `eeaca07a2c4bec75f4652e9f2853a75ff45684584d5e6074d99d112a41e5ddfc` |
| Core-source package | 4,428,228 | `caa150eda201d91c8ec6046f5a9017ab87e7ee936fe0f542957bff4efdd4b37f` |
| Flash plan | 586,282 | `64522f68968b3a063fef934c0304c3d37caaff21b7650aa6d31c10f25e2cbda8` |

The plan reports 821 placed, two unresolved, and five container-only records,
828 total. Its coarse ownership is 127,219 source, 87,796 generated, and
4,213,213 opaque bytes. Linux builder accounting is 126,560 source-owned,
86,208 generated patch, 32 wrapper, 3,436,974 opaque, 86,390 replaced stock,
and 182 in-place bytes. The shared config contains 649 functions, 598 patches,
and 80 relocated leaves.

The littlefs v2.10.1 source is a selected source-equivalent compatibility
baseline rather than proof of the vendor's exact checkout. Reproducibility
does not source-own the broader littlefs implementation or a G2 block-device
port. The replay was offline; no image was signed or flashed and no G2
hardware was operated.

## Preceding littlefs `lfs_tag_size` exact-root result

The exact-root replay qualifies the production dual-image
`lfs_tag_size` promotion. Fixed evidence is already closed: the main and boot
stock spans are `[0x004CAEB8,0x004CAEBE)` and
`[0x00410BC0,0x00410BC6)`, both contain `8005800d7047`, and complete-image
scans authenticate 15/14 direct callers without reviewed alternate or interior
ingress. The exact source authority is authenticated littlefs v2.10.1
`lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`.

| Item | Exact-root Linux value |
|---|---|
| Main leaf | offset `126424`, address `0x007B30FC`, patch `e8f220b900bf` |
| Boot leaf | offset `656`, address `0x00434708`, patch `23f0a2bd00bf` |
| Main overlay | `126430` / `8e252b96fd244107603046a4a0eb3ef17fe261e026bb52d793ccbbb764a5df56` |
| Main component | `3649826` / `a34fb1906c0b20702b7636866479b7680776aeda3cad7fb36a544bea78ffc6b8` |
| Boot overlay | `662` / `e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021` |
| Boot component | `149262` / `fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74` |
| Package | `4428320` / `70ec26aaf4ddb42ae04938edb4a54f3875c6d33a856e477cdf7acc461ebcff0d` |
| Flash plan | `599070` / `d40ee728ef3c5b5420aef232224ec178013a52d084d28ce9522b01f2387a3dc7`; `839 placed / two unresolved / five container-only` |
| Exact canonical source/generated/opaque ownership | `127305 / 87894 / 4213121` |

Effective flash-plan coarse source/generated/opaque ownership, if reported,
must remain separately
labeled as `127311 /
87888 /
4213121`; it is not interchangeable
with exact canonical ownership. The exact-root replay closes these fields;
tag-ID remains the settled preceding milestone. This offline qualification
authorizes no signing, flashing, filesystem mutation, reset, boot, or hardware
operation.

## Preceding nanopb `pb_decode_fixed64` exact-root result

Homebrew Clang 22.1.8 emits a 940-byte production-name object hashing to
`f447c5715142e7a5b2c144566ac3094a58727611e011137d440e8d549a2e329b`.
Its 30-byte, four-byte-aligned function text hashes to
`bfaf01f7496cce042c84c35708421508fbf2fa5acd9d9fcb209753901e09af10`
before relocation. It is placed at overlay offset 126,432 / `0x007B3104` after
two alignment bytes; resolving the sole `R_ARM_THM_CALL` to retained stock
`pb_read` at `0x0048F3BE` produces SHA-256
`4e067bc2e9e3cb63335507bd64f3e73321c24294ec3313c72f57cd801a9b8968`.

The 32-byte official entry becomes
`22f3aabf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf`.
The exact-root aggregate pins are:

| Item | Linux value |
|---|---|
| Main overlay | `126462` / `f5d4a4e441b1185001e031d1b9d319474ffd721c1280e1611e29f08169cb46cc` |
| Main component | `3649858` / `0d765ead02aa3d9981fe14b4aa8663bff57f12b307a2f9ce7e6d226225523a16` |
| Package | `4428352` / `75af4c1facb8c663cff2a8d4469625261ffa04d9c9587dc0db9ecf2c2f401b6d` |
| Flash plan | `599794` / `14644134ce433085cfba526710635ae6c1f769ab9cd90e27857da15779c3fc80`; 840/two/five |
| Exact source/generated/opaque | `127335 / 87928 / 4213089` |
| Coarse source/generated/opaque | `127343 / 87920 / 4213089` |

No bootloader homolog was authenticated; boot artifacts remain unchanged.
This was an offline exact-root replay with no signing, flashing, or hardware
operation.

## Preceding nanopb `pb_read` exact-root result

At this preceding milestone, Homebrew Clang 22.1.8 emitted the same 158-byte
unrelocated and relocated `open_cfw_nanopb_read` text as Apple Clang. The
relocated leaf hashes to
`8b3de44a2cf7ca2e07715c913db0fa454ef65cbc453366190b12736e455aa7a8`
and is placed at overlay offset 126,464 / `0x007B3124`, after two generated
alignment bytes. Its six absolute MOVW/MOVT relocations bind only the reviewed
private `buf_read` Thumb identity `0x0048F3A5` and the two runtime error strings
at `0x00787C70` and `0x0078B690`.

The complete stock entry `[0x0048F3BE,0x0048F454)` became `23f3b1be`
followed by 73 Thumb NOPs, SHA-256
`4dc433588344c12d1a0abfab8c5f1673c24f6702d8f285f67fb0fd8b8e6e3eab`.
All 13 external callers retained the stock entry address; no reviewed interior
or stored-pointer ingress existed. The milestone exact-root aggregate pins
were:

| Item | Linux value |
|---|---|
| Main overlay | `126622` / `990b4d60bff7764ed6f0400c1133fdfc2869624567e1539f1734f60c88c531b9` |
| Main component | `3650018` / `9d92d8a9aa41c3a274c1d28be05213def2994dcea2850eefefb96d796119e1bb` |
| Package | `4428512` / `0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9` |
| Flash plan | `601182` / `8ba103a92bcbfe060878c0091e6ef1608b3b5c2c55b1a94f5da8b4a2cf7fdcbc`; 842/two/five |
| Exact source/generated/opaque | `127493 / 88080 / 4212939` |
| Coarse source/generated/opaque | `127503 / 88070 / 4212939` |

At that milestone Linux main builder accounting was `126804` source, `86436`
generated patch,
`86618` replaced stock, and `3436746` opaque bytes. The manifest keeps 941
canonical Apple regions and collapses the alternate compiler-owned tail to one
coarse region as designed. No bootloader homolog was authenticated and boot
artifacts remained unchanged. The current exact-root result is the stream
constructor promotion immediately below. This replay was offline and performed
no signing, flashing, reset, boot, or hardware operation.

## Preceding nanopb `pb_istream_from_buffer` exact-root result

The reviewed `/Users/kalani/Repo/SybilSightABCD/openCFW` replay with Homebrew
Clang 22.1.8 emits a deterministic 972-byte object, SHA-256
`5622e997718fb1414b31fbc14d31dee25e99be05cd3df27e322f3c2b8d148fd7`.
Its 22-byte, four-byte-aligned function text hashes to
`6c23e37c9468d866db2e2cb6bf0ce8e103fb34df1078e740b4b8d5d799c257ff`
before relocation. The object has no allocated writable data. Its only two
executable relocations are `R_ARM_THM_MOVW_ABS_NC` and `R_ARM_THM_MOVT_ABS`
at offsets zero and four; both bind the canonical retained private `buf_read`
Thumb identity `0x0048F3A5`.

The linked leaf is placed at overlay offset 126,720 / `0x007B3224` and hashes
to `59438f30232883560f65ad4e58ff97c05dcdffdb6287fffcb7c1b79487df436d`.
The complete stock constructor `[0x0048F49C,0x0048F4B8)` becomes `23f3c2be`
followed by twelve Thumb NOPs, SHA-256
`902daf1332ace8eae1d3f71e324ddbc03ec2542d93530fa876f24228d40c86ed`.
All 30 callers continue to enter through the stock address while the returned
16-byte stream retains the callback identity above.

| Item | Exact-root Linux value |
|---|---|
| Apollo-main overlay | `126742` / `fa247345f47b279d1dcb4b1b0f86dca51dc10b432ab56ff4d57f93951669066d` |
| Apollo-main component/provider | `3650138` / `20e3de4270532b684b617689d44e551320da22fd9a94570b01d22f53ec8f27ed` |
| Core-source package | `4428632` / `c9f09923a8c97706f32aed0c0c7db455a9aed01eff06d968cf8be81ee552793f` |
| Flash plan | `603426` / `0573a3aa811b0beb9874ec0082638071d0b71bb07b43bfd3567ebbc14127d372`; 845 placed / two unresolved / five container-only |
| Exact source/generated/opaque ownership | `127623 / 88196 / 4212813` |

The shared config now contains 660 functions, 609 complete entry replacements,
and 91 relocated leaves. This is compile, relocation, packaging, and offline
analysis evidence only. No package was signed or flashed, and no G2 hardware
was reset, booted, or otherwise operated.

## Preceding nanopb `pb_decode_svarint` exact-root result

The reviewed `/Users/kalani/Repo/SybilSightABCD/openCFW` replay with
`/home/linuxbrew/.linuxbrew/bin/clang` 22.1.8 compiles the production source
twice to identical 968-byte objects, SHA-256
`866820ef347453a3cbf2feed221eeab0b571a9b79b6988cc17d2861b1aeaced5`.
The selected 50-byte, four-byte-aligned function text hashes to
`3617ea95d4a2cbabf3a1abb375e572323fffcebfa68cb4e19874cb4a831d9662`
before relocation. The only undefined symbol and only executable relocation
are `open_cfw_nanopb_decode_varint` and `+0x08 R_ARM_THM_CALL`; no allocated
writable section exists, and the sole eight-byte `.ARM.exidx` section hashes
to `01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d`.

After two alignment bytes, the linked leaf occupies overlay offset 126,744 /
runtime `[0x007B323C,0x007B326E)` and hashes to
`63e4707f5fd537094855d38f6b4df8578b77644c131e180db2e682d32fbc1fab`.
Its call resolves directly to the Linux source-owned unsigned decoder at
`0x007B2C80`. The complete stock span `[0x00490150,0x00490190)` becomes
`23f374b8` followed by 30 Thumb NOPs, SHA-256
`e6bb4ee4baec73757a5f465cf99a32e787fb25bd651b2b16e2e76fda4c6d18fd`.

| Item | Exact-root Linux value |
|---|---|
| Apollo-main overlay | `126794` / `be028b3e22b5952325965c029523dacb0b2d3bad3602c397de706a53708d88f0` |
| Apollo-main component/provider | `3650190` / `78ff4ac1538ad3d43076510f06a9ddb3ba1ca2a0f421d3778f96e2a40c6f1696` |
| Core-source package | `4428684` / `b5391623b98a886bf87989a5c28c5f500556866d08dbbff5c25535f6f707af06` |
| Component report | `1526818` / `9bc54ee3c66ddbbf4e3396143b05af0e156289c9802b6d6b5222d39c6828f2b5` |
| Package report | `2322` / `a54f2300f21b47519999fd5210f1fb2906410d8d6ee63630420ff018318db112` |
| Flash plan | `604150` / `5126f5582cbb6a260fccb13aa3b1259863a813867a3d4aac77c83dee2fccb348`; 846 placed / two unresolved / five container-only |
| Effective source/generated/opaque ownership | `127675 / 88260 / 4212749` |

The shared config contains 661 functions, 610 complete entry replacements,
and 92 relocated leaves. This is compile, relocation, packaging, and offline
analysis evidence only. No package was signed or flashed, and no G2 hardware
was reset, booted, or otherwise operated.

## Preceding nanopb varint32-pair exact-root replay

The reviewed exact root and Homebrew Clang 22.1.8 produce the complete
1,628-byte production object twice with SHA-256
`626893ac400caac8fa733f5740b272d218a1e32572fad4bfa636a4bce142c166`.
Private text begins at offset 126,796 / `0x007B3270`, its 16-byte literal at
127,018 / `0x007B334E`, and public text at 127,036 / `0x007B3360`. Both
functions emit authenticated eight-byte CANTUNWIND companions with exactly one
same-function `R_ARM_PREL31`; those metadata sections are deliberately
discarded from executable closure data.

| Item | Varint32-milestone exact-root Linux value |
|---|---|
| Apollo-main overlay | `127046` / `593833cbe89b7f195f97d0e9bef8b57c98c4efe4b7cf13a035b4604738c38364` |
| Apollo-main component/provider | `3650442` / `2712b0ca1feef4e75cb25c0d619814273d06d4aa82fbe85feb29dd874107c5ef` |
| Core-source package | `4428936` / `2a3c7b0298f3dcd52dc05fc3b0cbcf0bd3e282daa9c3b93ba47e4deff442865b` |
| Component report | `1540536` / `37f414b756c38766a2894dde6174efdb9ed174a8253071963d57c032b42f3592` |
| Package report | `2322` / `e79568709dcd979a2a06ed986b8fcc0d717bca88772e82e67d91ba4a475d048d` |
| Flash plan | `604887` / `de21f80249bcfda259e017512b8b25ba9e07437926cbe05d1e8e558f1177f424`; 847 placed / two unresolved / five container-only |
| Effective source/generated/opaque ownership | `127927 / 88516 / 4212493` |

The preceding signed-varint values above remain valid for their historical
milestone only. No image was signed or flashed and no G2 hardware was operated.

## Current nanopb skip-string exact-root replay

Homebrew Clang 22.1.8 emits the same 988-byte object
(`d2bdca5570c8e7a0ee1adfc9decfb3ad54f6c77abe7c7e3f05e0e3dd9f1c5bbe`)
and 34-byte text as Apple. Linux places the relocated leaf at offset 127,048 /
`0x007B336C`; its full-span patch hashes to
`738d3ad448d28a408c0aaa76f7c7188181966ac44bc22afe675bde4fd83a9f7d`.

| Item | Current exact-root Linux value |
|---|---|
| Apollo-main overlay | `127082` / `f24cf0e060530429679df9389571ffee397819dfa2c3abc00d26deb75a3e47ad` |
| Apollo-main component/provider | `3650478` / `5fe58e3af2a0b7fed55c6b7c33afbd1ac5c887860721b04859e2d49d81be828c` |
| Core-source package | `4428972` / `22117e0cd7d0b827a8c31d22eb509edb30651fef6a6308838a8220ff80f6c702` |
| Component report | `1545743` / `3e67859fefa8a82b615babb725cc662f957b3c3e902d6a26b74716841fd69182` |
| Package report | `2322` / `91c854c0a580bdd2cbc961a47b3f89943920c109b5baaa9a7e40a73ccb520fb5` |
| Flash plan | `605604` / `9da3d20004434bace4a5af3b88c720de1a38eb8b6cfda426f0d053309bbca327`; 848 placed / two unresolved / five container-only |
| Effective source/generated/opaque ownership | `127963 / 88548 / 4212461` |

This is current exact-root Linux production evidence, not pending or
provisional evidence. No image was signed or flashed and no hardware was
operated.
