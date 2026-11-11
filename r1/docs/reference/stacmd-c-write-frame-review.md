# STACMD write-frame native ACK word

`board/native_stacmd_frames.c` now runs write framing in a C kernel behind
a fourteen-byte frame bridge. Native `0x28c6c` uses incoming R3's saved
word at caller SP-24 for the header and each data acknowledgement, then
restores the complete final word into R3. Four private input words below
the native frame supply the C kernel's command/register/length/payload
values. The public API is unchanged.

REA and raw instructions agree on validation, truncated header arithmetic,
initial idle/header/direction bit, acknowledgement/parity checks, signed
length comparison, data writes, final idle/release and failure cleanup.
The C kernel uses the native ACK word without a zero fallback. Payload is
read through a volatile byte view before transmission and freshly after
acknowledgement for parity. ACK is loaded after each actual parity call.

The probe passes 3,824 stock/C comparisons. Actual native/source parity
code executes; idle, write/drive bits, ACK reader and release are modeled.
Cases cover command/register boundaries, zero/small/negative-signed lengths,
ACK failure/mismatch positions, partial/non-writing ACKs, full-width status
returns, all 256 one-byte payload values, payload changes during ACK,
live ACK changes during parity and changed release configuration.
No enormous positive-length completion claim is made.

Checks compare R0/R3, exact ACK pointers, helper order/arguments, payload
and configuration bytes, guards, callee-saved registers, SP and masks.
Callbacks are eight-byte aligned. Native modeled boundary depth is caller
SP-24; C uses SP-64 while retaining ACK at SP-24. The old compiled provider
already used that scratch address, but left R3 at `0xabc00003`; native and
the repaired C restore the example's final ACK word `0x1`.

The existing read-frame kernel and bridge retain exact compiled bytes and
relocation identities. The other 561 source units are unchanged. All 562
R1 units compile without failures or duplicate strong symbols. Eligibility
and imports remain 211 application / 34 bootloader, and
`make sources-check` passes. Exact bindings are in
[the machine-readable review](stacmd-c-write-frame-review.json).

The C body is 152 bytes plus its fourteen-byte bridge versus 130 native
instruction bytes. Private frames, arbitrary faults, exceptions,
concurrency, physical GPIO/wire timing, final boot/linking, qualification
and whole-image byte identity remain unproven. Controlled mutations are
not evidence of observed field failures. No G2 gate or source-plan
selection changes.

The subsequent [direct C write-frame review](stacmd-write-c-review.md) supersedes this bridge and private worker while retaining the saved ACK-word contract and requiring native provider depth.
