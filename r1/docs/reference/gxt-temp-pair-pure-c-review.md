# GXT310 paired temperature acquisition without register pinning

`runtime/native_gxt310_temperature_pair.c` now uses ordinary C output pointers
instead of fixed R4/R5 pointers, an unused captured R6 and empty assembly
constraints around each provider. It acquires the bus, enables the pair,
delays 80 ticks, stores channel 0 then channel 2 as raw halfwords, disables
the pair and releases the bus. Provider error statuses do not alter this
sequence. The public API returns void.

The normal compiled source object, previous object and locked stock entry
0x51260 match across 64512 cases (193536 executions). Tests execute the normal
compiled channel wrappers, passing addresses 0x90 and 0x94 to the final
modeled temperature provider. Twelve output layouts cover identical pointers,
one-byte overlap in both directions, adjacent and separated halfwords, and
unaligned addresses. Tests also cover boundary/raw high-bit values, seeded
random values, callback mutations before and after stores, error statuses
and interrupt masks. Halfword stores are ordered, guarded and narrowed to the
same low 16 bits. Callback order, relevant arguments and visible output state,
final output/guards, saved registers, SP and interrupt masks match.

The typed C contract excludes incidental final R0 from the void API,
callback-visible live register allocation and private frames. Bus, enable,
delay, final temperature-read and disable/release providers are modeled.
Physical sensor temperature, calibration, electrical response, elapsed delay
timing, faults and arbitrary private-stack aliases/concurrency are unverified.

Four independently compiled defects are detected: wrong first channel, wrong
delay, wrong second output pointer and omitted bus release. A clean baseline
is rerun after those defects. The companion JSON records fresh REA byte
matches, test/input hashes and the composition audit. No source-plan
qualification or byte-identity claim is added.

All 785 R1 units compile without failures or duplicate strong symbols; the
107 application and 22 bootloader linker-metadata imports are unchanged.
Strict source bootloader linking succeeds. All 782 unrelated nongenerated
objects retain identical hashes. The two generated bootloader objects retain
identical allocated bytes and relocations despite metadata changes. The global
source check still fails on the unrelated unlisted G2
resident_rom_thumb_set.S. Full application linking remains unfinished.
