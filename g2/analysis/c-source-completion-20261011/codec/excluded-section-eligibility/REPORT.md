# Codec A excluded-section eligibility checkpoint

The source-coherent combined Codec receipt is
`g2/build/c-firmware/20261011/codec-memcpy-alias-round/receipt.json`.
Its image-A candidate has 233 C inputs and SHA-256
`48d3a570fc11a976726c913803e7e2baab377b2297feadf4764beb0138363312`.
The separate image-B stage has 228 inputs and SHA-256
`ee7554b1e8273a82aa972892367562c46c4583a0d8d79ddbd8f8f680678afd5c`.
Both compile and link as candidates; neither is a complete firmware image.

`receipt.json` here classifies all 25 image-A sections outside the selected
source-root relocation closure: 17 pinned DSP library helpers, seven compiler
arithmetic helpers and one CRC wrapper, totaling 8,494 raw bytes. None is a
direct symbol bound to the 339 retained XIP native catalogue slots.
`selected-root-gc-memcpy-round/receipt.json` records a target linker GC run
against the **selected** candidate object: exactly those 25 sections are
discarded, all 311 directly native-bound XIP symbols survive, and the only
undefined image-A symbol is the authentic ambient KWS task-word input.
The selected initialized-data placement check passes 24 sections including
the 2,200-byte native SRAM tail.

This makes the 25 sections eligible for GC under the selected source roots.
It does not establish that no unmodelled stock function pointer, registration
record, or other stage entry calls a small excluded helper. In particular,
the stock native function-gap upper bounds exclude the intact large FFT
bodies from unnamed gaps, but cannot prove absence of every small indirect
entry. That native indirect-root audit remains the finite eligibility gate.

`native-gap-pointer-words.json` scans aligned address words in both loaded
image-A regions. It finds 13 XIP-to-XIP, 13 XIP-to-SRAM, zero SRAM-to-XIP, and
52 SRAM-to-SRAM pointer-shaped words into retained-catalogue range gaps.
The XIP cases include known AOUT/GPIO branch cases; the XIP-to-SRAM group is
the 13-way flash-info interior table. SRAM cases cluster in platform mode,
clock and IRQ continuation/table ranges. The receipt preserves every source
and target address for instruction-level consumer review. An aligned-word
scan alone cannot certify a function-pointer root or exclude encoded,
computed, other-stage or halfword references.

`classified-native-gap-words.json` binds all 78 aligned hits to nine native
consumer groups and their selected C enclosing bodies. Seventy-seven are
callback or interior dispatch addresses already represented as C function
references or switch cases. The remaining word at `0x10025ca8` is a literal
pointer used by `0x10025aee..0x10025af4` to copy 16 initialized bytes from
`0x10025cf4`; it is a data source, not an executable entry. The selected
start-mode-1 C branch had incorrectly reused the distinct `0x10025cd0`
low-power pair. It now references a typed `0x10025cf4` pair with exact words
`{16,0,0,1}`. `clock-mode1-correction/receipt.json` verifies both pairs,
32/32 bytes against stock, and isolated target `-Os`/`-O2` compilation
retains the prior 404/444-byte clock body sizes. Full native execution of the
corrected branch remains unqualified.

The source-only packed XIP capacity is 36,412 / 36,484 bytes, leaving 72
bytes before final linker alignment, veneers, literal pools, and exact
scatter. A corrected resident placement splits the 122 code sections around
the three fixed clock records at `0x10025cd0..0x10025d04`: 96 preceding
sections end at `0x10025c68`, then 26 following sections end at
`0x10026242`, leaving 674 bytes before the exact 2,200-byte initialized
tail. The earlier monolithic resident pack overlapped the internal clock
records and its claimed margin is superseded. These are capacity probes,
not final image placement.
Final XIP/SRAM section addresses, loader copy and BSS extents, `0x2002`
aliasing, ambient KWS words, and execution equality remain unresolved.
No final-layout executable ELF is admitted from this checkpoint.
