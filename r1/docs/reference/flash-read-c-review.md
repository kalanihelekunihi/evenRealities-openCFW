# R1 FlashDB read adapter and status scanner in C

The later [outer-reader review](flash-tsl-c-review.md) supersedes the outer
assembly-body status below: control is now C and the native frame remains.
The following records the earlier adapter/scanner round.

Two assembly implementations in `runtime/native_flashdb_log_read.c` are replaced
by C. The outer `r1_fdb_native_read_tsl` assembly bridge remains because its
32-byte scratch view must preserve existing bytes after partial or failed reads.
Its instruction body is unchanged.

`r1_fdb_native_flash_read` at native `0x3f03e` reads the FILE_MODE byte at database
+25 and returns error 2 for any nonzero value, without reading the partition or
calling its read routine. Otherwise it reads the potentially unaligned partition
word at +8, forwards address, buffer and size unchanged, and maps a negative
signed partition result to error 2. Zero and positive results return zero.
A packed volatile word view retains the native unaligned access and read order.

`r1_fdb_native_get_status` at native `0x3f076` scans the first byte of descending
four-byte slots, stopping at zero. Its C offset calculation preserves the native
32-bit left-shift truncation before the logical right shift; replacing this with
an unrestricted slot stride changes corrupted/high-count behavior. Count one
performs no reads. High/zero counts are checked against native fault addresses
or early-zero behavior, without claiming an exhaustive huge-buffer scan.
REA/Ghidra confirms both local instruction bodies; the analysis ELF's text is
the locked application. These local observations do not establish corpus coverage.

The normal object passes 1,246 paired stock/C emulator cases: 480 adapter cases,
262 scanner cases and 504 through the actual outer bridge calling the C helpers.
They cover nonzero mode flags, signed results, unaligned views, poisoned status
padding, stopping positions, wrapping counts, and partial/non-writing partition
reads. Ordered shared/scratch accesses, memory guards, result, return SP, saved
registers and interrupt masks agree. Two negative controls (treating any nonzero
read result as failure and removing status-offset truncation) are rejected.

A further 1,728 paired cases execute the new adapter, actual selected C
`fal_partition_read` and actual C partition/cache lookup. They compare wrapping
bounds, missing devices, driver offsets/arguments, diagnostics, ordered shared
reads, output bytes and native return mapping. Only the final flash-driver read
and diagnostic printer are modeled. The table/cache is seeded; initialization,
electrical flash operation and concurrency remain unverified.

All 573 R1 units compile without failures or duplicate strong symbols. Application
imports remain 176 and bootloader imports remain 34. All unrelated object hashes
and the manifest are unchanged. Five official qualification profiles compile,
but select only the unchanged outer assembly bridge; neither new C function
qualifies. That wrapper-only candidate was not promoted. The source plan is
unchanged, and a fresh complete hybrid application equals the locked 646,408-byte
stock image. Stored-byte provenance remains 3,881 source-built bytes, 642,279
binary pull-through bytes and 248 resource bytes. This does not prove full
source completeness or executable-C coverage.

The checks exclude private stack below the retained scratch view,
caller-clobbered registers/flags, arbitrary memory aliasing, asynchronous events
and physical flash behavior. The retained bridge is a partial C conversion;
no G2 source or workflow gate changed. See
[flash-read-c-review.json](flash-read-c-review.json) for build paths and hashes.
