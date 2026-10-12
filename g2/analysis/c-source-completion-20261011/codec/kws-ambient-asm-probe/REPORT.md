# Image-A KWS ambient frame and executable-link checkpoint

The native `0x10206cb0` prologue saves `r4-r9,r15`, subtracts 32 from SP, and copies the entire task frame at `0x10208c14`. Its own stores fill offsets 4, 8, 20, 24, and 28; offsets 0, 12, and 16 are inherited bytes of that stack frame. The selected source now forces the same target frame and uses named C-SKY loads to materialize those three existing words before the 32-byte copy. It defines no product values and calls no ambient-value helper.

`receipt.json` records a finite CK804EF QEMU fixture that seeded those caller-stack slots and observed all eight expected words at the copied task destination. The exact selected C source, not only an experimental copy, passed. This qualifies the bounded stack-copy behavior under the selected target compiler and fixture. It does not prove all caller stack histories or hardware behavior.

The coherent `codec-kws-native-frame-round` target build compiles 233 image-A source units and links SHA-256 `803a4c2122dadf2443537111047261f354deb7e78ed4ca5ad4e65140bcd6f97d` with zero undefined imports. Its separate image-B loaded stage captured 233 units. A conditional image-A source-root executable link resolves all relocations, but the first attempt put the reset symbol at `0x10023588`. Stock stage-1 jumps to `0x10023500`, so that ELF is **not an admissible boot layout**. The selected reset source has since been split into a named section for exact first placement; target compilation of that section passed, and a coherent full rebuild is pending.

The executable probe conditionally discards 25 selected sections with no source-root references. Native indirect/external roots, stage-2 XIP header emission and padding, stage-1 package assembly, physical SRAM/DRAM alias, runtime initialization, and hardware behavior remain gates for a complete image.

## Corrected source-only executable and stage-2 geometry

The next coherent `codec-reset-entry-layout-round` image-A candidate compiles 233
source inputs (linked object SHA-256
`55bf4a968f108d2abcafb526412686c56cc01e0e94b5b72fbd9ecea0388113f9`)
and has zero undefined symbols. The separate image-B stage compiles 242 inputs
(SHA-256 `fd98debc05bba630e52726cbe09caf43f64433bec2ab5f8a8ed16c65f7e27cde`)
with 13 genuine unresolved source/data imports. Both snapshots are coherent;
`source_complete` remains false.

`reset-entry-joint-layout/receipt.json` places 597 selected loaded source
sections under the conditional source-root GC rule. The relocatable joint
layout leaves 60 bytes in XIP, 104 bytes before the fixed clock records, and
674 bytes before the fixed SRAM tail. `reset-entry-executable-layout/receipt.json`
records a source-only EXEC ELF with entry **0x10023500**, no remaining ELF
relocations, exact vector/tail/XIP region bounds, and direct reset calls
resolved. Its ELF SHA-256 is
`e066ae2f2048e351fa8591c40a632f30e291beacab028cf7814187a6fa73d5e8`.
The linked XIP section ends at `0x1020be3c`, 76 bytes before the stock
stage-2 XIP extent. No named linker stub, PLT, or glue sections appear in the
map. This qualifies the selected linker’s branch/relocation reach under the
current script, not runtime behavior.

`stage2-packaging-geometry.json` validates the stock package BINH at
`0x958c`, stage-1 size `0x3000`, stage-2 payload length `0xc800`, and the
four-byte stage-2 XIP length word `0x8e84`. Its loader intervals match the
source ELF: XIP `[0x10203004,0x1020be88)` and SRAM
`[0x10023400,0x10026d7c)`. Exactly three source placement holes remain:
76 bytes at the XIP end, then 104 and 674 bytes in SRAM. The selected ELF
has no aligned 32-bit absolute word pointing into these holes. This is a
bounded check; computed or hardware-configured entries still require proof.

`build_stage2_source_payload.py` can assemble the 29 loaded named sections
into a 51,204-byte stage-2 analysis payload. It requires an explicit
`--gap-fill-byte` and has no default. The `0x00` analysis fixture validates
header/segment arithmetic and yields first SRAM vector word `0x10023500`;
its fill is **not authenticated product data**, and the output is not a
production firmware image. `external-root-scan.json` finds exactly one aligned
absolute code pointer outside A stage-2 in the stock container: the A stage-1
reset word. The B stage-1, B stage-2, and inter-image payload have none in
this bounded scan. Computed, encoded, unaligned, and external hardware roots
remain open, as do the 25 conditionally discarded pinned helper sections.

### Remaining image-A gates

- Resolve or formally exclude indirect/computed/hardware roots into the 25
  conditionally discarded source sections. The current aligned absolute-word
  scan and source relocation closure are bounded evidence only.
- Establish an authenticated fill and source-ownership policy for the three
  unassigned stage-2 intervals (854 bytes total), then qualify package-level
  BINH/checksum generation. The current `0x00` file is a structural fixture.
- Qualify physical SRAM/DRAM aliasing, reset/runtime initialization and
  selected C behavior on the actual target. The exact native stage-1 nominal
  copy and entry are proven, but a custom payload has not run on hardware.
- Complete the separate image-B loaded-stage source/data/layout and its 13
  current explicit imports before claiming the overall Codec image complete.

The independent `verify_stage2_source_payload.py` check compares all 29
emitted section byte ranges against the source ELF, checks the 0x8e84 header
and `0x10023500` first SRAM vector, and passes on the conditional 51,204-byte
fixture. It does not turn the unauthenticated gap policy into a product claim.
