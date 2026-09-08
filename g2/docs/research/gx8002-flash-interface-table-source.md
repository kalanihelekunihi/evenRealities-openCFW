# Source-authored flash dispatch table

The 120-byte table at package 0x18518 / runtime 0x20026504 now has a C definition
with 30 named fields, 23 reconstructed function references and seven explicit
null capabilities. Its compiled contents equal the shipped table. This is a
semantic dispatch definition, not an array of extracted pointer bytes.

Field order is checked against authenticated NationalChip lvp_kws commit
8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, include/driver/gx_flash.h, Git blob
71221ef72395e8b61642dd87291804aced433f58, with CONFIG_MTD_TESTS disabled.
The source uses a separately named internal struct. Each non-null field uses
GNU typeof of the recovered implementation declaration. The builder compiles
that header together with every referenced implementation with warnings as
errors, and checks all 30 target offsets plus the complete struct size.
The seven unused fields retain the identified upstream declarations.

The source contains no numeric function addresses. Linker bindings place the
named functions at their established entry addresses for this integration
stage. Every non-null function already has a separately qualified source
replacement. Stock bytes are read only by the verification path to compare
layout and contents. No executable or table bytes are copied into the object.

Both initializers now declare the same struct object and return its address,
replacing inconsistent byte-array declarations. The full initializer remains
428 bytes with compiled SHA d15c5553eaa56de14f59c48aa1b9dc5b35bddf50ad9b34b35ec760564a07428d;
its complete decoded qualification was rerun. The resume initializer remains
208 bytes and is still unadmitted because its frame exceeds the stock frame.
Both build reports now pin the shared interface header hash.

This is not yet a drop-in source implementation of GX_FLASH_DEV. The SDK exposes
four init arguments while the recovered initializer ignores them; SDK sync and
calcblockrange return void while the machine implementations return values;
several buffer, integer, enum and output qualifiers differ at the C type level.
These distinctions must be reconciled explicitly when rebuilding SDK callers
as C. Identical target pointer layout does not prove cross-translation-unit C
function type compatibility with that public API. Hardware behavior and the
remaining device records, profile BSS and complete firmware are unqualified.

Flash dispatch table integration completed on macOS; all 254 tests and final
package verification passed. There are now 17 source data regions and 151
total replacement regions, with 2160 source data bytes and 315346 retained
bytes. The 118 functions / 8180 C bytes remain unchanged. Codec and package
hashes are unchanged because the source-authored table exactly reproduces its
identified contents. No binary table payload is pulled into the linked object.
Whole-firmware source-only ownership and hardware qualification remain open.
