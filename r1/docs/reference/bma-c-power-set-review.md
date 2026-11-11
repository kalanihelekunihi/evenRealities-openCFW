# R1 Bosch power-save setter in C

The setter at stock `0x5468E` now uses C. It initializes a scratch byte to
zero, checks the device, reads register `0x7C`, updates bit zero with the
existing Bosch C byte helper, and writes that byte back. The first nonzero
status stops the sequence and propagates unchanged. The checker uses its
actual signed eight-bit return declaration. The retained write boundary now
has explicit four-argument types; its instruction bytes are unchanged.

All 2,304 modeled comparisons pass. A full byte sweep combines all 256
register values with enable inputs 0, 1, 2, 255, 256 and UINT32_MAX. A second
sweep varies checker/read/write statuses independently, whether the read
callback writes its byte, and null/non-null device arguments. Checks cover
call order, register/length/device arguments, initial scratch zero, identical
read/write scratch pointers within each execution, the exact byte written,
returned status and skipped operations after errors. Callback mocks poison
r0–r3; r4–r11, entry SP and eight-byte callback alignment pass.

REA confirms the read-modify-write branches and bit mask. Its inferred void
pseudocode return is not taken as authoritative; stock assembly and execution
show that the last executed operation status is returned. The candidate
executes the normal compiled C bit helper, while the checker and read/write
boundaries are explicit mocks. Physical sensor power state and bus behavior
are not tested. Private stack depths differ and are recorded separately;
complete fault state, private spills, timing and byte identity remain open.

All other functions in this source unit retain their instruction bytes.
All 561 R1 units compile, both compositions pass without duplicate strong
symbols, and unresolved sets stay at 238 application/34 bootloader.
`make sources-check` passes for both trees. No source-plan selection or
workflow gate changed.

[bma-c-power-set-review.json](bma-c-power-set-review.json) binds source/helper,
build, native/candidate bytes, REA results and ignored probe hashes under
`build/goal-r1-bma-power-set/`.
