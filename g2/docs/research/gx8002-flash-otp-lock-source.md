# OTP lock candidate

Recovered runtime_gx8002_flash_otp_lock.c from package0x16264 (not0x1626c,
which is inside the routine). Runtime entry10024250 agrees with the retained
interface table. Native macOS C-SKY compilation fits100/100 bytes and uses
the original16-byte frame:12 saved registers/LR plus4 local bytes.

It reads selected_device, descriptor pointer at+20, then flags at+16. After
wait-ready it reloads selected_device and reads the signed manufacturer
halfword at+6. Unsupported manufacturers return-1. Values0x5e/0x85 proceed:
read status1 into byte0, read status2 and OR bit((flags&7)+3) into byte1,
wait-ready, write-enable, then command-write(1,local_buffer,2). It ignores
helper returns and returns0 without a final wait-ready call. For region
values5..7 the selected bit is outside the stored byte, so narrowing drops
it; do not silently constrain the region to the descriptor's normal range.

The C source preserves these operations. Compilation uses LD.H+SEXTH in
place of LD.HS and different saved-register allocation. Decoded helper-order,
status-payload, state-reload, clobber and rejection qualification remains.
The routine is not admitted to the integration builder, and no OTP locking
or other hardware operation was performed.

Decoded comparison passes25800 cases, using all256 values of each status byte
in a permuted pair set plus32-bit extremes, ten flag patterns, five signed
manufacturer values and two helper-clobber seeds. The device pointer changes
across wait while flags remain from the original descriptor. The checker
requires the six-call sequence on supported devices and one wait on rejected
manufacturers, exact command arguments(1,SP-16,2), correct two-byte payload,
return value and16-byte frame. Helper failures are ignored as in stock; no
final wait is added. Four rejection tests pass. Helper effects are modeled;
these are not hardware locking tests. Admission adapter prepared separately.

OTP lock fully integrated. Native macOS codec build passes202 tests; full
package build and verify-artifacts pass with apple-clang. Ownership7220 C,
2040 source data,80 metadata,302 fill,316450 retained;113 functions and129
code occurrences plus16 data regions. Codec SHA:
f92c56731ae3896e8414d5d6c870073c24b77174258b9c3187cd675b7978064a.
Package SHA:44b611556ef32745f021fe892b58f26ba815feceb5f99f191abcdb9d3c387bcf.
Candidate pin identifies this hybrid, not vendor identity or hardware proof.
Full source-only goal active; no physical OTP operation.
