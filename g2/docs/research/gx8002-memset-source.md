# GX8002 source memset and strategy reset

The stock entry is a byte-narrowing instruction followed by the exact pinned
NationalChip SDK fast-fill implementation. That object is used solely to
identify lineage and compare behavior. The emitted replacement is compiled
from C: align with byte stores, fill four words per iteration, fill remaining
words, then emit at most three tail bytes. Volatile stores preserve width and
order; an alias-capable word type avoids inappropriate C strict-aliasing
assumptions. The original destination is returned and no stack frame is used.

The native macOS compiler emits 102 bytes inside the original160-byte interval.
Decoded stock/source traces pass45,224 cases across fill-byte values,
alignments, normal lengths, negative signed block counts and address arithmetic.
Another32 cases check large-count boundaries and loop prefixes. Counts with
high bit set retain stock's signed comparisons, including the transition back
to positive after leading alignment stores decrement the count. Prefix checks
do not claim that arbitrary multi-gigabyte ranges are valid memory.

Eight regression tests check alignment, byte masks, word offsets, zero length,
return value and signed-count boundaries. Strategy reset/init additionally
execute through the decoded stock/source fills for their164-byte object,
checking all41 word stores and4/8-byte nested frame peaks in70 cases. Five
regression tests check clear extent/value, nested target and stack restoration.

The strategy state now has a real C definition and an ELF NOBITS allocation at
its recovered address. NOBITS is source-defined zero-initialized storage and contributes no payload
bytes to the ownership sum. Complete startup, decoder and hardware qualification
remain separate work.

Full integration passed327 tests. The rebuilt macOS package passed artifact
verification with the libc notice included.133 C functions are integrated;
codec ownership totals9,004 C bytes,120 assembly,2,456 source data,80 metadata,
394 fill and314,038 retained bytes. The full source-only goal remains active.
