# QMA tap configuration C extraction

The stock `r1_qma_tap` entry at `0x872e4` now delegates its configuration
logic to C in `native_qma_configuration.c`. REA analysis and native Thumb
execution support this partial extraction. The 268-byte stock routine becomes
a 14-byte frame bridge and a 214-byte C body in the current compiler output.

Five register reads use bytes at offsets 0, 4, 8, 12 and 16 in the original
20-byte scratch span at entry SP-40. Failed reads can leave prior RAM in use.
The bridge retains those bytes and addresses; C receives the span explicitly
and uses volatile byte accesses. It does not read uninitialized C locals.
Configuration writes, full-width route selection, low-byte axis masks and the
last-write return value retain their stock ordering. Retained callback pointers
can change bytes before subsequent loads, which the C body preserves.

The ignored `build/goal-r1-qma-tap/verify.py` probe compares the stock image with
the compiled bridge and C body in 1,192 scenarios. It checks register-call
order and arguments, scratch byte accesses and final contents, return values,
callee-saved registers, restored SP, interrupt masks and callback alignment.
Cases cover absent read writes, all read-fill masks, full-width arguments,
invalid routes and callback changes through retained scratch pointers. The
six other function bodies in this compilation unit remain unchanged.

The complete R1 source build compiles 562 units without failures or duplicate
strong symbols. Application and bootloader imports remain 227 and 34.
Exact source, manifest, stock span, REA and build bindings are recorded in
[the machine-readable review](qma-c-tap-review.json).

Retry API callbacks are modeled in this probe. The C helper adds callback stack
depth below the preserved scratch span. Physical sensor behavior, timing,
fault-state equivalence, final linking and byte identity remain unproven.
This change does not qualify a provider or advance G2 workflow gates.
