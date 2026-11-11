# STACMD read-frame native scratch and live parity

`board/native_stacmd_frames.c` now runs the read parser in a C kernel with
an eighteen-byte frame bridge. Native `0x28bb0` saves length/R2 and output/R3
as distinct acknowledgement and data words at caller SP-48 and SP-44.
The bridge preserves those words and the native R2–R12 restoration. Two
private words below the native frame retain command/register for the C
kernel. The public four-argument API is unchanged.

REA agrees with the raw instructions. The parser retains bit-six command
validation, truncated header arithmetic, header parity, signed length
comparison, MSB-first byte accumulation, partial-byte stores on read failure,
inter-byte parity drive and success/failure idle/release ordering. ACK and
data calls receive their distinct native pointers. Failed/non-writing
modeled reads keep the existing saved-word seeds rather than zero defaults.

Output uses a volatile byte view. After storing a complete byte, native
reloads that byte before inter-byte parity. A controlled post-store mutation
changes the stored byte from zero to one: stock computes parity from one,
while the old compiled C code uses its cached zero. The repaired C matches
stock. This is a reconstruction regression, not an observed field failure.

The probe passes 1,584 stock/C comparisons. Actual parity code executes;
idle, drive/write-bit operations, lower readers and line release are
modeled. Cases cover command/register boundaries, zero/small/negative-signed
lengths, rejected/partial/non-writing ACKs, data-read failure positions,
full-width bit/status words, live scratch mutations and post-store buffer
changes. No giant positive-length completion claim is made.

Checks compare R0/R2/R3, restored R4–R12, exact reader pointers, helper
order and arguments, output/guards, SP and interrupt masks. Callback
alignment is checked. Native modeled boundaries run at caller SP-48;
C uses SP-88 while retaining the two native scratch addresses. Old replay
also shows one shared reader pointer and clobbered R2/R3, versus the native
two-word frame. The write-frame function retains exact compiled bytes and
relocation identities.

All 562 R1 units compile without failures or duplicate strong symbols;
the other 561 source units are unchanged. Eligibility and imports remain
211 application / 34 bootloader, and `make sources-check` passes. Exact
bindings are in [the machine-readable review](stacmd-c-read-frame-review.json).

The C kernel is 186 bytes plus its eighteen-byte bridge versus 184 native
instruction bytes. Physical GPIO/wire/timing, general concurrency, private
frames, arbitrary faults, exceptions, final boot/linking, qualification and
whole-image byte identity remain unproven. The write path remains a
separate review. No G2 gate or source-plan selection changes.

The subsequent [direct C read-frame review](stacmd-read-c-review.md) supersedes this bridge and private worker while retaining the separate ACK/data words, R12 restoration and live-byte reload, and requiring native provider depth.
