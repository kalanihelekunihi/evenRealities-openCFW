# Reverse-engineering acceleration benchmark

Measured on the `lorelei` Threadripper host; see
[`../../research/corpus/PROVENANCE.md`](../../research/corpus/PROVENANCE.md).

Status date: 2026-08-08

## Durable return corpus

All unique result material returned from Lorelei, plus the compact result files
that previously existed only on the remote host, is now repository-owned at
`research/corpus/`. The 12,684,322-byte
archive hashes to
`8e721a0b4fe872081f92d49a5393422b323cd077ae66e8c1badc083c7b8c240b`
and contains 20 result roots / 1,015 regular files. The fail-closed verifier
checks the outer identity, archive safety, 12 key results, and 980 entries from
17 nested checksum manifests:

```sh
python3 tools/verify_research_corpus.py --json
python3 tools/verify_research_corpus.py \
  --extract /var/tmp/opencfw-research/corpus
```

`research/corpus/PROVENANCE.md` records a tree hash for every
returned root. `research/corpus/PROVENANCE.md` accounts for
every Lorelei `opencfw-*` workspace and distinguishes preserved unique results
from excluded reproducible toolchain, checkout, project-database, and object
caches. No proprietary AmbiqSuite/ARM source was copied into the repository.

## Decision

Use `lorelei` as a headless throughput worker for independent Ghidra projects,
candidate-build matrices, hashing, and similarity scans. Keep interactive
single-function Rizin work local. The tested Ghidra concurrency default is 16
workers for independent import/decompile jobs. For the Apollo template-clone
workload described below, use 64 address chunks and `JOBS=64`: it was the
fastest measured end-to-end point, although only 6.69% faster than 16 workers.

Run a whole shard through one SSH command. Lorelei's SSH server refused the
tested multiplexed-session configuration, while a cold connection costs about
one second. One long-lived command therefore gives almost the same compute
time as working natively on Lorelei without introducing a second source of
truth for the repository.

## Matched hosts and inputs

| Property | Local workstation | `lorelei` |
|---|---|---|
| CPU | Apple M1 Max, 10 cores | AMD Ryzen Threadripper 2990WX, 32 cores / 64 threads |
| Memory | 64 GiB | 62 GiB; about 43 GiB available during inventory |
| Topology | unified-memory Apple SoC | four NUMA nodes |
| Storage | local workspace | 3.7 TiB NVMe; about 2.8 TiB available |
| Ghidra | 12.1.2 / Homebrew OpenJDK 21.0.12 | 12.1.2 / Temurin OpenJDK 21.0.12 |
| Rizin | 0.9.1 native Homebrew | 0.8.1 inside Cutter 2.4.1 Flatpak |

Both hosts used the official raw image at
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, 3,523,396 bytes,
SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

The user-local Lorelei tool installation is:

- `/var/home/kalani/.local/opt/ghidra_12.1.2_PUBLIC` from the official
  `ghidra_12.1.2_PUBLIC_20260605.zip`, SHA-256
  `b62e81a0390618466c019c60d8c2f796ced2509c4c1aea4a37644a77272cf99d`;
- `/var/home/kalani/.local/opt/jdk-21.0.12+8` from the Adoptium Temurin JDK
  archive, locally recorded SHA-256
  `e4446ff06a276155697597cc0f1b15da004ff083f4964a35271ecee567177370`.

Fedora's host is an atomic image and rejected a normal `dnf install`. No host
package overlay was made. The archives remain in
`/var/home/kalani/.cache/opencfw-tools` for reproducibility.

## Workload

The Ghidra unit imports the raw Cortex/Thumb image at `0x00437FE0` with
`-noanalysis`, creates and decompiles the five authenticated nanopb entries at
`0x48F7F4`, `0x48F968`, `0x48FB1C`, `0x48FB30`, and `0x49053C`, and deletes
the disposable project. Each independent task therefore includes JVM startup,
raw import, function construction, decompilation, and project teardown.

The reproducible harness is `tools/benchmark_headless_ghidra.sh`. Ghidra's
application output is suppressed for timing, but any failed task makes the
harness fail. Projects have separate temporary directories and only empty
directories are removed by the harness.

## Results

| Workload | Local | Lorelei native compute | Mac-observed SSH wall | Result |
|---|---:|---:|---:|---|
| 1 Ghidra task | 4.95–10.57 s normally observed; one 30.54 s outlier | 6.85–7.08 s | about native + 0.8–1.0 s | comparable latency; local measurements were load-sensitive |
| 8 tasks / 8 workers | 22.23 s | 9.76 s | 10.56 s | Lorelei 2.28x local throughput |
| 16 tasks; local 8 workers, Lorelei 16 | 78.68 s | 15.75 s | 16.38 s | Lorelei 5.00x local throughput in the observed workstation state |
| 32 tasks / 32 Lorelei workers | not run locally | 36.09 s | 37.00 s | slower per task than 16-worker point |
| 10 small Rizin process launches | 0.63 s | 2.58 s | 3.46 s | keep small interactive Rizin work local |

The Mac reported a load average above 480 during part of the run and several
unrelated CPU-heavy applications. The 5.00x figure describes obtainable wall
time in the actual working environment, not a clean-room CPU comparison. The
eight-task result is the more conservative demonstrated acceleration.

One remote Ghidra process peaked around 450–530 MiB resident in these runs.
Sixteen workers consequently fit comfortably in available memory. Observed
throughput was about 0.82 tasks/s at eight workers, 1.02 tasks/s at sixteen,
and 0.89 tasks/s at thirty-two. Start at `JOBS=16`; lower it when a shard uses
full analysis, larger databases, BSim, or memory-heavy scripts.

## Apollo-main 64-chunk production run

The authenticated installed application occupies
`[0x00438000,0x00794324)`, 3,523,364 bytes. The raw OTA component is 32 bytes
larger and is imported at `0x00437FE0`, so file offset `0x20` is runtime
address `0x00438000`. `tools/manifests/apollo-main-ghidra-64.tsv` tiles the
installed range into exactly 64 non-overlapping, gap-free, Thumb-halfword-
aligned chunks of 55,052 or 55,054 bytes. The generator
`tools/generate_apollo_ghidra_chunks.py` authenticates the component before
emitting boundaries.

`tools/run_apollo_ghidra_chunk_batch.sh` avoids 64 redundant whole-image
analyses. It seeds 24 unique valid Cortex-M vector targets, analyzes one Ghidra
project, closes it, then uses Btrfs reflinks to give each decompiler a private
copy of that 43 MiB analyzed project. Clone times in the smoke run were under
9 ms. Every worker exports the decompiled C for functions whose entry lies in
its half-open range and records configuration, inputs, status, timing, and
per-file hashes.

The initial analysis took 156.280 seconds. The two-chunk smoke run then
decompiled 793 functions in 18.058 and 12.016 seconds with no failures. The
same analyzed template was used for all concurrency comparisons:

| Layout / workers | Warm wall time | Functions | Failures | Per-chunk time |
|---|---:|---:|---:|---:|
| Equal-byte / 16 | 152.329 s | 7,370 | 0 | 23.092–48.628 s |
| Equal-byte / 32 | 163.799 s | 7,370 | 0 | 52.264–103.270 s |
| **Equal-byte / 64** | **142.780 s** | **7,370** | **0** | **86.217–142.691 s** |
| Function-balanced / 64 | 143.669 s | 7,370 | 0 | 91.332–143.535 s |

The fastest measured cold path is therefore about 299.060 seconds (4.98
minutes): one 156.280-second analysis plus one 142.780-second 64-worker
decompile. After the runner was hardened to hash all ten analyzed-project
files, the canonical replay took 145.251 seconds, making the audit-complete
cold estimate 301.531 seconds (5.03 minutes). Full-width execution
temporarily used about 19.4 GiB of aggregate Java RSS at the sampled peak and
left 28–33 GiB available; swap increased by about 0.5 GiB and the run completed
without an OOM or failed worker.

Equal-byte discovery also classified the address distribution: chunks 0–33
contain all 7,370 discovered functions, while chunks 34–63 contain none and
cover data/resources after `0x00600FAA`. This is not proof that no missed code
exists there, so those ranges remain in the complete tiling. A derived
function-balanced manifest assigns 115–116 discovered entries per worker, but
its measured wall time was statistically tied and slightly slower; raw
function count is not an adequate cost model for decompiler complexity.

The canonical returned `results.tsv`, `timing.tsv`, `INPUTS.tsv`, `CONFIG.tsv`,
`template-files.tsv`, and `SHA256SUMS` hash to
`396c9fd88b502d3671fa6d0cf207d45272e1b77f8147d311097708bd0208540c`,
`ac9c2a1d36c320aaf66d6db78b2eed09addf76d27f60ea2cfd5dfc521e7c4bba`,
`a8d2b43a992857bf946a9f39a3cc979dc4da0f5a921d612bd8cacfccfff35136`,
`bdaaaa85f397b25b67c5d5f06ccf07800f64a8e5baeacd2ea09656ccec6787dc`,
`7032a935509a344de22a58029fa3fcad80e21f341cfb8e0876c09a6207bceeea`,
and `3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f`.
The decompiler-marker corpus is byte-identical between the fastest run and
the audit-hardened replay: 9,311,951 normalized bytes, SHA-256
`32b47032d215df15bfa05db2b6ff0bd1622cbb7d09833467fb0171f2771c7212`.
The former remote and local `/var/tmp` paths are now working copies only. The
134-file, 11.7 MiB audit-hardened result is preserved inside the durable return
corpus as
`opencfw-apollo64-return.3LC1Dq/full64-j64-auth`.

After that working copy was removed, a local macOS replay with the same Ghidra
12.1.2, JDK 21.0.12, authenticated image, 64-way manifest, and scripts restored
the corpus at the same path. All 64 shards completed, all 7,370 functions
decompiled, and there were zero failures. Its host/timing-sensitive
`SHA256SUMS` envelope is
`87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e`;
the source-path correlation census is unchanged. Both the original returned
envelope and this independently generated local replay are accepted, while
every member remains individually authenticated by its selected envelope.

This five-minute figure is mechanical decompilation, not complete source
reconstruction. Naming, upstream attribution, boundary repair, data/code
classification, ABI recovery, and clean source recreation are now the
bottleneck. With 7,370 discovered functions, the present rough magnitude is
10²–10³ analyst-hours: approximately one to three months if automated upstream
matching eliminates most bodies, or three to twelve months if much of the
remaining corpus needs manual semantic reconstruction.

## Orchestration and integration policy

The local checkout was at `6adb0818d` with ongoing reconstruction changes;
Lorelei's clean checkout was older at `5f1c7794`. Do not synchronize the dirty
workspace wholesale or treat the remote checkout as an integration branch.
Instead:

1. send only a content-hashed tool/script snapshot and the explicit input
   manifest needed by a shard;
2. verify firmware, script, upstream checkout, and configuration hashes before
   remote execution;
3. execute all tasks under one SSH connection with bounded concurrency;
4. return structured text/JSON artifacts plus a SHA-256 integrity manifest;
5. validate the manifest locally, then review and integrate source/document
   changes in the local checkout;
6. never accept a Ghidra database itself as provenance when a deterministic
   script can export the underlying boundary, xref, p-code, or decompilation
   fact.

This makes SSH orchestration nearly equivalent to native remote execution for
compute while preserving one authoritative worktree. A fully native Lorelei
agent would save less than a second of connection cost per shard, but would
add worktree synchronization and result-integration risk.

## Apollo corpus-to-source integration lanes

A first source-integration replay copied the current local `openCFW` boundary
once to `/var/tmp/opencfw-source-lanes.l5hz6p/baseline` and created three
86-MiB Btrfs reflink workspaces. LVGL, Cordio, and path-gap agents processed
the same authenticated corpus concurrently without writing to the local or
remote authoritative Git checkout. Their event/final artifact SHA-256 pairs
are:

| Lane | `events.jsonl` | `final.md` |
|---|---|---|
| LVGL | `1d328767a5cd6067835e0a06cc99504b9472716efc6c690973c823310a83e8c0` | `88368c61541c6664379a373f50f2c3f05537dac2f14a5165a1c6d341c96f0c91` |
| Cordio | `7e8e650739ce3b4925be366fffea894619ab93026c69cb7d6649bb7fd7451786` | `58ad647edf8a31d7de393717183f9485b2e4ef59db87cd92326bbd1793cc7337` |
| Path gap | `3ba7f00f34c1d80100f19a722d8e67d0d509c177546eee7b4fb8d06a1de2192c` | `e4f0ef99ad07500c9a287f1a92275b0a2673d01b6755272380fdd4996859af06` |

Only explicit files were returned. Remote source hashes were checked before
reviewed local patches were applied; overlapping documentation was merged by
hand. Local review tightened the path-gap language so 273 raw exact-cell LDR
decodes remain distinct from the seven independently call/table-backed
function entries. The accepted analyzers hash to
`4fc49e747b59e4500e399a7c1a4923127cba49dea1887e910f85d38662f90962`
(LVGL),
`4151cae07989c32511e385b8028964a123a8249a1c110fb672dcd1408aef77a1`
(Cordio), and
`795b1741448294dee3343eaf1eeeabc0a262a8726f1e29cb84be902ea35e2e8b`
(path gap). Forty-nine focused tests then passed locally against the separately
returned audit-hardened corpus. No production overlay or package byte changed.

## EM9305 16-shard production run

The generic manifest runner is now implemented as
`tools/run_ghidra_shard_batch.sh`; its current work queue is
`tools/manifests/em9305-ghidra-pending.tsv`. It gives every range an isolated
project and captures structured result, status, log, input-identity, and
SHA-256 integrity artifacts.
On Lorelei, 16 ARC shards at `JOBS=16` and the default targeted
`FULL_ANALYSIS=0` all completed successfully in 18.042--18.299 seconds
(18.189-second mean) in the current checked-in replay. The same manifest with
broad auto-analysis took 24.882--29.549 seconds (26.497-second mean); targeted
mode retained all 16 instruction windows and decompile sections while reducing
mean shard time by 31.35%, a 1.46x throughput improvement. Set
`FULL_ANALYSIS=1` only for shards that need global analysis.

The returned `results.tsv`
SHA-256 is
`6547ee7fcbe6fd1164c84d1c16046b1acb8dc3bfa7923300351679b9d5b3cafa`;
`INPUTS.tsv` hashes to
`145ba2002bad9e554565cb9d1cf33a8478ca326f905aa72feda77453955caad0`,
`CONFIG.tsv` hashes to
`e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`,
and the `SHA256SUMS` file itself hashes to
`632a9ef24aaf7c7acab901838b9f9680a5bd2825e743cfe55159e45fe0b36b12`.
`INPUTS.tsv` now authenticates the runner itself as well as firmware,
manifest, configuration, and all three Ghidra scripts.
The verified return is preserved under
`opencfw-em9305-ghidra16-authoritative-return.dqmDy6/output` in the durable
return corpus; the remote directory is now only a disposable working copy.

The experimental ARC processor emitted constructor/p-code warnings in all
logs, but the batch still produced useful function boundaries and data xrefs.
Those results are treated as candidate evidence until GNU ARC disassembly,
raw bytes, Rizin, pointer topology, or authenticated source corroborates them.
For this run, the independent checks confirmed the QF/QK hook map and the
nine-entry function-pointer table.

## Residual-gap production run

After the two SDK archive censuses, the checked-in
`tools/manifests/em9305-ghidra-residual-round2.tsv` assigns 16 of the largest
code-bearing exact-function gaps to separate projects. GNU ARCv2 EM
disassembly first confirmed plausible entries for connection dispatch and
cleanup, encryption refresh/timeout, periodic scan/advertising, PAwR, PHY and
power control, WSF-adjacent voltage handling, and the post-QK-port runtime
gap. Lorelei completed all 16 projects at 16 workers in 17.644--17.993 seconds
(17.819-second mean) with no failed lane.

The returned `results.tsv`, `INPUTS.tsv`, `CONFIG.tsv`, and `SHA256SUMS` hash
to `348f056ae507c5042942b89d3bb4cfaae14c5bb8a7afa2a17ef723060e4124d2`,
`c0e56ddaf00441f82dc1f69a7f791fdc9685796787227e45789f848320e711c7`,
`e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`,
and `68aa2d88359c49f7ea88d5fc4fba29488319482bf5e08e3b2fdd58f1689834f6`.
The verified return is preserved under
`opencfw-em9305-ghidra-residual-round2-return.SvoSIJ/output` in the durable
return corpus; the remote directory is now only a disposable working copy.

Fifteen entries remain instruction-window candidates because the experimental
Ghidra ARCompact processor stopped their decompiler at unresolved constructor
p-code. One 12-byte entry decompiled coherently and was independently named by
the authenticated archive as `lctrSlvCheckEncOverridePowerControl @
0x00329554`; GNU ARC confirms that it returns whether the connection byte at
offset `0x27B` equals `0x1C`. No bad-p-code result was promoted as semantic
evidence. The run therefore validates the parallel isolation/result-return
architecture while also showing that GNU ARC plus exact SDK objects remains
the higher-confidence semantic path for this target.

## NOP-aware residual round three

`tools/manifests/em9305-ghidra-residual-round3.tsv` splits 16 newly identified
sleep, NVM, HCI, crypto, connection, master-init, periodic-data, and path-loss
entries into isolated projects. All processes succeeded in 16.766–17.023
seconds (16.901-second mean). The returned `results.tsv`, `INPUTS.tsv`,
`CONFIG.tsv`, and `SHA256SUMS` hash to
`8ac5db441830be8a84c4e5c449ebeab14f3eadcbd7e8ad4976b169db2edbea6e`,
`b07aa83a1ad6c7c5e63dfd794b4ce1cac8d62ca0d281d9857a82c90d8529e577`,
`e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`,
and `a295af90486b1ce08cd2e4cdc54114081e88f6b08409df96641f083aa63904bc`.

Fifteen entries stopped at constructor/p-code failures; the remaining crypto
entry could not be created as a Ghidra function. No semantic result was
promoted. The archive/GNU lane independently identified the same queue and
showed 98.630% aggregate meaningful-byte agreement for its 29 same-size
modified functions. This confirms that further parallel Ghidra attempts with
the current ARC processor have low expected semantic value; Lorelei remains
valuable for archive comparison, GNU disassembly, and candidate-build matrices.
Full accounting is in the
[residual segment census](em9305-residual-segment-census.md).

## Residual round four

`tools/manifests/em9305-ghidra-residual-round4.tsv` assigns 16 previously
unprocessed residual spans / 5,922 bytes to isolated projects. The queue covers
controller scan/advertising, RF control, application sleep, EM system and GPIO,
protocol-timer/RC-calibration, LL reset/scan, scheduler timing, ISO host events,
connection actions, PAwR initiation, HCI dispatch, runtime configuration, and
TX-queue/ACAD seams. All 16 processes succeeded at 16 workers in
17.217–17.502 seconds (17.341-second mean).

Thirteen entry decompilations stopped at the known experimental-processor
constructor/p-code defect. Three produced coherent entry-level candidates: a
four-byte return-12 leaf at `0x0030592C`, an interrupt context-save/callback/
`rtie` wrapper at `0x00305B1C`, and another interrupt wrapper at `0x00306384`
that calls `0x00311AB4`. These are useful boundary and semantic candidates,
and vector ABI plus normalized archive matching subsequently resolve the two
sampled wrappers and their paired timer/radio entries. Three handlers / 574
bytes are exact SDK bodies; the 186-byte radio-TX role is identified but
vendor-modified relative to the SDK's 380-byte TX body. The return-12 leaf
remains candidate-only.

The returned `results.tsv`, `INPUTS.tsv`, `CONFIG.tsv`, and `SHA256SUMS` hash
to `a7630016ab906f8aacb6d45682817357601eeb6d5e687928d3363e98c1d18097`,
`85ec123b402a9813bcf2727aa103c701ca22870b1a34629d4d300005c457becb`,
`e7a730cf196899bec0272f0f3413bfc80c622b5435512826f5c82414b8ef75ae`,
and `403d6da1ff3511d97de0eeb358e5ad892d09bb86121c2bd808847887f98ab76a`.
The remote and local `/var/tmp` directories are now dispensable working copies;
the verified return is preserved under
`opencfw-em9305-ghidra-residual-round4-return.xU4j4s/output` in the durable
return corpus.

## Cordio WSF source-candidate matrix

The source-integration path was exercised end to end on the newly recovered
G2 WSF timer functions. Lorelei authenticated official Packetcraft r19.02 and
r20.05 sources, applied only the recovered stock structure field order, and
compiled eight Cortex-M55/GCC 13.2.1 rows across `-O2`/`-Os` with inlining
disabled. Source fetch took 0.417307052 seconds and the full matrix took
0.800405321 seconds; individual compilation times were 59.7–69.2 ms. For this
unit, a single container running a bounded matrix is more efficient than 64
processes because compiler startup dominates.

The returned tar is 8,929 bytes / SHA-256
`59a67b7a29bf00aae45692f2beb745a96e27ca1dcb20c65b5733680d289d63d1`.
Its internal `SHA256SUMS` passed locally after return. The compact result table
is integrated at `tools/manifests/readiness-cordio-wsf-timer-matrix.tsv`,
SHA-256
`5609187015274a97cb734c6f47106e3fa9f65d05ee0873c10f4eebab60054323`.
The verified tar and its expanded result directory are both preserved under
the corresponding `opencfw-wsf-matrix-return.*` roots in the durable return
corpus.

r19.02 `-Os` alone emits a size-exact 40-byte
`WsfTimerNextExpiration(bool_t *)`; r20.05 emits a 28-byte no-argument helper.
No raw or strict-normalized candidate matches the stock IAR bodies. The result
therefore narrows source semantics and ABI without making a false exact-build
claim. Full interpretation is in the
[WSF timer recovery](cordio-wsf-timer-source-recovery.md).

The follow-on current-source matrix authenticates the complete eleven-function
candidate (`def199a7…` C, `ec4b58fc…` H), compiles 13 configurations, and
compares 143 function rows in **2.448108512 seconds**. All configurations
compile warning-free and link to zero unresolved symbols after providing the
13 declared seams. No raw or strict-normalized row matches stock. Eight of
eleven functions can be made size-exact under bounded configuration choices;
the unresolved best gaps are Init +4 bytes, ServiceExpired ±2 bytes, and
UpdateTicks -12 bytes. This remains IAR-shape evidence, not an exact-build
claim.

The verified return is preserved under
`opencfw-wsf-current11-return-v2.mvcPuA/` in the durable return corpus. Its tar
SHA-256 is
`b0c5614157d33fbeddbdfdaa88bcdd6927f58af64ce73cd274de45342c807fa6`.
Its full ledger SHA-256 is
`2da0db026a5235e3d5f61e5d59ea1bd390d0249d41b710f2a0606318a02381f1`;
compact tracked config and best-size summaries are authenticated by the WSF
timer analyzer. The rerun also proves all 13 objects and closure ELFs are
byte-identical across a provenance-comment-only source change.

## Cordio WSF OS/queue readiness return

The next Lorelei tranche authenticated the AmbiqSuite 2.5.1 `wsf_os.c` and
`wsf_queue.c` identities without redistributing their proprietary source,
compiled four OS and two queue probe configurations warning-free, and produced
48 structural function/config comparisons. The returned compact archive is
10,899 bytes / SHA-256
`14e42ec2a6c5f2ee11725cc9af75d96aad1b66d690170b7dbb3a266b6957687d`.
It is preserved under `opencfw-wsf-os-readiness-return.4bGhzQ/` in the durable
corpus.

The analysis-ready tables are also tracked directly:

- `tools/manifests/readiness-cordio-wsf-os-functions.tsv`, SHA-256
  `d02b53df6efc34eb17c9474c8117cf388c6b204536c8efd20cf6e6bdeb26a760`;
- `tools/manifests/readiness-cordio-wsf-os-include-closure.tsv`, SHA-256
  `c9e9210ad715f1dac18032ed3d327ee7c9860df587081f52f04e780135c9f0ee`;
- `tools/manifests/readiness-cordio-wsf-os-structural-comparison.tsv`, SHA-256
  `56dd44de9f0b36542220fedecf2a53f0ad5e0551d087cab571aa353fbb0b655e`;
- config and authenticated-source identity summaries beside those manifests.

No raw or strict-normalized row matches stock. `-Os
-fno-optimize-sibling-calls` is the best initial GCC shape lane at three of 12
exact-size functions and 64 aggregate absolute bytes of size delta. This
readiness result is the baseline for the stock-ABI FreeRTOS shim and full
13-profile OS/queue matrix; it is not an exact-source/compiler claim.

## Reproduction

Apollo cold run (omit `TEMPLATE_PROJECT` so the runner performs the one-time
analysis before launching all 64 chunks):

```sh
ssh lorelei 'cd /path/to/content-hashed-snapshot && env \
  JOBS=64 \
  JAVA_HOME=/var/home/kalani/.local/opt/jdk-21.0.12+8 \
  GHIDRA_HEADLESS=/var/home/kalani/.local/opt/ghidra_12.1.2_PUBLIC/support/analyzeHeadless \
  FIRMWARE=$PWD/ota_s200_firmware_ota.bin \
  GHIDRA_SCRIPT_DIR=$PWD/ghidra \
  MANIFEST=$PWD/apollo-main-ghidra-64.tsv \
  OUTPUT_DIR=$PWD/apollo64-output \
  ./run_apollo_ghidra_chunk_batch.sh'
```

For a warm replay, set `TEMPLATE_PROJECT` to the closed `template` directory
from a prior cold output and use a new empty `OUTPUT_DIR`. The runner rejects a
non-empty output directory and hashes the template path/configuration alongside
the firmware, manifest, runner, and Ghidra scripts.

Local eight-worker run:

```sh
TASKS=8 JOBS=8 \
JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home \
GHIDRA_HEADLESS=/opt/homebrew/Cellar/ghidra/12.1.2/libexec/support/analyzeHeadless \
tools/benchmark_headless_ghidra.sh
```

Lorelei sixteen-worker run after copying the harness and Ghidra script into
the content-hashed cache:

```sh
ssh lorelei env \
  TASKS=16 JOBS=16 \
  JAVA_HOME=/var/home/kalani/.local/opt/jdk-21.0.12+8 \
  GHIDRA_HEADLESS=/var/home/kalani/.local/opt/ghidra_12.1.2_PUBLIC/support/analyzeHeadless \
  FIRMWARE=/var/home/kalani/Repo/SybilSight/openCFW/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin \
  GHIDRA_SCRIPT_DIR=/var/home/kalani/.cache/opencfw-tools/ghidra-scripts \
  /var/home/kalani/.cache/opencfw-tools/benchmark_headless_ghidra.sh
```

The manifest generalization is complete. The next optimization is content-
addressed local caching of unchanged shard results and NUMA-aware placement
for analysis-heavy projects; neither is needed for correctness.
