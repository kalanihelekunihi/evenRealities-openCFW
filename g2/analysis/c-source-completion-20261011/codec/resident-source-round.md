# Codec resident source round

The authenticated image-A SRAM body is
`g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin`, base `0x10023400`, SHA-256 `53860d6974097ad494c6697df52f95b796360131fab63cd8bfd7efc9c5596de8`.

Four new source units in `g2/components/gx8002/app_callback_candidate` reconstruct five resident functions:

| Unit | Resident addresses | Evidence |
| --- | --- | --- |
| `resident_irq.c` | `0x10025560`, `0x1002556c` | Compiled section bytes equal stock: `00c0206080c020703c78`, `00c020643c78`. |
| `resident_cache.c` | `0x10025664` | Native disassembly: align cache line, write eight lines for each 128-byte block, finish by 16-byte lines to `0xe000f004`. Static C flow only. |
| `resident_queue.c` | `0x100261b8` | Ghidra `LvpQueuePut` and native `DIVS`, wraparound byte write, queue tail update, success/failure branches. Static C flow only. |
| `resident_timestamp.c` | `0x1002585c`, `0x10025930` | Native 64-bit multiplication by 1000, right shift 10, divide by 1000; clock register words at `0xa0400044/48`. Static C flow only. |

All four units compiled with pinned C-SKY GCC 6.3 (`-mcpu=ck804ef -mhard-float -O2 -std=c11 -Wall -Wextra -Werror`). An initial relocatable link with the previous 41-provider app candidate succeeded at `g2/build/codec-resident-irq-apollo/combined-resident.o` (SHA-256 `9325d0104294f591cd7f8a23e6d74de6215c5920aa4011739d55853a8d30efd9`), but its linker defaulted to `ck810`, emitted an architecture warning, and silently pulled compiler runtime. This initial object is superseded by the integrated build below.

The integrated builder `g2/firmware_c/build.py --image codec --include-experimental` now includes all four units. Its fresh output in `g2/build/c-firmware/20261011/codec-resident-arch-sourcediv-round` passes compilation and relocatable link. `-Wl,-A,ck803` sets the link architecture to the input objects' `Tag_CSKY_ARCH_NAME=ck803`, retaining `Tag_CSKY_CPU_NAME=ck804ef`; the previous `ck810` target warning disappears. A source-owned bitwise unsigned 64/1000 division eliminates the opaque `__udivdi3` import. `nm -u` reports no undefined symbols in this candidate object. The bitwise quotient was checked against independent Python integer division on 10,007 deterministic vectors, including zero and 64-bit boundary ticks.

This is compilation and static reconstruction, not native runtime equality or whole firmware completion. No C-SKY emulator was available in the retained tools or PATH. Cache, queue, and timestamp still need native execution or bounded stock oracles; product initialization data, startup, final memory map, and complete image layout remain separate obligations. No executable resident bytes were reused as source.

A separate retained Ghidra census constrains whole-image scope. Image-A
SRAM has **151** seeded functions spanning **11,313** aggregate body
bytes (`0x10023500..0x10026d5c`); image-A XIP has **362** functions and
**28,962** body bytes (`0x10203004..0x1020be7e`); image-B SRAM has
**288** functions and **37,645** body bytes
(`0x10003128..0x10016b40`). Source: respective
`g2/research/corpus/codec/ghidra/open-2026-09-29/*/functions-000.jsonl`.
The five above source-owned resident functions cover only a small
identified portion of image-A SRAM. The three region counts are not
added to the UART stage-2 denominator; native code may share underlying
implementations across separately loaded images, and this inventory has
not yet been crosswalked to all C providers.

Two further image-A SRAM bodies have evidence-backed C candidates in
`resident_small.c`: `0x10024244` flash type reads the word through the
pointer stored at product SRAM `0x200264f0` (native literal at
`0x1002424c` resolves to `0x200264e4`, plus `0x0c`), and `0x10025e38`
clock subband writes the fourth argument through the third-argument
pointer and returns zero via the shared native tail at `0x10025dbe`.
Both compile for pinned `ck804ef` target. This raises the specifically
identified image-A SRAM candidate set from five to seven of 151 seeded
entries, subject to target link and runtime qualification.

A third small resident candidate, `0x100247d4`, invokes the optional
callback stored at descriptor byte offset `0x30`. Direct native
instructions load that word into r0 and execute `jsr r0` when nonzero;
C keeps the raw function pointer value. It compiles for `ck804ef`.

These three `resident_small.c` bodies make eight explicitly identified
image-A SRAM C candidates against its 151-entry seed inventory. Source
ownership does not imply target runtime equality or complete load layout.

A connected flash-discovery source unit adds four more image-A SRAM
bodies: `0x1002364c` wait for SPI bus ready (16 bytes),
`0x1002365c` wait for RX FIFO empty (20 bytes), `0x10023684`
three-byte JEDEC command read (86 bytes), and `0x10024190` flash
catalog discovery (168 bytes). Direct native literals identify MMIO
`0xa2000000`, SRAM state `0x200264e4`, 24-byte entries at product SRAM
`0x20026624`, and fallback JEDEC ID `0xc22016`. The C candidate never
supplies unknown catalog entries. It compiles for pinned `ck804ef` and
is included in the codec experimental builder; native hardware runtime
remains unqualified. This brings explicitly identified image-A SRAM C
candidates to **12/151** retained seed entries. The 151-entry count
includes labels as short as one byte that still need data/code
classification, so this ratio is a source attribution measure only.

A connected flash command/status unit, `resident_flash_commands.c`, adds eight
image-A SRAM address-owned C candidates: `0x10023670`, `0x100236dc`,
`0x10023734`, `0x1002374c`, `0x1002375c`, `0x10023770`, `0x100242b4`,
and `0x10024330`. It calls the already source-owned SPI bus and read lowers,
uses the retained `0xa2000000` MMIO block, and includes no fabricated flash
catalog data. The fresh codec experimental build
`g2/build/c-firmware/20261011/codec-resident-flash-command-round` passed
candidate compilation and relocatable link. This raises identified image-A SRAM
C candidates to **20/151** seed entries, subject to native execution checks.

The next source unit, `resident_flash_transfer.c`, reconstructs two larger
resident bodies: word program `0x10023788` (148 native bytes) and word read
`0x10023cac` (164 native bytes). The direct native C-SKY disassembly from the
authenticated image at base `0x10023400` supplied register-write order,
command/address writes, FIFO polls, and the read branch based on the JEDEC ID
field of the product-selected entry. The selected entry pointer remains the
native SRAM contract at `0x200264e4+0x0c`; no product ID values or catalog
entries were synthesized. The source preserves native whole-word transfer
semantics (`byte_count >> 2`) and uint32 underflow for a nonzero length below
four bytes. The read branch tests unsigned `(jedec + 0xffe3c7ee) < 2` and
writes the native `0x40003219`/`0x40004218` extra controller words. Target
compilation/link receipt: `g2/build/c-firmware/20261011/codec-resident-flash-transfer-round`.
The receipt passed compilation and relocatable link (26 primary source
inputs, link return code zero, output SHA-256
`6ad8eafe8c841d4d01def4f5fb78f3240cc612a186569098b0c8ce13b035e249`).
The static identified set is **22/151** image-A SRAM seed entries. Native
hardware equality remains untested.

The protection graph adds five more native image-A SRAM addresses in
`resident_flash_protect.c`: block bounds `0x100238a4` (66 bytes), protection
status `0x100238ec` (144 bytes), protection set `0x100239a4` (198 bytes), and
lock/unlock `0x10023a70`/`0x10023a80` (14/16 bytes). The native code reads a
selected flash descriptor from SRAM `0x200264e4+0x0c`; its protection map at
descriptor offset `0x10` contains an entry pointer/count and eight-byte entries
(status value/mask, status-2 value/mask, protected-byte count). This source
defines the typed layout and algorithms but supplies no entries. Direct native
C-SKY instructions were checked for type halfword at descriptor offset 6,
iteration bound, write-enable and status-readback order, block size `0x1000`,
and return values. `codec-resident-flash-protect-complete-round` passed
candidate compilation/link. The identified image-A SRAM set is **27/151**.

A further connected source file, `resident_flash_range.c`, adds stock
`0x10023a90` block range (38 bytes) and `0x10023ab8` sync (8 bytes), both
calling the earlier source-owned lowers. Direct native instructions confirm
the second block query uses `address + bytes - 1` and ignores its return. The
fresh build receipt `codec-resident-flash-range-round` passes candidate
compilation and relocatable link with 28 primary source inputs, output SHA-256
`30e8158043ffc21a7eee00dbdb8d3f001bfcf56d824ec9d21a7e367518f5d026`.
The identified image-A SRAM set is **29/151**.

This inventory remains a subset of three separately loaded native regions.
The retained Ghidra lists have 151 image-A SRAM entries (35 bodies of at least
100 bytes), 362 image-A XIP entries (85 bodies of at least 100 bytes), and 288
image-B SRAM entries (101 bodies of at least 100 bytes). These counts are
candidate attribution obligations, not disjoint proof of missing C bodies.
The largest image-B seed, `0x10015d34` (2,212 bytes), currently has a decompile
warning for bad instruction data and float-typed pointer aliases; it needs
native instruction/type recovery before admission as C. Resident MMIO
execution, product flash-table values, image-B application/DSP source, and
final startup/link layout remain open.

The next connected flash unit, `resident_flash_xip.c`, reconstructs stock
`0x100242ec` device configuration (66 native bytes) and `0x1002436c` XIP
controller initialization (206 bytes). Direct native C-SKY instructions
confirm the nine-argument register/stack ABI, width validation, mode/dummy
fields, continuous-read bits, and MMIO bases `0xa2000100` and `0xa0300080`.
The device configuration uses stock read command `0x15`, write command `0x11`,
and bit `0x10`, calling existing source-owned command and wait lowers. The
fresh integrated codec experimental receipt
`g2/build/c-firmware/20261011/codec-resident-flash-xip-round/receipt.json`
passes compilation and relocatable link with 29 primary source inputs; output
SHA-256 `c3f37b53cfc5d81ed194330f5762f1bd41327b7b61fb1abbf17a89f56536a74f`.
The identified image-A SRAM C candidate set is now **31/151** seed entries.
This is static source reconstruction and target compile, with MMIO execution
and product configuration still unqualified.

The flash root `0x100245f0` (182 native bytes) is now source-reduced in
`resident_flash_initialize.c`. Its native disassembly establishes the platform
calls, `0xa0300090` and `0xa2000000` controller writes, stock JEDEC ID paths,
callback descriptor words at `0x200264e4+0x18/+0x1c`, nine-argument XIP call,
and return pointer `0x20026504`. The callback stores clear the C-SKY
function-pointer tag bit because the stock descriptor holds even instruction
addresses; downstream dispatch restores the target call ABI. The initial
integrated receipt `codec-resident-flash-initialize-round` passed compilation
and relocatable link with exactly two honest unresolved platform lowers,
`gx8002_resident_platform_config_25d74` and
`gx8002_resident_platform_gate_25080`.

Direct native inspection then recovered config dispatch table `0x100249a4`
(ten entries), gate tables `0x100253cc` (18 entries) and `0x10025414`
(19 entries), and module lookup body `0x10024a44`. The C candidates
`resident_platform_config.c` and `resident_platform_gate.c` implement the
associated `0x10025d74`, `0x10024a44`, and `0x10025080` bodies. They read
the native 26-entry, 16-byte-per-entry product module table at SRAM
`0x200266e0` as a required input; no table contents are fabricated. The
module-9 config and module-13 gate paths used by the flash root are grounded
in direct disassembly. Other dispatch paths are syntactic C candidates pending
bounded stock execution checks. Fresh integrated receipt
`g2/build/c-firmware/20261011/codec-resident-platform-integrated-round/receipt.json`
passes target compilation and relocatable link for 32 primary source inputs,
with zero unresolved symbols and output SHA-256
`2309459988ef996374447360e511823e3cb820f032f5f1e75d95eb2d0a72beaf`.
The identified image-A SRAM C candidate set is **35/151** seed entries.
Zero relocatable imports applies only to this selected source graph; the
whole codec image remains incomplete across SRAM/XIP/application data and
runtime qualification.

The board call graph adds `resident_board_init.c`: native image-A SRAM
`0x10024940` PMU wakeup-source read (66 bytes) and `0x10025cbc` board
initializer (20 bytes), plus a separate image-A XIP lower `0x10203c74`
(14 bytes). Direct instructions confirm wake source precedence from
`0xa0000034` bits 0/2/3/1 and fallback `0xa001002c & 1`, the board's
`source >= 2` flash-init condition, and four analog update MMIO writes of
`0x59` at `0xa0005040..0xa000504c`. Fresh experimental receipt
`g2/build/c-firmware/20261011/codec-resident-board-init-round/receipt.json`
passes target compilation and relocatable link for 33 primary source inputs
with zero unresolved symbols, output SHA-256
`296541c71437894ab5b2c7876e94203bce15da6c3b5047066b12b1eb39b6cef2`.
The specifically identified image-A SRAM C candidate set is **37/151**;
the XIP lower is tracked separately against its 362-entry inventory.
Relocatable composition does not establish placement in the separately loaded
native SRAM and XIP stages or hardware equality.

The larger flash interface `0x1002443c` (346 native bytes) now has a full C
candidate in `resident_flash_interface.c`, with four connected native lowers
in `resident_flash_interface_support.c`: SPI IRQ handler `0x10023ac0`
(30 bytes), protection descriptor initializer `0x100246c4` (28 bytes), VIC
IRQ enable `0x100254ac` (22 bytes), and IRQ registration `0x1002553c`
(30 bytes). The IRQ handler performs conditional volatile status reads from
SPI offsets `0x38` and `0x3c`; it is not a fabricated no-op. The IRQ table is
native SRAM `0x20026ef4`, 32 slots of two words; VIC enable is `0xe000e100`.

Native literal pool `0x10024598..0x100245ef` has SHA-256
`4bb100f1877eb39506465ad1ddb9bc1c458fcc00d38f6fc93cd879770df04f95`.
It supplies the exact JEDEC ID branch constants, raw handler/program/read
addresses, SRAM state `0x200264e4`, and return pointer `0x20026504`. The
protection initializer literal pool `0x100246e0..0x100246ef` has SHA-256
`1a7cbd276a1435ab085673a375c968bfbf57cba2ca2a4a0dae7571e4ecba4886`.
Its pointers/counts establish three contiguous eight-byte-entry input ranges:
`0x2002657c..0x200265a4` (5 entries), `0x200265a4..0x200265dc`
(7 entries), and `0x200265dc..0x20026624` (9 entries), immediately before
the flash catalog. C initializes their descriptor words at `0x20026ff8` but
supplies no unknown entry bytes. The native IRQ callback and transfer function
pointers are stored as even instruction addresses, clearing the C-SKY ABI tag
from C function pointers.

The independent static native branch model in
`verify_flash_interface_dispatch.py` compares the ordered instruction
branches with the C JEDEC classes on 100,107 deterministic values including
all literal boundaries; `flash-interface-dispatch-receipt.json` reports zero
class mismatches. This checks branch classification, not MMIO side effects or
C-SKY runtime equality. Fresh integrated receipt
`g2/build/c-firmware/20261011/codec-resident-flash-interface-round/receipt.json`
passes target compilation and relocatable link for 35 primary source inputs,
zero unresolved symbols, output SHA-256
`097ecc44935f4c2c6599b73a223aac21271c1ccd0fd43599a441f0a6cd49eb74`.
The specifically identified image-A SRAM C candidate set is **42/151**;
image-A XIP remains separately censused at 362 seeds, and image-B SRAM at
288 seeds. Whole-source completion also requires recovered product entry bytes,
all remaining native bodies and initialized data, stage placement/link layout,
and runtime equality.

The next flash program/erase unit `resident_flash_program_erase.c` adds
four image-A SRAM native bodies: address-to-command `0x10023b8c` (78 bytes),
page program `0x10023c34` (114 bytes), erase `0x10023d58` (158 bytes), and
chip erase `0x10023e00` (14 bytes). Direct disassembly confirms the dynamic
program callback at SRAM state `0x200264e4+0x18`, 256-byte page split,
write-enable sequencing, 4-KiB versus 64-KiB erase command (`0x20`/`0xd8`),
and the command buffer at state offset `0x10`. The address-byte lower uses
stock modulo-32 C-SKY shift semantics for four output bytes; the erase command
consumes three bytes at buffer offset `+1`. The native erase loop uses a
minimum 4096-byte budget before each step; C preserves that behavior, even for
partial final blocks. No flash runtime execution was performed.

Fresh integrated receipt
`g2/build/c-firmware/20261011/codec-resident-flash-program-erase-round/receipt.json`
passes target compilation and relocatable link with 36 primary source inputs,
zero unresolved symbols and output SHA-256
`bc78a7455411c6c2eff5c1f37a72619cd450d2b36ee81c9789f52ce86360bac0`.
The specifically identified image-A SRAM C candidate set is **46/151**;
image-A XIP and image-B SRAM remain separately censused. Product flash
catalog/protection contents, full source body inventory, loaded-stage linker
map, and hardware/CPU execution equality still block whole Codec completion.

The following connected flash round adds seven image-A SRAM bodies in
`resident_flash_otp_config.c` and `resident_flash_uid.c`: OTP status,
region count/set/get/size, lock, and UID read at stock addresses
`0x10023ae0`, `0x10023b24`, `0x10023b38`, `0x10023b60`, `0x10023b78`,
`0x10024250`, and `0x10024104`. These use the selected catalog descriptor,
the native SPI register path, and existing real flash lowers. The specifically
identified image-A SRAM C candidate set is now **53/151**. Image-A XIP has
362 separately retained seed entries and image-B SRAM 288; the seven new
bodies do not alter either census.

Typed product source data now covers the three OTP protection entry arrays
(21 eight-byte records), six flash catalog records plus zero sentinel,
six exact XIP name strings, one OTP configuration object, the 26-entry
module table, and its 72-byte configuration object. Native source extents are
`0x1002657c..0x100268c8` in image-A SRAM and
`0x1020be54..0x1020be88` in XIP. A first comparison found one manually
transcribed module dependency byte at offset 182; it was corrected to the
authenticated native value. `verify_resident_product_data.py` and
`resident-product-data-receipt.json` now compare 744 nonpointer bytes across
13 target object sections with zero differences, and confirm 14 catalog and
20 module `R_CKCORE_ADDR32` relocations. The flash discovery, module lookup,
and protection initializer C consumers use these typed source symbols rather
than fixed product-data address literals. This is source and target-object
evidence; final SRAM copy/XIP placement and runtime equivalence remain open.

Fresh integrated candidate receipt
`g2/build/c-firmware/20261011/codec-resident-product-linked-round/receipt.json`
passes C-SKY target compilation of 41 primary source inputs and relocatable
link with zero unresolved or duplicate strong symbols. Output SHA-256 is
`b776eea8ae514ad71c6fc532c1fcd32e925d5621e00d383ccec06bd5720f3032`.
`source_complete` remains false: at least 98 identified image-A SRAM bodies,
the independent XIP and image-B inventories, final initialized-data/linker
ownership, and qualified native execution are still outstanding.

The next connected OTP graph adds four native image-A SRAM bodies:
`0x10023bd8` erase (78 bytes), `0x10023e14` SPI transmit (160 bytes),
`0x10023eb8` page-split write (224 bytes), and `0x10023fa4` chunked read
(338 bytes). Direct C-SKY instructions in the authenticated SRAM image
establish the SPI register sequence, mux writes at `0xa0300090`, command
buffer at `0x200264f4`, OTP descriptor fields, unsigned bounds test, and the
signed `min.s32` 32-byte read chunk. The read path's decompiler output left
`r8` uninitialized; direct instruction `0x1002400e` defines it from remaining
bytes and 32. The candidate C therefore follows the instruction-defined
chunk size. These functions call already source-owned flash lowers and use
the typed catalog/OTP data; hardware execution has not been qualified.

`g2/build/c-firmware/20261011/codec-resident-otp-read-integrated-round/receipt.json`
passes C-SKY compilation of 44 primary source inputs and relocatable link,
with no unresolved or duplicate strong symbols. Output SHA-256 is
`edaed2f1a1bfc43371bb07a8bb880a5c1bbac1291ff335ebc91016e56e7a4f06`.
The specifically identified image-A SRAM C candidate set is now **57/151**,
leaving 94 inventory entries to attribute or source. Image-A XIP (362 seeds)
and image-B SRAM (288 seeds) remain separate. The resident image's virtual
source and runtime literal addresses have matching low 20 bits (for example
`0x1002657c` and `0x2002657c`), but the loader/scatter-copy mechanism and
final C linker placement have not been proved.

The next native connected route adds `0x1002475c` flash probe (80 bytes)
and descriptor dispatch wrappers at `0x100247b8` (28 bytes), `0x100247e0`
(20 bytes), and `0x100247f4` (28 bytes). Probe invokes the authenticated
callback word at `0x20026504` while flag byte `0x20026ff4` is below two,
records a nonzero callback result, and retries until a 64-bit clock delta
exceeds `0x4c4b3f` microseconds. The 64-bit clock lower at `0x1002585c`
was already source-owned; this round gives it an external typed C symbol.
The three wrappers forward native register arguments through descriptor
function pointers at offsets `+4`, `+0x34`, and `+0x58`, returning `-1`
when the selected pointer is zero. Dynamic callbacks remain actual runtime
input, not invented handlers.

`g2/build/c-firmware/20261011/codec-resident-flash-probe-dispatch-round/receipt.json`
passes C-SKY compilation of 46 primary inputs and relocatable link with
zero unresolved or duplicate strong symbols. Output SHA-256 is
`5fa13c38bd5659d1519c8b8786237a55c56d16af4ab8c96c6b95d23d99bb923b`.
The identified image-A SRAM C candidate set is **61/151**, leaving 90 seed
entries to attribute/source. Image-A XIP 362 and image-B SRAM 288 stay
separate; runtime callback and hardware equality are unqualified.

Retained `codec-flash-copy-arguments-001.json` identifies the normal BINH-A
copy source package span `[87060,101776)` and target IRAM span
`[0x10023400,0x10026d7c)`, exactly the 14,716-byte authenticated image-A
SRAM body. That span contains the typed product source data
`[0x1002657c,0x100268c8)`. The original loader finding marks this as a
conditional path and leaves the alternate sentinel route and the relationship
between executable `0x1002xxxx` and data-address `0x2002xxxx` unresolved.
The copy evidence does not establish a final source linker script or runtime
alias semantics.

The connected timer/startup round adds five image-A SRAM bodies:
`0x100258c4` timer dispatch (104 bytes), `0x10025944` microsecond delay
(72 bytes), `0x1002598c` millisecond delay (16 bytes), `0x10023528`
BSS clear (22 bytes), and `0x10024984` start-mode PMU test (30 bytes).
The timer dispatcher walks ten native 36-byte records at runtime
`0x20026d84`, compares 64-bit deadlines, invokes the stored callback,
updates the signed 32-bit interval-times-1000 deadline, and clears
one-shot slots. The delays use the already source-owned 64-bit clock. Direct
startup literals give the BSS word-clear span
`[0x20026d80,0x2002ecec)` (0x7f6c bytes), which contains the timer
records and flash protection maps. Start-mode preserves the PMU `+0x5c`
volatile read even though its value does not affect the return.

The flash protection map's 24-byte source object was corrected from a
zero-filled custom PROGBITS section to
`.bss.gx8002.flash_protection_maps.26ff8`; target `readelf -SW` now
confirms NOBITS. This establishes its zero-initialized source storage type,
while exact final BSS placement remains a linker obligation. Fresh receipt
`g2/build/c-firmware/20261011/codec-resident-timer-bss-start-nobits-round/receipt.json`
passes 49 primary C-SKY compilation inputs and relocatable link with zero
unresolved/duplicate strong symbols. Output SHA-256 is
`902190f8f037f024ffd0e7b3d29c547e0e805a7e11dc84d442dba9b2e0029c82`.
The identified image-A SRAM C candidate set is now **66/151** (85 retained
entries remain to attribute/source), with XIP 362 and image-B SRAM 288
still independent. CPU timing and final firmware layout are unqualified.

The connected memory/cache round adds four image-A SRAM native bodies:
`0x10025738` forward copy (126 bytes), `0x10025608` D-cache invalidate
(86 bytes), `0x100256c0` D-cache clean+invalidate (86 bytes), and
`0x1002571c` I-cache enable (28 bytes). The copy helper preserves the
native address-alignment split, 16/4/1-byte units, and the exact four-word
load/store order in its unrolled path; it supplies no overlapping-copy
guarantee. Cache variants write the authenticated command register
`0xe000f004` once per 16-byte line, unrolling 128-byte blocks with operation
bits 2 and 10. I-cache enable writes `0xb0000000`, sets bit 0, and polls
`0xb0000004 & 3` for 2. These are direct native instruction reconstructions,
not hardware execution evidence.

Fresh `g2/build/c-firmware/20261011/codec-resident-copy-cache-ordered-round/receipt.json`
passes C-SKY compilation of 51 primary source inputs and relocatable link,
with zero unresolved or duplicate strong symbols. Source digests for both
new translation units match this receipt. Output SHA-256 is
`a0ce207c6b5bf870776250c99374673693dba382a8b79dca0cec3c06bb0ecf53`.
Image-A SRAM identified C candidate coverage is **70/151**, leaving 81
retained entries to attribute/source. Image-A XIP 362 and image-B SRAM 288
remain separate; final memory map and native CPU/device behavior remain open.

The resident KWS/queue route adds four native image-A SRAM C bodies:
`0x100260d0` optional KWS callback (20 bytes), `0x10026340` active-SNPU
queue callback (22 bytes), `0x100263b4` standby setter (14 bytes), and
`0x100263c4` standby countdown (24 bytes). Direct instructions locate the
callback word at `0x20027b50` and queue/state at `0x2002e6ec`, both within
the authenticated BSS span. The queue callback passes the first and third
register arguments as a two-word record to the already source-owned
`LvpQueuePut` algorithm; standby state uses offsets `+0x4c/+0x50` and a
50-step countdown. Runtime callbacks and queue storage remain true inputs.

Native clock initialization addresses `0x20026904` and `0x20026954` as
ten eight-byte source-selection records, passing each record to the
source-select helper. The corresponding 160 source-image bytes at
`0x10026904..0x100269a4` are now typed C data in
`resident_clock_product_tables.c`. `verify_resident_clock_tables.py` reports
both 80-byte target-object sections exactly equal to authenticated stock
(`resident-clock-table-receipt.json`). Ghidra's two apparent function seeds
at `0x10026904` and `0x10026954` are thus initialized data records, not
missing C bodies. The earlier byte-checked protection/catalog/module data
also contain seven Ghidra function labels inside proven data extents. These
nine labels remain within the 151-entry raw census but are explicitly
data-classified; other labels have not all been classified.

Fresh `g2/build/c-firmware/20261011/codec-resident-kws-clockdata-round/receipt.json`
passes C-SKY compilation of 53 primary source inputs and relocatable link,
with zero unresolved or duplicate strong symbols. Output SHA-256 is
`b71a7762aec9e2c1e0d99cb1bda18097a84976aa0db232b00ddf83e4355fd620`.
Image-A SRAM identified C body coverage is **74/151 raw seed entries**.
The remaining 77 raw labels include at least nine proven data labels, so
at most 68 of those labels represent unimplemented bodies before further
classification. XIP (362 seeds) and image-B SRAM (288 seeds) are independent.
Native runtime and final linker/alias placement remain open.

The next connected clock query round adds image-A SRAM `0x10024d70`
(`gx8002_resident_clock_module_query_24d70`) and `0x10025180`
(`gx8002_resident_clock_gate_query_25180`). Retained native pseudocode and
instructions support their signed table bits, MMIO status/field reads,
special paired-module masks, and return encodings. Both use the already
source-owned six-word module-info lower; `resident_platform_gate.h` now shares
its exact 24-byte ABI across the providers. The module product table remains
source-owned data with a separate byte oracle.

Fresh `g2/build/c-firmware/20261011/codec-resident-clock-query-round/receipt.json`
passes 54 primary C-SKY compilation inputs and relocatable link, with zero
unresolved and duplicate strong symbols; output SHA-256 is
`4ee55c2f85407aa58167557ff48f57aa4de2e7afc4e87165a0477540f40df2ed`.
The 160-byte clock-table oracle still passes (`all_exact=true`). Image-A SRAM
has **76 identified C body providers** among 151 raw labels. Its remaining
**75 raw labels** contain **at least nine proven data labels**, so at most
**66 true body obligations** remain in that raw set. Other apparent data labels
in the source-image initializer have not yet received individual typed or
byte-oracle classification. Image-A XIP 362 and image-B SRAM 288 seeds remain
separate. MMIO execution, startup/scatter alias placement, and full codec
source/layout qualification remain open.

The cache-control round reduces two further image-A SRAM native bodies,
`0x100255c4` and `0x100255e4`, into `resident_cache_variants.c`. Direct
instructions at these addresses establish two C-SKY `sync` operations before
and after the MMIO sequence. Enable writes 1 to `0xe000f004` and 21 to
`0xe000f000`; disable clears bit 0 at `0xe000f000`, then writes 1 to
`0xe000f004`. The target C uses inline `sync` and volatile MMIO writes.
`g2/build/c-firmware/20261011/codec-resident-dcache-control-round/receipt.json`
passes 54 C-SKY source inputs and relocatable link with zero unresolved or
duplicate strong symbols; output SHA-256 is
`4ff3931d20d60f7e139276e7d5989d240d520eec1f784b5b951472edf7f890a4`.
This is target compilation, not native cache behavior qualification.

Image-A SRAM now has **78 identified C body providers /151 raw seed labels**.
The **73 remaining raw labels** include the same **nine independently proven
data labels**, giving an upper bound of **64 possible true bodies**. A fresh
raw inventory also shows 20 labels at or after `0x1002657c` in the source
initializer area. Eleven of these have not been individually typed or
byte-oracle classified; they are not silently counted as proven data. XIP
362 and image-B SRAM 288 remain separate seed inventories.

The next native/data round adds `0x100251ec` as C, preserving the saved
interrupt-state register through the SNPU enable bit-8 read/modify/write at
`0xa0300018`; the source-owned critical save/restore lowers supply the
machine ABI. The source initializer `0x100268c8..0x10026904` is now a typed
60-byte clock defaults object. Native clock init/switch consumers read or
write fields at offsets 0, 0x14, and 0x38; the remaining words retain their
authenticated values as positionally named fields. Target-object byte oracle
`resident-clock-defaults-receipt.json` is exact. This proves both raw seed
labels `0x100268c8` and nested `0x10026900` are data.

The two UART channel descriptors at `0x10026a94..0x10026b94` are typed
128-byte records, matching the XIP channel consumer's `channel << 7` index,
register-base field, callback fields, and native channel/baud/IRQ values.
`resident-uart-descriptors-receipt.json` proves all 256 target-object bytes
equal the stock initializer. This independently classifies raw seed
`0x10026a94` as data. Runtime alias/copy and final linker placement remain
unqualified.

Fresh `g2/build/c-firmware/20261011/codec-resident-uart-product-round/receipt.json`
passes 56 primary C-SKY inputs and relocatable link with zero unresolved or
duplicate strong symbols; output SHA-256 is
`9f17c7f617dfbd38c7b4b9f41a458bc706db2f54f31a031cd7530e42dcd10d49`.
Image-A SRAM now has **79 identified C bodies /151 raw labels**. Of the
**72 remaining raw labels**, **12 are independently proven data**, leaving
**at most 60 possible true body gaps**. Image-A XIP 362 and image-B SRAM
288 seeds are distinct regions and are not included in this bound.

The VIC helper round reconstructs six more resident native bodies:
`0x100254c8` clear-enable register, `0x100254e4` two-word enable restore,
`0x100254fc` mask wrapper, `0x10025504` unmask wrapper, `0x1002550c`
two-word snapshot plus 32 IRQ clears, and `0x10025534` save-disable wrapper.
The preexisting `0x100254ac` enable provider was corrected to preserve the
native bit-5..6 VIC bank extraction for IRQ values through 127. Direct native
instructions give MMIO base `0xe000e100`, clear-enable bank offset 32 words,
snapshot SRAM `0x20026eec`, and the loop bound 32. These C bodies use the
real source-owned VIC enable and critical-section interfaces; interrupt
behavior on hardware remains unqualified.

Image-A source bytes `0x100269a4..0x100269cc` are now represented by a
40-byte board state C object. XIP native `0x10203004` returns its runtime
alias `0x200269a4`, and `0x1020302e` reads its halfword at `+0x20`.
`resident-board-state-receipt.json` proves the target object section exactly
equals the 40 stock bytes; other field meanings and final alias placement
remain open. Raw seed `0x100269a4` is thus independently proven data.

Fresh `g2/build/c-firmware/20261011/codec-resident-vic-boardstate-round/receipt.json`
passes 57 C-SKY source inputs and relocatable link, with zero unresolved or
duplicate strong symbols; output SHA-256 is
`d02139a224bba0b8455e919a388282ef4fd99fcd5ed19ea017bc477c4d8a3baa`.
Image-A SRAM has **85 identified C bodies /151 raw labels**. The **66
remaining raw labels** include **13 exact-data-proven labels**, leaving
**at most 53 possible true body gaps**. Image-A XIP 362 and image-B SRAM
288 inventories remain separate.

The next connected clock leaf round adds five image-A SRAM C bodies from
direct instructions: trim gate `0x10024a10`, trim-state read `0x10024a1c`,
register-field update `0x10024a30`, packed module-divider read `0x10024ae8`,
and clock source selection `0x10024bcc`. The trim path calls the source-owned
module gate and reads PMU `0xa0010030` bit 0. Register update preserves the
native read, shifted mask clear, shifted value OR, and write order. The
divider reads the authenticated packed offset/shift/mask word through the
source-owned module table; source-select uses the low value byte of an
8-byte selector/value record and MMIO `0xa001008c`. Hardware behavior and
unbounded shift inputs remain unqualified beyond the supported native
product values.

Two additional raw labels are proven initialized data. Source image
`0x10025cd0..0x10025ce0` holds two 8-byte clock source records copied by
`0x10025a14`; `0x10025ce0..0x10025cf4` holds five signed start-mode PLL
adjustments indexed by `0x10025a88`. Typed C data and
`resident-clock-boot-literals-receipt.json` prove all 36 target-object
bytes equal stock. Their final placement and reset alias remain linker work.

Fresh `g2/build/c-firmware/20261011/codec-resident-clock-boot-table-round/receipt.json`
passes 59 primary C-SKY source inputs and relocatable link with zero
unresolved or duplicate strong symbols; output SHA-256 is
`6a333fb1f388258a7e200919af8a4137f8b3e523a6098363096fadcf003566ba`.
Image-A SRAM has **90 identified C bodies /151 raw labels**. The **61
remaining raw labels** include **15 exact-data-proven labels**, leaving
**at most 46 possible true body gaps**. Image-A XIP 362 and image-B SRAM
288 remain independent inventories.

The PLL/getter round adds three resident image-A SRAM C bodies:
`0x10024b04` source-owned PLL register sequence, `0x10025060` PLL wait,
and `0x100264dc` keyword-list BSS pointer getter. Direct native code
establishes the repeated ordered RMW writes under `0xa0005000`, the
configuration-word indexing through word 11, the status poll at
`0xa0005098 & 8`, and the getter literal `0x2002e79c`. The caller still
must supply the genuine 12-word PLL configuration; the source does not
invent product values. The nearby `0x100264d4` raw label is embedded literal
pool bytes in native disassembly and awaits explicit relocation/data
ownership, so it is not counted among exact-data-proven labels.

Fresh `g2/build/c-firmware/20261011/codec-resident-pll-getter-round/receipt.json`
passes 60 primary C-SKY inputs and relocatable link, with zero unresolved
or duplicate strong symbols; output SHA-256 is
`818188dbafd80519acbd97df37097a78d613009c677e017ed6eb2d67a1a4c6b3`.
Image-A SRAM now has **93 identified C bodies /151 raw labels**. Its **58
remaining raw labels** include **15 exact-data-proven labels**, leaving
**at most 43 possible true body gaps** before other literal/data review.

The first explicit other-region crosswalk is
`resident-other-regions-census.json`, generated from source-to-native
bindings and retained seed inventories. It records **18 XIP C candidates
bound to distinct native entries** among **362 raw image-A XIP labels**;
the other **344 XIP labels** are not yet attributed by this crosswalk, and
their code/data split is open. Image-B SRAM has **288 raw labels** and
**zero explicit bindings in this crosswalk**; this does not prove that
upstream DSP or other C cannot bind to them. Stage1/stage2 UART source
inventories remain separate from these three regions. None of these
candidate counts establishes whole-image source, alias/layout, or runtime
equivalence.

An isolated startup composition now reduces three further image-A SRAM
native bodies without forcing unowned descendants into the zero-import
selected graph. `resident_reset_entry_candidate.S` reconstructs `0x10023500`
with actual CR0/CR31 control, stack top `0x2002f7fc`, calls, and final loop.
`resident_system_initialize_candidate.c` reconstructs `0x1002354c`: CR19/20/21/18 updates, clock-root register arguments, conditional BSS clear,
board initialization, vector-base CR1, ordered VIC writes, and `psrset`.
`resident_main_candidate.c` reconstructs `0x10026314` from six native XIP
call edges and its event-tick loop. The startup C and entry assembly compile
for C-SKY; composition with the selected resident candidate succeeds as a
relocatable object, leaving exactly eight true external contracts: clock
root `0x10025a88`, vector table source `0x10023400`, and six XIP children
(including omitted seed `0x10207a7c`). See
`resident-startup-composition-receipt.json`; combined object SHA-256 is
`81221bc5b8d950d10d3d3834c653c05e8bd9076598e8292eec5c1eb788a2f6a8`.
This isolated root is **not** yet integrated into the selected image builder.

The normal BINH-A loader copy contract remains source package bytes
`[87060,101776)` to IRAM `[0x10023400,0x10026d7c)`, with stack top
`0x2002f7fc` and BSS clear `[0x20026d80,0x2002ecec)`. The source vector
table and the mapping from executable `0x1002xxxx` references to data
`0x2002xxxx` remain unowned linker/scatter obligations; no executable
payload bytes were copied into source. Counting these isolated candidates,
image-A SRAM has **96 identified C/assembly bodies /151 raw labels**;
**55 raw labels** remain, including **15 exact-data-proven labels**, so
**at most 40 possible true body gaps**. The last selected zero-import
graph independently remains at **93 bodies** and the fresh selected receipt
above. The other-region crosswalk now includes the source-owned XIP analog
update `0x10203c74`: **19 bound XIP C candidates /362 raw XIP labels**,
leaving **343 unbound raw XIP labels**; image-B SRAM 288 remains unbound
in that crosswalk.

The startup sources were initially isolated because the root's clock child,
vector data, trap/IRQ targets, and XIP application descendants were unowned;
placing an isolated root into the earlier zero-import graph would have hidden
the true source contracts. The current codec experimental manifest now
includes the real `0x10023500` reset assembly, `0x1002354c` system init C,
`0x10026314` main C, source-owned typed 64-word vector table, and
`0x10025a88` clock initializer C. The latter reconstructs native branch,
retry, source-selection, 19 module-source calls, divider/DTO calls, gate
restoration, and final analog writes. Native instructions correct the
decompiler's omitted module-2 divider argument to `(2,2)`. Its clock-module
lowers remain real imports; no product configuration is fabricated.

The vector table is typed C with relocations rather than copied stock
addresses. `resident-vector-relocation-receipt.json` proves the 64 native
target identities and relocation order: one reset, 31 exception bridge,
32 compact IRQ entries. The final linked vector bytes and absolute placement
remain unqualified. Native exception `0x100235f0/0x100235fc` now compile as
source assembly and close the exception-bridge import. The compact IRQ entry
`0x10025574` remains an explicit import: the available C-SKY assembler
rejects its native `fstms/fldms fr16-fr19` operands, including with
`-mfpu=fpv3`; `resident_irq_compact_unqualified.S` is excluded. No raw
instruction blob or substitute handler was linked.

Three additional C/assembly bodies close the analog/PLL path:
`0x100246f0` analog LDO write, `0x10024710` digital LDO read, and
`0x1002500c` bounded PLL wait. The native `0x10024730` digital-voltage body
reads a stack byte before initializing it; `resident_digital_voltage_ambient.S`
preserves that ambient read and calls the actual source-owned platform
configuration lower. This avoids inventing a zero stack value. The C-SKY
selected candidate therefore has **103 identified image-A SRAM bodies**,
with **48 remaining raw labels**, **15 exact-data-proven labels**, and
**at most 33 possible true body gaps**.

Fresh `g2/build/c-firmware/20261011/codec-resident-startup-ambient-round/receipt.json`
passes 68 primary C-SKY source/assembly inputs and relocatable link with
zero duplicate strong symbols and **ten genuine unresolved imports**:
clock module source/divider/DTO, compact IRQ entry, and six XIP application
children. Its output SHA-256 is
`7cbb0ef11313a7b5de911257292adce7212f9cec3b6979308300b30faa7bf38f`;
all nine current startup/clock source digests match the receipt. A successful
relocatable link does not produce the final IRAM/XIP scatter layout or prove
the `0x1002xxxx`/`0x2002xxxx` runtime alias, and native MMIO execution is
still unqualified. Image-A XIP and image-B SRAM body/data audits remain
separate at 19/362 explicit XIP bindings and 0/288 image-B bindings in the
conservative crosswalk.

Two further clock descendants are now source C candidates: native
`0x10024df8` divider and `0x10024f44` DTO in
`resident_clock_divider_dto.c`. Both preserve the module lookup, packed
product-field access, gate observation/restoration, and ordered volatile
register writes. Direct instructions at the corresponding addresses in the
retained image-A SRAM disassembly resolve the write order and return ABI;
the clock root now declares these two callees `void`. This raises the
identified image-A SRAM body count to **105/151**; of 46 remaining raw labels,
15 are separately proven data labels, leaving at most **31 potential true
body gaps**. Target compilation/link qualification and native MMIO execution
are independent gates.

Fresh target receipt `g2/build/c-firmware/20261011/codec-divider-dto-round/receipt.json`
passes 69 C-SKY primary inputs, relocatable link return 0, zero duplicate
strong symbols, and eight genuine unresolved imports. The two divider/DTO
imports closed; remaining are clock module source, compact IRQ, and six XIP
application children. Output SHA-256 is
`591358c3c84f908fe47721e5e80944b5925f49dad01c53a4f7433b2d934c2554`.
No stock MMIO execution oracle or final image layout is asserted by this
receipt.

The compact IRQ assembler limitation is an ISA configuration conflict, not
merely an operand spelling issue. Retained binutils `tc-csky.c` checks
`FREGLIST_DASH`: high floating registers are legal only with
`CSKY_ISA_FLOAT_7E60`, while the selected `ck804ef` setting uses a
16-register floating profile. An isolated named-instruction test of
`fstms/fldms vr16-vr19` compiles with `-mcpu=ck860f`; it fails with
`-mcpu=ck804ef -mfpu=fpv3`. The original CPU/decoder configuration and
mixed-architecture link remain unqualified, so the IRQ entry stays outside
the selected graph without register omission or an opcode blob.

The isolated `ck860f` object disassembles the named pair as
`f46e3410`/`f46e3010`, whereas the retained stock bytes are
`f4ee3400`/`f4ee3000`. Assembly acceptance therefore does **not** establish
instruction equivalence. The parser's 32-FPR ISA gate only diagnoses why
`ck804ef` rejects the source; native CPU variant and opcode semantics need
separate qualification.

The third clock lower, image-A SRAM `0x10024be0`, is now reconstructed as
`resident_clock_module_source.c`. The native instruction path resolves the
module/source validation, the 7/8 source translations, `0x247` selector
mask, `0x490000` dependency split, packed source bit/mask, and conditional
primary gate writes. Native table accesses are to the *indexed* source-owned
26-entry module table, including byte offsets `+0x25/+0x26`, rather than
lookups by module ID. Its source C calls the existing typed module lookup
and register-field lower. This is an admitted C candidate, with native MMIO
execution and final table alias still pending. It raises the image-A SRAM
identified-body count to **106/151**, leaving 45 raw labels, of which 15
have independent exact-data proof: at most **30 potential true body gaps**.

Fresh selected target receipt
`g2/build/c-firmware/20261011/codec-source-clock-round/receipt.json`
passes 70 C-SKY primary inputs, relocatable link return 0, and zero
duplicate strong symbols. The clock-source import closed, leaving seven
real imports: compact IRQ and six XIP application descendants. Output
SHA-256 is
`e5d004385b6f74a818840f7d788fc6365178dfd50598436444c658a5018e454d`.
This is source compilation and graph closure, not native MMIO or final
whole-image layout equivalence.

Two more connected native clock bodies are represented in C:
`0x1002599c` iterates modules 0..25 with source-query gates for modules
2, 7, and 8; `0x10025a00` sets the paired 7/8 dividers to zero. Native
instructions establish the status address `0xa001008c`, branch priorities,
26-iteration bound, and both divider calls. They are
`resident_clock_lowpower.c` and use actual selected typed lowers. This
advances the identified image-A SRAM body count to **108/151**, leaving
43 raw labels, including 15 data-proven, hence at most **28 potential true
body gaps** at that intermediate checkpoint.

That `0x10025a14` caller is now also C in the same unit. It copies the
source-owned 16-byte 1 MHz record pair, applies both source records, invokes
the module loop, snapshots module 11..25 gate states, clears dividers 7/8
and 10, then conditionally restarts the source-owned PLL configuration.
Direct native instructions establish the loop bound, snapshot address,
call sequence, and conditional save/restore of PLL word zero. The census
therefore advances to **109/151** identified image-A SRAM bodies, 42 raw
labels remaining with 15 exact-data labels, at most **27 genuine body gaps**.
The source record's final runtime placement at `0x10025cd0` and PLL alias
at `0x200268c8` remain linker/scatter-copy obligations.

Fresh `g2/build/c-firmware/20261011/codec-source-lowpower-round/receipt.json`
passes 71 target inputs, relocatable link return 0, zero duplicate strong
symbols, and seven genuine imports (compact IRQ plus six XIP application
descendants). Output SHA-256 is
`e0981f691b10bcef6fe2adcfe1c29cb7d9cbba78e76a010cb84f8e360d9ff44e`.
The low-power source hash in the receipt equals the current file hash
`1afb21a0271e2d49c4ed77639f8a06aafaf99d690aea0b3c543244138a8d0ba5`.
Compilation does not prove the MMIO side effects on native hardware.

The next native SRAM slice adds `0x100257b8` timer-channel initialization,
`0x100257e8` timer root, and `0x10026358` TWS queue tick. Direct native
instructions establish timer MMIO addresses/write order, the 0x168-byte
runtime zeroing, IRQ number 14 with the already selected `0x100258c4`
dispatch provider, and the TWS queue literal `0x2002e6ec`. Clock frequency
and XIP TWS calls remain typed real imports; no clock or product defaults
are fabricated. These three source C bodies raise image-A SRAM coverage to
**112/151** identified bodies, leaving 39 raw labels, 15 independently
exact-data-proven, at most **24 potential true body gaps**.

Image-A XIP `0x102099cc` memset is also a new C body from retained
pseudocode: byte-alignment prefix, four-word bulk writes, word writes, and
byte tail. It target-compiles in isolation and raises the conservative
XIP explicit binding crosswalk from 19 to **20/362** once selected in the
next full receipt. Runtime memory equality and final XIP placement remain
separate from this source reduction.

`0x100263dc` TWS audio callback is now a typed C source candidate from
native instructions and retained pseudocode. It preserves sequence/flag
updates, descriptor iteration, clock-ratio selection, 15-sequence publish
cadence, the native `0x2002e6ec` queue state, and event 91 dispatch.
Its `0x100260e4` buffer-update child and XIP application functions remain
real imported contracts. This advances SRAM to **113/151** identified
bodies, 38 raw labels remaining with 15 exact-data labels, at most **23
potential true body gaps**.

`0x10206fb0` LvpQueueGet is also now C with the authenticated five-word
queue ABI shared by source-owned SRAM QueuePut and C-SKY signed DIVS
remainder. It target-compiles in isolation. Including the XIP memset above,
the conservative image-A XIP binding count advances to **21/362** once the
next full graph captures this file. There is no native queue execution
oracle or final XIP placement claim yet.

Three small XIP descendants now have C bodies: `0x102073a0` audio-input
read accounting, `0x102077f8` power-lock query, and `0x10208cc0` application
event enqueue. The authenticated XIP image uses base `0x10203004`; its
literal words at `0x102073b8`, `0x10207804`, and `0x10208cd0` resolve to
runtime pointers `0x2002ecb0`, `0x2002dfbc`, and `0x2002ecd8` respectively.
The event wrapper calls the existing source-owned SRAM QueuePut provider.
This raises conservative explicit XIP bindings to **24/362**; native XIP
execution and final placement are still unqualified.

Four more image-A XIP TWS helpers now have C bodies:
`0x10206e9c` context-header address, `0x10206ec8` context acquisition,
`0x10206f08` mic-frame address, and `0x10207394` delayed-VAD mode read.
Native XIP literal words at `0x10206ea0`, `0x10206f04`, and `0x1020739c`
establish pointers `0x20027b60`, `0x20027b60`, and `0x2002ecb0`.
The context arena index uses `% 3` and stride `0x2140`; the frame lower
preserves the source's integer arithmetic and queue-record offsets. All
four compile for the selected C-SKY target in isolation. Conservative
XIP explicit bindings advance to **28/362**, without a native runtime
claim.

The timer root's remaining clock-frequency child at `0x10025210` is a
distinct 424-byte native code span with a 19-entry absolute jump table at
`0x10025460`. The authenticated table maps module 7/8 to the zero-result
branch, 17/18 to module 16, 20/21 to module 19, 23/24 to module 22, and
25 to module 10; other entries enter the common path. Its PLL branch uses
mode-dependent multipliers, bounded frequency windows, DTO scaling, and
divider read. The retained decompiler contradicts direct instructions on
one mode multiplier, so this child remains an explicit import pending full
native arithmetic reconstruction and bounded source/original checks.

The TWS audio callback's connected SRAM child at `0x100260e4`, plus its
native callback at `0x100260d0`, is now source C. Direct instructions
establish the 13-by-80 frame window, invalidate/shift/copy order, 1040-byte
destination and cache sync, consecutive context lookups, event argument
layout, and 28-bit pointer fields. The 0x260d0 callback loads the native
runtime function slot at `0x20027b50` and conditionally dispatches.
Native stack offsets `+0x18/+0x1c` are event words 3/4 relative to the
event at stack `+0x0c`; they are *not* fourth/fifth call parameters. The
source writes those fields and uses the three-register-argument
`0x10205d60` contract. An initial isolated prototype was corrected before
the final selected receipt.
Both compile in isolation for C-SKY; XIP DSP/event children remain real
imports and native execution remains unqualified. Image-A SRAM identified
bodies advance to **115/151**, leaving 36 raw labels including 15
exact-data-proven labels, at most **21 potential genuine body gaps**.

One of those raw labels, `0x100246c0`, is demonstrably an inline literal
word rather than a body: the native preceding `lrw r0` at `0x1002469c`
loads that word, whose authenticated bytes decode to `0x20026504`; the
next actual function begins at `0x100246c4`. This removes one candidate
code gap, leaving **at most 20 potential bodies** among the 36 raw labels.
The `0x20026504` target still needs final source relocation/alias ownership,
so this classification does not count as a completed initialized C datum.

Seven connected XIP TWS/CTC leaves now have C bodies: `0x10206ea4`
feature-buffer address, `0x10206eac` frame index, `0x10206f50` frame count,
`0x10208c28` event setup, `0x10208c68` identity return (direct native
`jmp r15`), `0x10208c6c` +0x410 pointer, and `0x10208c74` constant 0x208.
Native XIP literal words establish runtime pointers `0x20030000`,
`0x20027b60`, and `0x2002e85c` for the corresponding bodies. Each target
compiles in isolation. Conservative explicit image-A XIP bindings advance
to **35/362**; native execution and final source placement remain open.

Image-A XIP `0x10206c44` memmove is now source C: its native forward
branch calls the selected SRAM `0x10025738` memcpy, and its overlap branch
copies bytes backward. The function returns its destination and target
compiles in isolation. This closes the buffer-update shift import in the
next selected receipt and raises conservative XIP bindings to **36/362**.

Two connected XIP application roots now have C bodies in
`resident_xip_app_ticks.c`: `0x102085f8` mode tick and `0x10208d48`
event tick. Native XIP disassembly at the same addresses authenticates
the RAM mode record `0x2002e6e4`, XIP mode table `0x1020b1bc`, event
queue `0x2002ecd8`, application callback holder `0x20026d38`, callback
offsets `+8/+12`, and queue/callback/UART/watchdog call order. The
`0x102067a0` watchdog child is also source C; direct native instructions
write `118` to MMIO `0xa070000c`. The UART async child `0x10208334`
was then reconstructed in `resident_xip_uart_async_tick.c`: the native
32-byte queue packet, CRC check, exact `"Crc Error %d\n"` XIP literal,
and 16-by-28-byte RAM dispatch table with callback/context at +20/+24
are preserved. Its CRC lower is selected pinned NationalChip source;
the formatter remains a real import. A refreshed unique-address crosswalk
is **39/362** after this UART body. The prior hand count of 39 before
UART double-counted `0x10206fb0` because two C providers cover that same
native queue body. The app roots compiled and linked in the
experimental C-SKY candidate; native execution and image layout are not
yet qualified.

Four previously unbound image-A SRAM body addresses now have source C:
`0x1002381c` flash read chunker, `0x10023858` flash information query,
`0x10023980` protection mode query, and `0x10024810` platform read query.
The authenticated XIP jump table at `0x1020be1c` provides all 14 flash
information targets; the authenticated SRAM table at `0x100249cc`
provides all ten platform read targets. Direct native instructions give
the flash read 64 KiB signed `min.s32` chunking, state callback slot
`0x200264e4 + 0x1c`, protection pointer chain, and platform MMIO
read/output widths. These additions conservatively raise identified SRAM
body addresses from **115 to 119 of 151 raw labels**; the previous 36
unbound raw labels fall to 32, including 15 separately data-proven labels
and one inline literal, leaving **at most 16 plausible genuine bodies**.
The bound-address count is a C coverage measure, not native equivalence or
final image placement proof.

The next SRAM body, `0x10025d04`, is source C in
`resident_flash_otp_mode.c`. It preserves the native product-initializer
callback loaded from RAM `0x20026504`, module-13 clock/2, OTP descriptor
read, exact stock strings `"read flash otp error\n"` and `"8003A"`, and
the `0x8002` versus `0x8003a` output values. Its exact XIP string lowers
at `0x10206c7c` and `0x10206ca0` are source C after direct instruction
review. The callback's product implementation remains a typed runtime
input, and the clock frequency/formatter stay imported. Unique XIP
bindings rise to **41/362**. SRAM identified bodies conservatively rise
to **120/151 raw labels**. The apparent SRAM label `0x100264d4` is
two inline literal words (`0x2002e6ec`, `0x1020b250`) consumed by adjacent
code, not an executable body. With 31 still unbound raw labels, the 15
previously proven data labels and the two inline literal labels at
`0x100246c0` and `0x100264d4` leave at most **14 plausible genuine SRAM
body gaps**. Runtime execution and
source-linked placement are open.

SRAM `0x100248cc` OTP low-power entry is now C plus named target `sync`
and `doze` instructions. The direct native path gates on the source-owned
OTP mode probe, performs ordered analog MMIO bit inserts, switches to the
1 MHz source, writes cache command 5, then dozes. The C bit masks reduce
exactly to the retained pseudocode's `0xfffc16ff | 0x6800` and
`0xfffc1eff | 0x6000`; hardware execution remains untested. This raises
identified SRAM bodies to **121/151 raw labels**. Three more retained
labels `0x10026b94`, `0x10026bc8`, and `0x10026c1c` are contiguous
initialized records/table/config data, not code: their precise ranges,
sizes, and stock hashes are in `sram-data-classification-next.json`.
Their semantic fields, relocation ownership, and final placement remain
open, so they are classified as data rather than declared completed C
initializers. With 30 raw labels unbound, 15 earlier source-byte-proven
data labels, two inline literal labels, and these three further data
classifications, **at most ten plausible genuine SRAM bodies** remain.

The image-A SRAM audio record callback at `0x10026214` is now C in
`resident_audio_record_callback.c`. Direct native branches establish the
VAD nibble, PCM-frame index, signed frame divisor, unsigned sequence
remainder, queue-room checks, reconnect counter threshold 25, callback
arguments, and sequence reload after callback. The VAD query at
`0x10207404` remains an actual XIP body import. Three small XIP getters
used in the loop (`0x10206f74`, `0x10206f80`, `0x10206f84`) are source C
from direct native instructions and literal `0x20027b60`. Unique XIP
bindings advance to **44/362**. SRAM identified bodies advance to
**122/151 raw labels**; with the same 20 classified non-body labels,
**at most nine plausible genuine SRAM bodies** remain. Compilation and
native runtime qualification are reported separately.

The 642-byte image-A SRAM audio interrupt body at `0x10025e48` now has
an ABI-preserving named-assembly entry and C core. Direct native
instructions show that the entry carries ambient `r0` and `r4` into
disabled-status branches, so the entry passes both raw registers instead
of supplying zero defaults. The core preserves the three event groups,
volatile `0xa0a00100/104` enable/status reads, `0x20027330` product
callback slots, `0x124/148/168` and `0x128/14c/16c` event words, ordered
write-one-to-clear stores, and selected XIP memset lower. The C-SKY
candidate compiles/links coherently; native IRQ execution and callback
reentrancy have not been qualified. Conservatively, SRAM identified
bodies advance to **123/151 raw labels**, leaving 28 unbound raw labels;
the same 20 non-body classifications give **at most eight plausible
genuine body gaps**. Unique XIP bindings stay **44/362**, with image-B
separate.

The clean post-edit target receipt
`g2/build/c-firmware/20261011/codec-tws-memmove-final-round/receipt.json`
passes **81 primary C-SKY inputs**, relocatable link return 0, and zero
duplicate strong symbols. Its 14 real imports are clock frequency,
compact IRQ, six XIP startup/application children, and six XIP TWS
command/event/publish/data/submit children. Output SHA-256 is
`7492e869331e1ebabd61b076d02528bfbce68e499e7538e12f239a7079f753be`.
The four most recently edited TWS/XIP source hashes match the receipt,
and this build started after the corrected event layout and memmove
prototype were saved. Native CPU/MMIO execution, source scatter, and
whole-image completion remain open.

The native `0x10025210` frequency body is now `resident_clock_frequency.c`.
Its source names all 19 authenticated jump-table targets at `0x10025460`,
uses the existing six-word module-info ABI and source-owned module table,
and preserves the PMU/PLL read order, unsigned frequency windows,
mode-dependent multipliers, 64-bit DTO scaling, and divider call. Direct
native instructions resolve the retained decompiler's erroneous zero
multiplier for PLL mode 3: `movih r2,1500` is 98,304,000. `inct` is a
condition-code controlled add; the C-SKY ISA guide describes it as
"C=1 add immediate". A bounded static check compared all 19 native table
words with the source dispatch, plus each mode constant and three window
boundaries. This is instruction/source attribution, not a native execution
oracle. `check-clock-frequency-static.py` records the table-word and
source-constant check. The dedicated coherent target receipt is
`g2/build/c-firmware/20261011/codec-clock-frequency-round/receipt.json`:
**90 primary C-SKY source inputs**, compile and relocatable link PASS,
12 genuine imports, output SHA-256
`8b1a376fbdd2b59d2a8a811a3958f945ea91a9fae7106034767cd31aaa7deccf`.
Conservative SRAM body coverage advances to **124/151 raw labels**;
with 20 non-body labels independently classified, **at most seven
plausible genuine SRAM bodies** remain. Image-A XIP stays **44/362**
explicit body bindings; image-B SRAM 288 raw labels and final source
scatter/linker ownership remain separate open scopes.

A stricter post-build crosswalk corrects that conservative estimate.
`resident-sram-true-body-census.py/json` classifies all 22 native labels
at or after `0x1002657c` as initialized product data, plus five earlier
inline literal/BSS/clock records. This yields **27 data labels and 124
native code labels** among the 151 raw seeds. Five code entries use
deliberately renamed selected providers (`g2_codec_critical_save`,
`g2_codec_critical_restore`, `g2_codec_header_sync`, `g2_codec_timestamp`,
`g2_codec_queue_enqueue`). With those aliases and the fresh linked symbol
table, **123/124 actual code labels have selected C/ASM providers**. The
sole unbound seed is compact IRQ `0x10025574`, subject to the producer-CPU
instruction issue above. This is a source-address attribution census;
native behavioral qualification and the 27 data objects' final
relocations/scatter placement remain separate unfinished work. The
earlier `124/151` count used raw labels as its denominator and should not
be read as 124 source-defined executable bodies.

The connected XIP audio VAD root `0x10207404` and nine directly called
register bodies at `0x102045f4`, `0x10204630`, `0x10204664`, `0x10204698`,
`0x102046d8`, `0x1020470c`, `0x1020472c`, `0x1020477c`, and `0x102047ac`
are now C in `resident_xip_audio_vad.c`. Direct XIP disassembly establishes
the `0xa0a00000` register base, ordered field writes, and disjoint noise
ranges `[0,0x300000)`, `[0x300000,0x600000)`,
`[0x600000,0x1400001)`, and `(0x1400000,UINT32_MAX]`. It also shows
that the three low bytes passed to the VAD-weight setter are `0x000101`;
that setter ignores its high input byte. The printf lower at `0x10206c24`
remains the existing genuine formatter import. The dedicated coherent
`codec-vad-root-round/receipt.json` passes **91 primary C-SKY source
inputs**, compile and relocatable link, with **11 real imports** and
output SHA-256
`640cba4076e31e6107b692c85d983e58a91a8616af3d2e4acd4813f1c9b4f186`.
Image-A XIP explicit body bindings advance to **54/362**. Native VAD
execution and physical audio-register behavior are not qualified; XIP
source coverage, image-B, and final placement remain open.

The adjacent connected XIP environment-noise state transition at
`0x102075c8` is also source-defined in `resident_xip_audio_vad.c`. Its
historical candidate link name `gx8002_xip_tws_commit_102075c8` is
misleading; the native entry is `gx8002_audio_input_env_noise`, and its
actual caller passes the mutable context. The 118-byte direct native
body establishes thresholds `0x600000` and `0x3f00000`, signed counter
limits 51/151, asymmetric counter resets, and the context byte's low
three-bit update. A fresh coherent post-signature-correction receipt
`g2/build/c-firmware/20261011/codec-vad-env-coherent-round/receipt.json`
passes **91 primary C-SKY inputs**, compile and relocatable link, with
**10 genuine imports** and output SHA-256
`766a8da9a5fb2251c278a93dc781593e8e1fd959c0bf31fb651d3fb684d4dd57`.
The first `codec-vad-env-final-round` attempt was interrupted after the
source return type was corrected; it is not a completion receipt. XIP
explicit body bindings are now **55/362**; image-A SRAM remains
**123/124 native code labels**, and image-B SRAM 288 raw labels is a
separate source frontier. Native runtime and final layout remain open.

The connected XIP maximum-decoder root `0x102088f8` and its strategy-reset
child `0x10208964` now compile from `resident_xip_decoder.c`. Direct native
instructions preserve the conditional second max-score pass, the counter
at `0x2002e748`, selected strategy byte at event `+0x0d`, and the 164-byte
reset of `0x2002e7a8`. The former `tws_event` import name was historical;
the actual entry accepts an event pointer and returns zero. Its max-score,
strategy-selection, and CTC-clear children remain three distinct XIP
source imports; the latter is only a two-byte return in the stock corpus
but is retained as an import pending explicit source disposition. Fresh
`g2/build/c-firmware/20261011/codec-decoder-root-round/receipt.json`
passes **92 primary C-SKY inputs**, coherent compile and relocatable link,
with **12 genuine imports** and output SHA-256
`8d966f743faca5065aa1c09188ed3e742f6eae957ef0fa12a72bd5f70f90f3f5`.
The larger import count reflects the three newly exposed real children;
it is not a regression in source body coverage. XIP explicit bindings
advance to **57/362**. The broad XIP body/data partition, image-B, IRQ
producer CPU, runtime equivalence, and scatter/linker ownership remain open.

XIP mode initializer `0x102085a4` now compiles in
`resident_xip_mode_initialize.c` with two typed source-owned five-word
idle/TWS descriptors and their two-pointer selector. The native records
at `0x1020b1bc`, `0x1020b1c4`, and `0x1020b204` encode the exact IDs and
callback identities; `check-mode-descriptors.py/json` verifies all 12
authenticated words and records the source hash. The C root writes mode
state at `0x2002e6e4`, preserves default-to-idle selection, and reloads
the volatile selector after each indirect callback as native instructions
do. Seven descriptor callback bodies are visible as real XIP imports,
including two stock trivial bodies that are not represented by invented
success stubs. `g2/build/c-firmware/20261011/codec-mode-init-coherent-round/receipt.json`
passes **93 primary C-SKY source inputs**, coherent compile and relocatable
link, **18 real imports**, output SHA-256
`13e4c844f221f9e8e525df942e2281370e3ff85c1f0f06901d198680c5455389`.
The initial `codec-mode-init-round` build was interrupted to correct a
callback selector reload; only the coherent receipt qualifies this source.
XIP explicit body bindings advance to **58/362**. The callback bodies,
descriptor placement, adjacent XIP strings, native execution, image-B,
and final scatter/linker composition remain open.

Six mode descendants are now C in `resident_xip_mode_callbacks.c`:
native XIP `0x10206f9c` queue initialization, `0x10208624/34` idle
done/init, `0x10208644/4c` TWS buffer/done, and full `0x10208670` TWS
initialization. Direct instructions and native XIP strings support the
callback order, 56-byte queue in eight-byte elements, PMU wake source
test, error branch using the real audio-input initializer return, and
queue state writes at `0x2002e6ec+0x4c/0x50`. The stock return of
`0x102073bc` is the residual value from its hardware init child even
though the retained decompiler labeled that wrapper void; the C
import therefore has a `uint32_t` result. Hardware/audio/KWS lowers
remain genuine XIP imports. The dedicated coherent
`g2/build/c-firmware/20261011/codec-mode-callbacks-round/receipt.json`
passes **94 primary C-SKY inputs**, compile and relocatable link,
**20 real imports**, output SHA-256
`e26abf1354607b950769c23992649152c15d666c2db69504273998d915ac5366`.
Explicit XIP body bindings advance to **64/362**. This is source
compilation and static native attribution, not callback runtime or
product-data placement qualification.

The connected XIP application initializer `0x10208cd4` and its local
resume, watchdog, and suspend callbacks at `0x10208c7c/98/a0` are now
source C in `resident_xip_app_initialize.c`. Direct native instructions
support the 64-byte queue initialization, nullable runtime application
ops pointer at `0x20026d38`, indirect callback arguments, exact
`_LvpAppSuspend`/`_LvpAppResume` labels, registration order, and
`3000/2999` watchdog call. Register and watchdog lower bodies are
explicit genuine imports; the callback table is runtime product state,
not a zero-filled default. The coherent target receipt
`g2/build/c-firmware/20261011/codec-app-init-round/receipt.json`
passes **95 primary C-SKY inputs**, compile and relocatable link,
**24 real imports**, output SHA-256
`78e5f3ce0b440f700433c5ff2e8ad853f9614aaf0174b9ea4e1623082b55d572`.
The import count rose because this root exposes four registration/watchdog
contracts. Explicit XIP bindings are **68/362**; product state,
native callbacks, image-B, and final source linker placement remain open.
### Power callback registration and watchdog XIP round

`resident_xip_register_power.c` reduces native `0x102076c0` and
`0x10207718`: the two eight-slot callback registries at `0x2002dfbc`,
with native replacement/append and the selected resident eight-byte copy.
The coherent Codec receipt is `codec-register-power-round/receipt.json`:
96 primary source inputs, candidate compile/link PASS, 22 genuine imports.

`resident_xip_watchdog.c` reduces native `0x10206704`, `0x10206720`,
`0x102067ac`, and `0x102067b8`. Direct disassembly gives the watchdog
MMIO block at `0xa0780000`, callback slot `0x20027b48`, reset write at
`0xa001002c`, resident gate/IRQ callees, and terminal reboot loop. The
source preserves the integer timeout divider, sixteen-iteration exponent
selection, native log literal `level timout invalid\n`, and IRQ context.
The coherent `codec-watchdog-round/receipt.json` has 97 primary inputs,
candidate compile/link PASS, 19 real imports, and output SHA-256
`e78815e54a26866425cc8d6980c10a5d238d5a4a4159ec56984f4b81f7ead7d0`.
XIP crosswalk now binds 74 of 362 raw seed labels. These are source-body
and compiler results; native watchdog runtime and image layout remain open.

`resident_xip_kws_lifecycle.c` adds native KWS outer bodies `0x10206d90`
and `0x10206dac`, preserving conditional flash load, SNPU lifecycle order,
and callback slot `0x20027b50`. The new typed children at `0x10206cb0`,
`0x10205cf4`, and `0x10205d40` are honest imports. Coherent target receipt
`codec-kws-lifecycle-round/receipt.json`: 98 source inputs, compile/link
PASS, 20 imports, output SHA-256
`335ef4608852180e102bb708a95009f64e9e96b809a44118b42b2733199b3cc7`.
XIP explicit bindings are 76/362 raw seed labels; raw labels still include
data and do not measure executable coverage alone.

`resident_xip_snpu_lifecycle.c` reduces its connected SNPU init and exit
children `0x10205cf4` and `0x10205d40`. Direct native disassembly establishes
state base `0x20027350`, device register identities, IRQ callback address
`0x10205ce0`, and mask/suspend/unmask/conditional-exit order. Five XIP
children remain typed imports. `codec-snpu-lifecycle-round/receipt.json`
records 99 inputs, coherent target compile/link PASS, 23 imports, SHA-256
`288eb82939075aa0d76a9c158c4d0b59be9f1d41341bf069d96c00d8ad05b897`.
The XIP crosswalk is 78/362 raw labels (284 unbound, code/data mixed).

`resident_xip_snpu_children.c` reduces five further native SNPU children:
`0x102055a8/ac/b0`, `0x102058d4`, and `0x10205a90`. The first two
are literal single-instruction `jmp r15` source bodies. The other bodies
forward IRQ 12, initialize ten groups of eight TCB entries using native
constants, and suspend NPU after a native all-idle poll. Three NPU access
helpers remain genuine imports. `codec-snpu-children-round/receipt.json`
records 100 inputs, coherent target compile/link PASS, 21 imports, SHA-256
`bfcbbb68daf11996292edb872c8c29a1f9afc4e9f759959a98d7f98cadb077d4`.
XIP crosswalk: 83/362 raw labels, 279 unbound code/data mixed.

`resident_xip_npu_registers.c` closes NPU register leaves `0x10205600`,
`0x1020560c`, and `0x102056e4` using the exact native bit helper behavior:
clear/read bit zero at the passed register base and read bit 31 at base+12.
`codec-npu-registers-round/receipt.json` records 101 primary inputs,
coherent target compile/link PASS, 18 imports, SHA-256
`a8b75937d5efbbbfd67e6ec48b1a80a1b02a07039ad448ff6fd45a7a78a343ec`.
XIP crosswalk is 86/362 raw labels, 276 unbound code/data mixed.

`resident_xip_kws_flash_load.c` reduces native loader `0x10206cb0` and
task-copy child `0x10208c14`. It preserves five model-size calls, native
signed four-byte alignment, flash probe/read order from fixed source offset
`0xf804`, elapsed-time log, and a 32-byte task copy to `0x2002e85c`.
Stock leaves three task words as ambient stack bytes; C keeps them
uninitialized, so their runtime values remain an explicit precondition and
native equality is not established. Five model-size getters remain real
imports. `codec-kws-flash-load-round/receipt.json`: 102 primary inputs,
coherent target compile/link PASS, 22 imports, SHA-256
`c171651d6285ed8815b348d6840f75308dee0917a8576d8c9f59be372a878b8e`.
XIP crosswalk is 88/362 raw labels, 274 unbound code/data mixed.

`resident_xip_model_sizes.c` source-owns the five native return-immediate
model-size accessors `0x10208bf4/bfc/c04/c08/c10` (command `0x23cc`, weight
`0x1d7e0`, ops zero, data `0x3300`, temporary four). The loader now names
`gx8002_xip_kws_ambient_task_words` as a required input for the three
otherwise indeterminate stack words copied into task state; no zero fill
or guessed product data is used. The first model-size build was interrupted
after that source change. The fresh coherent receipt is
`codec-model-sizes-ambient-round/receipt.json`: 103 primary inputs, target
compile/link PASS, 18 imports, SHA-256
`733c42d2899fc3ce03b20cd5e17a1d4ed11c8dd94f1587bb5dd86c8730017e72`.
XIP crosswalk: 93/362 raw labels, 269 unbound code/data mixed.

`resident_xip_audio_input.c` reduces XIP audio input initialize/done
`0x102073bc/73f8`: native twenty-byte state clear, three fixed product
pointer identities, callback storage, lower residual return, and audio
exit. The two hardware lower bodies remain imported. The mode callback
declaration now matches the returned status ABI. Coherent target receipt
`codec-audio-input-round/receipt.json`: 104 inputs, compile/link PASS,
18 imports, SHA-256
`93b0f8066b6469a1986a9ea2b4b285cf17b25365daa191861ffe4ad3a3507884`.
XIP crosswalk is 95/362 raw labels, 267 unbound code/data mixed.

`resident_xip_audio_exit.c` reduces native `0x10204984`, preserving AIN
reset and module gate disable order 3, 2, 8, 7. Its receipt
`codec-audio-exit-round/receipt.json` has 105 inputs, coherent target
compile/link PASS, 18 imports, SHA-256
`03b9a002d2865f81b8a187deb70410e7c768f6999fad1969d045fe7095500ea5`.

`resident_xip_ain_reset.c` reduces native `0x10203c88` from direct C-SKY
instructions: MMIO base `0xa0a00000`, ordered bit writes, a hardware
status-bit-eight poll at offset `0x104`, and remaining reset writes. The
retained decompiler output incorrectly represented this as an infinite
loop. Receipt `codec-ain-reset-round/receipt.json`: 106 primary inputs,
coherent target compile/link PASS, 17 imports, SHA-256
`6182f314bfcf44d9c288b37155c2cf8cb1d7809ad134fabd764a42bd322ab3f1`.
XIP crosswalk is 97/362 raw labels; hardware runtime is untested.

`resident_xip_audio_initialize.c` reduces native `0x102047e4`: gate/reset,
audio state, relocatable config callback, resident IRQ-2 entry, and channel
MMIO branches. Audio input now passes source function relocations for the
resident record callback, the XIP config callback, and the native
one-instruction return callback `0x10207020`. This last body has no retained
XIP seed label, so it is source-owned but omitted from raw-label crosswalk.
`codec-audio-hardware-round/receipt.json`: 107 primary inputs, coherent
target compile/link PASS, 17 imports, SHA-256
`8c1cc7a8a144d9a137df40e6a15769a186c56cbd665d4f3339de9c8dfafd7908`.
XIP raw-label bindings: 98/362; 264 remain code/data mixed. Product config
callback `0x10207234` is the next substantive body.

`resident_xip_audio_config.c` reduces native `0x10207234` with the board
descriptor input and sixteen typed hardware/format children. The coherent
108-input `codec-audio-config-round/receipt.json` passed target compile/link
with 32 genuine imports, SHA-256
`04d1659f924e2dda396d161ec9d6d9339709cc9ba7a49bc606e0bbca62d3db8b`.
That was the source snapshot captured by the next all-six integration.

After that capture, `resident_xip_audio_board.c` binds native
`0x10203004/0c` to existing `board_uart.c` product providers and sources
`0x10203024` board initialization logs with exact stock strings.
`resident_xip_audio_register_leaves.c` reduces four AIN setters
`0x10204320/30/50/ac`; config reuses the selected
`gx8002_xip_tws_frames_per_channel_10206f74`. The latest coherent
`codec-ain-register-leaves-round/receipt.json` has 110 primary inputs,
compile/link PASS, 25 imports, SHA-256
`029d56b8318e40938d57e046a504af537eaa65088ed19ac7ebece0bead211750`.
XIP raw-label bindings are 104/362, leaving 258 code/data mixed labels;
native no-effect callback `0x10207020` is source-owned but unlabeled.

`resident_xip_audio_config_leaves.c` reduces native channel selector
`0x10203f70`, PGA gain `0x102042d4` with exact five-byte correction table
from `0x1020a8ee`, and FFT/VAD enable `0x10204570`. Coherent target
`codec-audio-config-leaves-round/receipt.json`: 111 inputs, compile/link
PASS, 22 genuine imports, SHA-256
`ba8dd577f04d4911e64e5d3d93e63333d3c845400b53b66aad5bf5df31befd3f`.
XIP raw-label bindings: 107/362, 255 code/data mixed labels unbound.

`resident_xip_audio_digital_inputs.c` reduces native PDM `0x10203e7c`
and I2S `0x10203ec8`, preserving module gate, ordered AIN register writes,
channel state at `0x20027330`, and PDM ten-millisecond delay. Receipt
`codec-digital-inputs-round/receipt.json`: 112 primary inputs, coherent
target compile/link PASS, 20 imports, SHA-256
`c007bec0a605ba833999d69fe2c24fb6a545a160a643488a267dc0d85d73d237`.
XIP raw-label bindings: 109/362, 253 mixed code/data labels unbound.

`resident_xip_audio_sadc.c` reduces native SADC root `0x10203e18`,
preserving analog-call order, selected gate 7, AIN bit six, and channel
state `0x20027330`. Seven genuine analog helpers remain imported.
`codec-sadc-root-round/receipt.json`: 113 primary inputs, coherent target
compile/link PASS, 26 imports, SHA-256
`33bef5dbf6e06e5273a9d0580b64b5c60090cabea0eeeb1d1ed210b50d039d95`.
XIP raw-label bindings: 110/362, 252 mixed code/data labels unbound.

`resident_xip_analog_registers.c` reduces seven connected native analog
register setters `0x10205e34/50/68/80/98/b0/c8`. Direct instructions give
the `0xa0005080` base, word access at offsets 8/16/20, masks, and low-byte
truncation on each write. `codec-analog-registers-round/receipt.json` is
the coherent 114-input target snapshot: compile/link PASS, 19 genuine
imports, SHA-256
`3e46801c11eb595f6b1594de79aa225263a461b6c3afce0bf509dd29c560e513`.
XIP seed bindings: 117/362 raw labels, 245 mixed code/data unbound.

`resident_xip_audio_evad.c` reduces the native enable and threshold bodies
`0x102043fc/44e0`, with direct AIN base/offset evidence and an explicit
valid-channel product precondition. `codec-evad-round/receipt.json` is a
coherent 115-input target compile/link PASS, 17 genuine imports, SHA-256
`d6a0e402fac9ad12c02add52996523cd3d896670fb51669f8d9faefe1b5f494a`.
XIP seed bindings: 119/362 raw labels.

`resident_xip_audio_buffer_queries.c` reduces eight native audio-buffer
query bodies, including source-address/size selection and PCM frame size.
The six native XIP literal-pool words at `0x10206e74/80/8c/98` and
`0x10206f70/98` all equal `0x20027b60`, so product header fields remain
runtime input at that typed SRAM address. `codec-audio-buffer-queries-round/
receipt.json`: coherent 116-input target compile/link PASS, 17 imports,
SHA-256 `a22b8225b44295cfc2e1675225cb0764d0c4347f04f3a2ec456be56dfc4aa087`.
XIP seed bindings: 127/362 raw labels, 235 mixed code/data unbound.

`resident_xip_audio_output.c` now reduces the complete 450-byte native
`0x10207070` output-dispatch body. Pinned NationalChip
`lvp/common/lvp_audio_in.c` owns the source algorithm and
`gx_audio_in_v2.h` owns the by-value output descriptor ABI. Direct native
listing confirms its channel 1/2/4/8 branches, C-SKY r0-r3 plus stack
record words, board offsets, and mandatory enable/call order.
`resident_xip_audio_output_modes.c` reduces direct register setters
`0x10204340/0x1020452c`; the latter preserves four distinct volatile
writes. `codec-audio-output-round/receipt.json` is a coherent 118-input
target compile/link PASS, 20 imports, SHA-256
`99969b79e30c429ce9148a93b03da0352bfa507fe42be5c49f4d137379a210b0`.
The four output engine contracts are now separately implemented in candidate
sources pending their own target receipt. Native runtime/hardware equality and
complete image layout remain unqualified.

Four native output engine bodies plus shared PCM channel setting are now
source-owned in `resident_xip_audio_output_pcm.c`,
`resident_xip_audio_output_logfbank.c`,
`resident_xip_audio_output_spectrum.c`, and
`resident_xip_audio_output_i2s.c`. Direct native disassembly authenticates
MMIO base `0xa0a00000`, active-channel state `0x20027334`, by-value C-SKY
record arguments, per-field volatile write order, and the I2S module-2 gate
provider. `codec-audio-output-lowers-round/receipt.json`: coherent 122-input
target compile/link PASS, 16 genuine imports, SHA-256
`8989af04470af9ce7dc2db3dd05ce18fd8551f07c6b07e555cadad4b267527ae`.
XIP raw-label bindings: 135/362, with 227 mixed code/data labels unbound.
The logfbank path's native unsigned divide requires nonzero frame count;
the selected board configuration sets that count to one.

`resident_xip_audio_standby.c` sources native standby startup `0x10207660`
and interrupt enable `0x102047b8`, including the state literal
`0x2002ecb0`, exact mask `0x30007`, enable register argument, and MMIO
write order. `codec-audio-standby-round/receipt.json`: coherent 123-input
target compile/link PASS, 15 genuine imports, SHA-256
`c976af5fdf4b5335bbe1c3a9115ee4f74b1750d240c02f33230ae814b0a4cc6a`.
Next source set recovers typed context-buffer initialization from the pinned
`lvp_buffer.c`/`lvp_context.h` and two exact native no-effect leaves.

`resident_xip_buffer_initialize.c` now represents stock `0x10206dc0`
with a typed 0x78-byte `LVP_CONTEXT_HEADER`, exact native SRAM clear extents
0x78/0x63c0/0x410, field offsets and initialized values. The five native
literal words at `0x10206e58..68` match the selected header/context,
feature, logfbank, mic, and `LVP_CONTEXT_VERSION` identities. This is
semantic runtime initialization C; source-owned allocation/placement for
all three SRAM extents still needs the final linker/startup map.
`resident_xip_ctc_offset_clear.c` and `resident_xip_idle_leaves.c` encode
three actual native return-only/zero-return bodies, verified as one or two
instructions rather than synthetic success substitutes.
`codec-buffer-idle-round/receipt.json`: coherent 126-input target
compile/link PASS, 11 genuine imports, SHA-256
`b195151ccc03b6dcc8f25528876a94f352098c2ba089516b32763fd9f2315951`.
XIP raw-label bindings: 141/362, 221 mixed code/data unbound.

`resident_xip_max_kws_initialize.c` reduces `0x10208944/78` using native
state literal `0x2002e744`, exact 66-byte diagnostic, and selected strategy
reset `0x10208964`. `codec-max-kws-init-round/receipt.json`: coherent
127-input target compile/link PASS, 10 genuine imports, SHA-256
`992849bce65bb9ed2e5515f38bb1e2dc4b930b1244a5cd5fbddd9896b1018c54`.
XIP raw-label bindings: 143/362, 219 mixed code/data unbound.

`resident_xip_tws_message.c` is exact source-owned 38-byte NUL-terminated
format data from native XIP `0x1020b250`, consumed by SRAM callback
`0x100263dc`. Its final XIP location is a remaining linker obligation.

`codec-tws-message-round/receipt.json` confirms the exact native
`0x1020b250` TWS format data as a coherent 128-input target compile/link
PASS, reducing the graph to 9 genuine imports; output SHA-256
`cce480d2f4f220c02e8d1c8bfb23c1d0ebc61f9fa6861ddb0bd40231f8456fde`.
The compiled C string's 38 bytes including NUL match authenticated XIP
bytes. Final source data placement remains open.

`resident_xip_snpu_run_task.c` now models native `0x10205d60` task-queue
body with pinned `GX_SNPU_TASK` eight-word layout, native SRAM base
`0x20027350`, 144-byte queue slots, exact command word `0x004100ff`,
and a 28-bit command-address mask confirmed from `zext ... 27,0`
(native disassembly corrects the retained decompiler's 27-bit mask).
Its resume/submit descendants remain real typed lower contracts. The
existing selected SRAM callback declaration was corrected to the same
pointer/function-pointer/return ABI. Target receipt pending.

## SPI master and pinned compiler runtime, 2026-10-11

The selected image-A candidate now includes native XIP SPI probe 0x10206480
and exact pinned LLVM compiler-rt 20.1.8 C sources for `__adddf3`,
`__divdf3`, `__fixunsdfsi`, `__floatunsidf`, and `__muldf3`. The downloaded
`fixunsdfsi.c` and `fp_fixuint_impl.inc` are exact revision-pinned with hashes
in the upstream provenance record. Their runtime FENV lowers
`__fe_getround` and `__fe_raise_inexact` remain explicit unresolved contracts;
no generic no-op exception provider was selected.

`codec-spi-compiler-rt-round/receipt.json` records 162 coherent image-A
sources and target compile/link PASS (SHA-256
`605c24a6823007bc0a565fca285360c41808b937d34353fa8d2b2d663affc177`).
Direct native C-SKY disassembly and pinned NationalChip `driver/spi.h`
then yielded four SPI register/list/setup/IRQ children in
`resident_xip_spi_leaves.c`. `codec-spi-leaves-round/receipt.json` records
163 coherent sources, target PASS, SHA-256
`5ee314fb92ecd9d2ab6c5b54bd936be4e14b09b25c0ed0a2d089941c0f81b5e7`,
and eight genuine image-A imports.

The 0x10206204 quick-transfer body is selected as the next 164th C source.
Direct native listing corrected the retained decompiler's truncated MMIO
addresses: the transfer gate writes 2 then 3 at `0xa030008c`. It also shows
RX chunks use `min(remaining, FIFO capacity)`. The full target receipt and
bounded hardware runtime oracle remain pending. XIP raw label bindings are
207/362; this is an attribution count over mixed code and data, not a
whole-image source-completion percentage. Image-A SRAM remains 123/124 true
bodies, with compact IRQ assembler/ISA qualification open. Stage2 96/96
retained seeded bodies are C candidates. Image-B is a separate loaded-stage
candidate. Full source-owned product data, layout/scatter, hardware runtime,
and native numerical equivalence remain open.

## UART receive and DMA descriptor graph, 2026-10-11

The selected image-A XIP sources now cover the direct-native UART receive
callback at 0x10208098, body probe at 0x10207cec, receive DMA dispatch and
completion, DMA channel selection/registration, transfer, and the complete
0x10203828/0x102038f4/0x10203c60 descriptor construction graph. The
descriptor source preserves the 4095-byte segment count, 24-byte descriptor
stride, source/target DMA translation, bitfield validation, and exact
0x2002e93c state literal. Pinned NationalChip layouts and direct C-SKY
disassembly were checked against the retained decompiler bodies. Hardware
runtime equality and final SRAM state ownership remain open.

`codec-uart-rx-round/receipt.json`: 173 coherent image-A source inputs,
target compile/link PASS, SHA-256
`f1d7c89d9baa0f7637c9a051d87f4035e7810e25e027a54158a5a4e1dab3f3d8`.
`codec-uart-dma-chain-round/receipt.json`: 177 coherent inputs, PASS,
SHA-256 `bfbf8cb269a00d1c139fbf766f297bfd728130ff1087e08734f58c3c678da544`.
`codec-dma-configure-round/receipt.json`: 178 coherent inputs, PASS,
SHA-256 `4c11b2b9c097d78f858bebe975c6e26e1ef7db0abb452c83828112ff6b2b4e85`.
The selected graph has six genuine imports: two floating-environment
services, the compact SRAM IRQ entry, console port product state, KWS ambient
task words, and UART channel product storage. These are not substitute
providers. XIP raw-label crosswalk is 245/362 bound, with 117 unbound mixed
code/data labels. This count is an attribution queue, not a true missing-body
count. Image-A SRAM remains 123/124 true bodies; stage2 has 96/96 retained
seeded C candidates. Image-B, source-owned initialized data, linker scatter,
and native execution gates are independent incomplete work.

The follow-on native UART transmit callback/message-body/body-done functions
at 0x10207f08/0x10207b38/0x10207c50 are selected in
`resident_xip_uart_send_path.c`. The callback uses the authenticated
0x2002e050 runtime state and 0x2002e578 six-row callback table. The source
preserves header/body/CRC/final phases, 14-byte header, 4-byte CRC, and
aligned DMA handoff. The UART transmit/CRC/message-start children remain
explicit genuine imports pending their own source reduction, and runtime
state/table initialization is still unowned. `codec-uart-send-round/receipt.json`
records 179 coherent image-A inputs, target PASS, SHA-256
`1fdc455abc6f1b2f71f2da26327dd4966945d0abae6c0c0ac9f5bbab6fb70e1c`.
The mixed raw XIP crosswalk is 248/362 bound, 114 unbound.

The next selected UART transmit lower source covers native 0x10203604 write
and 0x10203720 buffer setup, with typed 0x10203630/0x10203664 start/stop
providers. The latter two native addresses were already counted under
`channel_runtime.c` and are not counted twice. Native 0x102030c4 completion
and 0x10203108 DMA entry are selected, including the 12-word descriptor
and the authenticated two UART burst lookups. Existing 0x10207adc
message-start source now relocates to the selected C send callback; its
historical absolute callback literal was removed. Unsupported UART port
values at DMA descriptor word 8 remain a stated input precondition.

`codec-uart-tx-lowers-round/receipt.json` records 180 coherent image-A
sources and target PASS; `codec-uart-tx-dma-round/receipt.json` records 181
coherent sources and target PASS. The pinned NationalChip `base/src/crc32.c`
already selected for this image owns native CRC32 and crc32_no_comp
algorithms. A new three-register ABI binding for 0x102098a8 connects the
UART path to that source, correcting the decompiler's one-argument wrapper
signature. `codec-uart-crc-bound-round/receipt.json` is the latest coherent
target PASS: 182 image-A sources, SHA-256
`4a2a91dc563dd297dea583bd9f6f97f4838d98aa48a5c94e64311b3e03fff2a0`,
six genuine imports. The XIP raw-label crosswalk is 253/362, with 109 mixed
code/data labels unbound. The pinned CRC lower 0x102097f4 is source-owned
but not separately counted by the component-file crosswalk. Runtime/state
initialization, full image layout, and native execution remain open.

## Audio output IRQ and bounded XIP tail census, 2026-10-11

Direct C-SKY listing for native 0x102050cc proves the AOUT MMIO base is
`0xa0b00000`; the retained decompiler displayed zero-address accesses.
`resident_xip_audio_output_isr.c` now sources its full pending-bit and
callback control flow plus the two native register helpers at 0x102049c8
and 0x102049d8. `codec-aout-isr-round/receipt.json` records 183 coherent
image-A sources, target compile/link PASS, SHA-256
`f09e6293bf755d2c7ccb7e9165decbf903bf7d8337db703598ce68af8ee06a47`,
and the same six genuine imports. Hardware interrupt behavior remains
unqualified by execution.

The raw XIP crosswalk is 256/362. Of 106 unbound Ghidra labels, 23 labels
at and after 0x1020a8aa are in the native literal/data tail (408 bytes of
Ghidra envelopes): gain/correction tables, selector/default values, CRC
table, dispatch/name data, and short strings. The other 83 labels (9,806
envelope bytes) are an upper bound on unbound code bodies; selected pinned
`crc32_no_comp` at 0x102097f4 is already source-owned but omitted from the
component-file crosswalk, and compiler runtime bodies need individual ABI
attribution. The remaining main code clusters are AOUT, NPU/SNPU, GPIO,
sample-app command/audio, and softfloat/arithmetic. Exact initialized data
placement, SRAM aliasing, and runtime equality remain independent gates.

Five further true AOUT bodies are selected in
`resident_xip_audio_output_controls.c`: fixed SRC, SDC address read, frame
drain, aligned sample-buffer configuration, and mute. Direct native
instruction reads distinguish playback MMIO `0xa0b00000` from SDC/sample
buffer MMIO `0xa0b80000`, which the retained decompiler conflated as
zero-address globals. The frame drain uses the selected real millisecond
delay provider. `codec-aout-controls-round/receipt.json` records 184
coherent image-A source inputs, target PASS, SHA-256
`00c2d8a0ddeaed9276c6900914389a5c5f271e1476e4b5348e386c4295bedca4`,
and six genuine imports. The XIP raw crosswalk is 261/362. Remaining 101
labels comprise 23 native literal/data tail labels and at most 78 code
labels, including the already selected pinned CRC lower. Hardware behavior
and product memory placement remain unqualified.

The AOUT I2S/DAC configuration wrappers (0x10204c64/0x10204c90) and
ordered register lowers (0x10204ab0/0x102049e8) are source candidates.
The native seven-entry Lodac jump table at 0x1020a8f4 was decoded into
seven semantic C cases with exact strobe order. Full 0x10204d38 PCM
configuration includes all eight native clock ratios, A0B80000 SDC flags,
and an exact 118-byte mismatch format string from 0x1020a9b0.

A same-name edit briefly replaced the earlier tracked
`resident_xip_audio_output_pcm.c`, which owns 0x10203dc8/0x10203fa8.
The in-progress build was interrupted, that original file was restored
byte-for-byte from the unchanged Git index, and the new 0x10204d38 source
was placed in distinct `resident_xip_aout_config_pcm.c`. The restored file
SHA-256 `96ff5c401415e5982f4e9ada0fc06f58410150abf70b6c6202e0599949eab177`
matches its last pre-edit coherent source snapshot. Lodac's earlier
`codec-aout-lodac-round` receipt is superseded for graph/source coverage.

`codec-aout-pcm-corrected-round/receipt.json` is the authoritative current
candidate: 188 distinct coherent image-A inputs, target PASS, SHA-256
`275a858dadb304ad936c2e813f401b5a586056a7be4b224e08e28b6cad89a3f3`,
six genuine imports. Both PCM source paths and their distinct hashes are
recorded in that receipt. XIP raw-label bindings are 267/362; 23 unbound
labels are data-tail labels and at most 72 are possible code labels.

The direct-native AOUT lifecycle functions at 0x102052e0, 0x10205318,
and 0x10205344 are now distinct C source in
`resident_xip_audio_output_lifecycle.c`. The free path preserves the
native non-null context precondition (its field is cleared before the
later null test), ordered playback/sample register accesses, and the
selected memset lower. The callback path retains both callback pointer
fields and the playback-enable write. Exit clears the three native
control bits in order and gates modules 11 and 15 through the selected
platform provider. `codec-aout-lifecycle-round/receipt.json` records
189 distinct source inputs, a coherent target compile/link PASS, SHA-256
`d1344ebd6a374a925e7bf67e62d4e22f00780076e30677738d80772648a974c9`,
and the same six genuine imports. The native raw-label crosswalk is
270/362; 23 remaining labels are in the literal/data tail and 69 are
an upper bound on possible missing code. Native execution, full data
placement, and stage composition remain unqualified.

The next selected AOUT source reconstructs the channel-field register
update at 0x102049b0 and suspend/resume at 0x10204ec0/0x1020521c.
It retains the native context flag branches, ordered volatile register
operations, and module 11/15 clock-gate calls. The retained pseudocode
for suspend uses a narrow AND mask on the pending register; the C
candidate preserves that operation instead of inferring a generic clear.
`codec-aout-suspend-resume-round/receipt.json` is a coherent target PASS
with 190 distinct image-A inputs, SHA-256
`7165f12960f1aca14935bcd93fd104264719a35cd7231aa066e1f2ae52eef551`,
and six genuine imports unchanged. Raw XIP bindings are 273/362;
23 native labels are in the literal/data tail and 66 are an upper
bound on remaining possible code labels. Hardware execution and full
source-owned data/layout still require independent proof.

Seven further NPU XIP bodies now use the selected exact register-read
and set-bit lowers: interrupt-bit decoding at 0x102056f0, ordered
non-overflow and overflow clears at 0x102057e0/0x10205838, and the
four address/task-head register queries at 0x10205870/0x102058a4/
0x102058b4/0x102058c4. The source preserves each decoded output bit
and field address; it does not manufacture a register backend.
`codec-npu-queries-round/receipt.json` is a coherent target PASS with
191 distinct image-A inputs, SHA-256
`4553ff14ed895021f9ebcd8615869856b4165c72da946d75e64fb94641c121ca`,
and the same six genuine imports. The image-A XIP crosswalk is
280/362: 23 unbound data-tail labels and at most 59 possible code labels.
The pinned CRC lower is already selected but outside this component-file
crosswalk. Native execution and source-owned data/scatter layout remain
separate whole-image gates.

The SNPU interrupt chain now includes native 0x10205ce0 ISR state gate,
0x10205bd8 status dispatch and callback queue walk, 0x10205b1c
overtime reset, and 0x10205ad8 32-word diagnostic dump. The queue
indices and callback fields are bound to the already selected native
0x10205d60 task constructor. The diagnostic format literals were
verified byte-for-byte in the official Codec payload at offsets
82330, 82338, 82408, 82438, and 82461. The status function's
bit-6 return expression follows the retained decompiler's explicit
byte cast; native execution qualification is still needed for that
edge and callback paths.

`codec-snpu-overtime-round/receipt.json` is a coherent target PASS with
194 distinct image-A source inputs, SHA-256
`6f83123f9db1236d3c5b18616c9c2c28a02213c67b8a3d875ad9dbf300f88ce4`,
and the original six genuine imports. It closes the temporary overtime
reset import exposed by the preceding 193-input status snapshot.
The XIP crosswalk now binds 284/362 raw labels; 23 remaining labels
are in the literal/data tail and at most 55 are possible code labels,
including pinned CRC lower outside the component-file crosswalk.

The GPIO XIP interrupt service (0x10205ee0) and disable-trigger
(0x10206074) are now selected C. Stock literal-pool words at package
offsets 0x0f4ac, 0x0f574, and 0x0f658 all resolve the 32-entry,
12-byte callback table to SRAM 0x20027930. The ISR preserves the
32-pin pending snapshot, per-pin callback and acknowledgment order.
Disable-trigger clears the five native configuration registers and
resets that pin's three callback words. Its direction helper is already
selected source. The remaining enable-trigger function at 0x10205fb4
has an eight-way native jump table at 0x1020aca4, whose entries have
been extracted but need branch-body decoding before source selection.
`codec-gpio-irq-disable-round/receipt.json` is a coherent target PASS
with 195 distinct image-A source inputs, SHA-256
`df33e11020ea65f4803f2242db485c25b68f26380f534d082b316329ff34bb59`,
and six genuine imports. XIP raw-label bindings are 286/362;
23 labels remain in the literal/data tail and at most 53 are possible
code labels. Hardware IRQ execution and full SRAM initialization/
placement remain unqualified.

Direct C-SKY disassembly of 0x10205fb4..0x10206073 and all eight stock
table words at 0x1020aca4 close GPIO enable-trigger as a full C body.
Modes 1, 2, 3, 4, and 8 set the pin bit in offsets 0x2c, 0x28,
0x24, 0x14, and 0x18 respectively; modes 5, 6, and 7 only register
the interrupt. Every valid pin records the callback triple and
registers IRQ 1 with the relocated selected ISR symbol, including
out-of-range trigger modes. Pins >=32 return -1 before writes.
`codec-gpio-trigger-complete-round/receipt.json` is a coherent target
PASS with the same 195 source files, SHA-256
`6e8851aeb62594b4a4d92ec01c2ada7a6a690722cb29b66ec9559c390a98a8b3`,
and six genuine imports. XIP raw-label bindings rise to 287/362;
23 labels are in the data tail and at most 52 are possible code labels.
GPIO IRQ timing and callback execution remain unqualified on native
hardware.

The complete native UART async teardown at 0x1020854c is selected C.
It aborts transmit and receive for two existing channel slots, clears
their active words, then zeros three distinct SRAM regions in stock
order. Literal-pool words at 0x10208598/9c/a0 resolve the bases to
0x2002e360 (0x1c0 bytes), 0x2002ecc4 (0x14 bytes), and 0x2002e050
(0x2f8 bytes). These are runtime clear extents; they do not alone
establish source-owned startup allocation or initial contents.
`codec-uart-async-done-round/receipt.json` is a coherent target PASS
with 196 distinct image-A inputs, SHA-256
`f4f41d965ee80460f597dde81b4a295a0cdec4401aff49793351ff8d9de2de5f`,
and six genuine imports. XIP raw-label bindings are 288/362;
23 data-tail labels remain and at most 51 are possible code labels.

Direct C-SKY disassembly closes the two notification service bodies
0x1020979c and 0x102097c8. Both native literal pools resolve the shared
state base 0x2002e8f0. VAD notify checks its +0x34 halfword, prints the
exact stock `notify vad status\n` string at 0x1020b8f4, and calls the
already selected event prepare/dispatch providers. Poll re-reads the
+0x20 timestamp after the selected clock provider and raises GPIO 2
when the unsigned difference is at least 61, then zeros the timestamp.
`codec-notification-service-round/receipt.json` is a coherent target
PASS with 197 distinct image-A source inputs, SHA-256
`643ea91b4ba478d91f7c9821275dac22ea07cc8765aa9d3e2a405987e60027eb`,
and six genuine imports unchanged. XIP raw-label bindings rise to
290/362, with 23 data-tail labels and at most 49 possible code labels.
The runtime source/initial value of the shared state fields remains a
whole-image data/layout obligation.

The connected multiboot switch at native 0x10207a80 is now selected
C. Direct C-SKY disassembly fixes its SRAM selector address
0x20033ffc, sentinel 0xaabbccdd, exact stock log strings at
0x1020b148/0x1020b162, 16-byte cache-clean range, and reboot order.
It binds to already selected printf, resident cache clean, and reboot
bodies. The selector's initial production value and placement are
still product data/layout obligations, independent of this control
flow. `codec-multiboot-source-round/receipt.json` is a coherent target
PASS with 198 distinct image-A inputs, SHA-256
`ed36d95b5d373cb000c5a486a413f87a830777fc4ce3963879ee19ca8a12a281`,
and six genuine imports. XIP raw-label bindings are 291/362;
23 data-tail labels and at most 48 possible code labels remain.

The AOUT frame submission function at 0x102051a8 is now a selected
full C body. Direct native instructions prove the eight-byte frame
copy, signed frame-span division, ordered reads/writes at sample MMIO
0xa0b80000, conditional playback start through two selected helpers,
and zero-frame error return. Context byte +0x19 is a nonzero divisor
precondition present in stock behavior; the source does not invent a
fallback. `codec-aout-push-frame-round/receipt.json` is a coherent
target PASS with 199 distinct image-A inputs, SHA-256
`0e0b283dd59ccded14921f7346d1df3c88126c22f184abd4b83c3f01078ff267`,
and six genuine imports. XIP raw-label bindings are 292/362;
23 data-tail labels and at most 47 possible code labels remain.
Hardware frame transfer and the width precondition remain runtime
qualification obligations.

The AOUT channel selector at 0x1020502c now owns its exact 12-byte
stock lookup table at 0x1020a9a4 and three ordered register updates.
`codec-aout-channel-table-round/receipt.json` passed coherent target
compile/link with 200 distinct image-A sources, SHA-256
`b3af314cf1d10d9caca53d8b6536c6916a91a0d4abdb844f536265ad4fffdf78`,
and six genuine imports. Its XIP binding count was 293/362.

The adjacent 0x1020a910 dB table is now 37 semantic `(register code,
signed dB)` C records rather than an opaque payload. Encoding those
records as little-endian halfword pairs reproduced all 148 original
bytes exactly (SHA-256
`d576318ca73483bedc9e54e13f8d0ebd8cd62fddf92083c5c1514e833a58db99`).
Full set/get dB control flow at 0x10204f90/0x10204ff0 preserves
clamping, scan, register bit replacement, original requested value,
and the no-match fallthrough into the adjacent channel-table first
record `(0,1)`. `codec-aout-db-table-round/receipt.json` is the later
coherent target PASS: 201 distinct image-A sources, SHA-256
`b8a0fb0516d1146a9731ad3e78a6389ca57638495e7920f7b6369e0c4848544b`,
six imports. XIP bindings are 295/362; 23 data-tail labels and at
most 44 possible code labels remain. Final ROM table placement and
hardware behavior still need whole-image qualification.

Native AOUT hardware initialization at 0x10204f18 is now a selected
full C body. It enables clock gates 11/15, makes three ordered writes
to control +0x20, applies the special mode-2 +0x04 branch, waits
without a synthetic timeout for status bit 0x100000, acknowledges the
native register value, and enables bit31 of the base register.
`codec-aout-hw-init-round/receipt.json` is a coherent target PASS with
202 distinct image-A inputs, SHA-256
`e09e50efdb8bf43ba2b047b749e107dc7bdb81ad826fa1eb51f46f5d587f7ad5`,
and six genuine imports. XIP raw-label bindings are 296/362;
23 data-tail labels and at most 43 possible code labels remain.
The register wait and clock behavior have not been qualified on hardware.

The adjacent playback allocator 0x10205254 has a stock branch that
sets its context pointer to zero and then writes fields at offsets
0x14/0x18. This path requires an explicit native fault/precondition
assessment before C selection; a fabricated successful fallback would
change behavior. Its 0x10205374 child returns a proven fixed product
config pointer 0x20026c1c, whose producer/layout remain open.

The eleven public AOUT table dispatch bodies at 0x10205374 and
0x1020537c..0x10205599 are now C in `resident_xip_aout_dispatch.c`.
They retain the active table word at 0x2002734c, exact error string,
stock slot offsets, zero-slot return, and unaltered argument registers.
`codec-aout-dispatch-round/receipt.json` is a coherent target PASS with
203 distinct image-A sources, SHA-256
`527343dc726b9c7597ace53432904da11b6fca86db4006f5e79bd5be5d7c960b`,
and six genuine imports. Runtime function-pointer calling and table
placement are still unqualified.

The full native playback allocator 0x10205254 is C in
`resident_xip_aout_alloc_playback.c`. Direct C-SKY disassembly confirms
the three-part context guard, 36-byte clear, byte active flag, selector
call, ordered AOUT MMIO writes, IRQ13 registration, and return address.
On guard failure stock sets r4 to zero and stores at absolute addresses
0x14, 0x18, and 0x30 before the MMIO path. The C candidate retains
these volatile numeric-address stores. Whether that path faults or writes
to mapped hardware remains an unresolved CPU/memory-map runtime question;
the source does not substitute a success return. The comparison is against
the full 32-bit mode even though the context field is one byte. The first
allocator build snapshot (`codec-aout-allocator-round/receipt.json`) is a
coherent target PASS at 204 inputs, SHA-256
`4ebedcb1bbd31958497031bb0eaa6a1f05d6a1370b802d374004c1843efac084`;
it predates the full-width comparison correction. The corrected source
is in the next build snapshot.

Native stage2 SRAM 0x10026bc8..0x10026c1b is a 21-word AOUT operation
table, copied or aliased to the 0x20026bc8 address used by XIP calls.
`verify_aout_product_table.py` confirms all 21 original words and
SHA-256 `b5466e260001986f04418e55cdc810ea9654f2f6b1c3ef24dbd95af7b3995f8a`.
`resident_xip_aout_product_table.c` expresses each nonzero word as a
typed relocation to an independently selected C provider; slot twelve
is the exact zero. Its 84-byte C struct and section are source owned,
while final SRAM placement and 0x1002/0x2002 alias or copy semantics
remain open. The adjacent 52-byte context record and 88-byte config
record are still product initialized-data obligations.

The corrected combined `codec-aout-table-final-round/receipt.json` is
a source-coherent target PASS with **205 distinct image-A inputs**,
SHA-256 `5fa4a8ec146a26edb31c8736ab50861afa9798eac3b8b74790db5b0b9c8e5c5a`,
and the same six genuine imports (`__fe_getround`,
`__fe_raise_inexact`, compact IRQ entry, console port, ambient KWS task
words, and UART channel storage). Target ELF inspection shows section
`.gx8002.sram.aout_operations` has size 0x54 and alignment four,
with exactly 20 `R_CKCORE_ADDR32` provider relocations at the stock
nonzero word offsets. The zero slot at +0x30 has no relocation. XIP
address bindings are **308/362**; 23 unbound labels are data-tail and
at most **31** remaining labels may denote executable code (including
the pinned CRC body tracked outside this component crosswalk). SRAM
retained true-body coverage remains 123/124, with the compact IRQ ISA
frontier open. This is C candidate compilation and relocation identity,
not native runtime equality or a complete loaded image.

The neighboring stock AOUT context at SRAM 0x10026b94..0x10026bc7
is 52 bytes: one pointer to the exact XIP string `"0 route play"`,
followed by 48 initialized zero bytes. Consumer accesses support typed
fields for allocated flag, owner word, mode, mute/dB, frame range,
callbacks, and config pointer. The 88-byte config record at
0x10026c1c..0x10026c73 has eight nonzero initialized words, at offsets
0x04, 0x1c, 0x34, 0x38, 0x40, 0x44, 0x4c, and 0x54; all others are
zero. `resident_xip_aout_runtime_data.c` owns these as two typed C
records and a route string. `verify_aout_context_config.py` independently
checks the native ranges and exact initialized values. Its final XIP/SRAM
placement and 0x1002/0x2002 alias remain open.

Four additional complete application XIP bodies at 0x10208d98,
0x10208dcc, 0x10208dec, and 0x10208e20 are C in
`resident_xip_app_audio_gpio.c`. The audio range callback preserves
unsigned wrap arithmetic and the two alternate frame ranges before
forwarding to the selected AOUT push wrapper. GPIO suspend/resume and
event callbacks preserve exact stock format strings, pin 6, trigger
registration, timer start, and the 2000 state write. Runtime state
0x2002e8c4 is a genuine separately initialized product contract. XIP
bindings rise to 312/362; 23 remaining data-tail labels and at most 27
possible code labels remain. Target build receipt is pending below.

`codec-aout-context-app-gpio-round/receipt.json` is now a coherent
target PASS with **207 distinct image-A inputs**, SHA-256
`a1bf04026b9ff86fdb551bad4107137c22d7e3e8f7c05be213e909c0d77466b7`,
and the same six genuine imports. Target ELF inspection confirms an
88-byte AOUT config section whose raw bytes have exactly the stock
SHA-256 `1d5c6201e8d1d2cc00d6fa541ac409a9b36e2ba9bee03073e35edf914a6c6a84`;
the context section is 52 bytes with one `R_CKCORE_ADDR32` route-string
relocation at offset zero, and the route section is 13 bytes. These
prove source-owned initializer content and relocation shape, while
final address placement and native execution remain unqualified.

The remaining image-A SRAM compact IRQ entry at 0x10025574 is now
resolved at source and byte level. The earlier `fr16-fr19` operand was
a decoder interpretation error: the stock opcode pair
`f4ee3400`/`f4ee3000` assembles as `fstms/fldms fr0-fr7` under the
selected `ck804ef` target. With only that operand correction, the
entire named-instruction IRQ assembly, including its literal pool,
is **80/80 bytes exactly equal** to stock range
0x10025574..0x100255c3 (SHA-256
`4603c68912b68c0dc567ddcea48266e00421c600eec7ac5c0e8db8a55dfc9288`).
`irq-compact-source-receipt.json` records the comparison. This supersedes
the earlier architecture mismatch hypothesis; native runtime and final
vector placement still require qualification. The selected graph build
including this source is pending below.

Two connected app setup bodies, 0x10208e4c and 0x102096fc, and the
11-registration command builder 0x10209258 are now C candidates.
The UART setup's source-owned four-word descriptor exactly matches
stock XIP 0x1020b688..0x1020b697, SHA-256
`f5cd8f6ebe63cf67229afeed7c2ce254291d7a23d98c97a68c2b38d9353d6f3c`.
All 11 command names and IDs are native attributed; two 32-byte
payload descriptors retain the product address 0x2002e8f0. The builder
returns the last registration result as the native ABI does. The
callback 0x10209430 remains an actual connected body import. XIP
bindings rise to 315/362, 23 data-tail labels, at most 24 possible
code labels; the coherent corrected build is pending below.

`codec-irq-app-commands-corrected-round/receipt.json` now passes with
**210 distinct image-A inputs**, source snapshot coherent at link,
SHA-256 `d19ef01fd5e3d976996843281164a03e49b0b2d83eb0a0414e8c3de9c9e56a76`,
and six genuine imports: the two floating-environment contracts,
app command callback 0x10209430, console port, ambient KWS task words,
and UART channel storage. Compiler-generated `memset` was eliminated
by explicit calls to the selected 0x102099cc provider. The selected
IRQ object's `.text` SHA-256 is the exact stock 80-byte hash above.
All **124/124 identified true image-A SRAM bodies** now have selected
C/ASM candidate source. This closes the retained SRAM body census,
not the whole image's initialized data/scatter, runtime, or separate
loaded-stage obligations.

The native 0x10208e80 mic-buffer calculation and 0x1020913c I2S stop
body are selected C. The first preserves the unsigned frame-span
arithmetic, divisor preconditions, and address outputs; the second
preserves the exact stop/log/padmux/free/exit/state-clear sequence.
`codec-mic-buffer-i2s-stop-round/receipt.json` passes with **212 distinct
image-A inputs**, coherent at link, SHA-256
`e611838b225956cbd6d876225f4bcda673a86a284b23083afa004facf6112897`,
and the same six genuine imports. XIP attribution is 317/362, with 23
data-tail labels and at most 22 possible code labels. Runtime
equivalence of these bodies is still unqualified.

The complete native start-I2S body 0x10208ff0 is now selected C,
including its active guard, old-handle cleanup, 7..10 padmux,
clock/AOUT setup, three stack descriptors, exact stock log strings,
and 0/-1 return. Direct ISA and literal review plus isolated CK804EF
target syntax compilation passed. The coherent selected
`codec-start-i2s-round/receipt.json` passes with **213 distinct image-A
inputs**, SHA-256
`de8d73f874c0c9c5b424dad01ab5236a9ac50c5457c54bec9a6f3f3a3cd8130c`,
and the same six imports. Attribution was 318/362, 23 data-tail, at
most 21 possible code labels at that snapshot.

The adjacent native sample-event 0x10208f04 and I2S request-tick
0x102091bc are now selected C candidates. The event source preserves
the context status notification, 100/101 wake dispatch, and guarded
91 first-frame path with both mic-buffer queries and exact range push.
The tick source preserves request state, lock/start and stop/unlock
branches, signed 10-count timeout, and exact logs. Both pass isolated
CK804EF target syntax checks; the selected coherent receipt is pending.
Attribution is **320/362 XIP**, 23 data-tail and at most **19 possible
code labels**. Native runtime behavior remains unqualified.

`codec-app-audio-event-tick-round/receipt.json` passes with **215
distinct image-A inputs**, coherent at link, SHA-256
`2356cd826ff56c71acb44a732225868561f327b1f00ba6c678bceea2b1509180`,
and six unchanged imports. The next selected source round corrects two
issues found during direct native review: I2S tick now declares its
void stop callee correctly; audio channel field 0x102049b0 now takes
an integer register index and accesses `0xa0a00000 + ((index+10)<<2)`.
The former selected pointer interpretation would have been invalid
for native caller index zero. The remaining operation preserves the
native six-bit insertion at bits 10..15.

The formerly imported app command callback 0x10209430 and stateful
tokenizer 0x1020995c are now selected full C candidates. The callback
preserves all eleven independent command branches, exact stock logs,
version request byte setup, gain check, GPIO/padmux operations, and
request descriptor writes; tokenization uses the native SRAM state
cell 0x2002e934. Isolated CK804EF target syntax checks passed. The
selected coherent receipt is pending. The XIP crosswalk is **322/362**,
with 23 data-tail labels and at most **17 possible code labels**.
Runtime, product data initialization, and final placement remain open.

`codec-app-command-callback-native-round/receipt.json` passes with
**217 distinct image-A inputs**, coherent at link, SHA-256
`3f373ed1a9609e579329aa4472e915694cb51f6a08c2006c9e6de0e31dc7587b`.
The app-command callback import is now closed. Five genuine imports
remain: `__fe_getround`, `__fe_raise_inexact`, the console port cell,
ambient KWS task words, and UART channel storage. This is link/source
evidence, not native execution equivalence.

Native review also invalidated the retained 0x10209c74 "UART DMA"
catalogue label. Instruction 0x10209c70 falls directly through into
0x10209c74, and the continuation branches back within the 0x10209aa4
unsigned division algorithm. It is an interior code label, not an
independent function. The crosswalk now records this separately.

Two further native arithmetic bodies are selected C: 0x102098b4
unsigned 64-by-32 quotient/remainder and 0x1020a528 `__muldi3`.
Each compiled to an isolated CK804EF object with no unresolved symbol;
deterministic host arithmetic checks passed 100,005 and 100,006
cases respectively. The original stock instruction ranges were
reviewed for ABI and arithmetic, but stock execution equality remains
unqualified, particularly divisor-zero behavior. Four more exact
revision-pinned LLVM compiler-rt C algorithms (`comparedf2`,
`fixdfsi`, `subdf3`, `udivdi3`) are selected alongside the five earlier
pins. This is a semantic-library candidate with C source provenance;
native soft-float ABI and IEEE equality require separate proof.
The crosswalk is **333/362 labels**: 324 component C/ASM candidate
bindings, nine pinned-library algorithm candidates, 23 data-tail
labels, one interior false function label, and at most **five possible
code labels** still unbound. One of those five, 0x102097f4 CRC, has a
previously pinned source body outside this component crosswalk. The
new selected arithmetic/library build is pending.

`codec-runtime-arithmetic-source-round/receipt.json` now passes with
**223 distinct image-A inputs**, coherent at link, SHA-256
`90e0be958dbdd4cc37ac817f73c94ee85071f66d375ef03c7da1fb4a03dcaad8`,
and the five unchanged genuine imports. The reproducible host
`verify_runtime_arithmetic.py` receipt pins the two C source hashes and
records 100,006 multiplication and 100,005 nonzero-denominator division
cases. Native execution and pinned soft-float ABI remain unqualified.

Two more internal runtime bodies, native 0x1020a704 unpack-double and
0x1020a7e8 compare-parts, are now selected C. Direct ISA inspection
corrected the retained decompiler's missing 20th fraction bit, the
normal mantissa implicit bit, and quiet/signaling NaN classification.
`verify_fp_parts_host.py` checks 100,008 IEEE class/normalization bit
patterns and 100,007 pairwise ordering cases against independent host
expectations; its receipt records the current source hash. Isolated
CK804EF target compilation has no unresolved symbols. The selected
coherent build is pending. The XIP crosswalk is now **335/362**: 326
component-source bindings, nine pinned-library algorithm candidates,
23 data-tail, one interior false label, and at most **three possible
code labels**. Of those, 0x102097f4 CRC has previously pinned source;
0x10209dd8 fpadd-parts and 0x1020a574 pack-double remain true direct
source reconstruction work. Whole Codec source/data/scatter/runtime
and image-B completion remain open.

`codec-fp-parts-source-round/receipt.json` passes with **224 distinct
image-A inputs**, coherent at link, SHA-256
`c4cd748c95e35a5ae97d0775f38f6e40686044a0465e0a82e33dbc095062cad5`,
and five unchanged genuine imports. The selected graph now includes
0x1020a704 unpack and 0x1020a7e8 compare, while runtime/ABI equality
remains unqualified.

Native 0x1020a574 pack-double and 0x10209dd8 fpadd-parts have now
been selected as C candidates. The former preserves normal/subnormal
round-to-nearest-even, zero, infinity, quiet-NaN, and overflow cases.
The latter preserves special-value early returns, the source-owned
five-zero-word canonical NaN object at stock 0x1020bd08, sticky
alignment, sign-sensitive subtraction, and normalization. Isolated
CK804EF objects each have zero undefined symbols. Reproducible host
receipts at current source hashes record 100,008 unpack/pack
roundtrips, 20,000 exact-rational rounding cases, and 99,909
non-NaN IEEE addition matches. Stock native execution and soft-float
ABI equality are not established by those host checks.

The 256-byte stock division lookup 0x1020bd1c is also selected as a
source-owned C initializer generated from `byte_index.bit_length()`;
the receipt proves all bytes and SHA-256
`14a5d850c255623f9472e3c650abce0c78d32f0276b315b3a276a0462d97a1ac`.
The pinned NationalChip CRC table has a separate 1024-byte exact
algorithmic receipt. `data-tail-ownership.md` classifies all 23
post-code raw labels, including string-boundary aliases and the flash
dispatch table whose interior branch relocations remain a layout gap.
The retained XIP **seed-label** crosswalk is now **338/362 source
candidate bindings**, 23 data-tail labels, one proven interior false
function label, and **zero possible unbound code labels in that
catalogue**. This census does not prove all executable XIP bytes or
source scatter/layout coverage. The selected 227-input Codec receipt
is now terminal PASS: `g2/build/c-firmware/20261011/codec-xip-seed-source-census-round/receipt.json`
records 227 distinct image-A source inputs, a coherent source snapshot
at link, output SHA-256
`06ebb482748cb7ffe936f3346bb1f0a20eefd8db55b89c93447d59953f460e55`,
and five genuine imports (`__fe_getround`, `__fe_raise_inexact`, console
port storage, ambient KWS task words, and UART channel storage).
`candidate_compilation_passed=true`; `source_complete=false`.

`audit_xip_range_gaps.py` adds a byte-range guard to this label census.
The retained function-range union covers 28,554 of the 30,886 bytes in
0x10203004..0x1020a8aa; there are 267 gaps totaling 2,332 bytes.
Largest reviewed gaps include an unsigned-division continuation
(0x10209d02..0x10209d8c), literal pools, and branch case blocks that
are semantically represented in selected C. The range gaps are not a
missing-function count. Their literal/branch relocations and final
placement require whole-image source/layout qualification.

The five remaining link imports are genuine boundaries. The two
`__fe_*` hooks arise from the pinned compiler-rt FP algorithm. Its
`fp_mode.c` would supply nearest rounding and suppress the inexact
exception, but the GX8002 FPU/environment policy is not established,
so that default is not selected. The console-port cell and two
0x80-byte UART channel records have native typed consumers; exact SRAM
object extent, startup initialization, and scatter ownership still
need proof. The KWS loader reads ambient task words from the native
stack; no source producer or valid default has been established.

The two initialized UART channel records now have a shared typed C
definition and XIP consumers use that symbol. The target section is
writable and its 256 bytes still equal stock exactly (SHA-256
`63c9aeaf67fd2385d2b68b3c18ae2e871d7d94392b1f347ef23a49a2fc81fde2`).
The coherent `codec-uart-sram-owner-round/receipt.json` passes with 227
inputs, SHA-256
`27958e259b7245760f872b85270d922a6ee57980fa2a448b3f5fc31e89c9c578`,
and four remaining imports. Runtime 0x20026a94 alias placement is not
proved by this relocatable link.

The stock SRAM span 0x10026c74..0x10026d7c has now been reconstructed
field by field: two receive words, two 88-byte keyword descriptors,
sample registration with eight pointer fields, and the initialized
32-byte request. `verify_sample_app_tail_semantics.py` checks all 264
bytes against stock, SHA-256
`334e9013b3a6e11393389efc5d871d274b33fa4290f7df4273a35218a790d100`.
`resident_sample_product_data.c` expresses these values as C fields
and real function/name relocations. Its isolated CK804EF object compiles;
`verify_sample_tail_target.py` confirms 272 scalar/string bytes in
eight sections and nine pointer relocation offsets. The selected full
Codec build with this additional source is pending. Final SRAM scatter,
XIP placement, and runtime equality remain open.

`codec-sample-product-data-round/receipt.json` then passed with 228
distinct image-A inputs, source snapshot coherent at link, SHA-256
`a441f744dc7941736a4c8514b0ffbd7249b4fb96e81a42f97b0d27e01248af88`,
and four unchanged genuine imports. `source_complete=false`.

The broader SRAM gap audit shows 122 retained function-range gaps
totalling 3,403 bytes out of the 14,716-byte loaded image. The gaps
mix initialized data, vectors, literal pools, branch case blocks, and
unseeded code. It exposed a real board-state extent error: native XIP
audio code reads and writes through byte +0xec of the board object,
whereas the previous C initializer only covered 40 bytes. Its source
now owns the full mutable 240-byte 0x100269a4..0x10026a94 record;
all target section bytes match stock, SHA-256
`e1d1077d066d53c1e39bcefca3ec0294d43ace92ffc1a986d2a432cd931dde2e`.
The board getter now relocates to that source symbol.

The flash runtime source initializer 0x100264e4..0x1002657c is also
represented in C: an exact 32-byte mutable state object and a 30-slot
API table whose seven zero slots are exact and whose 23 function slots
are relocations to the selected flash bodies. Native dispatch reads
API offsets +4, +0x34, and +0x58; four other native callers use its
0x20026504 runtime alias. The console-port word at 0x2002731c is now
a source-owned four-byte NOBITS object inside the authenticated startup
BSS clear span. `verify_board_flash_data.py` records these target
checks; final exact address placement, data copy, and runtime behavior
remain unqualified. A coherent selected build for this chunk is pending.
Native table slot zero points to 0x1002443c; two existing C callsites
invoke it through a four-register callback type while its selected
provider is declared `uint32_t(void)`. The machine may ignore surplus
register arguments, but this C function-pointer mismatch needs a native
ABI qualification before runtime-equivalence admission.

`codec-board-flash-bss-round/receipt.json` is now terminal PASS with
230 distinct image-A inputs, source snapshot coherent at link, SHA-256
`d00675f1ec394e16812c9407597693f3cadf3ccb021ab69bb6b8789c20ad5baf`,
and three genuine imports: `__fe_getround`, `__fe_raise_inexact`, and
`gx8002_xip_kws_ambient_task_words`. The console storage import was
closed by the proved BSS object. `source_complete=false` remains correct.
The named data sections form one contiguous, source-owned 2,200-byte
initialized tail at 0x100264e4..0x10026d7c, in addition to the
256-byte vector source at 0x10023400. Section adjacency and runtime
alias placement have not yet been achieved by a final linker map.

`audit_sram_range_gaps.py` now records each of the 122 function-range
gaps by stock hash and adjacent retained function. Named source-data
intervals account for 1,707 of the 3,403 gap bytes. The residual 107
fragments/1,696 bytes include 53 address-literal-word pools (382
bytes), 29 zero alignments (58 bytes), and 25 mixed/nonword/scalar
fragments (1,256 bytes) that need direct native classification. The
largest are a clock/platform jump-table and constant pool at
0x100253b8 (244 bytes), the already sourced unseeded TWS buffer
updater at 0x100260e4 (212 bytes), and case-block regions next to
selected platform/flash functions. Residual gap bytes are not a
missing-function count or proof of final source layout.

The remaining 18 mixed residual fragments were then individually
associated with their native neighboring startup, flash, platform,
clock, or scalar-literal source candidate. Together with the seven
large regions, all 25 mixed fragments/1,256 bytes now carry explicit
candidate attribution in `sram-function-range-gap-receipt.json`.
This closes the range-gap *triage* queue, not code/data identity,
instruction equality, interior jump-table relocation, or final loaded
layout qualification.

`codec-data-reloc-final-round/receipt.json` is terminal PASS for the
230-input image-A candidate, source coherent at link, output SHA-256
`4bf4688c38c3f7f4c2ce5629283f357203b050f8b60ca5f5ccd8913cb949e934`.
It includes the source-owned UART receive configuration address binding
and leaves the same three genuine imports. After that build, three
unproven keyword-record semantic field labels were changed to neutral
offset labels (`field_28`, `field_48`, `field_54`). An isolated CK804EF
recompile of the changed initializer passes `verify_sample_tail_target.py`:
272 exact scalar/string bytes across eight target sections and nine
pointer relocations. The metadata rename is not part of the preceding
full-link source snapshot; the next integrated receipt must capture it.
No final placement/scatter copy or runtime equality follows from this
isolated object check.

The optional `--codec-placement-check` is now wired into the selected
Codec builder. It invokes `image_a_known_data.ld` and
`check_known_data_link.py` only after the image-A relocatable link
passes. The gate pins and checks 24 named sections: the 256-byte vector,
23 contiguous initialized sections totaling 2,200 bytes, and the
four-byte console BSS word inside the native clear span. The full
`codec-placement-gated-round/receipt.json` is terminal PASS with 230
source inputs and source snapshot coherent at link, including the
neutral keyword labels (source SHA-256 `e68225734c47a8204173bfcaee09491a5077101c6bbd388162a61180a3689adc`).
The image-A candidate SHA-256 remains
`4bf4688c38c3f7f4c2ce5629283f357203b050f8b60ca5f5ccd8913cb949e934`;
the isolated placed object SHA-256 is
`93cd57b5da8df1d9de19f4e360286345d8bc72599f9e539c5cd5c070a68074f2`.
The three true imports are unchanged. Image-B's separate candidate
also compiled coherently in this run. The known-data placement gate
does not establish the final executable/XIP map, relocated pointer
values, hardware alias, package copy, or native runtime equality.
## Image-A FENV, shift lowers, and XIP placement probe

The selected image-A candidate now compiles `resident_fp_environment_csky.c`
under `-mcpu=ck804ef -mhard-float` using pinned C-SKY glibc FPUv2 register
semantics. Target disassembly confirms a live `mfcr ..., cr<1, 2>` rounding
read and runtime `fdivs` inexact operation. The pinned LLVM 20.1.8
`ashldi3.c` and `lshrdi3.c` are source-owned compiler lowers, each 44 bytes
when isolated at O2 with no further imports. Their authenticated URLs and
SHA-256 hashes are recorded in the existing LLVM provenance file. Real-device
directed rounding is still unqualified.

`g2/build/c-firmware/20261011/codec-fenv-shift-coherent-round/receipt.json`
records a terminal combined Codec build: image-A 233 coherent selected inputs,
target compile/link PASS, candidate SHA-256
`87a041c4015726b0d137e22d12ab25a7211526937c08580d3b271b6ad485042f`;
24 authenticated data placements PASS. The sole image-A unresolved symbol is
`gx8002_xip_kws_ambient_task_words`, a genuine runtime/product input.
Separate image-B captured 226 coherent inputs and linked SHA-256
`d6a7eb922f6c5a4468cb1305c741142e2bf792fa4acf909c47e43283c507a0c5`;
its nine genuine inputs remain explicit. Both subimages remain
`source_complete=false`.

The fresh image-A XIP audit is 249 direct named slots that fit, 62 stock
fixed-slot overflows totaling 1,150 bytes, and 28 labels without a direct
suffix symbol (27 mapped to other source functions, one false interior label).
A bounded relocatable packed link places all 311 direct source symbols plus
two additional XIP functions in 26,692 bytes starting at `0x10203004`, leaving
4,194 bytes before native code end `0x1020a8aa`. Ten other authenticated
helper bodies already total 4,208 bytes at O2; source placement of the rest,
literal data, linker branch reach, outside-stage references, loader copy,
`0x1002`/`0x2002` alias behavior, and native runtime remain open. An isolated
O2/Os target probe reduces those ten body sizes to 3,536 bytes with Os, but
does not qualify a final link or hardware behavior. The reproducible audits
and exact symbolic pointer evidence are in `xip-relocation-candidates.md`.

The subsequent `codec-xip-unbound-os-round/receipt.json` is the terminal
source-coherent size-policy checkpoint. Image-A has 233 inputs, target
compile/link PASS, candidate SHA-256
`3060f87ab1719228b1f58fb6ebe8ae8170934d17ee274f395ea1de047e2e0911`;
all 53 SHA-guarded `-Os` source selections applied with zero stale inputs,
and the 24-section known-data placement check passed. Its only unresolved
symbol remains `gx8002_xip_kws_ambient_task_words`. Separately loaded image-B
has 226 coherent inputs, linked SHA-256
`aa9ae4ab78a1e01ad9825b239c352741703c269e0b06a401acba1fab26a83deb`,
and nine genuine imports. Both loaded stages remain source incomplete.

The new selected image-A object retains 249 fixed-slot eligible direct
functions, 62 overflows, and 28 no-direct suffix labels. Its packed direct
XIP probe is 26,632 bytes. `audit_xip_packed_lower_bound.py` additionally
counts 4,020 bytes of 18 mapped helper bodies, 3,848 bytes across 59 named
XIP read-only sections, and 44 bytes of sample strings: **34,544 bytes of
the 36,484-byte native XIP payload**, leaving 1,940 bytes before remaining
code/data/alignment/veneer obligations. This is 1,152 bytes below the prior
candidate's same bounded floor, not proof that the final payload fits.
`kws-ambient-task-words-boundary.md` records native instructions proving no
local write to task words 0, 3, or 4 before the full 32-byte child copy;
the caller does not supply them. No default-value C provider is selected.
