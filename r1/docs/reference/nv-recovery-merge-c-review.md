# Fill-only NV recovery merge in C

The C implementation of stock `0x7bd68` closes
`r1_native_nv_recovery_merge_boundary`. It verifies the CRC and fills missing
cached identity, temperature and accelerometer calibration fields without
replacing valid local data. Existing class handles and dirty-state ownership
are reused; no direct flash flush is added.

Battery type 1–4, nonzero ADC compensation within -500 through 500 except -1,
and ring size 6–15 are retained when already valid. Valid incoming values fill
invalid local values. Each serial string is filled only when its local length
is 255; incoming lengths must be 1–30, and trailing local bytes are preserved.
Temperature calibration uses its first-byte sentinel; accelerometer calibration
uses its first signed-halfword sentinel. Accelerometer-only recovery still
forces a serial-class write, matching stock's control flow.

All 3,666 stock/C trace comparisons pass and execute every one of the 984 native
instruction bytes. Tests cover all 128 changed-field combinations, scalar
boundaries, CRC rejection, null input, modes, live handle replacement and four
input alignments. Independent CRC and fill-only oracles check admitted writes.
Actual C CRC and memory routines execute; KV and logging callbacks are modeled.

Another 440 cases execute actual cached-class reads and writes. They check
payloads, dirty flags, preserved bytes, critical-section balance and real
class-size mismatch handling. Fourteen C-only cases verify that failed reads
and incorrect record lengths produce no writes. Six compiled defects changing
preservation, zero ADC handling, serial admission, accelerometer writes, CRC
admission and read-error handling are rejected.

The C version accepts only the dispatcher’s 116-byte record and stops if any
cached read fails, preserving records whose current state is unavailable.
Scratch buffers are initialized. Completion returns zero rather than exposing
incidental logger/cache result registers; return words are normalized in stock
comparisons. These are explicit differences from stock's unsafe error paths.

All 855 units compile and both relocatable payloads compose. All 844 prior
nongenerated objects remain unchanged. Application imports fall from 64 to 63;
bootloader imports remain 22. R1 manifest validation passes. Successful cached
writes still depend on the existing persistence worker. Physical persistence,
radio operation, final linking and boot remain unverified.

[Machine evidence](nv-recovery-merge-c-review.json) binds source, REA, probes,
negative controls and build reports.
