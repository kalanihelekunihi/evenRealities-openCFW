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

## Targets

| Target | What it does | Needs |
| --- | --- | --- |
| `./make.sh g2-test` | tests for the kept G2 tools; tests that read payloads skip when they are absent | nothing |
| `./make.sh g2-reference` | repacks the six official payloads into the byte-identical reference EVENOTA | G2 payloads |
| `./make.sh g2-verify` | reference build, manifest verification and research-corpus authentication | G2 payloads |
| `make -C g2 research-corpus` | authenticates `g2/research/` | nothing |
| `make -C g2 ghidra-harvest` | re-exports Apollo pseudocode from an analyzed Ghidra project | Ghidra, JDK, G2 payloads |
| `./make.sh r1-test` | structural check of the R1 decompilation corpus | nothing |
| `./make.sh r1-verify` | adds the exact-byte R1 image oracle | R1 images |
| `make -C r1 vendor-audit ...` | authenticates the fetched R1 archives and FreeRTOS/CMSIS/CmBacktrace submodules | fetched cache, initialised submodules |
| `./make.sh third-party` | checks every initialised submodule is at its pinned commit | nothing |
| `./make.sh tools` | lists the pinned analysis tools | nothing |

`g2-reference` proves the container format and payload identities. It does not
reconstruct source. `build`, `g2-build`, and `r1-build` compile selected source
providers through the hybrid path described below. The byte-identical C builds are defined phase by phase in
[`roadmap.md`](roadmap.md) and gated by
[`../g2/workflow/PROCEDURE.md`](../g2/workflow/PROCEDURE.md).

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
