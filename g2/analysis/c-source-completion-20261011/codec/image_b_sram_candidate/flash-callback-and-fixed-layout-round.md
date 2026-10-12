# Image-B initialized data, callback, and placement round

The selected image-B archive at `build-stage2-late-audio-source-round/receipt.json` has 301 C units, no callable imports, and 15 address/data imports. The strict stock-length linker experiment remains the earlier 294-unit snapshot (`build-strict-uart-record-placement-final-round/receipt.json`): `PASS_LAYOUT_ONLY`, 0x340 bytes before the fixed clock data. That headroom is insufficient for the subsequently recovered 21 audio callback bodies.

All initialized words at `0x100168c0..0x1001708c` have typed source ownership. The audio root/state at `0x10016c84..0x10016cb8` and `0x10016d0c..0x10016d60` retain authenticated fields; the 21-word audio callback table at `0x10016cb8..0x10016d0c` uses 20 C function relocations and one native zero slot. The 31-word flash callback table at `0x10016d80..0x10016dfc` uses 23 C function relocations and eight native zero slots. The six flash-profile name pointers use relocations to source strings. All non-pointer bytes of these records, including the 0x10016b84..0x10016c84 UART pair, have compiled/stock byte checks. The normal 300-byte initialized tail ends at `0x1001708c`.

An independent aligned-word scan of the entire 1996-byte initialized span found 93 pointer-shaped words: 62 into image-B IRAM (21 audio, 29 flash, 12 normal-tail), 29 into DRAM, and two MMIO base addresses. Their word addresses fall in the source-owned clock/UART, audio, flash, and normal-tail groups; this scan found no additional aligned function-table root in the span. See `initialized-pointer-roots-receipt.json`. It does not establish absence of computed, compressed, or unaligned pointers elsewhere.

The experimental late-audio linker script places 2536 bytes of source audio callback code at `0x1002d800`, beyond the source-reserved BSS end `0x2002d79c`. `build-late-audio-source-final-round/receipt.json` links 305 selected/experimental objects, fixes the initialized data addresses and vector/entry, and reports `PASS_LAYOUT_ONLY`, ELF SHA256 `f63e434e22a6305053dc9a06038b64c01584e78b62c71f52295c74c1570df50a`. This is not a stock-package-compatible or bootable proof: the stock stage-2 length is `0x1408c`, ending at `0x1001708c`, so the product loader would need an authenticated extended transfer/placement and the post-BSS code would need runtime stack/alias qualification. A single contiguous transfer through the late section would need a `0x2b1e8`-byte stage-2 payload and would cross the BSS/retained alias interval; zero padding could overwrite retained/noinit state. The stock stage-1 normal branch at corrected runtime `0x10000d4c` authenticates a fixed `0x1408c` copy; it does not load this island. A split or other authenticated loader mechanism is necessary (see `stock-loader-late-layout-receipt.json`). The late-section end leaves 7704 bytes below native stack top versus a 4892-byte compiled stack annotation, but runtime maximum is not established.

The 301-unit late-section archive passed three complete IMCRA original-byte QEMU fixtures with 89/89 observed words each (`imcra-full-build-stage2-late-audio-source-round-*-receipt.json`). The pure flash range mapper passed eleven stock/C cases (`flash-range-oracle-receipt.json`); the audio dB branch passed nine return/state cases (`audio-db-oracle-receipt.json`). Flash device effects, audio MMIO ordering, divide-zero and out-of-range hardware behavior, product loader/IRAM-DRAM alias, BSS interior field roles, unbounded FP domains, and whole runtime stack remain unqualified. `source_complete=false` and `bootable=false` remain correct.

The current 305-object final-layout snapshot has 540 bytes of space between
source `.rodata` and the fixed initialized clock records. The measured
`.late_audio` section is 2,536 bytes across 21 functions, leaving a 1,996-byte
deficit for stock-length co-placement (`late-audio-size-census-receipt.json`).
The largest functions are PCM configuration (678 bytes), DAC configuration
(328), hardware configuration (228), and the audio IRQ (214). These sizes
identify concrete optimization targets. The PCM and DAC configuration bodies
repeat ordered volatile register updates; merging them requires a caller and
MMIO trace proof because an ordinary helper call can change the ordering or
read count. No source body has been omitted or merged on size evidence alone.

The CRC source now computes the same reflected polynomial bitwise instead of
storing its 1,024-byte pinned table. This is a behavioral size variant, not
byte-identical native code or timing equivalence. The two exported CRC routines
matched pinned NationalChip source directly in 264 host cases spanning length,
alignment, and seed. A hash-coherent 301-unit CK804EF archive and 305-object
final-layout experiment pass (`crc-bitwise-size-round-receipt.json`): the
compiled CRC object falls from 1,210 to 62 bytes, the pre-data headroom grows
to 1,688 bytes, and the late-audio deficit falls to 848 bytes. The unchanged
stock loader still cannot deliver the late section. The CRC is called with
variable lengths during UART transmit and record registration; its increased
execution time needs deadline qualification.

The native 513-word sine lookup is exactly symmetric around quarter-wave
boundaries, except for its two explicitly retained zero-crossing residuals.
`generate_imcra_cosine_table.py` now proves all 513 stock words reconstruct
from 129 stored float words plus those residuals, and emits a source lookup
that retains the interpolation arithmetic order. The selected C-SKY object
contains 516 bytes of sine data; `verify_imcra_target_table.py` reconstructs
all 2,052 original bytes from that object and passes. Three full IMCRA
original/source QEMU fixtures remain 89/89 equal after this optimization.
The behavioral lookup adds integer branches and may have different timing or
exception behavior outside the measured domain.

With both source optimizations, the independent
`image_b_stock_length_source_fit_probe.ld` co-places all 21 recovered audio
callbacks in `.text` before the fixed initialized data. The final ELF has
301 selected plus four experimental objects, no `.late_audio` island, and a
576-byte gap between `.rodata` end `0x10016680` and fixed clock data at
`0x100168c0`. `stock-length-fit-receipt.json` verifies all loadable source
sections fall within the unchanged stock transfer
`0x10003000..0x1001708c`, with fixed data and reset addresses preserved.
This is a source placement result. Package integrity, stage-1 transfer/alias
behavior, retained RAM, hardware timing, physical MMIO effects, and full
firmware source coverage remain open; `source_complete=false` and
`bootable=false` remain the correct flags.

The first stock-length fit ELF had four source BSS symbols placed at the
beginning of BSS despite names that encoded later native addresses. The
current `build-stock-length-bss-slot-round` source/linker snapshot corrects
platform shadow, mode loop/index, and tokenizer cursor with exact BSS section
placement and linker assertions. It retains the 576-byte flash margin and
extracts an 82,060-byte source stage2 payload. Native system init skips the
BSS clear when `preserve_memory` returns nonzero, so retained RAM values remain
ambient. See `runtime-producer-audit.md` for the 15 named archive contracts.
