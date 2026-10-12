# Boot PLL context-read round

Locked image SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

Native Thumb in the SYSPLL configure body at `0x42740c` validates the context magic, then performs a 32-bit read at context offset `+4` (`0x427424`) and a separate 32-bit reread at offset `+0` (`0x427426`) before testing the active flag. The selected static `pll_configure` previously reused its first context word and omitted the second word read. It now uses volatile context access in the native order. The read at `+4` has no data-flow consumer, but is still an observable bus/fault/concurrency access; it must not be optimized away.

The coherent `boot-coplacement-pll-context-read-round/receipt.json` is `PASS_BOUNDED_LINK`: 373 C/ASM units, 1,010 source providers, three explicit ROM imports. Selected `unit_013.o` disassembly of the inlined caller shows `ldr.w r0,[r8,#4]` at `+0x1ce` followed by `ldr.w r0,[r8]` at `+0x1d2`. This proves emitted load order for this candidate; no physical SYSPLL execution or whole-body equality is claimed.

The body crosswalk auditor now gives validated selected static definitions precedence over an address string in a file header. `selected_static_bindings.json` already had a real `pll_configure` definition binding; the updated basis cites the observed reads. The refreshed crosswalk has 654 directly rooted catalogue entries, 158 rooted header-only proof leads, and zero rooted entries without a machine crosswalk. Header-only leads are attribution work, not a count of missing C bodies. The previous rooted list had 161 header-only leads; the reduction of three includes precedence corrections, so it does not represent three new implementations.

Next high-value source proof target is the 332-byte SYSPLL postdivider body at `0x427160`, already represented by selected `clock_generators.c` but currently supported only by its source header in the crosswalk. Its full scoring and copy branches need native comparison. The three ROM contracts, indirect/root qualification, source data/scatter placement, and runtime behavior remain open; this round does not complete the Bootloader image.
