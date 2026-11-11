# QMA reset polling in C

`r1_qma_reset` now uses ordinary C instead of naked assembly. Stock entry
`0x871c4` and REA/Ghidra establish two polling phases with separately
zero-initialized output bytes. Every helper status is ignored and reset
returns zero even after polling times out.

The preamble writes `36=b6`, delays five units, writes `36=00` and delays
100. The first phase writes `11=80`, delays two, then reads register `11`
until its output byte is `0x80` or 102 reads have occurred. The second
phase writes `33=08`, delays five, then reads register `33` and delays
ten after every read, including a completing read. It stops when the
post-delay byte is five or after 102 reads. On the final allowed iteration
the count limit exits without another scratch-byte test.

Const volatile views of ordinary scratch bytes preserve reloads after
callbacks, including a delay using an output pointer retained by an
earlier read. Each phase uses a stable pointer and the two pointers are
distinct. Only the initialized low bytes in the native saved words are
owned; their surrounding bytes and private frame layout are not copied.

Stock/source comparison passes 292 scenarios covering completion near
both loop boundaries, responses beyond the cap, full timeouts, partial
non-writing reads, delay-driven byte changes, ignored random status
values and interrupt masks. An independent polling oracle checks counts
and the full write/read/delay plan. Ordered scratch-byte reads, callback
traces, return values, callee-saved registers, restored stack and masks
match. Mocked calls clobber caller-saved registers/flags and require
eight-byte stack alignment.

The C and stock bodies are both 138 bytes; this does not establish byte
identity. All other QMA configuration function instruction bodies remain
unchanged, including the setup and identity/layout caller bodies. All
562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-reset/report.json`; imports remain 227 application
and 34 bootloader.

Physical sensor reset, delay timing, complete fault state, final linking
and byte identity remain unverified. No source-plan selection or G2
workflow gate changed. [Machine-readable evidence](qma-c-reset-review.json)
binds source/build/native hashes, REA observations and ignored probes
under `build/goal-r1-qma-reset/`.
