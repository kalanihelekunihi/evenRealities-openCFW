# Stream logger raw-result ABI adapter

The sensor-stream reducer's last logging import now resolves through a
four-byte tail branch to the already linked `nrf_log_frontend_std_2` provider.
There is one logger implementation. The reducer's compiled function body is
unchanged. Its C algorithm remains C; only this raw-register boundary uses
assembly.

REA confirms the sixteen-byte stock wrapper at `0x799d6`, which passes two
arguments to the internal logger and returns without restoring R0. The
pinned Nordic SDK declares the corresponding frontend `void`. An ordinary
C call cannot portably capture that raw result; redeclaring the SDK logger
as integer-returning would be incompatible. The adapter preserves the four
argument registers, SP and caller LR and returns the selected SDK provider's
raw R0. It adds no frame and duplicates no logging logic. This does not
promise identical incidental R0 values between the source SDK internals
and stock logger internals.

The existing rate-reducer fixture now reaches the modeled SDK entry through
the actual adapter. All 2,367 stock/C pairs pass, including varied raw
returns, log modes, buffer resizing, provider mutation, timer updates and
zero-divisor paths. Another 1,024 direct cases verify arbitrary arguments,
stack argument bytes, LR, return R0, callee-saved registers, SP and masks.
Three compiled defects (discarded result, modified ticks, modified owner)
fail behavioral assertions. The normal fixture is rerun after defects.

The current strict application ELF confirms why a local C expression cannot
replace this branch: `nrf_log_frontend_std_2` at `0x8b05a` calls SDK `std_n`,
whose last path can leave either its header word or the dequeue result in R0,
then tail-branches to the weak `log_pending_hook` at `0x8afcc`. That hook is
an empty leaf in the current link, so it preserves whichever R0 the SDK path
left. The SDK C signatures for all three functions remain `void`. Capturing
that value through an incompatible C declaration would make the source
undefined, and returning a guessed constant would break the tested raw ABI.
The four-byte branch remains the source-compiled boundary.

All 801 R1 units compile without failures or duplicate strong symbols;
application imports decrease from 93 to 92. The other 798 object hashes
are unchanged; two generated boot objects retain allocated bytes and
relocation identities. Strict bootloader linking passes without unresolved
references. R1 source checks pass; global source checks retain the unrelated
G2 unlisted `resident_rom_thumb_set.S` failure. The source-composition
receipt's explicit unresolved counts are refreshed from the actual report.

The SDK logger is modeled at entry; this test does not execute its backend.
Physical sensor timing, asynchronous logging and complete application final
linking remain unverified. No source-plan selection changes. See the
[machine-readable review](stream-log-abi-review.json) for evidence hashes.
