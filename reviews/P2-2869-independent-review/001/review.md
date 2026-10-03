# Independent review 2869

Status: **PASS_SCOPED** (`accepted: false`).

The candidate source hash matches the inventory image. Both claimed extents match their byte hashes, and the isolated static replay regenerated 144 Thumb instructions with exact byte tiling across `[0x4213D8, 0x4213E6)` and `[0x4213E6, 0x421548)`. The candidate artifact hashes also match its receipt.

I checked the relevant control flow and literal values against the decoded instructions. The helper at `0x4213D8` returns its input unchanged; the helper at `0x4213DA` adds `0x280` only when the unsigned input is at least `0x200`. The provider wrapper snapshots the control words before the null-destination test, selects the stated limits and gate bits, compares against the wrapped 32-bit `offset + count`, applies source-base adjustment, and calls `0x41D28A` with source/destination/count on the valid path. Error returns and the provider call's ignored return are consistent with the listing. The referenced literals resolve to the values stated in the pseudocode, including `0x421570` and the source bases.

This packet is a static body map. It does not establish provider implementation, physical reads, aliasing/fault behavior, or changing configuration behavior. No whole-image completeness or canonical admission is claimed.
