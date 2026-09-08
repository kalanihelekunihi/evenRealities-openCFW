# GX8002 TWS initialization

The TWS initialization source is adapted from NationalChip/lvp_kws commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The shipped configuration uses
MAX decoding, a seven-entry queue of eight-byte elements, standby FVAD state
2 and countdown 50. The MAX decoder identification is supported by the
upstream initialization and its matching diagnostic string, not a guessed
choice among decoder variants.

The initial handwritten unsigned wakeup prototypes were rejected when
compiled alongside upstream's enum declarations with `-Werror=enum-int-mismatch`.
The build now extracts exact enum/prototype declarations from authenticated
upstream headers into a small generated interface header. The firmware C uses
that enum directly. A target compilation probe checks the enum's underlying
compatibility and COLD/WDT values. Queue, mode and SNPU types are included from
upstream headers. No binary data supplies any source declaration.

The native macOS C-SKY compiler emits 108 bytes matching stock, with the
original 12-byte frame. A continuous instruction model checks both stock and
candidate against independent expected traces in 5,130 cases. Checks cover
initial flag versus other modes, cold/watchdog versus other wakeup values,
audio success/failure, volatile caller registers, exact helper arguments,
and standby write order. Seven regression checks include queue size, wakeup
threshold, countdown, helper and return-frame mutations.

This reconstructs initialization control flow. Decoder/audio/KWS services,
TWS callbacks, message and BSS state remain separate dependencies. Returning
helper models do not prove hardware behavior, timing, or whole-TWS operation.

Full integration passed 305 tests. This adds one C function (108 bytes), for
129 C functions / 145 occurrences, two architecture entries and 27 source-data
regions. Codec ownership is 8,730 C bytes, 120 assembly, 2,280 source data,
80 metadata, 336 fill and 314,546 retained bytes. The emitted bytes match the
previous stock region, so the codec hash is unchanged. Decoder and remaining
TWS functionality still need reconstruction; the full goal remains active.
