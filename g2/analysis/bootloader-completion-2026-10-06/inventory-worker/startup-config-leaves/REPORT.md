# Startup configuration leaves

Independent reconstructed C in `leaves.c`;265 original-instruction comparisons PASS in `comparison.json`. Separate module only, not integrated into verified checkpoint.

`0x422416` (26-byte body) returns6 for null configuration; otherwise copies20 bytes to `0x2000007c`, returns0. Literal is at0x422464, derived from the aligned Thumb PC-relative load at0x422422. Neighboring literal0x422468 points elsewhere and is not this destination. Aligned and unaligned input pointers and surrounding destination bytes compare. Original copy helper0x41568c is modeled as synchronous byte copy; helper internals, overlap behavior and atomic publication remain unverified.

`0x4222a0` (50-byte body) takes selector, first, second; truncates selector to8 bits;4/5/6 call0x4216d4/4217d2/421978 respectively with first/second and return their result. Other selectors return7. Tests cover0..259,ffffff04 andffffffff with distinctive child returns. Startup calls selectors4 and5 with zero arguments. Child bodies are explicit injected boundaries, not recovered HAL functionality.

Compile `leaves.c` freestanding Cortex-M33/Thumb/soft/O0, link with `module.ld` to `/tmp/opencfw-startup-leaves.elf`, and run `verify.py` using the existing analysis Python. Linker warns when creating Thumb veneers to synthetic child symbols; execution comparison confirms modeled calls. No stock executable fallback exists in the source machine. Provenance hashes and original instruction trace are recorded.

## Shared integration and real-copy probe

Shared candidate162b0683… passes all7 offline cases,265 direct leaves and affected logger/kernel/UART/startup suites;637 inputs/162 objects were unchanged at promotion.456 alignment mappings PASS;35 numeric aliases,42 segments,zero receipt source mismatches. Newer plain-formatter candidate8ba02bde… also passes265 direct leaf cases.

`native-copy-a9.json` preserves the unmodeled helper probe:264/265 comparisons agree; aligned source input20001000 copies all20 correct bytes but returns20000090 instead of0 under A9, while the unaligned input20001001 and null case agree. Original trace visits wrapper MOVS r0,#0 at42242c, so this discrepancy is not accepted as a recovered hardware return contract. The current direct shared proof continues to model the copy helper and records that boundary. No child HAL implementation or real hardware publication/drain is certified.

## Instrumentation cause isolated and native-copy supplement

The earlier aligned-copy failure is reproduced by a no-op SRAM memory-write hook; removal/scoping restores behavior in authenticated and independently assembled code. New MMIO-scoped native verifier passes271 wrapper cases across all8 source alignments; native descriptor-copy orchestration supplement passes64. These supersede the native-copy uncertainty for these bounded fixtures without deleting the old failed receipt or claiming hardware/general-copy closure. See `../copy-it-reproduction/REPORT.md`. Current verified shared checkpoint is e1049dc3…; three configuration children are now source defined with5,896 direct comparisons, while two frequency generators remain open.
