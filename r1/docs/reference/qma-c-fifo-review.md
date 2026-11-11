# QMA bounded FIFO C extraction

The stock FIFO entry at `0x86ff4` now delegates bounds, reads and logging to
`r1_qma_fifo_body` in `native_qma_transport.c`. REA decompilation agrees with
the native control flow; raw-image execution checks the compiled extraction.
The 190-byte stock entry becomes a 10-byte frame bridge and a 200-byte C body
with the current compiler. This conversion does not establish byte identity.

The bridge preserves the incoming R3 word at entry SP-24. Its low byte supplies
the depth when a read does not write; the final pop restores the modified word
into R3. C receives that existing byte through an explicit volatile pointer.
Replacing it with a zeroed local would change stock behavior.

Null output returns `UINT32_MAX`. A failed depth retry logs the state error
and returns `UINT32_MAX`. Successful depth reads mask bit 7, reject depths
above 64 with the depth error, and otherwise request six bytes per sample up
to the unsigned caller capacity. Zero capacity still invokes the read with
length zero. FIFO-read and reset-write statuses do not change the returned
sample count. Each log-mode query retains the native short-circuit order.

The ignored `build/goal-r1-qma-fifo/verify.py` probe passes 2,944 stock-versus-C
scenarios. Both sides execute their actual read/write retry loops. Coverage
includes every depth byte, capacity boundaries, all five-attempt outcome and
fill masks, null output, non-writing reads, retained scratch changes, changing
bus addresses, changing log modes and caller-saved register/flag clobbers.
Checks include callback arguments/order, log text, scratch accesses, output
bytes and guards, R0/R3, callee-saved registers, SP and interrupt masks.
All six other instruction bodies in this source unit remain unchanged.

The full R1 build compiles 562 units without failures or duplicate strong
symbols; imports remain 227 application and 34 bootloader. Exact hashes and
probe bindings are in [the machine-readable review](qma-c-fifo-review.json).

Bus, delay and logging callbacks are modeled. The C helper adds callback stack
depth while retaining native scratch addresses and eight-byte alignment.
Physical FIFO behavior, timing, fault-state equivalence, final linking and
byte identity remain unproven. No provider selection or G2 gate changes.
