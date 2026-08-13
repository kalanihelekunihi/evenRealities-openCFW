# Retained crash-log correlation

## Outcome

The recovered function at `0x0007F030..<0x0007F0C2` is a product-owned retained-log adapter,
not a formatting or transport implementation. Its 146-byte body has SHA-256
`c4537ceff474ee9645f623f81a6e5f86132a49f3170927b3c5d879aa1745f585`.
Function-local calls resolve to toolchain `vsnprintf`, bundled SEGGER RTT, the admitted health
crash-record initializer, and memory clearing. No Goodix, GoMore, GXCAS, QMA, YHM2710, sensor,
or health-algorithm dependency is present.

OpenR1 therefore implements only the R1-owned policy in `r1_retained_log`: a caller-owned
3,008-byte retained buffer, a 3,007-byte append-length ceiling and 3,006-byte normal payload
ceiling, one-time state reset, an
injected first-use callback for crash-record initialization, newline termination, and an injected
transport writer. The Nordic adapter uses the SDK-bundled `SEGGER_RTT_Write`; formatted bytes are
supplied by the toolchain/provider side, so OpenR1 does not recreate `vsnprintf`.

## Recovered behavior

The stock entry ignores a null format pointer. On first non-null input it marks the retained state
initialized, clears a 3,008-byte log buffer and a separate 1,008-byte retained workspace, binds a
retained record pointer, writes the `0x5A5A5A5A` marker, and invokes the crash-record initializer.
It then formats into the remaining log capacity, appends one newline after a positive result,
advances a 16-bit length, and writes the newly appended span to SEGGER RTT channel zero.

The clean API keeps the separate workspace and crash record behind the first-use callback rather
than inventing their ownership. It records initializer and transport errors without discarding a
captured line, matching the stock best-effort diagnostics role. A null rendered pointer is inert;
an explicit zero-length rendered value performs first-use initialization but appends nothing.

## Safety difference

C `vsnprintf` reports the number of characters that would have been written. The stock function
uses that return value directly for its newline index and retained length, even when it exceeds the
remaining buffer, creating a recovered out-of-bounds edge. OpenR1 caps the captured bytes at the
remaining 3,007-byte payload region, places the newline within the final byte, reports truncation,
and refuses further appends after the buffer is full. This is a memory-safety hardening of malformed
or oversized diagnostic output, not a change to normal in-capacity behavior. Byte 3,007 remains
unused in normal operation, matching the recovered `vsnprintf` capacity.

## Verification

Tests cover null and empty inputs, one-time initialization, callback error recording, exact bytes
sent to the transport, newline placement, full-capacity truncation, post-full refusal, reset, and
invalid arguments. The source compiles under strict C11, ASAN/UBSAN, and the freestanding
Cortex-M4 profile. The ownership verifier pins the recovered extent, size, hash, and clean-room
disposition. The linked Nordic image retains both the portable functions and the SEGGER RTT adapter
through `.openr1_retained_log_api`.

The portable reset and append functions link at `0x000349F0` and `0x00034A08`; the SDK adapter
links at `0x00037258`, SDK-bundled `SEGGER_RTT_Write` at `0x0002765C`, and the retained API table
at `0x0003B3C8` with size `0x0C`. The verified unsigned application is 90,956 bytes text,
236 bytes data, and 132,456 bytes BSS. Its HEX and BIN SHA-256 values are
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81` and
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`.

This component changes no signing, boot verification, rollback, authorization, flash-protection,
or deployment behavior.
