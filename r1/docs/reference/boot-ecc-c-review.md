# R1 bootloader portable-C ECDSA route

The exceptional-point failure documented below is corrected by the subsequent
[complete mixed-add verification change](boot-ecc-complete-c-review.md). This
review retains the earlier baseline evidence and its original limitations.

The normal bootloader profile now selects the pinned SDK's micro-ecc ECC/ECDSA
adapters with a source slice of upstream micro-ecc revision
`541b3a78026420a3e369c4c9281c396b5e531113`. File hashes, exact URLs and the BSD
license are retained under `third-party/upstream/micro-ecc-<revision>/`.
The SDK's own micro-ecc build script identifies this upstream project as its
provider; the older Cordio copy in this repository has a different API and was
not reused.

The profile selects P-256 only, 32-bit limbs, native little-endian coordinates
matching the SDK adapter, optimization level 2, and `uECC_PLATFORM=0` to select
portable C instead of ARM assembly. The four CC310_BL provider units are
replaced by two SDK micro-ecc adapter units and upstream uECC.c. The software
SHA-256 route remains enabled. No private-key generation or signing is used by
DFU verification; the SDK RNG callback remains its existing fail-closed branch
when no RNG backend is configured.

The CC310 initialization registration is removed with that backend. The existing
SDK `nrf_crypto_init` runs its now-empty backend registration range and sets its
normal initialized state. This does not supply a fabricated CC310 init function.
The signed-app update requirement, fixed recovered public key, LFRC settings and
DFU byte-order conversions remain unchanged.

## Build evidence

`build/sources-goal-r1-boot-ecc-c/report.json`: 777/777 units compile, 696
application plus 81 bootloader, with no duplicate strong symbols or failures.
All 696 application object hashes are unchanged from the software-hash build.
The bootloader relocatable object has 22 unresolved linker symbols and no
remaining crypto function imports.

The strict linker helper produces
`build/goal-r1-boot-ecc-c/strict/bootloader.elf` with no undefined symbols.
The recovered layout reports 0x5940 (22848) FLASH bytes including copied data,
leaving 1728 bytes in the existing 24 KiB region. The linker RAM/stack and flash
assertions pass. No region was enlarged, runtime archive implicitly linked,
stock executable crypto pulled through, or signature check bypassed.

## Crypto verification and known defect

`build/goal-r1-boot-ecc-c/verify.py` executes the actual final ELF's SDK crypto
initialization, public-key import and ECDSA frontend/backend in Thumb emulation.
Independent P-256 signatures are generated and checked by Python cryptography.
Tests cover four deterministic keys derived from SHA-256 seeds, both valid s representatives, changed hash and
signature, reversed r/s byte order, zero/out-of-range scalars, wrong valid key,
short signature and the product trust anchor rejecting foreign signatures.
Register/stack preservation and interrupt masks are checked at every call.
`verification.json` records 48 checks over 61 calls and the ELF hash.
`hash-final.py` additionally passes 21 one-shot SHA-256 cases against this same
final ELF through its actual `nrf_crypto_hash_calculate` entry; the previous
154 streaming cases remain separate frontend/backend probe evidence. Two compiled defect
controls (accepting invalid signatures and incorrect hash endianness) are detected,
followed by a passing baseline run.

A separate `generator-probe.py` **fails** a valid signature for private scalar 1
(public Q=G): the backend returns invalid signature. An earlier randomized run with small scalar keys also rejected a valid signature;
small-key edge behavior is not qualified. The source's G+Q precompute
uses a zero x-coordinate difference for this case. This is a confirmed upstream
edge-case limitation, not a passing test or qualified generic P-256 implementation.
The fixed product public key was checked as a valid P-256 point by cryptography;
its x differs from G.x, so the specific G/-G precompute degeneracy does not apply
to that trust anchor. A positive vendor-signed DFU package test is still required;
foreign-signature rejection alone does not prove that integration.

## Boundaries

This closes the source bootloader's final-link crypto dependencies, not the
whole firmware objective. The application still has 124 imports. Full C startup
conversion, the upstream ECDSA edge case, positive signed-package verification,
physical boot/DFU/flash/settings behavior, timing, stack high-water mark and
power remain outstanding. This is an SDK-derived bootloader with a recovered
layout and trust anchor, not a proved replacement for the physical stock image.
No device was flashed. The build requires no paid compiler or byte identity.
R1 source validation passes; global sources-check retains the unrelated known
G2 unlisted assembly-file failure.
