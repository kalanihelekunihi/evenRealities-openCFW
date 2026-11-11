# QMA interrupt dispatch C extraction

The IRQ frame bridge described below is superseded by the
[ordinary C interrupt entry](qma-irq-pure-c-review.md). The current entry uses
a local initialized status word and does not promise incidental R3 restoration.

The native IRQ entry at `0x86fa8` now delegates its read and dispatch logic to
`r1_qma_irq_body` in `native_qma_transport.c`. REA confirms the native scratch
initialization, ten outer attempts and interrupt-bit dispatch. Raw instructions
also show observable R0/R3 values that its inferred void pseudocode omits.
The stock entry is 72 bytes; the current compiler emits an 82-byte C body,
a 10-byte frame bridge and a two-byte callback ABI adapter.

The bridge retains the four-byte scratch word at entry SP-16. C explicitly
zeros it once, then requests four status bytes from register 9. Failed reads
retain earlier bytes; ten unsuccessful retry calls produce 50 bus attempts
and return R0=10. The native read helper and its C counterpart only return
zero or one. After success, bits 0-2 of byte 0 select the live any-motion
callback. Byte 1 is reloaded after that callback, so retained scratch changes
can enable or suppress tap dispatch. The tap pointer is also loaded live.

Without the tap flag, R0 contains byte 1 shifted left 26; a null tap pointer
returns zero. A tap call exposes its machine R0, although its declared C
signature is void. The `bx r0` adapter captures that value without an
incompatible function-pointer call. The frame restores the final scratch word
into R3. C helper stack depth differs from stock below that preserved word.

The ignored `build/goal-r1-qma-irq/verify.py` probe passes 4,278 stock-versus-C
scenarios. Both sides execute their actual read retry loops. Cases cover all
256 values of each dispatch byte, null callbacks, every possible success
position among 50 bus attempts, exhaustion, partial/non-writing reads,
delay changes to retained scratch, live address changes, any-motion changes
to the scratch and tap pointer, replacement tap callbacks, and full-width
callback results. Checks include callback arguments/order, runtime accesses,
scratch accesses, R0/R3, callee-saved registers, SP, interrupt masks and
eight-byte callback alignment. Seven other function bodies are unchanged.

The full R1 build compiles 562 units without failures or duplicate strong
symbols. Imports remain 227 application and 34 bootloader. Exact source,
manifest, image, REA and probe hashes are in
[the machine-readable review](qma-c-irq-review.json).

Bus, delay and event callbacks are modeled. Physical interrupt delivery,
sensor timing, complete fault-state equivalence, final linking and byte
identity remain unproven. No provider selection or G2 gate changes.
