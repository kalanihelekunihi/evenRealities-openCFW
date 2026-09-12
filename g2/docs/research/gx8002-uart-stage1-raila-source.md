# GX8002 UART boot stage-1 rail-sequencing operation A (CD-001)

Reviewed clean-room C-SKY assembly for the third rail-sequencing
operation of the UART boot stage-1 (IRAM) image, runtime
`0x10000860`, package `0x8B0`, 464 bytes. Registered as
`uart-stage1-raila` (`compiled_assembly`, byte-identical section).

## Envelope

- Routine `0x10000860..0x10000A30` (package `0x8B0..0xA80`, 464 bytes:
  460 code + one shared 4-byte literal-pool word holding
  `0x20002018`, the fill entry-table base, referenced by two `lrw`).
- Single external callee: the admitted `pmu_fill_desc`
  (`0x10000780`). No `rts` in the span: every path ends in a
  retry or in the fail tail, so the routine never returns.
- Entry `(id, arg1, arg2)` in `(r0, r1, r2)`; `arg2` is dead on every
  path (the fill overwrites `r2` first; the body writes it before any
  read). The battery sweeps `arg2` to prove it.

## Behavior (decoded)

- `id > 25` fails at once. `arg1 == 2` goes to the bit-mask check;
  `arg1 >= 3` reaches the divisor dispatcher directly with the frame
  still live (no pop: entry `bf` targets `0x922`, not the pop); `arg1`
  in `{0,1}` calls the fill.
- Fill failure, or entry byte 6 equal to `0xFF`, fails with unset
  address registers (same branches, no outcome claim: leftover arms).
- Otherwise the m-cell bit selected by entry byte 6 must differ from
  `arg1`; ids below 23 continue only for ids 16/19/22 (bits of
  `0x490000`), ids 23+ poll the `desc[3]` word instead; the
  descriptor-table combined test folds `desc[3]` with shift bytes
  from the entry table at `0x20002018` (neighbor entries `id+1/id+2`,
  bytes 5), which is the fill table itself, not a separate table.
- The `id-7 <= 1` arm (ids 7, 8) and the `arg1 == 1` arm select store
  sequences; every other path folds and latches. The `id == 7` arm
  shifts `arg1` right by 2 and retries; the `id == 8` arm signed-
  divides `arg1` by 6 (`divs`) and retries; other ids fail.
- The bit-mask check retries the fill for mask `583` bits
  (`{0,1,2,6,9}` under 10). Every pop frees the 36-byte frame and
  restores the entry-pushed caller registers, so retries drift up
  the caller stack and observe popped caller words: the first retry
  still carries the entry id, later ones carry caller pattern and
  fast-fail in the fill guard. The fail tail reports -1, cycles the
  shift (`sextb`), forces `arg1` to 1, and re-enters the body.
- The merge/store arms overwrite the entry-pointer register with
  mask/table bytes, so later fail-loop iterations read wild but
  deterministic addresses (same pc and address on all sides).

## Provenance

`g2/components/shared/gx8002/runtime_gx8002_uart_stage1_raila.S`
(MIT, clean-room transcription; notice
`NATIONALCHIP-UART-BOOT-STAGE1-RAILA-NOTICE.txt`). No SDK text is
reproduced and no SDK register map is used: every address comes from
the fill-provided descriptor and every constant is a stock immediate.
The gas spellings `lsl`/`lsr` assemble to the stock `tlsl`/`tlsr`
encodings byte-for-byte (probed: identical bytes, objdump prints
both back as `tlsr`/`tlsl`).

Assembly (rather than C) because the body keeps its working set in
high registers across the fill call and re-uses one frame pointer
for the retry/fail drift machine: a C shape would spill private
stack traffic that the battery would have to exclude from
comparison. A private half-body C probe (entry gate, fill, first
gates, id table, desc poll; 194 stock bytes) compiles to 108 bytes
with the tranche flags, so size alone would likely fit the envelope;
the choice keeps every push/pop/drift access in the compared trace.
The probe was scratch-only and is not kept in the tree.

Two decode subtleties the battery arbitrated (both resolve to the
plain reading; recorded so the next tranche does not re-derive
them): the entry `arg1 >= 3` arm skips the pop (first transcription
draft routed it through the pop and missed byte-identity by one
byte), and retry fills observe popped caller seeds rather than the
entry id (first oracle draft scanned for the entry id and diverged
after the second fill; the fix models the fill id as the current
r5). At most two fills carry descriptor traffic per run; later
retries fast-fail in the fill id guard.

## Verification

`g2/tools/verify_gx8002_uart_stage1_raila.py` (report
`docs/research/gx8002-uart-stage1-raila-verification.json`, **228
cases**, zero exclusions):

- Assembles the `.S` with the tranche flags, links the section at
  its runtime entry together with the recompiled fill into one
  `raila.elf` with no undefined symbols and no relocations; the
  464-byte section exactly fills the envelope at aligned package
  offset `0x8B0` and is byte-identical to stock (corroboration, not
  admission).
- Decoded-target execution of stock vs linked body over a flat
  word-RAM model (entry table plus margin, b0 cell, both domain
  windows, tall pattern caller window for the drift; unmapped
  addresses trap): identical **unfiltered** access traces (kind,
  address, width, value of every read and write, including
  push/pop/drift traffic), identical final RAM, identical registers
  (all 32 plus sp) at non-trap stops. Stop rule shared by all three
  sides: 260 fail re-entries, 60 fill calls (never reached: chains
  are bounded by construction at 3 fills), or the first unmapped
  access. All 228 battery cases stop at traps (fail-loop wild
  reads); trap stops compare pc (as a faultable-pc set per oracle
  block), address, traces, and RAM, but not the register file.
- Independent Python oracle on every case: label-block emulation
  stated from the decoded structure (entry gating, fill scan with
  current-r5 id, bit test, id table, desc-table test, merge/store
  arms, dispatcher, mask check, fail tail with shift cycling, table
  polls, pop drift). The oracle agrees with stock on all 228 kinds,
  traces, RAM states, and registers.
- Battery: 3 table modes (direct, entry-0 fallback, scan hit) x
  entry classes (arg1 in {0,1} x ids
  {1,2,6,7,8,9,16,19,22,23,25}; arg1 == 2 x ids {0,1,2,6,9,10,11,25};
  arg1 in {3,12} x ids {0,7,8,9,25}) x entry bytes (A: b4 3, b5
  0x5a, b6 7; B: b4 31, b5 0x7f, b6 -128) x m/d3 bit set/clear x
  shallow/deep table bytes x entry0 spots x arg2-dead triples.
  Arm coverage from trace signatures: descpoll 26, tpoll chain 38,
  stored5 latch 5, storearg 32, merge/d4-latch 52, foldrot retry 13,
  asr/divs retry 10, mask-check retry 12.
- `g2/tests/test_gx8002_uart_stage1_raila.py` (23 tests):
  interpreter unit checks for the new opcodes (`divs` truncation
  incl. negatives and div-by-zero, `asri`, signed `cmplti`,
  two-operand shifts, two-operand `nor`, push/pop, `bsr` cap,
  rejections), fail-visit and fill-cap stop counters, trap pc sets,
  oracle leftover/dead-arg2/retry-id/stored5/table-helper checks,
  full-battery edge coverage, stock-envelope regression, and
  fit/no-relocation/byte-identity regression. Native host execution
  is infeasible (the leaf dereferences 32-bit target addresses that
  truncate on the 64-bit host); the interpreter tests execute the
  assembled target object instead.

Accepted boundary (documented, not verified): id-range, fill-fail,
and entry-6-0xFF arms reach the fail tail with unset address
registers; trap-stop register leftovers are
implementation-defined. Register shifts by a register count use the
low 5 bits, signed division truncates with the divisor always the
nonzero constant 6 on executed paths (both sides share the
executor, so agreement holds by construction; hardware semantics
remain unqualified). Hardware timing and whole-device behavior stay
unqualified (`hardware_qualified: false`).

## Integration

Registered as `uart-stage1-raila` in
`tools/build_gx8002_source_candidate.py` (artifact `raila.elf`,
baseline above) and in the `gx8002-source-candidate` test list in
`g2/Makefile`. Tranche admission was verified through the builder's
exact `reviewed_replacements` + `compose` path in a private output
dir (`g2/build/continue-analysis/CD-001/raila-compose`): 1
replacement, 464 compiled bytes, ownership split at package
`0x8B0..0xA80`, firmware size unchanged. The generated
`gx8002-source-candidate-build.{json,md}` and experimental manifest
pins regenerate from the green shared run, so they are deliberately
not hand-edited here. Shared-gate status below.

## Remains (CD-001, still retained)

CD-001 is now 2,306/8,192 bytes source-owned (1,842 prior + 464
here). Still retained: init routine (`0x100001BC`), handshake
orchestration (`0x100001FC`), receive loop (`0x100002C8`), time-ms
leaf (`0x100003BC`, dead-path trap, envelope too small), the
`0x1000046C`/`0x100004A4` trap tails, the beacon (`0x100004D0`),
configure/announce/handshake (`0x100005C4`/`0x1000065C`/`0x100006D8`),
the `0x10000C9C` flow, both dispatchers (`0x10000D98`/`0x10000EA0`,
D98 fit floor 298 B vs 264 B envelope, deferred) and everything they
gate, the rail sweep (`0x10001378`, ~600 B two-exit loop, needs an
end/shape mapping pass first), the `0x100019C0` region, postambles,
the `0x10001DDC` orchestrator, and the `0x10001E60..0x10002000`
tables. Hardware qualification stays blocked by unavailable physical
evidence.
