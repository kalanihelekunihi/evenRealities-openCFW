# Unsigned division provider and original behavior

The authenticated GNU14.2.1 Cortex-M0+ `libgcc.a` members `_udivsi3.o` and
`_dvmd_tls.o` link exactly to all280stock bytes: division `[0xA6C0,0xA7D4)`
276bytes, and the actual weak divide-zero helper plus alignment
`[0xA9A8,0xA9AC)`4bytes. The only executable relocation is the original BL
at `0xA7C4` to `0xA9A8`, independently decoded before linkage. No stub or manual
byte patch is supplied. `results.json` pins archive/member/ELF hashes.

This removes the unknown binary-provider identity at the clock call target.
It is an authenticated runtime-library **binary comparator**, not a source
rebuild: source text, producing revision and runtime exception licensing still
need their own authenticated evidence. No bytes increment the54entryPDLcensus.

Historical UIDIVMOD extent correction: the real wrapper is
`[0xA7CC,0xA7D4)`8bytes, followed by the signed divider. The old16byterow
overlaps that following body. UIDIV is266instructionbytes, followed by two
alignment bytes; the archive's symbol size independently confirms this.
Original symbol rows are untouched.

Original-instruction execution passes98synthetic register/stack cases across
both entrypoints. For84nonzero-divisor cases, unsigned quotient agrees with
integer division; UIDIVMOD additionally returns the remainder in r1. Fourteen
zero-divisor cases execute the genuine stock hook and return quotient0.
UIDIVMOD leaves the original dividend as remainder when divisor0. These are
observed firmware/library semantics, not defined C division-by-zero semantics.
No provider return or exception behavior was stubbed. All cases are in
`original-results.json`; `test_original.py` reproduces them offline.

Readable interface:

```c
// EABI register contract; not a production replacement.
// __aeabi_uidiv: r0 = quotient, r1 has no normal-result contract here.
// __aeabi_uidivmod: r0 = quotient, r1 = remainder.
// Observed stock zero-divisor policy: quotient 0; uidivmod remainder dividend.
```

Source discovery next input: authenticate matching GCC ARM unsigned-division
and zero-hook assembly sources (typically the ARM libgcc assembly providers)
and the applicable GCC Runtime Library Exception against this exact toolchain
release/build. Archive equality alone cannot satisfy whole-source completeness.

C-SKY independently reviewed accessor/descriptor packets already contain
caller/ABI evidence and the additive BNEZAD correction. No justified new
execution/admission work is available locally: positive8..0 behavior is supported,
but exact target ISA/configuration applicability and coordinator-owned adoption
remain boundaries. No campaign records were edited or accepted counters advanced.
