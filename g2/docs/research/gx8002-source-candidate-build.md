# GX8002 C integration candidate

Date: 2026-09-08. The 214 qualified C functions and five architecture assembly routines now supply bytes to an
experimental firmware container and complete EVENOTA package built on macOS.
This is an intermediate hybrid, not the final source-only firmware.

```sh
make -C g2 gx8002-source-candidate
make -C g2 codec-source-experimental
```

The native C-SKY toolchain and pinned NationalChip SDK source must be available
as described in the analog/cache research notes. The builder recompiles and
replays each qualification, then requires complete equality with the reviewed
reports, including source and target-code hashes. Unexpected changes fail
before firmware emission. The SDK objects serve only as comparison oracles.

## Ownership and container integrity

The [build report](gx8002-source-candidate-build.json) assigns every codec byte:

| Owner | Bytes |
| --- | ---: |
| Compiled C, 230 occurrences of 214 functions | 14,416 |
| Compiled architecture assembly | 156 |
| Generated source data | 3,113 |
| Generated FWPK and UART header metadata | 80 |
| Generated unreachable envelope fill | 712 |
| Authenticated retained stock | 307,615 |
| Total | 326,092 |

The C sections preserve their original entry addresses. An explicitly
authenticated partition assigns the platform-config unused tail to the source
PLL frequency table, keeping code and data ownership disjoint. All are relocation-free. The builder rejects overlaps, changed
source reports, changed object payloads, incorrect stock intervals, and any
change to retained ranges. It regenerates both FWPK CRC-32 values and the
UART stage-2 byte-sum checksum. BINH structure and stage-1 CRCs still validate.
Four additional tests exercise these integration boundaries.

`--require-source-only` correctly exits nonzero because retained ranges remain.
The default six-component source-readiness ledger is unchanged: this separate
candidate does not retroactively promote bytes in the existing default build.

## Built artifacts

Codec: `build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin`

SHA-256: `26da0f0d9fe13d659128ba11b07288ee32d940e21208efe9cbc82c92d7abdab6`

EVENOTA: `build/codec-source-experimental/package/g2-openCFW-s200_v2.2.6.10-codec-source-experimental.evenota.bin`

Size: 4,750,780 bytes. SHA-256:
`f31253a2f4d0bd0e022617cadd4ae11a7e41c63848cb45eefe3f8f6e26947064`.

The explicit experimental manifest pins these artifacts. Package assembly and
`open_cfw.py verify-artifacts` pass, with zero unresolved flash regions. The
builder's "byte-identical reference" message refers to this manifest's pinned
candidate hash, not equivalence to the original vendor firmware.

No firmware was flashed. Package integrity and function-level comparisons do
not establish hardware timing, startup, complete functionality, or source-only
completion. Continue recovering retained runtime/data/model functionality and
qualifying whole-image behavior; do not treat this intermediate package as the
finished goal.

The [I2S tranche](gx8002-i2s-source.md) adds three functions at six stock
occurrences, reducing retained bytes by a further 96.

The [VAD curve tranche](gx8002-vad-curves.md) adds five functions at nine
occurrences. Shorter code has separately reported generated fill; it is not
counted as compiled C.

The [model interface tranche](gx8002-model-interface.md) adds 106 byte-exact
source-built bytes. Its integration preserves the existing package hash.

The [RAM-copy recovery](gx8002-task-copy-recovery.md) replaces 126 stock bytes
with 96 compiled bytes and 30 separately counted unreachable fill bytes.

The saved-task setter adds 20 byte-exact linked C bytes, with its copy call
resolved to the recovered source routine. This admission leaves package bytes
and hashes unchanged. See [setter verification](gx8002-model-set-task-verification.json).

The application resume callback adds 28 byte-exact linked C bytes using the
pinned upstream application layout; package bytes remain unchanged.

Watchdog stop and suspend dispatch add 44 byte-exact source bytes. Watchdog
stop includes one documented BCLRI inline assembly instruction within its C
function; no encoded instruction bytes are embedded. The `compiled_c` ledger
category includes this explicitly documented source-level assembly.

Three queue sections now compile directly from authenticated, unmodified
NationalChip SDK C: Init, IsEmpty and IsFull, totaling 54 bytes. The builder
selects only these reviewed sections from the larger translation unit.

Upstream QueueGet adds 70 compiled bytes and four unreachable fill bytes,
replacing its 74-byte original body after 2,196 exact access-trace comparisons.
Unlike the earlier exact matches, this integration changes the package hash.

Upstream QueuePut supplies its explicitly reviewed `.sram_text` section at
the original SRAM entry: 86 compiled bytes plus four separately counted fill
bytes replace the 90-byte stock body. Both queue directions are now rebuilt.

The event-trigger wrapper adds 20 byte-exact linked C bytes against the rebuilt
queue-write routine. This addition preserves the current package hash.

CRC integration adds two compiled functions (172 bytes), one mathematical
lookup table (1,024 generated-source-data bytes), and 20 fill bytes. The build
report counts 57 replacement occurrences: 56 code regions and one data region.

Console integration adds 72 compiled bytes and four unreachable fill bytes
after 420 MMIO and 6,160 port-wrapper comparisons. The console entry itself
is byte-exact. Totals are now 60 replacements (59 code and one data region).
Existing port descriptors and configuration globals remain retained data.

Logging integration adds six functions: upstream ui2a, putf, patched putchw,
tfp_format, and recovered printf/fputc wrappers. These contribute 752 compiled
bytes and 60 unreachable fill bytes, replacing 812 retained bytes. Target
flags include -fwrapv for signed minimum negation. The BSD notice accompanies
the experimental package. Totals are 66 replacements, including one data
region. Ordinary inputs and finite ABI/target comparisons are qualified;
this is still a hybrid without device/timing qualification.

UART dispatcher integration adds 132 C bytes, 14 C-authored diagnostic-string
bytes and four unreachable fill bytes. Totals are 68 replacements: 66 code
regions and two data regions. Existing registration and queue storage remain
retained. Admission reruns 240 target cases and requires reviewed report
equality before selecting the linked code and byte-aligned string sections.

Event tick and watchdog service add 90 compiled bytes, with no new fill.
Totals are 70 replacements (68 code and two data regions). The event tick
qualification covers callback-driven application replacement and ordered
UART/watchdog servicing; initialization and state storage remain retained.

Power registration integration adds 176 compiled bytes with no new fill.
Totals are 72 replacements (70 code and two data regions). Qualification
checks 720 stock/source state transitions; all registry storage, including
the unrecovered eight-byte header, remains accounted as retained stock.

IRQ integration adds seven routines: upstream VIC enable/disable and PSR
save/restore wrappers, recovered registration, and enable-bank save/restore.
These replace 176 retained bytes with 168 compiled bytes and eight unreachable
fill bytes. Totals are 79 replacements (77 code and two data regions).
Admission rebuilds pinned upstream dependencies, compares PSR bodies exactly,
and reruns 1,610 ordered-access cases. IRQ storage and dispatcher remain retained.

Clock lookup integration adds 160 compiled bytes and four unreachable fill
bytes, plus 487 bytes of authenticated upstream parameter, DTO, and divider
tables. Totals are 83 replacements (78 code and five data regions). The tables
are rebuilt and linked to their original addresses; no extracted data payload
is used to generate them. Admission repeats 42,160 lookup comparisons and exact
table checks. The larger gate routine and analysis wrapper are excluded.

Clock gate integration adds 254 compiled bytes, 148 compiler-generated switch
target bytes, and two unreachable fill bytes. Totals are 85 replacements
(79 code and six data regions). Admission reruns 8,432 MMIO comparisons and
requires reviewed section hashes. Both lookup calls target the source-built
helper; regenerated switch targets replace their stock counterparts together
with the gate code. Watchdog initialization itself remains under qualification.

Watchdog initialization and ISR integration adds 156 compiled bytes and a
22-byte C diagnostic string, with no new fill. Totals are 88 replacements
(81 code and seven data regions). Admission repeats all 16-bit timeout inputs,
MMIO/call ordering cases, and callback/clear-register checks. Clock gate, IRQ
registration and printf resolve to source-built entries. Handler storage and
hardware interrupt timing remain unqualified.

Application startup and reboot integration adds 158 compiled bytes, 29 source
registration-name bytes, and two unreachable fill bytes. Totals are 93
replacements (84 code and nine data regions). Startup code and strings are
byte-exact; reboot code matches stock and its callback reaches the verified
reset wait. Admission repeats 72 startup cases and both reboot entry paths.
Existing application/queue state and hardware startup/reset remain unqualified.

The startup BSS clear adds 28 compiled C bytes and eight unreachable fill bytes
in its 36-byte stock envelope. All 8155 writes match the fixed shipped bounds.

System initialization adds 164 compiled C bytes with qualified control-register,
service-call and VIC-write ordering. Its external service dependencies remain
separately tracked and hardware behavior remains unqualified.

Reset-reason and startup-mode queries add 96 compiled C bytes and four bytes
of unreachable fill, removing their complete 100-byte retained envelopes.

Five SPI transport/polling functions add 230 compiled C bytes and two fill
bytes. Full read/write and nested polling comparisons are replayed at admission.

Shared flash state now contributes 32 source-authored data bytes. A single
header defines the layout and typed callbacks across six modules, and the
verifier compiles them together to reject conflicting declarations. Existing
function payloads and package hashes are unchanged. Totals are 125 replacement
regions: 112 code occurrences and thirteen data regions. All 137 tests and
macOS package/artifact checks pass.

Protection status/mode integration adds 180 compiled bytes (including five
source-level CK804 narrow-load instructions) and four unreachable fill bytes.
Admission repeats 114,752 decoded comparisons. Totals are 127 replacement
regions: 114 code occurrences and thirteen source-data regions. The existing
137 integration tests and nine new protection tests pass.

Protection setter and lock/unlock wrappers add 234 compiled bytes (including
four explicit source-level byte-load instructions) and two fill bytes. Totals
are 130 replacement regions: 117 code occurrences and thirteen data regions.
Admission replays 78,496 setter cases, 60 wrapper cases and 32 aliases. All
155 tests in the native macOS codec target pass.

Protection policy tables and their initializer add 168 source-data bytes and
44 byte-exact compiled C bytes. Totals are 134 replacement regions: 118 code
occurrences and sixteen source-data regions. Codec/package hashes are unchanged
by this ownership migration. All 155 native codec tests pass.

Flash interrupt integration adds 30 compiled C bytes and two fill bytes.
Totals are 135 replacement regions: 119 code occurrences and sixteen data
regions. Admission repeats 846 decoded cases; all 159 native codec tests pass.

Full flash-interface initialization adds 428 compiled bytes and eight fill
bytes, after 35,328 full-function and 4,150 dispatch comparisons. Totals are
136 replacement regions: 120 code occurrences and sixteen data regions. All
164 native macOS codec tests pass. Interface/BSS ownership and physical startup
remain separately unqualified.

Range and chip erase integration adds 180 compiled bytes and eight fill bytes.
Totals are 138 replacement regions: 122 code occurrences and sixteen data
regions. All 172 native macOS codec tests pass. Original unsigned wrapping
erase behavior is preserved and documented, not independently corrected.

Read-wrapper integration adds 60 compiled C bytes with no new fill. Totals
are 139 replacement regions: 123 code occurrences and sixteen data regions.
All 177 native macOS codec tests pass. Callback bodies remain separately
qualified; synthetic wrapping tests do not establish physical buffer validity.

Integrated page-program wrapper on macOS. Native codec build passes all183
tests; full EVENOTA build and verify-artifacts pass under apple-clang.
Page-program contributes120 C bytes without envelope fill, with640 decoded
boundary cases and eight overflow/clobber cases. Current ownership:6938
compiled C,2040 source data,80 metadata,296 fill,316738 retained bytes.
There are108 functions/124 code occurrences and16 data regions (140 total).
Codec SHA-256:3c3009eb0bcc3f4c9a36f033bfc83ad059beccb0d3d19e7ef6a2937444edf164.
Package SHA-256:b0e409bbbc10c96c8f85af87a50adefac582365ed581593254b42bd00d5113a6.
The manifest pins the new candidate; matching that pin is not vendor binary
identity or hardware qualification. No hardware operation was performed.
OTP callbacks, device/interface data, BSS/startup ownership, other codec code
and the other firmware components remain. Full source-only goal stays active.

Block-bounds/range/sync integration is complete in the experimental package.
Native macOS codec build passes194 tests; full package build and
verify-artifacts pass with apple-clang. Current ownership7052 compiled C,
2040 source data,80 metadata,302 fill,316618 retained bytes. There are111
functions/127 code occurrences and16 data regions. Codec SHA-256:
0de84f82cd67e10efd7c5cf82d2a54e5dbb55e39b5756adcb7296d02484e31ee.
Package SHA-256:eec3a743137a7677b744fafc764eb4d2e30fca0add1d01f1222c4743a7bd21e2.
The new hash pin identifies this candidate, not vendor-byte equivalence.
No hardware operation; complete source-only firmware remains unfinished.

OTP status integrated into the full experimental package. Native macOS codec
build passes198 tests; full build and verify-artifacts pass under apple-clang.
Ownership:7120 C,2040 source data,80 metadata,302 fill,316550 retained bytes;
112 functions/128 code occurrences plus16 data regions. Codec SHA-256:
f1f109b0c7f1fb9eb6fe837a8b67bc58ddbba2e98f27d120ec1332c4c2a113d7.
Package SHA-256:6374fd9287ce5049798221df2f5963a6ecf08d12810eb06ed2345611dcc5acb4.
Candidate hash pin does not imply vendor-byte identity or hardware validation.
The source-only goal remains active; no hardware operation was performed.

OTP lock fully integrated. Native macOS codec build passes202 tests; full
package build and verify-artifacts pass with apple-clang. Ownership7220 C,
2040 source data,80 metadata,302 fill,316450 retained;113 functions and129
code occurrences plus16 data regions. Codec SHA:
f92c56731ae3896e8414d5d6c870073c24b77177858b9c3187cd675b7978064a.
Package SHA:44b611556ef32745f021fe892b58f26ba815feceb5f99f191abcdb9d3c387bcf.
Candidate pin identifies this hybrid, not vendor identity or hardware proof.
Full source-only goal active; no physical OTP operation.

OTP erase fully integrated:207 tests pass; macOS full package build and
verify-artifacts pass. Ownership7312 C,2040 data,80 metadata,302 fill,316358
retained;114 functions/130 code occurrences/16 data regions. Codec SHA:
e0e125de64f3ebd3f3cf510b9ad1cac594ee6c2d96759fdd9fee63b1dc1ae50f.
Package SHA:87f057ec9cae015378f8abd9dcc041fcd39e5bae35e8d49ae6e1afd25c0aa6f1.
Candidate pin is not vendor identity or physical qualification. Goal active.

OTP transmit fully integrated:214 tests pass; native macOS package build and
verify-artifacts pass.115 functions/131 code occurrences/16 data regions;
7472 C,2040 data,80 metadata,306 fill,316194 retained bytes. Codec SHA:
ff9b2c77bf14c3816086e4629cc1c81cd20bc1deae6a79f58feeadc60e20f1fe.
Package SHA:1cac2b2301ef15916da06e874b603401b5f3fde6cd48b6367627f90b0baad178.
Candidate pin is not vendor identity or hardware qualification. OTP write
also passes ten new overflow cases besides1344 baseline cases; rejection
checks and admission remain. Full source-only goal active; hardware untouched.

OTP write fully integrated:224 tests pass; native macOS package build and
verify-artifacts pass.116 functions/132 code occurrences/16 data regions;
7700 C,2040 data,80 metadata,314 fill,315958 retained. Codec SHA:
fd31c84f5ac7ccb96f4f4cbf823f4b00ffbff58fea7d403b05608ba64dcb7904.
Package SHA:6da65e662d06b6d2ac448ae968735d917bbe22f5f062a8f12cc0493ec39fb9ca.
Candidate pin is not hardware proof or vendor identity. Full goal active.

OTP read fully integrated:238 tests pass; macOS package build/verify-artifacts
pass.117 functions/133 code occurrences/16 data regions;8044 C,2040 data,80
metadata,322 fill,315606 retained. Codec SHA:
002ff61b09074547584386a2ddb6f46ee2ab17f7b88b0bcbbbdbbad5278fb0c2.
Package SHA:faa96c088ea31e15bc22f0e89f674505e9ca2dea9039d4a5598ee9a595dfa3dd.
Candidate pin does not imply vendor identity or physical qualification.
Full source-only goal remains active.

The [keyword-list tranche](gx8002-max-list-source.md) adds 120 C bytes and
97 source string bytes, plus a source-defined eight-byte BSS list. All 342
integration tests pass. The full decoder remains incomplete.

The [TWS lifecycle tranche](gx8002-tws-shutdown-source.md) adds 44 C bytes
and 24 source string bytes. All 349 integration tests pass. Because these
compiled bytes equal stock, the codec/package payload hashes remain unchanged.

The [recognition/audio shutdown tranche](gx8002-stream-shutdown-source.md)
adds 30 C bytes and two unreachable fill bytes. All 357 integration tests pass.

The [driver-exit](gx8002-driver-exit-source.md) and
[audio-reset](gx8002-audio-reset-source.md) tranches add 314 C bytes and
82 unreachable fill bytes. All 375 integration tests pass. Audio reset
preserves individual volatile accesses and the original hardware wait loop.

The [SNPU suspend tranche](gx8002-snpu-suspend-source.md) adds 72 C bytes.
All 385 integration tests pass. Live pointer reloads and the idle wait remain
faithful to stock; full SNPU state and hardware behavior are not qualified.

The [IRQ wrappers](gx8002-irq-mask-source.md) and
[SNPU clock gate](gx8002-snpu-clock-source.md) add 52 C bytes. All 398
integration tests pass. The suspend path now uses source-built mask/unmask
and clock operations; primitive NPU register helpers remain separate.

The [NPU register/control tranche](gx8002-npu-register-source.md) adds
50 C bytes and 36 assembly-dependent bytes, plus 14 unreachable fill bytes.
Three C routines with explicit instruction wrappers are conservatively
accounted wholly as compiled_assembly. Their fully defined portable C
versions are comparison-only. All 417 integration tests pass.

The [NPU accessor tranche](gx8002-npu-accessor-source.md) adds 108 C
bytes and eight unreachable fill bytes. All 427 integration tests pass.
The compiled payload equals stock, so codec/package hashes are unchanged.

The SNPU overtime reset and diagnostic dump add 248 compiled C bytes,
147 source string bytes and eight unreachable fill bytes. All 534 native
macOS integration tests pass. There are 239 replacement regions, including
194 C occurrences, five architecture routines and 40 source-data regions.

The task-descriptor initializer adds 108 compiled C bytes and 16 bytes of
unreachable envelope fill. All 542 native macOS integration tests pass.
Totals: 179 C functions at 195 occurrences, five architecture routines,
40 source-data regions, and 240 replacement regions.

Cache-clean and descriptor-cache publication add 110 compiled C bytes and
six bytes of unreachable fill. All 557 native macOS integration tests pass.
Totals: 181 C functions, 197 C occurrences, five architecture routines,
40 source-data regions and 242 replacement regions.

Command-chain submission adds 124 compiled C bytes and 20 bytes of
unreachable fill. All 571 native macOS integration tests pass. The composed
submission/cache checks cover 2,304 stock/source combinations, with six
additional ordering and mutation tests. Totals: 182 C functions at 198
occurrences, five architecture routines, 40 source-data regions and 243
replacement regions. Outer task execution and hardware qualification remain
separate; 310,992 codec bytes still come from authenticated stock.

Outer task admission adds 188 compiled C bytes and 12 bytes of unreachable
fill. All 593 native macOS integration tests pass. The four-routine composed
checks cover 38,400 stock/source combinations. Totals: 183 C functions at
199 occurrences, five architecture routines, 40 source-data regions and
244 replacement regions. Retained stock remains 310,792 codec bytes;
hardware qualification and complete source ownership remain outstanding.

The SNPU state query adds 12 compiled C bytes, identical to stock. All597
integration tests pass. Totals:184 C functions at200 occurrences, five
architecture routines,40 source-data regions and245 replacement regions.
Codec and package hashes remain unchanged.

GPIO interrupt dispatch adds 68 compiled C bytes. All607 native macOS
integration tests pass. Totals:185 C functions at201 occurrences, five
architecture routines,40 source-data regions and246 replacement regions.
Retained stock remains310,712bytes. Callback bodies and hardware behavior
remain outside this interrupt-handler qualification.

GPIO direction/level setters add132 compiled C bytes and12 fill bytes.
All613 integration tests pass. Totals:187 C functions at203 occurrences,
five architecture routines,40 source-data regions and248 replacement regions.
310,568 codec bytes remain retained stock.

GPIO trigger registration adds176 C bytes and16 fill bytes. All622 native
macOS tests pass. Totals:188 C functions/204 occurrences, five architecture
routines,40 source-data regions and249 replacement regions. The old switch
table remains retained pending reachability/ownership analysis.

Trigger disable adds92 C bytes. All630 macOS integration tests pass.
Totals:189 C functions/206 occurrences, five architecture routines,40 data
regions and250 replacement regions. Retained stock remains310,284 bytes.

GPIO and SPI-list initialization add44 compiled C bytes identical to stock.
All637 macOS integration tests pass. Totals:191 C functions/207 occurrences,
five architecture routines,40 data regions and252 replacement regions.
Payload hashes remain unchanged; retained stock remains310,240bytes.

SPI master registration adds one C function replacing a 104-byte envelope
with 92 compiled C bytes and 12 bytes of unreachable fill. All 647 integration
tests and the macOS package build and artifact verification pass.

DW SPI cleanup adds 12 byte-identical compiled C bytes. All 651 integration
tests and the complete macOS package build and artifact verification pass.

DW SPI IRQ adds 32 compiled C bytes. All 656 integration tests and the full
macOS package build and artifact verification pass.

DW SPI probe adds 256 compiled C bytes with 12 bytes of unreachable fill.
All 667 integration tests and macOS package build/artifact verification pass.

DW SPI quick transfer adds 602 compiled C bytes and 32 bytes of unreachable
fill, replacing its 634-byte stock envelope. All 695 integration tests pass.
The macOS package rebuild succeeds at the updated hash above; artifact
verification passes. Retained stock and hardware limitations still apply.

Padmux get/check/set/init and the 64-byte typed default table pass all721
integration tests. The macOS package rebuild succeeds; artifact verification
passes. This remains a hybrid containing retained stock.

RTC ISR/start/set and source-authored diagnostic pass all732integration tests,
macOS package rebuild and artifact verification. Retained stock remains308800
bytes; physical hardware and whole-firmware source-only qualification are open.

The clock-divider checkpoint passes 735 integration tests on macOS. Its
28-byte C routine uses the recovered two-register ABI and has 12,800 decoded
comparison cases. Package assembly and artifact verification both pass after
updating the explicit experimental hashes. The oversized frequency candidate
and RTC initializer remain outside this admitted set.

The clock-frequency checkpoint passes 778 integration tests and package artifact
verification on macOS. It adds the 444-byte source clock function and 76-byte
switch table, plus a 16-byte source PLL table in the explicitly partitioned host
tail. This removes 520 retained bytes. RTC initializer remains outside this
admitted set, and hardware/source-only completion remains unproven.

### Board-pin initializer integrated on macOS (2026-09-08)

The native C-SKY integration completed with 791 passing tests in 21.704 seconds. The initializer adds 104 compiled C bytes; its diagnostic and configuration table add 45 source-data bytes. Codec ownership is now 14,300 compiled C bytes, 156 assembly bytes, 3,090 source-data bytes, 80 metadata bytes, 708 unreachable-fill bytes, and 307,758 retained stock bytes. The 209 C functions account for 225 occurrences.

The macOS apple-clang package build and verify-artifacts both completed successfully. Codec SHA-256: `23452eb8ae7c4848550a1d75afa5f3f6bc8850ffaad04acde19e4a13cd197379`. Package SHA-256: `eccc87d1a2d35a629e96e589360458dfa624b34ac76ed4abeb16159db082cb67` (4,750,780 bytes). Notices copied into the package directory. No hardware qualification or source-only completion is claimed. The source-only goal remains active; gsensor lifecycle and the retained code/data still require reconstruction.

### Sensor accessor package verified on macOS

The 802-test integration and apple-clang package build/verify-artifacts completed successfully. Current codec has 210 C functions at 226 occurrences, 14,324 compiled C bytes, 3,113 source-data bytes and 307,711 retained stock bytes. Codec SHA-256 e3b04bad77fd6e5df232ed910bb56d34d358c54ec4514dee49e449a94a3d6227; package SHA-256 844046c8b1a2c2effd440c45f7e794ebaad242b1f5d28f5a9e7067a35b6c0b82. Notices copied. Source-only and hardware-qualified remain false.
