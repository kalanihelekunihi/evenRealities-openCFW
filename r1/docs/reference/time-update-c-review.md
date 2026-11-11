# Clock-update adapter: C provider frame and callback state

The current [constraint-free clock review](time-update-pure-c-review.md) supersedes the register/frame constraints below. Both entries now use ordinary C; Clang and GCC retain the backend/state contract without byte identity or incidental caller-register requirements.

`application/runtime/native_time_update.c` now implements the adapter at
`0x8aeb0` in C. Its naked assembly body and authored state/registration
literals were removed. This file has no remaining emitted inline-assembly
instructions; empty register constraints retain provider-visible values.
The pending setter's code and relocations remain unchanged.

REA read the complete 144-byte native window: 136 bytes of code and two
literal words. The adapter checks registration and snapshot availability,
compares the full incoming offset against the sign-extended stored halfword,
conditionally clears the 20-byte calendar cache, and calls the backend.
The raw pending byte is XORed with 1; it is not normalized to Boolean.
Successful updates may publish the old timestamp and pending byte according
to that cached decision.

The exposed context/backend slots are at frame `+0/+4`. The original backend
in R6 supplies the get slot, while the update callback is loaded through the
possibly changed backend slot after get returns. A get callback may replace
or null that slot or change context. The C implementation retains this order,
including the stock null-backend fault rather than adding a new guard.

Empty constraints bind R4–R11 around provider calls. The scratch union retains
the normal 56-byte provider frame and caches the raw pending decision. Without
an explicit volatile cached copy, a GCC candidate omitted the conditional
publication and diverged after a callback changed sync state. That
counterexample and a reproducible GCC negative control are retained. The final
candidate passes both compilers; the fixture also seeds an existing timestamp
nonzero to detect unconditional publication directly.

Each of the Clang and GCC parent objects passes 9,552 stock/C pairs in each
of two modes: modeled memory clear and actual native/source memory clear.
Snapshot executes actual stock/C code. Actual-clear mode executes the normal
EABI and musl providers; only backend get/update callbacks are modeled.
Shared helper objects use the normal Clang build even when the parent uses
GCC. Checks cover:

- Registration, snapshot/get/update availability, raw pending bytes, offset
  boundaries, raw update statuses and old timestamps.
- Backend/context replacement, sync/cache mutation and 32 matching null-backend
  faults per compiler and mode.
- Callback arguments/order, shared memory, status, final saved registers,
  interrupt masks, R4–R11 at provider entry and the 56-byte frame.

Five negative controls reject an incorrect frame, Boolean pending policy,
stale backend, missing R11 binding and truncated offset comparison. The
existing pending setter passes its 4,096 full-register pairs again.
Private saved-register/padding aliases, raw caller-clobbered registers/flags,
arbitrary backend faults beyond the tested null case, concurrent access and
physical RTC behavior remain outside this proof.

All 576 R1 units compile with no failures or duplicate strong symbols. The
other 575 objects and strong symbol sets are unchanged; imports remain 164
application and 34 bootloader symbols. The runtime unit now uses the C/SRAM
profile. Its shared header uses a self-contained relative include; that
include-only change does not alter other compiled objects. Bootstrap remains
compile-only pending its separate callback/ABI work.

Official qualification compiles 15 generic and nine supported GCC variants,
reselecting only the already admitted Clang setter. No adapter bytes qualify.
The exact source plan is unchanged, and the canonical hybrid retains locked
application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Coverage remains 4,035 source-built bytes, 642,125 retained executable bytes and
248 resource bytes. Source-built totals include assembly and data; complete
source firmware and adapter byte identity remain unproven.

The [machine-readable receipt](time-update-c-review.json) records REA,
execution, controls, compiler counterexample, qualification and audits.
Ignored probes are under `build/goal-r1-time-update-c/`.
