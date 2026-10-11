# Touch reset descriptor and layout candidate

The official touch wrapper SHA-256 is
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`.
After its 32-byte wrapper, the image maps at `0x3300`. The vector gives
initial SP `0x20002000` and reset handler `0x4675`. The bounded reset slice
`0x4692..0x46d6` reads a copy descriptor at `0xb578` and a zero descriptor
at `0xb584`. Their original words are source `0xb58c`, target `0x200004c0`,
count 241 words; and target `0x200008a8`, count 428 words. The code then
calls `0x3464`, which is outside this candidate.

`reset_tables.c` source-defines the bounded descriptor loops.
`layout_fixture.ld` places synthetic input at the original load and RAM
addresses and asserts the descriptor, data, and BSS layout. This fixture
does not contain the original initialized bytes or an image reset entry.

`verify.py` compiled the source for Cortex-M0+ with warnings as errors,
linked the synthetic layout, and matched all 20 original descriptor bytes.
It compared the original reset slice against the source function under
Unicorn over the entire affected RAM window for 75 combinations: copy counts
0, 1, 2, 241, 400; zero counts 0, 1, 2, 428, 600; and three input seeds.
All 75 passed. `results.json` records hashes and the exact bounded domain.

The existing touch archive receipt reports 45/45 source C units compiled,
8 provider objects, and zero unresolved globals. This reset candidate is
separate from that archive.

The reset prefix at `0x4674..0x467e` calls a no-op at `0x4670`, then writes
`0xaced8865` to register `0x40030038` and masks interrupts. Its hardware
response is unknown. The suffix at `0x467e..0x4692` copies 192 vector bytes
from `0x3300` to `0x20000400`, writes the latter to VTOR, then performs the
authenticated copy/zero loops. `reset_prefix.c` and `reset_suffix.c` express
these bounded contracts. `verify_suffix.py` separately compared the original
prefix MMIO/PRIMASK effects and suffix RAM/VTOR effects to compiled source
over four initial patterns; all passed. The original reset handler retains
its stack frame at the comparison cut, so SP is not asserted equal to the
standalone prefix function. The call at `0x46d6` to runtime `0x3464` remains
outside this test.

The original copy payload has 964 bytes, 93 nonzero words, and SHA-256
`201d8c71916eb1169ef32e05464ea73b4dd535f018f97b84441919ba4091233d`.
Its words include 11 flash-range, 17 RAM-range, and 3 peripheral-range
addresses. Existing source owns the first 12-byte EEPROM configuration and
the 24 MHz delay initializers (9 source-owned bytes in the archive). Pinned
vendor `system_cat2.c` line 58 defines `SystemCoreClock` from its 24 MHz
default macro; the isolated data source defines that reset value. Later
clock updates remain unproved. The stock payload appears only as validation
input here; no opaque original byte range was inserted into source or a
linker fixture.

`init_word_inventory.json` classifies all 241 copied words by address,
value shape, and source status. Seven words contain **25 verified
source-owned bytes** in five disjoint islands: 12 EEPROM configuration,
4 delay32k, 1 MHz scale, 4 kHz scale, and 4 SystemCoreClock. The high three
bytes of the MHz word are not attributed by that one-byte source symbol.
Two further words are GNU CRT callback addresses with authenticated binary
attribution but no source-built object in this archive. The other 232 words,
including apparent zero padding, lack a source ownership/relocation proof.
Pointer-range shapes in the inventory are only heuristics.

`reset_owned_data.c` expresses the mutable EEPROM configuration and vendor
default clock. `owned_islands.ld` makes an isolated absolute link with five
separate load segments, each at its original RAM VMA and flash LMA. The
compiled section bytes match all 25 stock bytes. This is a partial layout
proof: the 939 other bytes of the copy payload are absent and the ELF has no
entry point or executable image claim. `inventory_owned_islands.py` rebuilds
and checks the sections and program headers.

`scan_archive_init.py` inspected every `.data` and `.rodata` section in every
member of the authenticated 45-unit archive, including their symbols and
relocations. Ten sections exist; two contain function-pointer relocations.
The only informative eight-byte match inside the 964-byte reset payload is
the existing 12-byte EEPROM configuration. The delay sections are shorter
and already validated as exact islands. A zero-filled pointer table can
coincidentally match stock zeros before relocation, so it is not a new
source-owned match. None of the source-defined mode, dither, pin-function, or
switch tables matches this initialized RAM payload. No `cycfg_capsense.c` or
`cycfg_capsense.h` generated configuration source is present in the retained
touch acquisition. Pinned public CapSense design examples are useful for
structure, but their values do not establish this product's table ownership.
`archive_init_section_scan.json` retains the section and relocation census.

The 45-unit archive, all three reset source objects, and the owned-data
object pass a whole-archive
**relocatable** link with zero undefined symbols. The GNU provider objects
emit enum-size and GNU-stack warnings, recorded by the link command; these do
not establish ABI safety or final placement. `archive_link_results.json`
records the archive/link hashes and source-data inventory. This is not an
absolute executable link: the fixture's synthetic `.touch_data` and BSS do
not include the real archive sections.

Remaining integration areas are (1) the 939-byte initialized-data ownership
and relocation map, chiefly product CapSense configuration; (2) the `0x3464`
startup composition; (3) full absolute linker map and executable link;
(4) whole-payload byte comparison; and (5) hardware validation. The first
area cannot be closed by the current archive's initialized sections and needs
the matching product generated configuration source or independent field-by-field
reconstruction. These are five distinct evidence areas, not five guaranteed
tasks or a defensible time estimate. No full touch image link or executable
has been claimed.

## Retained SDK/linker attribution audit

The retained Infineon `cy8cproto-040t/TOOLCHAIN_GCC_ARM/linker.ld` explicitly emits a three-word copy record (`__etext`, `__data_start__`, data word count) followed by a two-word zero record (`__bss_start__`, BSS word count). This is the same **descriptor grammar** observed at `0xb578` and `0xb584` in the locked touch image. The vendor script's defaults, however, place flash at `0x00000000` and RAM at `0x20000000`, while the observed image starts at `0x3300` and copies to `0x200004c0`; the retained file is a template, not the product's final linker map or proof of producing options. Its `config/design.cycapsense` identifies a `P4_MSCV3_LP` example design with a linear slider, but it is not attributable to this product's generated configuration. It cannot supply the missing initializer values.

A targeted retained-acquisition filename scan found that example `.cycapsense` and generic linker templates, but no product `cycfg_capsense.c`, `cycfg_capsense.h`, product `.cycapsense`, or final touch `.map`. The existing 45-object initialized-section census still owns exactly 25 of the 964 reset-copy bytes; 939 remain without independently explained source and absolute placement. The two CRT callback words have binary attribution only. No opaque stock bytes were copied into source, and no absolute executable link was attempted. The five integration areas above remain the finite estimate; the first requires an attributable product configuration or field-by-field reconstruction plus relocations before the third can close.
