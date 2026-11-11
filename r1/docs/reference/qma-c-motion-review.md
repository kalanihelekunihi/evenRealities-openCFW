# QMA any-motion configuration in C

`r1_qma_any_motion` now uses ordinary C instead of naked assembly. Stock
entry `0x86d40` and REA/Ghidra establish four zero-initialized read bytes
for registers `0x18`, `0x1a`, `0x1c` and `0x2c`. It sets bit zero in `0x2c`
and writes that byte, then reads the live chip ID. IDs `0x90` and `0xfa`
also write `2e=10`. It always writes `2f=00` and `30=ff`.

Enabling sets bits zero through two in `0x18` and bit zero in both route
bytes, writes `0x18`, then writes `0x1a` for axis zero or `0x1c` for axis
one. Other axis values skip that route write. Disabling clears those
bits and writes all three registers regardless of axis. Retained output
pointers observe the scratch updates, and route bytes are reloaded after
the `0x18` write, preserving callback changes.

Native POP restores the first two modified parameter words into R0/R1:
the original axis/enabled upper 24 bits combined with the final scratch
bytes for `0x18`/`0x1a`. The C function uses a uint64 result to reproduce
both words, including changes by later callbacks. Its only source caller
discards the result and retains its previous instruction body. This is
an execution contract, not an inference of the original source-language
return type. Saved R2/R3 upper bytes are not admitted as parameters or
return values.

Stock/source comparison passes 2,112 scenarios covering full-width axis
and enable values, every partial-read pattern, supported/other live IDs,
ignored statuses, pointer retention, scratch mutations before and after
write-back, and interrupt masks. Probes independently check register-call
order, arguments, both result words and masked scratch stores. Ordered
byte accesses, state/guards, callee-saved registers, restored stack and
masks match. Mocked callbacks clobber caller-saved registers/flags and
require eight-byte alignment.

The C body is 256 bytes versus 238 stock bytes. Every other QMA
configuration instruction body remains unchanged. All 562 R1 units
compile without failures or duplicate strong symbols in
`build/sources-goal-r1-qma-motion-verified/report.json`; imports remain
227 application and 34 bootloader.

Only the initialized bytes and two owned parameter words are reproduced;
private frame layout is not. Physical motion-event operation, timing,
complete fault state, final linking and byte identity remain unverified.
No source-plan selection or G2 workflow gate changed.
[Machine-readable evidence](qma-c-motion-review.json) binds source/build/native
hashes, REA observations and ignored probes under `build/goal-r1-qma-motion/`.
