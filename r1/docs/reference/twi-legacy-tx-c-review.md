# Legacy TWI transmit copies: typed C providers

Current implementation: [ordinary C transmit shim and packet-chain integration](twi-write-chain-c-review.md). Fixed-register constraints described below have been removed.

`application/board/native_hw_twi_legacy_tx.c` supplies C providers for the
native wrappers at `0x78a24` and `0x78a32`. Both instantiate the pinned Nordic
SDK 17.1.0 `nrf_drv_twi_tx` inline path; no SDK implementation was copied.
The shared header provides their typed legacy-instance interface.

REA read both complete 14-byte native bodies. Each advances the instance
pointer by four bytes to its embedded TWIM instance, forwards the four
register arguments and the fifth stack argument, and calls `nrfx_twim_tx`.
The native SDK-entry frame is 16 bytes. The C unit disables sibling calls and
uses an empty R4 constraint to retain that frame and the fifth argument's
provider-visible register value. No authored assembly instructions were added.

The normal Clang object passes 11,520 stock/C pairs across both wrappers,
byte address/length boundaries, both Boolean fifth values, raw return statuses,
incoming flags and two instance addresses. Checks compare all five arguments,
the embedded-instance offset, provider SP, R4–R11 and APSR, final saved
registers, masks, caller fifth word and data effects. The modeled SDK provider
can modify the buffer or its outgoing fifth argument. Four negative controls
reject the wrong instance offset, wrong fifth value, missing R4 constraint and
a sibling-call frame.

Strict official GCC qualification does not compile: all six scoped variants
encounter `-Werror=unused-parameter` in the pinned SDK's naked SVC declarations.
The original receipts are retained. A GCC probe with only
`-Wno-error=unused-parameter` added compiles and passes the same 11,520 pairs;
warnings remain in its log. That probe is separate from official qualification,
and no product warning policy was changed. Ten generic Clang variants compile
but accept no exact regions. These C wrappers are not byte-identical selections.

Normal composition builds all 577 R1 units without failures or duplicate strong
symbols. The existing 576 objects and callers are unchanged. The new providers
depend only on the already linked SDK `nrfx_twim_tx`; application/bootloader
imports remain 164/34. Existing register adapters do not yet consume the new
providers. Their separate C conversion must preserve the native stack aliases.

One such boundary is now verified by eight actual native write-adapter runs,
with TX modeled to return 17 without modifying memory. At length 80, the
register prefix starts at frame `+4`, and payload byte 79 lands at frame `+84`,
overlapping the saved R4 low byte. Both adapters consequently return that
mutated R4 value. Length 79 preserves R4; length 81 returns 9 before TX. This
is stock execution evidence, not a proposed guard change. A C rewrite must not
silently replace this behavior with a larger private buffer or a different
length limit. The existing register bridges remain unchanged.

The canonical hybrid application retains locked SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The source plan remains unchanged: 4,035 source-built bytes, 642,125 retained
executable bytes and 248 resource bytes. Source-built totals include assembly
and data. Complete source-only firmware remains unproven.

The transmit tests cover valid byte-sized address/length and Boolean
`no_stop` values. Raw caller-clobbered R1–R3/R12/LR, private stack padding and
saves, arbitrary faults and concurrent access remain outside their comparison.
The SDK TX operation is modeled; these tests do not prove physical bus, DMA or
IRQ behavior.

The [machine-readable receipt](twi-legacy-tx-c-review.json) records REA, SDK
hash, normal build, strict GCC limitation, diagnostic probe, controls and native
write-boundary evidence. Probes are under `build/goal-r1-twi-legacy-tx-c/`.

The subsequent [TWI read C review](twi-read-c-review.md) replaces both read bridges with direct C and connects them to these providers. Write paths and their length-80 saved-R4 overlap remain unchanged.

The subsequent [packet-write C review](twi-packet-write-c-review.md) removes both packet-write bridges and their helper kernels while preserving the 16-byte frame. Packet read paths and register-write adapters remain unchanged.

The subsequent [register-write C review](twi-register-write-c-review.md) replaces both register-write bridges while preserving the length-80 overlap. Read function bytes and relocations are unchanged. The actual bulk packet/register/legacy-TX C chain passes 9,000 comparisons at native SDK depth 136.
