# R1 bootloader C SHA-256 backend

The normal bootloader profile now selects the pinned SDK's `nrf_sw` hash backend
and `components/libraries/sha256/sha256.c`, replacing the CC310_BL hash backend
unit. The SDK explicitly describes this C backend as legacy hashing for
bootloader use. It implements the same SHA-256 digest through the existing
`nrf_crypto_hash_*` frontend. No private CC310 context adapter or implementation
is supplied. This is a software backend change, not stock instruction identity.

The profile disables only CC310_BL SHA-256 and enables NRF_SW SHA-256. CC310_BL
ECC, ECDSA, initialization and signed-update policy remain enabled. The application
profile is unchanged. The SHA implementation and backend remain in their pinned
SDK locations with their existing notices; the manifest records both units.

## Verification

`build/sources-goal-r1-boot-sha256-c/report.json` records 778/778 compiled units:
696 application and 82 bootloader, zero failures and duplicate strong symbols.
All 696 application object hashes match the previous report. Bootloader imports
fall from 27 to 24, removing exactly the three `nrf_cc310_bl_hash_sha256_*` calls.

`build/goal-r1-boot-sha256-c/verify.py` links the actual compiled frontend, backend
and C SHA-256 with the participating runtime objects and executes them in Thumb
emulation. Across 154 streaming cases and 27,100 calls, digests match Python
hashlib. Cases cover empty input, abc, SHA padding/block boundaries, random
inputs up to 8192 bytes, and seven chunk sizes. It also checks zero-length
updates, short output rejection without writes, output length and sentinels,
invalid context/null argument errors, stack restoration, preserved core
registers and interrupt masks. It does not exercise an invalid NULL digest-size
pointer, which the SDK frontend does not validate.

`defects.py` compiles two changed implementations: a wrong SHA round constant
and little-endian digest output. Both fail the digest oracle. A clean sequential
rerun then passes. No stock crypto binary is needed for these algorithm checks.

The strict GNU link using the recovered boot layout now leaves exactly two
undefined code dependencies: `nrf_cc310_bl_init` and
`nrf_cc310_bl_ecdsa_verify_secp256r1`. It fails and produces no firmware ELF;
no verification bypass or dummy provider was added. The 22 memory/table symbols
continue to resolve through the layout.

R1 manifest validation passes (778 units, 575 reconstructed source files, zero
excluded units). Global `make sources-check` still fails on the pre-existing
unlisted G2 `resident_rom_thumb_set.S`; that work was preserved.

## Remaining limits

This proves software hash results and source composition, not physical DFU or
complete firmware. Software SHA has different timing, RAM and power behavior
from CC310; target measurements remain required. ECDSA and initialization must
be implemented or routed through a validated C backend before a full link can
succeed. The recovered LFRC settings remain required on R1 hardware. No flash,
settings write, source qualification, paid compiler or byte identity claim is
part of this change.
