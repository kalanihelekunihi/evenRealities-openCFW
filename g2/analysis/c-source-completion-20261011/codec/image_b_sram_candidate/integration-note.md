# Image-B SRAM candidate integration

Image-B is a separately loaded GX8002 program with the pinned 82,060-byte
`binh_b_stage2.bin` corpus (SHA-256
`d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`).
It must have its own C-SKY CK804EF hard-float relocatable result under the
Codec receipt. Do not append its units to image-A's `source_paths` or link its
object into image-A's `candidate.o`.

The reproducible subbuild is:

```sh
python3 g2/analysis/c-source-completion-20261011/codec/image_b_sram_candidate/build.py \
  --output <firmware-c-output>/codec/image-b-sram
```

Its `receipt.json` binds every source and object hash, linked output hash,
architecture, and true undefined symbols. A distinct
`codec.image_b_sram_candidate` receipt field can contain that receipt and the
subbuild command status. `source_complete` and
`data_and_final_layout_complete` must remain `false`. The current selected
subgraph compiles and links with three true imports; image-B reset/data/layout and
117 retained catalogue functions outside this candidate remain unqualified.

The source manifest is the explicit `SOURCES` array in the subbuilder, currently
111 units, including 100 under `g2/components/gx8002/image_b_sram_candidate/` and
11 pinned LLVM compiler-rt sources. It is not a
filesystem glob. The subbuilder uses the same pinned C-SKY toolchain and Docker
image as image-A but compiles and links independently.

The connected audio registration round is recorded in
`registration-graph-receipt.json`: catalogue coverage is 157/288; three
additional callback bodies outside the catalogue are source-owned. The
target link retains only the two explicit floating-point environment imports.
The subsequent clock lookup, UART width, boot slot, and 16-record callback
table round brings catalogue coverage to 161/288, with bounded host checks
in `verify_uart_width_code.py` and `verify_audio_registration_table.py`.
The callback-table dispatcher and pinned CRC sources are recorded in
`dispatch-crc-receipt.json`; they raise catalogue coverage to 163/288 and add
one uncatalogued native callback consumer. The full 256-word CRC table matches
native initialized data exactly. Bounded host checks cover 108 CRC vectors and
four dispatcher cuts; the registered callback success path remains open.
The callback table and `0x2002cb80` heap-end word still need source-owned
final SRAM placement, and the mode at `0x2002cb84` has no attributed boot
initializer. The new table at `0x2002cf30` and boot marker at `0x20033ffc`
likewise require final SRAM ownership and runtime validation.

Typed flash profile configuration in backup_flash_profile_data.c has a field-level native payload check in flash-profile-data-receipt.json. Its runtime placement under the candidate DRAM mapping remains open.

The UART audio and DMA chain round is recorded in `uart-dma-chain-receipt.json`.
Five further catalogue bodies and two native callback/ring bodies are source-owned,
raising catalogue coverage to 168/288. The 105-unit target archive has linked
SHA-256 `ec44bad2687c25bda22949225aacf88f1463d4aded98be5e6872ec590e07c87a`;
all recorded source hashes match current files. Six host ring writer state cases pass.
At that checkpoint, the remaining imports were TX-complete callback 0x1000afc4, the native
out-of-domain DMA direction stack word, and two floating-point environment
primitives. Callback/ring SRAM placement and physical UART/DMA behavior remain
open. The 0x1000acbc DMA completion wrapper re-enters the segment sender with
the native null availability pointer.

The full native TX-complete state machine at 0x1000afc4 is now source-owned
(`uart-tx-complete-receipt.json`): header, payload, CRC, and six-record
completion dispatch. Seven bounded host state cuts pass with address rebasing
and stubbed children. The 106-unit C-SKY archive links with SHA-256
`c7b9cafdffcb20320355a81c2f2baa12780914b508de648447140a1d36fb9a79`
and only two FP environment plus one native ambient descriptor import.
Catalogue coverage remains 168/288. The six 16-byte callback records at
0x2002d148 require source-owned initialization and final SRAM placement.

The symmetric UART receive DMA submit and apply bodies at 0x100047a4 and
0x10004188 are recorded in `uart-rx-dma-receipt.json`. Four bounded host
cases cover allocator failure, ports 0 and 1, and the native invalid-port
return. The 108-unit C-SKY archive links with SHA-256
`0d13ac8094297d485f450bc1126d1d1214bd2579b4c1d64de0252b5918652fd8`;
all source hashes match. Catalogue coverage is 170/288, leaving 118 bodies
outside the candidate. Native receive packet handler 0x1000ad60 is the next
connected full-body frontier.

The complete receive packet body 0x1000ad60 is source-owned in
`uart-rx-packet-receipt.json`, with three bounded address-rebased host cuts.
The 109-unit C-SKY archive links with SHA-256
`e38d189b8c96ee9885f00a9517bec32a98ba1fae4f6219970d1e8e352b4ce68f`,
with current source hashes matching the receipt. Catalogue coverage is
171/288, leaving 117 outside. RX DMA callback 0xaf94 and RX IRQ callback
0xb198 are genuine exposed code contracts. Native 0xaf94 passes null
input/availability pointers, so address-zero behavior remains explicit.

The native RX DMA completion callback 0xaf94 and full RX IRQ parser 0xb198
are now source-owned (`uart-rx-callback-receipt.json`). Four bounded IRQ
state cuts pass with host SRAM/pointer rebasing, in addition to three packet
cuts. The 111-unit C-SKY archive links with SHA-256
`0d880ccd716a179d86cfc4a5cafabd2cdcc56130c7e46a02a1b2d9476abd94ad`;
all source hashes match. True imports are two FP environment primitives,
the native out-of-domain TX DMA direction word, and the native word-at-zero
read reached through the RX DMA callback. No address-zero value is supplied.
RX scratch/header-progress/ring/registration/callback SRAM ownership and
physical IRQ behavior remain open.

The connected UART lifecycle, register-apply, and IRQ-source round now owns
native 0x1000b5f8/0x1000b6f0/0x1000451c/0x100043a4 and uncatalogued
0x1000ace8/0x1000ad10/0x10004250. It preserves the exact two-port
abort/configure sequence, UART register masks, status-bit service order,
and native callback record arguments. `verify_uart_apply.py` passes two
rebased register cuts; `verify_uart_irq.py` passes five callback/byte-transfer
cuts. The native zero-address read and invalid-port ambient descriptor
remain explicit imports, as do two FP-environment helpers. C-SKY binary64
rounding/exception behavior and physical IRQ interleavings are not proven.

The next 119-unit source-coherent C-SKY archive also owns the 0x1000bde8
UART ring enqueue literal and 0x1000b91c denoise allocation/record entry.
`verify_denoise_state_init.py` passes two rebased allocation/result cuts.
The archive receipt is `build-uart-ring-denoise-round/receipt.json`, linked
SHA-256 `9ef45e3b10a24688f49ba0ac31ea8b86882e40f0c8c7dd6bbd6bd0a4b934ac45`;
119/119 units compile, all source hashes match, and `ld -r` passes. The
new genuine descendant is IMCRA state initializer 0x1000e384; its retained
decompiler graph truncates at a bad-data edge, so no completion is inferred.
Catalogue coverage is 177/288, leaving 111 outside this separate image-B
candidate. Source-owned SRAM initialization, final scatter/placement,
runtime FP/heap behavior, and live hardware qualification remain open.

The IMCRA follow-on uses actual C-SKY ISA past the retained decompiler's
false bad-data stop. `backup_imcra_state_init.c` implements native
0x1000e384 and size helper 0x1000e314, including 25 checked regions,
the two ordered 257-word initializers, 512 window samples, compensation,
zeroing and error/log paths. Four host-rebased layout cuts pass. The
0x1000ee64 cosine lookup uses a typed 513-float sine table generated from
`sin(2*pi*i/512)`: 511 words match directly and two native zero-crossing
residuals are explicit. The target-compiled 2052 table bytes match stock
exactly; eight bounded host angles pass. The source IEEE `__extendsfdf2`
helper passes 9967 finite bit-pattern comparisons. Native 0x100100a4 is
an authenticated call-through to the genuine 0x100100bc power core.

The final 123-unit C-SKY receipt is `build-imcra-final-round/receipt.json`:
123/123 compile, `ld -r` PASS, all source hashes current, linked SHA-256
`630a2bbbac50e45f7a4dad015005818a8fe36a46946979ccbcb0faf60bfabc97`.
Catalogue coverage is 181/288, leaving 107 outside. True imports are
the power core, two FP-environment helpers, the native word at address
zero, and the invalid-port ambient UART direction. Full FP exceptional
behavior, power core, initialized SRAM, final scatter, and live hardware
remain open.

## fdlibm connected image-B round (2026-10-11)

Separate image-B source list has 118 candidate C units plus 11 pinned
compiler-rt units, 129 total. `build-fdlibm-round/receipt.json` is the
source-coherent C-SKY compile/relocatable-link receipt; linked SHA256
`f2749202bcbf2aa938c479d2ab3e588eaa890db7c3ef1775a0ce20da18eb812f`.
New source-backed catalogue entries: power core `0x100100bc`, sqrtf
`0x10010bcc`, quiet NaN `0x10011298`, fabsf `0x100112c4`, logf
`0x10010768`, logf entry `0x100100ac`. Additional native scalbnf
`0x10011194` was absent from the 288-lead catalogue but is source-owned.
Coverage is 187 of 288 catalogue leads by the current address crosswalk,
with 101 outside; whole-body, initialization, scatter and physical runtime
qualification remain open. Four true imports remain, listed in the receipt.

## IMCRA block-scale round (2026-10-11)

Separate image-B source set now has 119 candidate units plus 11 compiler-rt
units, 130 total. `build-imcra-block-round/receipt.json` is source-coherent
and target link PASS, linked SHA256
`b60b2d601c114b7f6249fe026a118a23ca1c74198422475880ee716725139a62`.
New native-catalogue bodies `0x1000e28c` and `0x1000e2c4` have 9/9 bounded
host branch fixtures. Current address crosswalk is 189/288 leads, 99 outside.
Four genuine imports remain as listed in this round's receipt. Full
image-B data, reachable body equivalence, scatter, and hardware proof remain
open.

IMCRA constructor round: `build-imcra-substates-round/receipt.json` (134 CK804EF units; linked SHA256 `33d597a2d2a86222c9adf47909c2601f7660c31c2deeba9eee284f36caee1d86`; 197/288 native catalogue entry crosswalk, 91 outside). Separate loaded image B remains source/data/layout incomplete.

IMCRA D round: `build-imcra-d-round/receipt.json` (135 CK804EF units; linked SHA256 `74688b132c329399a1ff3f5d9c8102cacd9edef6aecf25917797b08bd911a29c`; 198/288 catalogue entries, 90 outside). Binary64 exp and product configuration remain genuine imports.

Current final IMCRA D/runtime receipt: `build-imcra-d-runtime-final/receipt.json`, 136 units, linked SHA256 `2dc5b232117835bdf823217b41d27b9ed17b6914ced99e689cd4076fa7c7d05d`, 198/288 catalogue entries crosswalk, 90 outside.

Float exponential round: `build-exponential-float-round/receipt.json` (137 CK804EF units; linked SHA256 `c86e3789f67fb24b7d8125e0c1407e7c42daa2c5363d0076382e839cd57f7050`; 199/288 catalogue entries, 89 outside). Native binary64 exp and product data remain explicit.

Binary64 exponential round: `build-exp-double-round/receipt.json` (138 CK804EF units; linked SHA256 `ac45b89ee8b314b161eecbc4b1cc97c9d34d4c099a7e9575c841f5e9f24c86aa`; 200/288 catalogue entries, 88 outside). Native expf and exp source now linked; source/data/physical gates remain open.

Audio-out and tokenizer round: `build-aout-tokenizer-round/receipt.json` (140 CK804EF units; linked SHA256 `474bffd9c0aace77930df28b811b755a1c89e28aca406be67f1bf022f3488df6`; 210/288 address crosswalk, 78 outside). Cursor RAM is a new genuine import; table contents/scatter remain open.

Formatter and gsensor round: `build-gsensor-workstate-round/receipt.json` (143 CK804EF units; linked SHA256 `2063fd9a860fd438928eef6067e3fdf7f04c44f6b7125de60cc0094e0b5f1938`; 213/288 address crosswalk, 75 outside). Gsensor RAM is explicit, physical/layout gates remain open.

DSP transform round: `build-dsp-transform-round/receipt.json` (145 units, SHA `3966987db76c81d77a8036070733bf88ac3e798a4c82c9d6712a3f36c656aea0`). Target defined-symbol crosswalk 215/288, 73 outside; this supersedes address-text mention counts. Real DSP/FFT/profile contracts newly opened.

## Current clock data and IMCRA sizing round

`build-clock-imcra-size-round/receipt.json` is the current separate loaded
image-B source snapshot: 160 CK804EF units compile and `ld -r` passes, linked
SHA-256 `64eb78d96fd1d4af91bbc9d6d6b676d5ded79e2d65675109b940bece254d9670`.
`backup_clock_tables.c` owns 26 typed clock module records, 17 divider
records, and three DTO records copied as field initializers from the pinned
NationalChip Grus SDK. `verify_clk_table.py` checks all 26 module records
against the stock initialized field values and native pointers. The three
clock-table catalogue addresses are data, not callable bodies; final linker
placement still needs relocation qualification. `backup_imcra_allocation_size.c`
owns genuine native arithmetic body `0x1000c6a4`; the stock setup call
`(2,3,512,256)` returns 17088 in the retained decompiler expression, and
1003 bounded host arithmetic cases pass. This is a source-expression check,
not native C-SKY execution. Eight true linker imports remain in the receipt.
The callable address crosswalk is at most 232/288; at least three of the
remaining addresses are now typed clock data and one is a BSS boundary.
The image-B source/data/layout and physical runtime gates remain open.

The next coherent separate receipt is `build-runtime-divide-round/receipt.json`:
161 units compile, `ld -r` passes, linked SHA-256
`42065f282354655c305946cc663263ff22bd03f3c0b091abcb4f71a6874c3ef3`.
Native 0x1000c5d0 implements an in-place 64-by-32 unsigned quotient with
the remainder in the result register; its only observed call at 0x100050c0
uses divisor 1024. The new C body passes 1003 host quotient/remainder cases
for nonzero divisors. Native divide-by-zero behavior is unqualified. Eight
true imports persist. The address-suffix census is 236/288 including three
clock data entries, or 233 callable addresses at most. Of 52 outside,
0x10003144 and 0x10004c78 are data/decompiler boundaries, while 0x10004880
still needs authentic compact-IRQ assembler support. Runtime and math aliases
remain to be reviewed against selected compiler-rt before counting missing
implementations.

IMCRA layout round: `build-imcra-layout-round/receipt.json` has 162 C-SKY
units and a passing relocatable link, linked SHA-256
`948be00d57f1ad9c5edf51ed7a5a91875645852805541001518a6494e1245d1b`.
Native body `0x1000d1fc` is now C: all 13 region offsets and write ordering
derive from the retained body, and the diagnostic format string is the
native `0x10014200` text. A bounded 1000-case host comparison of the 13
result fields passes. The source body operates on an already allocated IMCRA
context; final SRAM placement and physical execution remain open. Eight
genuine imports persist. The address-suffix census is 237/288 including
three typed clock data addresses, leaving at most 51 catalogue addresses
outside and 234 callable address matches at most.

Beamforming initialization round: `build-beamforming-init-round/receipt.json`
has 163 CK804EF source units and a passing relocatable link, linked SHA-256
`1a9ccc42590c1ea234b06bd58b2cc32eca43b3c13f222894ed52589c6c369c1b`.
The new `0x1000b800` body follows the pinned NationalChip
`lvp/lvp_mode_denoise.c` initializer with stock-native overrides: angles
35/45/55, 512/256 frame sizing, 2.0 gain, 0.035 distance, and exact
native float/register/stack argument order. It uses the selected four-word
porting configuration copier, two real heap allocations, sizing and layout
bodies, and exact stock failure strings. Two genuine descendants are now
visible as typed imports: beamforming create `0x1000de40` and angle setter
`0x1000c6e8`; ten total imports. This is target compile/link and native
instruction/source corroboration, not native execution or hardware proof.
The address-suffix census becomes 238/288 including three typed clock data
entries, leaving 50 outside (at most 235 callable address matches).

Beamforming create wrapper round: `build-beamforming-create-wrapper-round/receipt.json`
has 164 CK804EF source units and a passing relocatable link, linked SHA-256
`6d22691c95739cced1d9d9dd333ffd9738f0130231faad0d34384263dce5b664`.
`0x1000de40` now has full C argument remapping to core `0x1000ce14`.
Target `objdump -dr` reproduces the native wrapper's 24-byte temporary
stack, integer-register reorder, eight stack reads, six stack writes,
`fr1 <- fr0`, and `fr0 <- original stack word`; two final independent
register moves are scheduled in reversed order without changing effects.
The only new lower contract is core `0x1000ce14`, so ten imports remain.
Native angle setter `0x1000c6e8` and core `0x1000ce14` contain unresolved
FPU/bad-data regions in retained decompilation and no attributable `gsc`
source is present in the pinned NationalChip checkout. They remain real
source-body obligations; the wrapper does not claim their completion.
Address-suffix census: 239/288 including three typed clock data entries,
49 outside, at most 236 callable address matches.

Beamforming process forwarding round: `build-beamforming-process-wrapper-round/receipt.json`
has 165 CK804EF source units and passing `ld -r`, linked SHA-256
`dd37c8579ce086fd1f018fa73cb82c65ec49019f8bf040a26596ce16a5c812b8`.
The C implementation of `0x1000dea0` compiles to the same C-SKY instruction
bytes as stock across its entire 20-byte body, modulo the unresolved
relocation to `0x1000d46c`. Its fifth argument is the native stack word,
and the lower return register is preserved. The real `0x1000d46c` body is
now visible as the eleventh true import; retained decompilation stops on an
FPU/bad-data edge. Address-suffix census: 240/288 including three clock
data entries, 48 outside, at most 237 callable address matches.
