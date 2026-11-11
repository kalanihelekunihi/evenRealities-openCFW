# R1 optical history append in C

`native_gomore_optical_append.c` supplies the native ABI at stock `0x948d8`.
The [receipt](gomore-optical-append-c-review.json) binds the production object,
REA evidence, replay and source qualification. No inline assembly or persistent
RAM is added.

The function shifts 225 raw floating-point history words forward from index+25,
then appends 25 sign-negated samples, or positive zeros for any nonzero missing
word. It reloads the input descriptor for every sample, preserving aliases and
partial-fault behavior. Present data then invokes the native IIR filter on the
last 25 entries; the raw return is zero. The checked generic callback utility
keeps its guards and behavior under the `_checked` suffix.

The production object passes **1,280 native/C pairs**, including **192 fault
cases**, comparing exact writes, invalid access address/width, FPSCR, result,
filter arguments and 16-byte provider stack depth. Inputs include signed zero,
infinities, signaling/quiet NaNs, subnormals and descriptor/history aliases.
Seven compiled defect variants are rejected. A second **1,280-case** run links
the existing C filter; that run expands writes to bytes because the C filter
stores its ready word bytewise. Exact filter access width is outside that run.

The normal build compiles **690 units** with no failures or duplicate strong
symbols, retaining **179 application / 34 bootloader imports**. All 688 prior
units outside the renamed generic owner retain source and object hashes.
Qualification selects no new replacement. The canonical source plan and hybrid
composition remain unchanged: 4,369 source-built executable bytes, 641,791 stock
executable bytes and 248 resource bytes. Hybrid output equality does not prove
complete C reconstruction or source byte identity.

The optical estimator root remains unresolved. REA confirms its 1,196 instruction
bytes occupy two ranges, `0x69834..0x69c4f` and `0x69c8a..0x69d19`, spanning
1,254 bytes around a literal pool. A contiguous 1,196-byte read would omit its
tail. Its complete body and dependent pseudocode are preserved under the ignored
build experiment. No physical-device validation or complete source-only link is
claimed.
