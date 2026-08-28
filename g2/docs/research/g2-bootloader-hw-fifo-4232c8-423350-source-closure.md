# G2 bootloader per-instance FIFO source closure

Three authenticated bodies at `[0x004232C8,0x00423350)` now compile exactly
from maintained MIT C under both reviewed Cortex-M55 profiles. The
70-byte read, 52-byte write and 14-byte drain bodies have SHA-256 values
`7b349febf39ea04555da281af9f701f56cc26ed342d170a42e8e57db46798792`,
`06f979293ecda1e5d879a567c915acfbcb6fcf74cbc3d29660b53343a508a7ab`
and `f070519f752fc88363405ec74084da9733180bb83f63db34d3ae7945719bd9af`.
The first two bodies are relocation-free. The drain's unrelocated SHA-256 is
`65ca62db644548ffece82ad775314f8110e0e4646f560dc3d95c569ce4e98a89`
and its strict call binds the source-owned read service.

The read service polls register offset `0x18` bit 4, reads data from bank offset
zero, rejects data words with any `0xF00` error bit as `0x08000000`, optionally
stores low bytes, and reports the completed count. The write service polls bit
5, writes low bytes to bank offset zero, and reports the completed count. Both
use the four-bank `0x40039000`/`0x1000` layout. The drain wrapper invokes read
with a null destination, capacity 32, and no count output.

Five focused tests pin all bodies, the bank literal and successor; cover
available/empty/error reads, null-output draining, full/partial writes, counts,
bank selection and both reviewed target compilers.

Canonical provider accounting becomes 22,463 source-owned, 16,528 generated
patch, 16 alignment, and 124,833 retained official bytes, including 362 cave
bytes and 6,876 exact in-place bytes across 273 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,630,216-byte flash plan has SHA-256
`e72497682bb30fa59d7389f82853b14aafe094568da5aa816ea50e060824f7ae`
with 6,652 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The earliest retained executable body remains
the 570-byte initializer at `0x0042308E`; the next body after this FIFO cluster
begins at `0x00423350`. Live FIFO flags/data, MMIO ordering, error behavior,
concurrency and peripheral qualification are explicitly blocked by unavailable
authorized responsive G2 evidence; firmware-wide functional completeness is
not claimed.
