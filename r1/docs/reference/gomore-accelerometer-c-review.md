# R1 GoMore accelerometer cache and Goodix callback registration in C

`native_gomore_accelerometer.c` supplies the stream sample callback `0x6a5a4`,
cache reader `0x6a600`, open/close callbacks `0x6a61c`/`0x6a648` and Goodix callback
registration `0x4c3b8`. All five are ordinary C with no new assembly or executable
blobs. The [review receipt](gomore-accelerometer-c-review.json) binds production
source/object hashes, REA bytes/literals, replay artifacts, native initialization,
negative controls, qualification and normal composition.

The stream callback clamps the initial input count at offset 180 to 25, then
copies samples to the shared cache with arithmetic halving of each signed axis.
It preserves X-store/Y-read/Y-store/Z-read ordering, reloads the live count each
iteration, narrows the loop index to a byte and publishes the final low count
byte. It retains the native unchecked live-count behavior. The reader captures
that byte before writing the caller's count halfword, then moves exactly six
bytes per captured sample using the existing overlap-safe provider. The order
matters when count/output pointers alias cache state or samples.

Open registers `acc`/`gh` with the sample callback, rate 1 and flags 0 only when
the cached stream handle is zero. It publishes the returned handle after the
call. Close unregisters a live handle and clears the slot afterward, preserving
provider mutations. Registration installs open, close and read in the existing
Goodix callback table. The stream callback matches the existing three-argument
stream-dispatch contract; the read/stop callbacks match the existing void Goodix
helpers. These void callback contracts do not promise incidental native R0 values.
Only the registration root's return word is compared.

The new bounded state is a count byte at `0x20006e44`, handle word at
`0x20006e48`, and 150 sample bytes at `0x2001e334`: 155 owned bytes. Stock RW and ZI
handlers execute over poisoned memory with guards, and an independent RW decoder
agrees that all 155 bytes start at zero. Three padding bytes between count/handle
and two bytes after the sample cache remain unowned. Existing temperature state
and Goodix callback-table owners are reused. Final whole-image source-only RAM
placement remains unproven.

The fixture passes 472 paired stock/C cases, executing actual C movement and
Goodix registration/read/stop helpers. Cases include signed axis extremes, the
25-sample edge, controlled live-count changes during stores, source/destination
aliases, unaligned buffers, captured-count aliases, stream error words and
registration/unregister mutations. Sample writes are checked for halfword width
and exact order. Public memory and logical faults are compared; callee-saved
registers, SP, masks and FPSCR are checked. Callback pointers are normalized only
for the reconstructed functions. Caller-clobbered registers/APSR and private stack
residue are excluded. Seven compiled defects are rejected: wrong cap, unsigned
halving, preloaded axes, fresh copy count, wrong open gate, early close clearing
and wrong handler order. Stream register/unregister operations remain modeled;
controlled writes do not establish physical interrupt or concurrency safety.

All 636 units compile and both relocatable compositions succeed without duplicate
strong symbols. All 635 earlier objects remain identical. The handlers-register
startup import is resolved, reducing application imports from 173 to 172;
bootloader imports remain 34. Manifest checks pass. None of the five roots passes
instruction qualification. The source plan stays at 4,339 source-built bytes, and
a fresh hybrid matches the locked artifact with 641,821 executable pull-through
bytes and 248 resource bytes. Complete source-only linking and physical firmware
validation remain unfinished.
