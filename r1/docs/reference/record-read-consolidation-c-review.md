# One canonical cached health-settings getter

`runtime/native_record_read.c` now forwards its four-word void entry to the
existing r1_kv_health_get in native_health_profile.c. It no longer repeats
the read/copy algorithm. The wrapper explicitly discards the canonical
getter's incidental two-word return; existing consumers of that typed return
retain their interface. The canonical getter's output uses a packed,
may-alias word view, preserving unaligned destinations without a naturally
aligned uint32_t dereference. This source change produces an identical
canonical profile object under the selected compiler/profile.

The earlier standalone getter duplicated an already-existing stock 0x735e0
implementation. This consolidation corrects that ownership issue without
another dated implementation or a new runtime state owner. The normal wrapper
object references only r1_kv_health_get. One canonical function owns cached
reads, fallback preservation and the three ordered output stores.

All 1240 stock/C cases pass: the previous 520 modeled reads, 80 actual KV/
memcpy reads and 384 existing settings-callback cases, plus 128 direct canonical
return comparisons and 128 profile-feature consumer cases. Added comparisons
check both return words against stock and independently check the seven
binary32 feature values and validation result. Cases include null/unaligned
outputs, valid/invalid profiles, signed halfword features and zero sentinels,
all partial-read lengths, nonwriting/error reads, cached-size mismatch,
callback data mutations and explicit fallback words. Warm FP with default
FPSCR is used; saved core/VFP registers, SP and interrupt masks are checked.
Source execution is prohibited from entering stock instructions.

Five compiled defects are detected: wrong wrapper fallback argument, zeroed
canonical fallback, short read, wrong final output word and corrupted upper
return. A clean final baseline runs afterward. Fresh REA getter/profile bytes
match the locked image. The companion JSON records their receipts and the
probe/build audit.

The cached KV and memcpy bodies execute in integrated cases. Critical-section
callbacks are modeled. The settings callback's logging mode is zero and its
later update boundary is modeled. Private frames/aliases, incidental void-
entry register outputs, faults, concurrency, physical persistence and first-
use FP behavior are outside the proof. Unaligned feature-output observations
apply to the selected ARM build; no cross-architecture portability is claimed.

All 799 R1 units compile without failures or duplicate strong symbols; imports
remain 97 application and 22 bootloader linker metadata. Strict source
bootloader linking succeeds. The canonical profile object's hash is unchanged,
as are 796 prior object hashes in total. Only the void-wrapper object and the
two generated bootloader metadata hashes differ; generated bootloader allocated
bytes and relocations remain identical. Global source checking retains the
unrelated unlisted G2 resident_rom_thumb_set.S failure. Full application linking
remains unfinished. No source-plan qualification is added.
