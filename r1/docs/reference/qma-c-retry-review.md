# QMA transport retries in C

`r1_qma_read_retry` and `r1_qma_write_retry` in `native_qma_transport.c`
now use ordinary C instead of naked assembly. Stock entries `0x8714c`
and `0x873f4` each make at most five bus attempts. Any nonzero bus result
returns one immediately; five failures return zero. Reads delay five
units after every failure, including the final failed attempt. Writes
do not delay. Both reload the runtime address byte before each attempt.

The read wrapper preserves the full register argument, data pointer and
32-bit length. The write wrapper preserves the full register argument,
passes length one, and keeps one stable pointer to its initialized
four-byte value parameter. Its low byte is the requested payload; changes
to the parameter word by a callback remain visible on the next attempt.
A volatile runtime view preserves the byte-wide live address reads.

REA/Ghidra confirms both retry loops. Its write pseudocode emits an extra
stack-derived fifth argument; instructions and the established motion-bus
ABI use R0-R3 for four arguments. No fifth parameter is admitted.

Stock/source comparison passes 1,536 scenarios, including all 32 five-bit
success/failure sequences, full-width registers/lengths/values, null data
forwarding, nonzero success words, interrupt masks and caller-saved flag
clobbering. Bus and delay callbacks change the runtime address and read
buffer; write callbacks change the owned value word. Probes independently
assert attempt and delay counts, ordering, stable write-pointer identity,
complete parameter contents, live address reads, retained partial data,
context/guards, returns, callee-saved registers and restored stack/masks.

| Entry | Stock bytes | C bytes |
| --- | --- | --- |
| Read retry | 56 | 66 |
| Write retry | 46 | 52 |

The delay, chip-ID, IRQ and FIFO function instruction bodies remain
unchanged. The delay receives a proper C argument declaration; its
assembly and timing behavior are not converted here. All 562 R1 units
compile without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-retry/report.json`; imports remain 227
application and 34 bootloader.

Bus and delay calls are modeled. Private frames differ, and controlled
runtime placement at `0x20007698` does not establish final layout.
Physical bus operation, delay timing, complete fault state, final linking
and byte identity remain unverified. No source-plan selection or G2
workflow gate changed. [Machine-readable evidence](qma-c-retry-review.json)
binds source/build/native hashes, REA observations and ignored probes
under `build/goal-r1-qma-retry/`.

The later [chip-ID review](qma-c-chip-id-review.md) moves that probe logic
into C while preserving its saved-R3 seed through a minimal frame bridge.
