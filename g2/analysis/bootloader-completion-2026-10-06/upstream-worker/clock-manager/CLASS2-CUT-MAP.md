# Clock class 2 provider cut map

This is a bounded source-recovery note for the stock class-2 request and
release pair in the locked G2 2.2.6.10 bootloader. It records observed calls
and state only; it does not substitute branches into the image for source.

## Image binding

The image is `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, mapped at
`0x00410000`.

| Routine | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| class-2 request | `0x421bd2..0x421cce` | 252 | `beaa4d231ad6eca158c9b2aac09a55b69258e213980ac1ce2cd704a33d1344f5` |
| class-2 release | `0x421cce..0x421d28` | 90 | `3dac14d8bed9201a8c8e9147d2216bb399ccb35b33642840d4ad49ad3a691c6e` |
| mode sampler | `0x41d676..0x41d68c` | 22 | `99d5d0ab5ea09e8dd0364a2598e84f2e5be0036f16363430412566d7374359f1` |
| mode apply | `0x41d3e4..0x41d43c` | 88 | `83045d8e1a536eac5c198d6779d9e4a542e3ac151100ce2d372f1d44122c2aa1` |
| callback cleanup | `0x421ba4..0x421bd2` | 46 | `7bce9267762f0c94865d13a566fd4c0476bf127b1f1781e659016de79124461b` |
| callback wait loop | `0x4216b2..0x4216d4` | 34 | `eb69fa2933ef30723f342fbc330927d681c6ca5d2ac077b77bf5e7ed1689a795` |

Hashes are recomputed from the bound image in the worker environment. Ghidra
raw listings are in `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/decomp/00421bd2.c`,
`00421cce.c`, `0041d676.c`, `0041d3e4.c`, `00421ba4.c`, and `004216b2.c`.

## Direct class-2 semantics

The request first checks the word at `0x20000080`; zero returns status 7. It
then checks/updates class row 2 in the shared per-user bitmap at
`0x20026e74 + 16`, using a low-byte user ID. A user already present follows
the active callback-timeout adoption path and returns zero after cleanup.

For a new user, the provider samples the current-mode value with the helper
at `0x41d676` (bit 8 of the word at `0x4002012c` takes precedence and yields
mode 2; otherwise bit 0 yields mode 1; otherwise mode 0). It also reads the
mode-select byte at `0x2000007c`. If the sampled mode conflicts with that byte,
it returns status 3. With mode 0, it invokes mode-apply 3 with a one-byte value
of 1 when the selector is 1, or mode-apply 2 with a null argument otherwise;
the active byte at `0x2002719b` is set only on the latter path and only when
not already set. If no conflict remains, it sets the class-2 user bit.

The callback state uses active byte `0x2002719b`, a pointer slot at
`0x20027040`, and a local timeout initialized to 150. An active callback
adopts the count through the slot. The request publishes its own local timeout
pointer, restores PRIMASK, then calls the shared callback cleanup routine.
That cleanup waits while both the timeout and active byte are nonzero, calling
`delay_us(10)` and decrementing the timeout; it then clears active state and
the pointer slot under a saved PRIMASK.

Release is idempotent for absent users. Otherwise it clears the user bit under
saved PRIMASK, scans for any remaining class-2 user, and on last release calls
mode-apply 4 with a local byte set to 1, then clears `0x2002719b` and
`0x20027040`. It restores PRIMASK and returns zero. The raw class request and
release ranges use direct `MRS PRIMASK`/`CPSID i` and saved-PRIMASK restore;
there are no privileged-mode or IRQ-enable helper calls in these ranges.

## Implemented helper boundary and validation

`clock_class_provider2.c` implements the request/release pair, mode sampler,
all selectors of mode apply, and callback finalizer/wait loop as C. The helper
uses the stock four-argument ABI: mode in R0, value pointer in R1, unused
argument in R2, and initial local result in R3. It returns the stock 64-bit
`CONCAT44(local_10, status)` in R0/R1. Selectors 0/1 update `0x40020120`;
2/3/4 update the radio config/mode registers; selector 5 calls the source
clock dispatcher for class 2/user `0x34`, writes the selector value, and sets
mode bit 7; selector 6 updates the config/mode and releases the same nested
user. Selectors above 6 return status 6 while preserving the R3 seed. The
class-2 request/release paths use selectors 2/3/4. Bitset/count and PRIMASK
operations are local source code; `delay_us` uses the source provider in
`clock_class_provider4.c`.

The standalone test compares original class-2 request/release instructions
and each direct mode-apply selector against compiled source. It covers the
two `0x40020120` writes, both value-dependent modes, nested selector-5 class-2
success/failure and accepted/rejected values, selector-6 release, and the
invalid-selector return seed. Class-5 tests include zero-timeout callback
completion and the masked clkgen configuration boundary. Class-6 tests include
each config-divider rejection branch and the silicon-revision-gated power
initialization branch. Incremental `make OUT=out/repro test` passes 128 cases
and reaches 4,588 distinct stock instruction bytes total; all 88 bytes of the
mode-apply range are now reached. The checked case details and source/image
hashes are in `out/repro/comparison.json`.

MMIO and SRAM are synthetic. The final cycle wait reaches ROM Thumb address
`0x41`, intercepted by the test. No physical peripheral or timing behavior
is claimed.
