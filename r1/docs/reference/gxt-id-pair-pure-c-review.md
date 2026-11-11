# GXT310 paired chip-ID acquisition without register pinning

`runtime/native_gxt310_id_pair.c` now uses an ordinary C pointer instead of
binding the output to R4 and applying empty assembly constraints around every
provider. It still acquires the bus, enables both channels, delays 80 ticks,
publishes count 2, reads channel 0 then channel 2 into successive bytes,
disables the pair and releases the bus. Provider error statuses do not alter
the sequence. The public return type is void.

The implementation is compared against the previous compiled object and the
locked stock entry at 0x510d8. Tests execute normal compiled channel wrappers;
the final chip-ID reader, bus, enable/disable and delay providers are modeled.
All ID byte values, high raw result bits, output offsets, interrupt masks,
provider errors and callback output mutations are exercised. Comparisons check
ordered byte stores, callback order/arguments, state visible to callbacks,
final output/guards, saved registers, SP and interrupt masks. The void API does
not promise the incidental final R0 value. Callback-visible live register
allocation and private frame placement are also excluded.

The companion JSON records case counts, defect controls, fresh REA byte
matches, build/input hashes and object audits. Physical sensor identity,
electrical response, elapsed delay timing and concurrent or private-stack
aliases remain unverified. This change does not qualify new source-plan
regions, and compilation is not a full application link.

The suite passes 36,864 cases (110,592 executions) and four independently
compiled defects: wrong count, wrong delay, wrong first channel and omitted
release. A clean final-build baseline is rerun after the defects. The updated
C source produces an identical complete compiled object under the selected
profile; register constraints were redundant here. All 782 nongenerated prior
objects have identical hashes. The two generated bootloader objects differ
only in metadata, with identical allocated bytes and relocations.

R1 source checking passes at 784 units; builds have no failures or duplicate
strong symbols. Import sets remain 114 application and 22 bootloader linker
metadata. The strict final source bootloader link succeeds. The global source
check retains the unrelated unlisted G2 resident_rom_thumb_set.S failure.
