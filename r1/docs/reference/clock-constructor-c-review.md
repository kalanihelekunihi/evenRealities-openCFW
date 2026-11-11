# Native clock constructor: state aliases and callback reloads

Current status: [bootstrap normal-link integration](clock-bootstrap-link-review.md) closes the later callback gate; the results below retain their original scope.

The C constructor in `application/board/native_clock_bootstrap.c` now copies
configuration words before publishing either word, derives the UTC offset from
the copied state, and reloads its exposed backend/context slots across
callbacks. It remains compile-only. The second-change callback still needs
its own frame validation before this unit can participate in normal linkage.

REA read all 152 bytes at native `0x8adc0`: 136 executable bytes and four
literal words. Raw Thumb decoding shows a 24-byte frame, with saved context at
frame `+0` and backend pointer at `+4`. The native constructor reloads the
backend after init and update callbacks, allowing either callback to replace
or clear it. It passes a zero-extended 16-bit offset to update and preserves
incoming R1 as context when snapshot fails and the default backend is bound.
This is observed byte evidence, not a complete Ghidra procedure-analysis claim.

The former C implementation used `memcpy`, reread the input configuration's
offset after copying, did not recheck backend nullness after callbacks and compiled with
a 32-byte normal Clang frame. The revised C uses ordered volatile SRAM word
views and an escaping scratch union. In the recorded normal Clang build its
context/backend slots are at frame `+0/+4`, and provider calls retain the
native 24-byte frame. No inline assembly or fixed-register constraints were
introduced. The padding is a compiler-layout candidate, not a portable ABI
guarantee.

The actual normal Clang object passes 4,400 stock/C execution pairs, including:

- Registered-state early return, raw snapshot flags, absent callbacks and
  failed or successful initialization.
- Null/default input, input aliases into shared state and registration memory,
  offset/epoch boundary words and incoming context aliases into exposed slots.
- Init/update callbacks that replace or clear the backend, change context, or
  mutate state before the next callback.
- Callback argument order, shared memory, status, final saved registers,
  stack pointer and interrupt masks.

Snapshot and bind execute their actual stock/C bodies. Init, update, tick bind
and cache clear are modeled; default init executes its actual body. Default
backend and second-change function pointers are normalized by role. The C
getter can fold to its constant backend, so getter call-boundary identity is
not established. Private saved-register aliases, raw caller-clobbered
registers/flags, provider scratch reads, concurrency and physical RTC behavior
remain outside this proof.

Negative controls reject a shorter frame, signed update offset and rereading
the aliased input offset. The alias control initially survived because the
fixture seeded equal low halfwords in adjacent state words. Distinct words
were added, and both the real normal object and all negative controls were
rerun successfully; the comparison was strengthened.

GCC9 compiles the revised constructor but fails the native frame check:
32 bytes instead of 24, with context/backend slots at `+4/+8`. Its rejection
is retained in the receipt. GCC does not inherit the Clang validation.

All 576 R1 units compile without failures or duplicate strong symbols. The
other 575 objects and six other bootstrap functions are unchanged. The
manifest is unchanged, the bootstrap remains excluded, and both normally
composed payload hashes are identical to the prior build. Imports remain
164 application and 34 bootloader symbols.

Official qualification compiles four generic and twelve supported GCC
variants and only reselects existing fragments. No constructor bytes are
admitted. The canonical hybrid application retains locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and the unchanged source plan: 4,023 source-built bytes, 642,137 retained
executable bytes and 248 resource bytes. Source-built totals include assembly
and data; complete source firmware remains unproven.

The [machine-readable receipt](clock-constructor-c-review.json) records REA,
normal execution, negative controls, GCC rejection, qualification and audits.
Ignored probes are under `build/goal-r1-clock-constructor-c/`.
