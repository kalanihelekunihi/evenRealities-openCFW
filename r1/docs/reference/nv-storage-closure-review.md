# Cached NV storage and health setter closure

Normal composition now includes `runtime/native_nv_table_config.c` as the
single C owner of the `ble_mult`, `health`, `hsync` and `r_size` cached
classes and their four symbolic handles. The stock decompressor executes
in the initialization probe. Its guarded 6,492-byte output matches the
known initialized-data hash; all 228 class bytes match the compiled objects,
including health defaults and header flags. Each four-byte handle has one
`R_ARM_ABS32` relocation to its corresponding class. The linked probe
matches all 244 cold bytes. Header/payload offset assertions were added.

The three active health/settings/ring-size handle imports resolve with no
additions, reducing application imports from 214 to 211. The BLE class is
also source-owned; this does not establish a new BLE consumer or complete
NV persistence. The eight data objects are writable, non-executable and
four-byte aligned.

Integration uncovered an existing relocation-sensitive fault in the
assembly settings setter at native `0x73604`. Its input section permits
two-byte alignment, but the inline literal is positioned using fixed
padding that assumes a four-byte function address. A controlled old-source
replay reaches the cached reader at `0x1008000`; at `0x1008002`, the literal
load reads two bytes beyond its label, yields `0x2000`, and faults before
the cached reader. This is a reproduced source-placement defect.

The setter logic is now C. A ten-byte bridge retains the native 24-byte
saved frame and restores R1/R2/R3 from its first three words. Null input
remains a no-op. The body ignores the initial cached-read status, performs
three ordered word load/store pairs, reloads the live handle and writes
the twelve-byte record. The source unit now uses the existing C profile
with unaligned word access enabled. Its other function,
`r1_record12_apply`, retains exact section bytes and relocation identities.

REA agrees with the raw setter instructions. A linker script explicitly
places the C bridge at both `0x1008000` and `0x1008002`, and the probe checks
the linked symbol address. Each placement passes 2,915 stock/C comparisons,
for 5,830 total. Actual cached reader/writer, health read/write wrappers,
settings setter and pinned musl copy execute; only port critical callbacks
are modeled. Cases cover all four classes, size rejection, dirty flags,
unaligned buffers, null inputs, settings input aliases within the saved
frame, payload/input changes and live handle/port replacement. API/copy
arguments, callbacks, class/buffer bytes, saved-word restoration, R0,
callee-saved registers, SP, masks and callback alignment are checked.

All 562 R1 units compile without failures or duplicate strong symbols;
455 application objects participate. Bootloader imports remain 34. The
other 560 source units are unchanged and `make sources-check` passes.
Exact bindings and the old placement failure are recorded in
[the machine-readable review](nv-storage-closure-review.json).

The C setter body is 54 bytes plus its ten-byte bridge versus 42 native
instruction bytes. Final layout/boot integration, whole-arena ownership,
flash persistence, physical health/recovery behavior, complete private
frame/fault/timing identity, final firmware linking, qualification and
whole-image byte identity remain unproven. No G2 gate or source-plan
selection changes.
