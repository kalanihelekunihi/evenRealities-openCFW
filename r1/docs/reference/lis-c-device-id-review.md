# R1 LIS2DW12 device-ID getter in C

The getter at stock `0x7517C` now uses a typed C call to read one byte from
register `0x0F`, returning the transport status unchanged. This unit now
includes the pinned ST header, replacing its handwritten transport declaration.
Only this manifest unit gains the ST and ARM C-library include paths; its
strict compiler options and composition participation remain unchanged.

All 2,096 callback comparisons pass. They cover every byte value, four
transport statuses, callbacks that do or do not write the destination,
null/all-one handle values and byte destination offsets 0–3. Callback
arguments are checked explicitly; destination bytes outside the requested
byte remain unchanged. Mocks poison r0–r3; r4–r11, entry SP and callback
eight-byte alignment pass.

Five additional comparisons check normal and mutated context reads, null
and truncated contexts and an unmapped callback target. Ordered context
accesses and fault kind/address/size match. Fault-time temporary register
contents and complete architectural fault snapshots are outside this check.
REA confirms the register/length call setup. Its inferred void pseudocode
signature is not treated as authoritative: stock assembly preserves the
transport's post-call r0, and execution verifies that status propagation.

The compiled getter is 10 bytes versus stock's 14 and tail-calls the existing
C transport. Callback SP is unchanged from entry versus stock's eight-byte
frame. No byte, private spill or timing identity is claimed. The other five
function bodies in this unit remain byte-for-byte unchanged from the preceding
motion-request build. Physical sensor/I2C behavior remains untested.

All 561 R1 units compile, both compositions pass without duplicate strong
symbols, and actual unresolved sets remain 238 application/34 bootloader.
No source-plan selection or workflow gate changed.

[lis-c-device-id-review.json](lis-c-device-id-review.json) binds source,
manifest, header, build report, candidate/native bytes, REA data and ignored
probe hashes under `build/goal-r1-lis-id/`.
