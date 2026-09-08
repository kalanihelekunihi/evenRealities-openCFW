# Pad multiplexer getter candidate

The stock 44-byte section at package 0xfb18 / runtime 0x1020658c matches the
complete `.text.padmux_get` section in the authenticated NationalChip
`drivers_lib/padmux/grus_padmux.o` object. Its blob is
`e42a2efc51c4ebacf55575630907be84888ba61a` at SDK commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The object is comparison-only.

The C candidate rejects unsigned IDs above 32 (including negative signed IDs),
reads one word from 0xa0010090 + 4*(id/8), and returns the selected four-bit
function field. Pin 32 is accepted by the observed bound; it must not be
silently rejected on an assumed 32-pin limit. Native macOS compilation emits
40 bytes within the 44-byte region. SDK `gx_padmux.h` is authenticated.

Decoded MMIO/return/ABI qualification remains pending. The candidate is
unregistered and makes no firmware or hardware-readiness claim.

Decoded stock/C qualification now passes 3,034 cases: every valid pin ID,
invalid boundary/negative IDs, repeated nibble values, and walking-one/zero
word patterns. Four target tests cover pin 32 and deliberate changes to the
register address, nibble mask and upper bound. Source admission still awaits
reviewed evidence pinning and integration; physical pad behavior is unproven.

The reviewed getter report now pins verifier/builder hashes and exports the
standard integration row and ELF artifact. All 3,034 decoded cases and four
target tests pass after pinning. It is qualified but remains unregistered while
the active transfer integration finishes.
