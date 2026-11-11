# Bosch direct-read frame wrapper in C

The last inline assembly in `native_bma_reads.c` is replaced by a C wrapper.
REA reconfirms stock `0x87bbc`: 128 uninitialized scratch bytes at entry SP−152,
validation before callback dispatch, full-word status testing and live dummy-byte
reloads. The existing C read body and copy implementation are unchanged.

A 144-byte uninitialized C array reserves 128 callback bytes and 16 private
bytes. With the normal Clang profile its wrapper saves eight bytes and reserves
152, passing SP+8 as the fifth argument. The published callback buffer therefore
remains entry SP−152. The wrapper totals 160 bytes including its outgoing
argument area; callback depth remains −192 (stock −152), or −200 through the
product adapter (stock −160). Private saves differ from the former assembly
bridge and stock. Successful data comparisons are bounded to the native 128-byte
buffer; arbitrary stack inspection/corruption and excessive successful transfers
remain unverified.

The normal-build object passes 6,332 direct native/C pairs, 6,332 product-adapter
pairs and 1,791 read-control regression pairs. The actual null checker and copy
helper execute. Tests retain full-word register/status values, no-write callback
buffers, dummy reloads and context aliasing, observed context access order,
public buffer addresses, preserved registers and interrupt masks. A 128-byte
unreserved C array fails the callback-pointer assertion, establishing that the
frame check detects the tempting shorter replacement.

The fresh normal build compiles all 706 units without failures or duplicate
strong symbols. Imports remain 178 application / 34 bootloader. No physical bus
validation, complete source-only firmware link or new byte identity is claimed.
See the [machine receipt](bma-c-read-frame-review.json) for source/object hashes,
REA evidence, tests and limits. The earlier direct-read review records the
preceding bridge implementation; this review supersedes that wrapper only.

Qualification selects zero bytes for this wrapper. The fresh R1 hybrid remains
stock-identical with the unchanged canonical plan: 4,381 source-built executable
bytes, 641,779 stock executable bytes and 248 resource bytes.
