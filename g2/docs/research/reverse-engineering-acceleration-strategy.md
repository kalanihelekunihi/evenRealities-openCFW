# Reverse-engineering acceleration strategy

## Evidence model

Training-set recollection and web research are candidate generators, not
provenance. A dependency identity becomes authenticated only after repository
evidence records the upstream object ID, tree/blob hashes, license, relevant
source span, configuration/ABI discriminators, and its relationship to stock
bytes. Exact compiler output is strong confirmation but is not required when
different toolchains preserve the same source semantics and ABI.

For a short candidate interval, the preferred workflow is:

1. use embedded paths, strings, constants, ABI shapes, and remembered project
   history to identify a repository and release/commit window;
2. query the upstream repository and release history, recording immutable Git
   object IDs rather than mutable branch names;
3. check out the bounded tags/commits into an external cache and hash the
   candidate source definitions;
4. compile the matrix with recovered macros, target ABI, optimization flags,
   and plausible compiler versions;
5. normalize relocations and addresses before comparing text, rodata, call
   topology, and semantic discriminators with stock;
6. classify the result as exact, equivalence interval, altered upstream, or
   merely source-compatible; never promote a remembered identity by itself.

This avoids decompiling functions that can be proven from authenticated
upstream source, while retaining a fail-closed distinction between exact
vendor provenance and a deliberate compatibility baseline.

## Tool lanes

| Lane | Use here | Adoption state |
|---|---|---|
| Ghidra 12.1.2 headless/PyGhidra | deterministic decompilation, p-code, data types, Function ID/BSim, scripts | installed; invoke with Homebrew OpenJDK 21 via explicit `JAVA_HOME` |
| `tools/ghidra/DumpFunctionDecomp.java` | reproducible one-function headless decompilation | added; raw-image loader/base/processor profile still to be scripted |
| `tools/generate_apollo_ghidra_chunks.py` | authenticated Apollo address tiling | added; emits the canonical 64 equal-byte halfword-aligned chunks and can derive a function-balanced 64-way tiling from a verified Ghidra corpus |
| `tools/run_apollo_ghidra_chunk_batch.sh` | analyze-once/reflink-clone Apollo decompilation | added; 64 Lorelei workers decompiled 7,370 discovered functions with zero failures in 142.780 s after one 156.280 s analysis; every input, range, status, log, and result is hashed |
| Rizin 0.9.1 | fast boundary, branch, raw Thumb, and ARCompact inspection | installed; exact-address `arc -b 16 -E little` verifies all 31 EM9305 calls, but global xrefs miss ARCv2 EM short-register/long-immediate boundaries |
| GNU ARC binutils 2.46 | authoritative ARCv2 EM instruction decoding and source-candidate object comparison | disposable Lorelei package; `elf32-littlearc`, `-mcpu=em`, and `-M cpu=em` correctly decode EM7D long immediates that ARC700/Ghidra/Rizin analysis misaligns |
| `tools/disassemble_em9305_arcompact.py` | authenticated stock-range ARCv2 EM disassembly | added and replayed on Lorelei; creates an ARCv2 EM carrier object, rejects ARC600 wrappers and unaligned/out-of-package ranges, then invokes GNU objdump deterministically |
| `tools/run_ghidra_shard_batch.sh` | manifest-driven parallel Ghidra isolation/export | added; current targeted 16-way Lorelei replay completed all shards in 18.042--18.299 seconds, 1.46x faster by mean shard time than broad auto-analysis; runner/configuration are now authenticated inputs |
| `tools/compare_em9305_sdk_archive.py` | relocation-normalized ARC archive-to-stock scanning | optimized with an equivalent unmasked-run anchor; enforced QP/C scan is 0.32 s on Lorelei; six known lanes plus two discovery rounds and boundary-qualified low-floor replay prove the 1,435-function scanner floor and fail closed on unknown relocation types |
| `tools/run_em9305_sdk_archive_batch.py` | authenticated parallel SDK archive census | added; 16 archives at 16 Lorelei jobs finish with zero failures, the largest in 12.228 s; runner/comparator/configuration/archive identities and reports are hash-manifested |
| `tools/analyze_em9305_sdk_discovery.py` | deduplicated per-function SDK map and coverage gate | added; enforces 1,146 new address/body fingerprints / 132,610 bytes, aliases, critical anchors, zero conflicts/overlaps, and emits the complete dynamic function map |
| `tools/analyze_em9305_sdk_link_order.py` | exact-neighbor section-order, vector-ABI, and authenticated short-prefix recovery | added; enforces 156 strict/NOP-aware ranges / 202 placements, four vector-resolved handlers, and six exact four-byte prefix leaves, raising exact coverage to 1,494 functions / 157,122 bytes while keeping low-byte, relocation-only, same-size-modified, and size-delta tiers distinct |
| `tools/compare_em9305_modified_sdk_functions.py` | relocation-masked comparison of placed modified bodies | added and replayed on Lorelei; pins nine symbols / 1,204 bytes, 942/1,008 matching compared bytes, per-function mismatch counts, firmware/archive/compiler identities, and report SHA-256 |
| `tools/compare_em9305_nop_aware_modified_sdk_functions.py` | independent comparison of the second same-size modified tier | added and replayed on Lorelei; pins 29 functions / 4,496 bytes and 3,815/3,868 matching meaningful bytes (98.630%) |
| `tools/compare_em9305_size_delta_sdk_functions.py` | GNU ARC opcode-sequence comparison of bounded size-delta placements | added and replayed on Lorelei; pins 13 functions / 3,940 stock bytes against 3,820 archive bytes, with 1,225 matched instructions and every per-function sequence ratio above 86% |
| `tools/analyze_em9305_residual_segments.py` | complete residual segment/status ledger | added; partitions 43,204 bytes into 264 vector, 1,812 alignment, 7,470 post-text data/table, and 33,658 unresolved code-or-mixed bytes with 1,083 per-segment hashes |
| Synopsys MetaWare T-2022.09 build 004 | exact compiler provenance for EM9305 SDK objects | identified from authenticated archive `.comment` sections; compiler is not locally available, but the embedded version/LLVM/target/`-Os` tuple replaces generic compiler guessing |
| GNU ARC GCC 16.1.1 | fast normalized builds of surviving QP/C source epochs | disposable Lorelei package; the complete eight-unit history builds 80 comparison objects in 12.63 seconds, while the stock-compatible lane builds 48 in 8.82 seconds at four jobs |
| `rz-ghidra` | Ghidra Sleigh and decompiler inside Rizin (`pdg`) | not installed; high-value next addition, pinned to a Rizin-compatible release |
| Google BinDiff | cross-build function matching and transfer of names/comments | evaluate after producing Ghidra projects for stock and compiled candidates |
| Ghidra BSim/Version Tracking | similarity search across the locally built release matrix | preferred native database lane before adding a service bridge |
| FACT | searchable/comparable firmware inventory and extraction plugins | optional; heavier Linux service, most useful across many firmware releases |
| RetDec signatures | library-generated signatures for statically linked code | optional secondary oracle; not authoritative for provenance |

The matched local/Lorelei benchmark and remote integration policy are recorded
in [`lorelei-re-acceleration-benchmark.md`](lorelei-re-acceleration-benchmark.md).
Lorelei now has a hash-pinned, user-local Ghidra 12.1.2/JDK 21 installation.
The tested default is 16 independent import/decompile workers in one SSH
command: eight parallel jobs completed 2.28x faster than the loaded local
workstation, while 32 concurrent jobs reduced per-task throughput. The Apollo
analyze-once/reflink workload is different: 64 workers completed its 64 chunks
in 142.780 seconds, versus 152.329 at 16 and 163.799 at 32, so that lane uses
all 64 logical CPUs. Small Rizin invocations remain
faster locally because Lorelei currently exposes an older Flatpak-bundled
Rizin with substantial process startup overhead.

Lorelei now also has a source-integration lane over the returned corpus. The
local dirty checkout is copied once into an isolated baseline under
`/var/tmp`, then Btrfs reflink clones provide one writable workspace per
non-overlapping task. Remote agents never edit the authoritative checkout and
never merge a remote Git branch. Each lane returns an explicit changed-file
list, tests, evidence, and file hashes; new files are transferred through an
encoded content boundary, hash-checked locally, and applied with reviewed
patches. Overlapping documentation is merged manually.

The first three-way replay ran LVGL, Cordio, and path-gap recovery in parallel.
It produced the production-excluded `lv_iter_create` mapping, a closed
36-path/114-function Cordio map, and seven independently witnessed missed
functions. The lanes passed 20, 24, and nine focused tests remotely; all
imported analyzers were then replayed against the separately returned local
corpus. Reusable task contracts live in `tools/prompts/apollo source-lane.md`.
This workflow permits remote source edits and tests while keeping local review,
production admission, and package ownership authoritative.

For EM9305, stock Ghidra lacks ARCompact support. Lorelei therefore carries a
disposable build of the Apache-2.0 ARC processor module from NSA Ghidra pull
request 3006 at commit `d3fbf109ada6d051750e973779170c1758622530`.
Its 44,816-byte `ARCompact.sla` hashes to
`61af75c6e9beb457b72c6d4a55dd2f6822921694be37a436ffa9b7b9f1941737`.
The module is adequate for bounded disassembly/decompilation but still emits
occasional constructor/p-code errors. Global Ghidra and Rizin analysis both
misalign some legal ARCv2 EM six-byte long-immediate forms. A disposable
Fedora `binutils-arc-linux-gnu` 2.46 package on Lorelei now supplies the
independent instruction oracle: its objdump SHA-256 is
`278eb56300a03b7b3b39b1742d32376b856aa26917077f548288d6ed826b10a2`, and
`-mcpu=em`/`-M cpu=em` resolves the missing forms. Exact-address Rizin still
validates branches. These tools are analysis-only, not vendored or accepted
as production dependencies. See the
[EM9305 audit](em9305-qpc-arcompact-audit.md).

A direct raw-binary `objcopy -B arc` conversion is explicitly excluded: it
sets the ELF machine to ARC600 and can misdecode the same long-immediate forms
despite an objdump `-M cpu=em` request. The repository wrapper obtains the ELF
header from an `-mcpu=em` GCC carrier object before adding the authenticated
firmware section, and verifies that objdump reports `architecture: ARCv2`.

Stock-facing semantic discriminators reduce the historical QP/C matrix to six
complete eight-file source epochs and three normalized code epochs. The
authenticated EM9305 SDK oracle selects QP/C v6.5.1, and its `lib_QPC.a`
directly matches 36 stock functions. Across six enforced and 48 discovery SDK
archives the relocation-normalized scanner plus independent entry checks prove
the 1,435-function scanner floor. Strict and NOP-aware exact-neighbor link
order, vector-ABI, and short-prefix recovery raise exact coverage to 1,494 functions /
157,122 bytes (74.504950% of the controller application) and
function-provenance identification to 167,684 bytes (79.513296%), while pinning the exact
MetaWare compiler tuple. The expanded census also selects the Packetcraft/EM
Bleu Bluetooth-5.4 controller artifact and `LL_VER_NUM=28992`; public r20.05c
is retained only as an older source comparator. GCC remains useful for source-history
discrimination, while archive comparison is the stronger stock-production
oracle. The prior 48-object interval still compiles in 8.82 seconds at four
Lorelei jobs and remains fail-closed historical evidence.

## Ghidra MCP evaluation

Ghidra itself has no bundled MCP server. Third-party options currently include
`13bm/GhidraMCP` (a smaller socket bridge), `bethington/ghidra-mcp` (broad GUI
and headless endpoint coverage; the previously listed `0xflux` repository is a
fork), and `clearbluejar/pyghidra-mcp` (PyGhidra/CLI orientation). Before
enabling one, pin its commit and transitive dependencies, review its
file/script/mutation endpoints, bind only to loopback, disable arbitrary script
execution by default, restrict file access to the openCFW workspace, and test
against a disposable Ghidra project. MCP-derived facts must still be exported
into deterministic repository analyzers and evidence files.

An isolated `2026-08-08` evaluation pinned PyGhidra-MCP `v0.2.5` at commit
`f29063b8636100b71e9c3aec61fe056827c556e4` (Apache-2.0; license SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`).
The resolved trial stack was PyGhidra-MCP 0.2.5, PyGhidra 3.1.0, MCP 1.29.0,
ChromaDB 1.5.9, and ghidrecomp 0.5.9 in a disposable Python 3.13 environment.
It successfully opened a project created by Ghidra 12.1.2 with the authenticated
`ARM:LE:32:Cortex`, `BinaryLoader`, and `0x00437FE0` base settings and exposed
20 initial MCP tools. The project binary listing worked over stdio.

Two constraints keep it out of the current fast path. Version 0.2.5 rejects
raw files whose only supported loader is `BinaryLoader`, so openCFW must create
the project with `analyzeHeadless` first. Its read, metadata, and decompile tools
also fail closed while Ghidra marks that project analysis-incomplete. Our
targeted `-noanalysis` multi-address script deliberately has that state and
returns bounded functions in about five seconds; forcing whole-image analysis
solely for MCP would be slower and would create a second persistent analysis
artifact. Python 3.13 also emitted an unresolved-forward-reference warning in
`pydantic-settings`, although server startup and project listing succeeded.

The adoption decision is therefore **defer, not reject**: use the pinned MCP
server later against a disposable, fully analyzed project when semantic search,
interactive cross-references, or repeated multi-tool exploration amortizes the
analysis/indexing cost. Keep targeted headless scripts as the production lane
for already authenticated addresses. No Ghidra/Rizin MCP server is registered
in the current Codex session.

Primary project references:

- <https://github.com/NationalSecurityAgency/ghidra>
- <https://github.com/rizinorg/rz-ghidra>
- <https://github.com/google/bindiff>
- <https://github.com/13bm/GhidraMCP>
- <https://github.com/bethington/ghidra-mcp>
- <https://github.com/clearbluejar/pyghidra-mcp>
- <https://github.com/fkie-cad/FACT_core>
- <https://github.com/avast/retdec>

## Immediate application

The nanopb defaults helper demonstrates this hybrid lane: upstream knowledge
identified the function shape, Rizin authenticated the 166-byte boundary and
seven calls, and the pinned 0.4.9 source span reduced the unknown closure to
three named helper families. Ghidra headless then independently recovered the
same control flow and ABI from the raw image. Next, preserve a disposable
analyzed project, generate decompilation/p-code artifacts for the remaining
iterator and dispatcher helpers, and compare locally compiled candidate
objects where source/configuration hashes alone do not settle the result.

For a function whose boundary is already authenticated, prefer raw import with
`-noanalysis` plus `tools/ghidra/DumpFunctionDecomp.java`. The adjacent
`pb_field_set_to_default` query completed in about five seconds and recovered
the required control flow and ABI accesses. Escalate to full-image analysis,
BSim, or BinDiff only when discovery, cross-references, or comparison requires
the larger analysis database.

The first release-matrix proof fetched only the four peeled nanopb commits in
the plausible interval and hashed the exact definition span. This verified an
identical 0.4.7--0.4.9.1 function without compiling every release. Use builds
when source/configuration hashes do not already settle the candidate.

`DumpFunctionDecomp.java` now accepts multiple function addresses. One raw
noanalysis import decompiled seven iterator functions in 6.3 seconds, avoiding
seven JVM/project startups and the roughly four-minute whole-image analysis.
Use multi-address batches for contiguous authenticated clusters, then export
the recovered boundaries and topology into a fail-closed Python analyzer.
