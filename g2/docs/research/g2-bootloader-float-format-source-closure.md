# G2 bootloader float and formatter source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Authenticated boundary

The stock fixed-point converter is `[0x00415AB6,0x00415BF6)` / 320 bytes,
SHA-256
`d3c06c2907e1a0e8b3890aae57449889724a45e0a45bb167c8947d8de11743d6`,
with sole direct caller `0x00415F5E`. The formatter core is
`[0x00415BF6,0x00415FAE)` / 952 bytes, SHA-256
`43f3f8c080c595922a87cf7657943dcea958b983e5f3a78a244d513f42b232bb`,
with sole direct caller `0x00415FC6`. Complete-image Thumb scans find no
other direct caller or interior entry.

## Recovered behavior

`runtime_float_to_fixed.c` decodes binary32 sign, exponent, and mantissa,
rejects capacity below four, emits `0.0` for either signed zero, reports the
stock underflow/overflow errors, bounds precision by the 20-byte caller
buffer, and preserves decimal carry rounding. It uses the hard-float AAPCS-VFP
entry ABI and calls only the source-owned unsigned decimal writer.

`runtime_format_core.c` binds the already reviewed clean-room IAR logging core
shared with Apollo main to bootloader helper symbols. The binding fixes the
bootloader CRLF byte at `0x200271C4` and the source float converter. It
preserves the raw argument cursor, eight-byte alignment for `ll` and double,
all supported conversions and width/precision rules, nullable output sizing,
fallback strings `0.0`, `#.#`, and `?.?`, and the stock rule that `%f` consumes
no argument when the destination is null.

## Production integration

Apple clang emits 320 bytes at `0x00434A78` and 968 bytes at `0x00434BB8`.
The first leaf has one strict relocation; the second has 15 strict calls only
to the ten preceding source-owned numeric/format leaves. Generated non-linking
Thumb redirects replace both complete stock bodies and NOP-fill every
remaining stock byte. The independent Homebrew clang profile emits a
separately pinned 960-byte formatter leaf with the same relocation graph.

The fail-closed analyzer and tests authenticate source and transitive shared
source identities, stock hashes, callers, literal addresses, compiler
profiles, raw/final leaf bytes, relocations, patch bytes, provider accounting,
package hashes, and flash plans. Host oracles exercise normal, boundary,
fallback, and null-output behavior. No hardware operation occurs.

## Validation boundary

Software closure is complete for these two bodies, not for the whole
bootloader. Live boot, logging, CRLF, variadic-cursor, and floating-point
evidence requires an authorized responsive G2 right temple. That physical
evidence is unavailable, so hardware validation is explicitly blocked; no
signing, transmission, flashing, erase, or reset was performed.
