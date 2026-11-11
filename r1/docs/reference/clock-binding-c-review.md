# Clock snapshot and bind: single C owner

`application/board/native_clock_binding.c` now supplies the linked snapshot
helper at native `0x5a990` and bind helper at `0x5a9b4`. The snapshot assembly
definition was removed from `runtime/native_time_update.c`; its two event
functions retain identical code and relocations. The duplicate C definitions
were removed from `native_clock_bootstrap.c`. That constructor and its
second-change callback remain compile-only.

The locked application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
REA read the complete 64-byte window containing both helpers, including their
registration literals. This is observed byte evidence, not a claim of complete
Ghidra procedure analysis. The native executable extents are 32 and 24 bytes;
each is followed by a four-byte literal.

Snapshot reads registration byte `+12` and word `+16`, testing
`(-flag & snapshot) != 0`. A Boolean flag test would change opaque-word
behavior. It publishes the snapshot output before loading context at `+20`;
an output alias can therefore change the context subsequently returned. Bind
checks the backend's get slot at `+8`, stores backend and context, then publishes
the registration byte. Volatile packed SRAM views preserve access widths and
alias order without inline assembly. These views are not MMIO abstractions.

For each of normal Clang and GCC9, stock/C execution passes:

- 11,802 direct helper pairs: raw flags, opaque pointer words, null outputs,
  overlapping output/context and registration aliases, unaligned output words,
  bind-slot guards, access order, final memory, status, saved registers, stack
  pointer and interrupt masks.
- 9,216 live time-update parent pairs: actual stock parent against the unchanged
  relocated parent calling C snapshot, with backend get/update and cache clear
  modeled. Cases cover registration and callback availability, raw pending
  flags, signed offsets, wrapped arguments and callback statuses. All modeled
  provider calls retain the parent's native 56-byte frame.

Three negative controls reject Boolean flag substitution, an early context
read, and early publication of the bound flag. Normal composition builds all
576 R1 units without failures or duplicate strong symbols. Its import sets
remain 164 application and 34 bootloader symbols. The other 573 existing
objects are unchanged; only the old bootstrap and runtime owners change, with
one new C unit added. The manifest otherwise remains unchanged.

Official qualification compiles one generic variant and three GCC variants
(`O2`, `Os`, `Og`), accepting no new exact regions. The canonical hybrid rebuild
retains the locked application hash and the existing source plan: 4,023
source-built bytes, 642,137 retained executable bytes and 248 resource bytes.
Source-built totals include assembly and data. This change does not establish
complete source firmware or byte identity of these C helpers.

Private saved-register aliases, caller-clobbered registers and flags, arbitrary
faults, concurrent access and physical RTC behavior remain outside the proof.
Doubleword SRAM stores are compared as ordered word accesses; atomicity is not
established. Constructor ABI validation remains a separate dependency.

The [machine-readable receipt](clock-binding-c-review.json) records normal
build, REA evidence, execution, qualification, audits, probe hashes and limits.
Ignored probes are under `build/goal-r1-clock-binding-c/`.

The subsequent [time-update C review](time-update-c-review.md) replaces the formerly retained parent assembly with C, validates both compiler parents and preserves the existing exact source plan.
