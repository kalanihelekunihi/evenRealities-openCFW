# STACMD receive adapter native frame

`board/native_stacmd_receive.c` now uses a ten-byte frame bridge and C copy
kernel for native adapter `0x969ec`. Its saved incoming R3 word at caller
SP-16 is passed to the bit reader, copied to the output, and restored into
R3. The C kernel returns a private `uint64_t` pair carrying native R0/status
and R1/copied word; the public API remains `uint32_t`. The output store uses
a volatile packed word view to support the native unaligned store.

REA and raw instructions agree on the native adapter. A controlled old-
source replay shows its buffer at SP-12 and R3 left at `0xabc00003` after
the modeled reader clobbers registers. Native and repaired C instead use
SP-16 and restore the copied `0x12345678` word. The new kernel reads the
bridge's raw saved word rather than creating a separate uninitialized C
temporary or inventing a failed-read default.

The probe passes 1,536 stock/C comparisons. In 256 cases, actual bit-reader
code executes with modeled input/read-pin callbacks. Cases cover the
0/1/999/1000 polling boundaries on both sides, sample values 0/1/2/`0xffffffff`,
live pin/read-callback replacement and output alignment/alias choices.
Both implementations execute exactly 104 NOPs per actual-reader case.
The 1,280 modeled-reader cases cover arbitrary status words, seeded saved
words and absent/one/two/four-byte writes, including output aliased to the
saved word. These do not claim that stock's actual reader omits its store.

Checks compare R0/R1/R3, reader pointer, GPIO sequence/arguments, output
and configuration bytes, guards, callee-saved registers, SP and interrupt
masks; callbacks must be eight-byte aligned. The aggregate GPIO callback
depth is caller SP-48 in native and SP-56 in C. The existing reader's
compiled bytes and relocation identities are unchanged.

All 562 R1 units compile without failures or duplicate strong symbols;
the other 561 source units are unchanged. Eligibility and import sets
remain 211 application / 34 bootloader, and `make sources-check` passes.
Exact bindings are in [the machine-readable review](stacmd-c-receive-frame-review.json).

The C kernel is 18 bytes plus its ten-byte bridge versus sixteen native
adapter bytes. Private frames, arbitrary faults, exceptions, concurrency,
physical GPIO/wire behavior, sampling timing, final boot/linking,
qualification and whole-image byte identity remain unproven. Equal NOP
counts do not establish equal elapsed time. No G2 gate or source-plan
selection changes.

The subsequent [direct C adapter review](stacmd-adapter-c-review.md) supersedes this bridge and private worker while retaining the saved-word contract and strengthening reader-depth and overlap checks.
