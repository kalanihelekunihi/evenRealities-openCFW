# Building and verifying openCFW

Every target runs through the root [`Makefile`](../Makefile), or through
`./make.sh` from any directory. Each device keeps its own Makefile, which
`make -C g2` and `make -C r1` run directly. Every gate fails closed: a
hash, size or pin mismatch aborts the build.

```sh
./make.sh help
./make.sh test          # G2 tool tests + R1 corpus check; no vendor inputs needed
```

## Prerequisites

| Need | For |
| --- | --- |
| Python 3.9+, GNU make, Clang with ARM cross-compilation support, GNU ARM linker (`arm-none-eabi-ld`) | hybrid build |
| Git with submodule support | `third-party/` pins |
| The tools in [`../tools/bootstrap/`](../tools/bootstrap/README.md) | decompilation and byte matching; see [`tooling.md`](tooling.md) |
| Docker, existing ARM GNU GCC 12.2 and 9-2020-q2 caches, pinned PDL/nRF5 SDK headers | selected license-free GCC providers |
| Original producing compilers | optional compiler-comparison research; not invoked by the default license-free build |

## Versioned firmware mirrors

The versioned G2 and R1 release mirrors are tracked under
`g2/blobs/official/g2-<version>/` and `r1/blobs/official/r1-<version>/`.
Each directory includes release metadata and `SHA256SUMS` alongside its
firmware assets. See [`LICENSE`](../LICENSE) and [`NOTICE`](../NOTICE) for
licensing terms and boundaries.

## Inputs that are not tracked

| Input | Where it goes | Identity record |
| --- | --- | --- |
| Additional R1 captured reconstruction images (bootloader, UICR, APPROTECT) | `r1/blobs/official/2.2.6.0009/` | [`PROVENANCE.md`](../r1/blobs/official/2.2.6.0009/PROVENANCE.md) |
| nRF5 SDK 17.1.0 and R1 archive sources | any absolute cache directory | [`../third-party/fetched/`](../third-party/fetched/README.md) |
| Upstream libraries | `third-party/upstream/*` | `git submodule update --init --depth 1 <path>` |
| Toolchains and SDK caches | `vendor-cache/` | see [Local inputs](#local-inputs) |

## Targets

| Target | What it does | Needs |
| --- | --- | --- |
| `./make.sh sources-check` | every file in `g2/src` and `r1/src` is listed in its `sources.json` once, and every unit exists | nothing |
| `./make.sh sources` | compiles every reconstructed source unit, checks each link group for duplicate strong symbols, composes ARM relocatables | Clang, `arm-none-eabi-ld`, Docker + `vendor-cache/` for codec, EM9305 and GCC units |
| `make -C g2 source-link` | strictly links the seven G2 source-build relocatables into ELFs and binary payload candidates; Apollo main uses an uncalibrated C fuel-gauge candidate | a fresh G2 `sources` report and the same open toolchains |
| `./make.sh sources-qualify` | compiles the ARM units and selects functions whose bytes equal the stock payloads at their anchors | as `sources`, plus the official payloads |
| `./make.sh g2-test` | tests for the kept G2 tools; tests that read payloads skip when they are absent | nothing |
| `./make.sh g2-reference` | repacks the six official payloads into the byte-identical reference EVENOTA | G2 payloads |
| `./make.sh g2-verify` | reference build, manifest verification and research-corpus authentication | G2 payloads |
| `make -C g2 research-corpus` | authenticates `g2/research/` | nothing |
| `make -C g2 ghidra-harvest` | re-exports Apollo pseudocode from an analyzed Ghidra project | Ghidra, JDK, G2 payloads |
| `./make.sh r1-test` | structural check of the R1 decompilation corpus | nothing |
| `./make.sh r1-verify` | adds the exact-byte R1 image oracle | R1 images |
| `./make.sh r1-source-link` | compiles every R1 source unit, then strictly links and exports checked application and bootloader regions plus separate boot UICR words | R1 source inputs, Clang, Arm GNU tools and cached SDK headers |
| `./make.sh r1-source-regions` | builds those regions and exports a sparse Intel HEX containing only the checked C-linked application, bootloader and UICR words | same as `r1-source-link`; each output directory must be fresh |
| `make -C r1 vendor-audit ...` | authenticates the fetched R1 archives and FreeRTOS/CMSIS/CmBacktrace submodules | fetched cache, initialised submodules |
| `./make.sh third-party` | checks every initialised submodule is at its pinned commit | nothing |
| `./make.sh tools` | lists the pinned analysis tools | nothing |

`g2-reference` proves the container format and payload identities. It does not
reconstruct source. `build`, `g2-build`, and `r1-build` compile selected source
providers through the hybrid path described below. The byte-identical C builds are defined phase by phase in
[`roadmap.md`](roadmap.md) and gated by
[`../g2/workflow/PROCEDURE.md`](../g2/workflow/PROCEDURE.md).

## Reconstructed source build

`g2/src/` and `r1/src/` hold every reconstructed source; each tree's
`sources.json` lists the units, the toolchain and the exact flags each one
compiled with when the experiments were merged on 2026-10-21. The fields are
described in [`../g2/src/README.md`](../g2/src/README.md).

```sh
./make.sh sources-check
./make.sh sources SOURCES_OUT=build/sources-$(date +%Y%m%d)
```

`tools/build/sources.py build` writes one object per unit, a per-payload
relocatable for the ARM link groups, and `report.json` with every command,
input hash, defined/undefined symbol set and failure. It exits non-zero when a
unit fails that the manifest does not record as `"expect": "fails"`, or when
two linked units define the same strong symbol. Docker units run in one
container per toolchain. A full build takes about eight minutes.

A unit can select a dependency graph from its compiled object with
`"retain": {"linker": "arm-none-eabi-ld", "symbols": ["entry", "state"]}`.
The named roots must be defined in that object. A relocatable section-GC link
keeps the roots and their dependencies; the original compiler object, its
symbol inventory, the selection command and the selected object are recorded.
Definition and import checks use the selected graph. Missing roots, failed
selection or invalid output fail the unit and never publish the full object
as a fallback. Per-function/data sections are needed to discard unrelated
definitions; remaining duplicates are still errors. This is composition
selection, not firmware byte qualification.

Generated units keep their `{gen}/…` manifest identity for frontier matching,
then compile from `build/generated/<device>/…`. Qualification records and
selected-plan metadata retain that identity as `manifest_source`; the firmware
builder regenerates these inputs before compiling selected providers. See the
[generated-input qualification check](../r1/docs/reference/generated-qualification-review.md).

Compiling is not byte identity. `sources-qualify` (`qualify_sources.py`) reads
the same manifests, compiles each ARM unit and selects only whole functions
whose bytes equal the stock payload at an anchored address; the hybrid
`source-plan.json` is built from those selections.

G2 final source linkage is a separate, strict step. It validates the source
report against current inputs, links each payload, writes ELFs and binaries,
and records hashes in `link-report.json`. Apollo main now uses a source-only,
uncalibrated fuel-gauge candidate. The final link does not load the Nordic
object archive, but the candidate has not been validated against battery
measurements or physical hardware:

```sh
make -C g2 source-link SOURCES_OUT=build/g2-current \
  SOURCE_LINK_OUT=build/g2-source-images
```

The final linker accepts the architecture-specific assembly units registered
in `sources.json`. A successful link alone does not establish whole-artifact
coverage, all-C code, correct hardware behavior, or an OTA package.

The codec A link emits a source-built BINH stage-1 load, XIP and SRAM loads,
and a C-generated NPU command stream as separate regions. To package them
into BINH A, supply a declared 120,800-byte weight asset and a JSON provenance
file whose `sha256` matches that asset. With codec B selected too, the same
link writes a codec FWPK candidate. Select `--bundle-candidate` with all seven
G2 payloads to assemble a six-component EVENOTA candidate using the recovered
container metadata:

```sh
python3 tools/build/link_g2_sources.py \
  --source-out build/g2-current \
  --out build/g2-source-candidate \
  --codec-a-weights build/declared-model/weights.bin \
  --codec-a-weights-provenance build/declared-model/provenance.json \
  --bundle-candidate
```

The weight asset is external to the C build and must have an independently
established source before the result can count toward source completeness.
The link report records both its digest and provenance, along with each OTA
component's digest and whether the bundle matches the locked target. The
packaged image is only a candidate until model behavior, hardware startup and
byte equality are verified.

For a read-only comparison with the authenticated stock components, run:

```sh
python3 g2/tools/compare_source_candidate.py \
  --candidate build/g2-source-candidate/g2-source-candidate.evenota.bin \
  --link-report build/g2-source-candidate/link-report.json \
  --out build/g2-source-candidate-comparison/report.json
```

The report lists size
deltas and same-offset byte matches for all six components, and separately
checks the codec KWS command window. Same-offset matches are diagnostic only:
changed section placement can shift a correct function, so the report is not
a source-coverage or behavioral proof.

`r1-source-link` links each participating R1 application object with the recovered
GNU memory layout and toolchain C/runtime libraries. The strict linker adapts
the source-owned log and SDK observer registries to final flash/RAM addresses,
keeping their record-size assertions. It does not pull in stock
executable regions or suppress unresolved references. Use fresh output paths
for each attempt, for example:

```sh
./make.sh r1-source-link R1_SOURCE_OUT=build/r1-source-try1 \
  R1_LINK_OUT=build/r1-link-try1 R1_BOOT_LINK_OUT=build/r1-boot-link-try1
```

The linker receipt and complete diagnostic log are written even when this
target fails. In the latest 2026-11-11 1,045-unit source checkpoint, all 963
application and 82 bootloader units compile and compose; `sources-check`
records 834 R1 source files and none unbuilt. The strict
application link now resolves every reference, places the 512-byte vector
table at flash origin, and uses 694,120 of 696,320 available flash bytes.
The strict bootloader link also passes. These receipts are
`build/sources-r1-event-dispatch-ordered-20261111/report.json`,
`build/r1-link-event-dispatch-ordered-20261111/report.json` and
`build/r1-boot-link-event-dispatch-ordered-20261111/report.json`. The linkers verify
that all 941 participating application units and 82 bootloader units come
from repository or generated `.c` files with matching source/object hashes;
the application map has no archive members.
The application vector now starts MSP at the linker RAM top `0x20040000`:
the old stock pointer `0x2003beb8` fell 1,720 bytes inside the relinked
`.bss`. The C vector unit reserves an 8 KiB MSP stack, and the strict link
checks its lower limit stays above static data. Current static RAM ends at
`0x2003c570`, leaving 6,800 bytes before the reserved stack.
The bootloader receipt also checks its existing 16 KiB heap and 16 KiB MSP
reservations against linked RAM bounds.
The strict linkers now also export checked raw regions: `application.bin`
starts at `0x27000` and is 694,244 bytes; `bootloader.bin` starts at
`0xf8000` and is 23,024 bytes. The bootloader export supplies separate
four-byte UICR words at `0x10001014` and `0x10001018`, rather than padding
the raw region across that address gap. The same strict-link receipts record
the raw image hashes. These are region
artifacts, not a complete installable bundle: SoftDevice, settings/MBR pages
and package metadata are outside the two raw images.
`r1-source-regions` also emits a sparse `r1-source-regions.hex` and a
provenance report after checking that both link receipts came from the same
source build, their image hashes still match, the UICR words are exact, and
the ranges do not overlap. It preserves the gaps rather than filling them;
the HEX excludes the same external SoftDevice and settings content
([source-region review](../r1/docs/reference/source-region-hex-review.md)).
The NADT calculation root passes bounded stock-output replay through 100
fresh direct and calibrated input calls at 25, 50, 100 and 200 Hz. The [NADT replay review](../r1/docs/reference/goodix-nadt-root-replay-review.md)
records the comparisons and limits; 2,072 flash bytes remain for changes.
The link excludes stock executable regions but does not establish byte identity or complete behavior
([direct-link and size review](../r1/docs/reference/application-source-link-review.md)).
The reset entry and five fault-vector adapters have C source. The R1
manifest also compiles its bootloader startup vectors from C; some R1 C files
still include `naked` declarations. A source scan including headers finds 23
`__asm__` tokens on 19 lines across 8 R1 files, so the current link is not yet an
assembly-free firmware. The Goodix wear hook is now an isolated ordinary C
unit with a frame-pointer flag; its paired stock/C replay passes and the
other generated hook functions match their prior object bytes.
The GoMore packed consumer's raw frame bridge now uses checked C stack
allocation; its stock/C and later provider-chain replays pass.
The Goodix I/O dispatcher now has its own C unit, with all other generated
hook function bodies unchanged. Its fixed-frame transfer still uses assembly.
The application map now has zero archive members. Its last prebuilt Newlib
member was `strcpy`, used by Segger RTT; the existing R1 libc source unit owns
that function in C. The strict app linker rejects future archive members.

## Local inputs

`vendor-cache/` is ignored by Git and holds toolchains and archives that are
authenticated by hash where they are used:

| Path | Contents | Provision |
| --- | --- | --- |
| `vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update`, `nRF5_SDK_17.1.0_ddde560`, `newlib-source-6d79e0a`, `st-lis2dw12-*` | R1 GCC, SDK and library sources | [`../third-party/fetched/README.md`](../third-party/fetched/README.md) |
| `vendor-cache/g2/touch-gcc-matrix/` | Arm GNU 10.3/11.3/12.2 Linux toolchains and `pdl-input/` used by the touch PDL providers | release URLs and hashes in `tools/build/touch-gcc-acquisition.json` |
| `vendor-cache/g2/touch-gcc-14.2/` | Arm GNU 14.2.Rel1 and its `pdl-input/` | Arm GNU release archive |
| `vendor-cache/g2/csky-abiv2-gcc-6.3/` | C-SKY ABIv2 V3.10.15 GCC 6.3 (GX8002) | `third-party/downloaded/install-csky.py` |
| `vendor-cache/g2/arc-gnu-2026.03/` | ARC GNU 2026.03 (EM9305) | `tools/build/fetch_arc_toolchain.py` (`tools/build/arc-toolchain.json`) |

The Docker image `opencfw/iar-base:10.10.2-local` runs the C-SKY and ARC
compilers; `ubuntu:24.04` runs the Linux Arm GNU builds through
`tools/build/linux_gcc.py`. The entries may be symlinks to an existing cache.

## When a target fails

- **`cannot read ... provider` or `official payloads not present`:** the
  untracked inputs are missing. Put them where the identity record says.
- **A digest mismatch** means the input is not the pinned artifact. Do not
  re-pin to make it pass. The target identities are fixed.
- **`not at pinned commit`** from `third-party`: a submodule was moved. Run
  `git submodule update <path>`, or record a deliberate upgrade as its own
  change together with the evidence for it.

## Hybrid firmware build

The default `./make.sh` and `./make.sh build` targets use the license-free
Clang/GNU source plan through `open-build`. They do not invoke IAR's license
checkout. `open-build` is an explicit name for the same default path.

```sh
./make.sh                               # default license-free hybrid build
./make.sh open-build                    # explicit name for the same build
./make.sh g2-build HYBRID_OUT=build/g2-hybrid
./make.sh r1-build HYBRID_OUT=build/r1-hybrid
./make.sh hybrid-test
./make.sh g2-reference                  # explicit stock-only reference repack
```

Outputs must go to a fresh directory. The default source plan executes **72
compiler invocations** over 69 source files and consumes **160 exact provider
regions**: 22 Apollo main bodies, 23 touch PDL bodies, one CASE body, 60 R1
application bodies and 54 immutable R1 data objects. These supply 5,585 stored
bytes from freshly compiled source,
including literal pools and identified assembly providers. Use the generated
coverage report for the smaller C-instruction count; source-owned bytes and
C executable bytes are different measurements.

The selected providers include LVGL copies, BLE/Nordic/FreeRTOS leaves, native
charger/GXT/ST25/YHM/watchdog leaves, formatter output, GPIO/clock/flash/SCB/MSCLP
routines and a CASE critical-section body. The mnemonic delay primitive and
startup/interrupt-mask assembly are separately classified. No opcode arrays or
verification-only endpoints supply provider instructions.

The source plan is `tools/build/source-plan.json`. Every build invokes its
compilers afresh, discovers and hashes consumed headers, verifies inputs before
and after compilation, requires explicit native bindings for selected
relocation-bearing bodies, checks exact sizes and region hashes, and inserts bytes extracted from the fresh ELF
objects. A selected provider failure aborts; it never silently falls back to
stock. The objects, extracted provider files, compiler identities, input hashes,
commands and logs are retained in the output directory. Other object functions
are not counted as source-built firmware.

The original qualification pass tested 7,341 compiler configurations across
2,402 distinct source/payload pairs. `tools/build/source-qualification.json`
records the source inventory and outstanding failures. Follow-up passes tested
63 touch GCC configurations and 1,268 R1 GNU GCC configurations. These are build
experiments, not source-completion percentages. **This does not establish
that every finished source provider is integrated.** Many behavior-tested bodies
still differ in size/instructions or need production relocations, stock ABI,
shared-data placement or a compatible compiler. They remain integration debt
and are pulled through. The current selector accepts anchored, whole-function exact matches, either
relocation-free or linked using unambiguous recorded native function addresses.
Unique native-entry matching can recover missing aliases and scalar linker
bindings from original literal/branch relocations. It requires sufficient fixed
instruction bytes, a unique inventoried entry and exact equality after a fresh
source compile/link. Ambiguous matches are rejected. Additional architectures
and dependency-rich sources still need further qualification.

The build authenticates the cutting manifests and official inputs, assembles
each payload, and packages the six G2 payloads as the locked EVENOTA. R1 output
is `payloads/application.bin`, the locked 2.2.6.0009 application OTA. It excludes
the resident bootloader, SoftDevice and UICR; it is not a whole-device image.
Full-source completeness and hardware behavior remain unproven.

`build-report.json` records exclusive half-open file-offset regions, hashes,
blockers and byte totals for `source-built`, `binary-pull-through`,
`vendor-binary`, and `resource-file`. Source rows identify the selected symbol,
extracted file and compilation receipt. Resource rows identify their kind and
evidence; `resource_totals` separates fonts, images, descriptors, strings, lookup
and DSP tables, model weights, configuration and container metadata. A binary
region can contain both code and unclassified data; it is not an executable-byte
census. Shared ranges are counted once, and source/resource overlap is rejected.

The resource catalog identifies **11 corroborated custom font roots**, covering
**204,748 unique stored bytes**: descriptors, cmaps, Unicode lists, glyph
descriptors, bitmap stores and the opacity palette. Existing structural and
consumer evidence identifies these ranges; it does not prove live rendering.
Resource files preserve their exact storage encoding and are consumed in the
assembled output. The catalog also includes 428 images and their descriptors,
known G2 text/tables/weights, and R1 startup strings/configuration. R1 has no font
claim in this catalog. Compressed mixed code/data initializers and vector tables
remain pulled through instead of being labeled non-executable resources.
`resource-inventory.json` preserves the font qualifications and exclusions.

To repeat discovery without changing firmware sources or evidence:

```sh
python3 tools/build/qualify_sources.py --out build/source-discovery \
  --optimizations recorded Os Oz --link-functions --match-functions
python3 tools/build/qualify_sources.py --profile touch-gcc \
  --out build/touch-gcc-discovery --link-functions --match-functions
python3 tools/build/qualify_sources.py --profile r1-gcc \
  --out build/r1-gcc-discovery --optimizations recorded Os O2 Og --link-functions
python3 tools/build/catalog_resources.py
```

Discovery writes a proposed `source-plan.json` and compilation audit below its
fresh output directory. Review that proposal before replacing the checked-in
plan. `--source-plan PATH` selects another reviewed plan for a build. The
resource catalog generator validates every evidence range against authenticated
payload bytes and splits overlapping same-kind claims into exclusive ranges;
conflicting resource classifications abort.

The production CLI defaults to `--compiler-mode license-free` and currently
accepts only that mode. It admits Clang and fingerprinted ARM GNU GCC through
the repository driver; it rejects arbitrary legacy `--recipes` commands because
those do not declare their compiler. The low-level cutting helpers retain recipe
support for tests, but those commands are not the production license-free path.
The compiler-mode receipt is included in `build-report.json`. No IAR activation
or proprietary compiler invocation is performed by this build.



## C instructions versus executable and non-executable pull-through

Every build writes `coverage.json`, `coverage.csv` and `coverage.md`.
`./make.sh coverage HYBRID_OUT=build/hybrid` displays the Markdown summary.
The denominator is the **stored G2 OTA bundle** (4,301,227 bytes) plus the
**R1 application OTA** (646,408 bytes). Their combined denominator is
4,947,635 bytes. Missing R1 resident images, external NOR and expanded RAM
images are excluded; compressed content is never counted twice.

The categories form an exclusive partition: C-compiled executable bytes,
identified source assembly instructions, compiled literal/data bytes,
confirmed executable pull-through, confirmed non-executable pull-through,
compressed initializer pull-through, unclassified pull-through, and generated outer-container metadata. ELF ARM
`$t`/`$a`/`$d` mapping symbols separate compiler instructions from literal pools.
Known wholly handwritten assembly providers do not count as C instructions.
C translation units may still contain intrinsics or inline assembly.

The existing G2 classification baseline and authenticated resource catalog
provide conservative code/data claims. Function-inventory envelopes are
reported separately as an **estimate** because they can include literal pools
and data; they do not promote unknown bytes to confirmed instructions. A complete
three-way executable/data/source percentage is therefore **not yet proven**.
The report exposes unclassified bytes instead of silently assigning them to
executable or non-executable pull-through. Percentages in the confirmed
pull-through categories are lower bounds.

`tools/build/integration-status.json` explicitly records that not all finished
source is integrated, and fallback includes both implementation and integration
debt. The installed IAR 10.10.2 container failed an actual compilation because
licensing is unavailable. Stock-compatible IAR/Arm Compiler/MetaWare versions,
remaining source, ABI and placement qualification remain requirements. The touch
GCC profile uses the existing authenticated Linux GCC 12.2 toolchain in Docker,
with read-only inputs and a writable build directory. It does not activate any
license. A successful source build or exact container hash is not hardware proof.

### Remaining-byte evidence

`remaining-classification.json` and `.csv` partition every byte still classified
as unresolved. They distinguish byte-verified disassembly observations, function
envelopes, prior candidate correspondences, accelerator command streams, mixed
compressed content, and bytes with no finer evidence. These are evidence tiers,
not a new executable/non-executable claim: disassembly can decode literal pools.
The summary reports both byte counts and percentages of stored firmware.

`python3 tools/build/catalog_disassembly.py` reauthenticates the existing G2
instruction ledger and each referenced instruction artifact, checks original
payload bytes, and produces the compact `disassembly-evidence.json` catalog.
Each build checks the catalog's payload and span hashes again. R1's existing
instruction listing is checked directly. This operation creates no decompilation
or firmware implementation.

GNU GCC qualification for existing G2 source can be repeated with
`python3 tools/build/qualify_sources.py --profile g2-gcc --optimizations Os --link-functions --match-functions --out build/g2-gcc-discovery`.
Nonmatching code remains integration debt even when its bounded behavior tests
pass. Exact equality is required after compilation and placement; replacing
compiler instructions with original opcode bytes is not a source provider.

`python3 tools/build/qualify_data.py --out build/r1-data-discovery` qualifies
existing, explicitly reviewed R1 calibration, ctype and floating-point lookup
objects. Data providers must be immutable, non-executable ELF objects without
relocations, have unique complete placement, and pass the same fresh compile
and byte-identity checks. Their bytes are reported as compiled non-executable
data. Writable state and BSS are not emitted into the stored image by this path.

The 20,300 stored bytes of compressed G2 initializers are separately accounted
from confirmed non-executable pull-through. Their expanded RAM contents may
include executable code; storage compression does not establish their runtime
classification. They remain binary providers, not resource-file providers.

Short-function placement qualification uses an independently named native entry,
checks every non-relocation byte, recovers only existing ELF scalar relocation
bindings, and requires full equality after linking. It does not relax unique
whole-image matching. Repeat it against a discovery compilation directory with
`python3 tools/build/qualify_placements.py --compilation build/source-discovery/compilation --out build/placement-discovery`.
Two additional R1 providers (18 instruction bytes) qualified through this path.
The GNU G2 pass compiled 2,112 of 2,171 configurations; its 12 exact regions were
already selected. Sixty-six hard-float configurations added no exact regions.
