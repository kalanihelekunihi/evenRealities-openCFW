# GX8002 cache reconstruction and upstream boundary

Date: 2026-09-07. `make -C g2 gx8002-cache-source-check` builds and checks two
cache functions using the native macOS C-SKY toolchain. Both remain candidates
outside the production firmware provider.

## Data-cache enable: use upstream CSI

`runtime_gx8002_dcache_enable.c` delegates to `csi_dcache_enable()` in the
unmodified `core_ck804.h` from NationalChip SDK commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`.
The core and compiler intrinsic headers carry C-SKY's Apache-2.0 notice.
The SDK root license and all six transitive SDK headers are authenticated
against their Git blobs before compiling; the
[report](gx8002-csi-source-verification.json) records those hashes.
SDK include directories are compiler system includes; the local adapter
retains `-Wall -Wextra -Werror`. No SDK object is linked into the output.

The resulting 32-byte section exactly matches the original at three offsets:
12,772 (boot stage 2), 95,704 (image A SRAM), and 251,604 (image B SRAM).
It preserves two synchronization instructions, invalidation at `0xE000F004`,
cache enable value 21 at `0xE000F000`, then two more synchronization instructions.
There are no relocations or undefined symbols. Any code-hash difference fails
verification; this adapter does not accept an approximate match.

This pins one qualified upstream function, not the complete header API.
For example, unused `__USADA8` in this snapshot has unsigned absolute-value
warnings under modern GCC. It is not emitted by this adapter and has not been
admitted as a DSP implementation.

## Instruction-cache enable: separate hardware controller

The authenticated stock `gx_icache_enable` does **not** invoke generic
`csi_icache_enable()`. Stock uses a different controller at `0xB0000000`;
the generic CSI implementation uses `0xE000F000`. Name similarity would lead
to an incorrect substitution.

`runtime_gx8002_icache_enable.c` reconstructs the actual sequence: write zero
to controller word 0, read that word and write it OR 1, then repeatedly read
word 1 until its low two bits equal 2. The original unbounded polling behavior
is preserved; no timeout or failure policy is inferred.

The reconstructed target section is 28 bytes, with register-allocation
changes. The [report](gx8002-icache-source-verification.json) records its hash
and authenticated stock occurrences. Restricted target interpretation checks
140 controller-readback/status-sequence cases, including delayed readiness,
upper status bits, and continued polling. Tests also ensure unsupported
instructions fail and infinite branches exhaust the execution bound.

These checks validate the local instruction sequences. They do not qualify
startup, call boundaries, peripheral timing, interrupt behavior, or a complete
codec image. Both reports emit zero firmware bytes and leave production
ownership accounting unchanged. Native source compilation is now available;
source-only whole-image integration remains the next substantive boundary.

## Data-cache disable: same upstream algorithm, pinned as assembly (CD-004)

`gx_dcache_disable` is the mirror of `gx_dcache_enable`: clear
`CACHE->CER`'s `EN` bit, then write `CACHE_CIR_INV_ALL_Msk` to `CACHE->CIR`,
inside the same `__DSB()`/`__ISB()` barrier pair. The pinned upstream header's
`csi_dcache_disable()` implements exactly this, but this repository's C-SKY
toolchain lowers the single-bit `&= ~EN_Msk` to an `andni` instruction in a
different register than the stock object, which uses `bclri`. Editing the
vendored header to coax a different instruction choice is not an option, so
`runtime_gx8002_dcache_disable.c` pins the upstream algorithm as reviewed
inline assembly — every mnemonic, register and immediate is the disassembled
stock body — instead of C. `verify_gx8002_dcache_disable.py` compiles it and
requires the result to be byte-identical to the authenticated stock object at
every occurrence before returning a report; a diverging compile fails closed
the same way the enable/icache checks do.

The resulting 36-byte section exactly matches the stock object at three
package offsets: 12,804 (boot stage 2 IRAM, the span this closes part of for
work item CD-004), 95,736 (image A SRAM), and 251,636 (image B SRAM). There
are no relocations or undefined symbols. `make -C g2 gx8002-source-candidate`
now routes all three occurrences as `compiled_assembly`; see
`docs/research/gx8002-source-candidate-build.json` for current totals.
