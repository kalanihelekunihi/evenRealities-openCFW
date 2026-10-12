# Bounded image-A XIP relocation candidates

The current C-SKY compiler's `-Os` still does not fit three of the
largest body sections into their fixed stock slots:

| Native entry | Stock slot | `-O2` section | `-Os` section | Known selected references |
| --- | ---: | ---: | ---: | --- |
| `0x10206a84` tinyprintf formatter | 416 | 580 | 520 | One PC-relative relocation from `0x10206c24` printf wrapper |
| `0x10207070` audio input/output | 452 | 602 | 552 | Four PC-relative relocations in `0x10207234` configuration |
| `0x10208098` UART receive callback | 532 | 648 | 548 | Three 32-bit address relocations from `0x10207c9c`, `0x10207cec`, and `0x10208458` |

The retained native direct-callee catalogue names exactly the first
two caller relationships. Native image-A XIP contains no aligned raw
32-bit address literal for either of those targets. The UART callback
is a pointer argument rather than a direct callee. Its three stock
address words occur at `0x10207ce8`, `0x10207ed0`, and `0x10208538`,
each in a separately catalogued literal gap adjacent to the same
three source-owned caller bodies. The candidate ELF uses
`R_CKCORE_ADDR32` symbol relocations from those bodies instead of
hard-coded `0x10208098` constants.

These bounded facts permit a *candidate* layout in which those three
providers move to source-owned XIP addresses and their selected C
callers/pointer words relocate with them. A final linker must receive
an authenticated free XIP region and qualify branch reach, all
consumer pointers, jump/literal pools, and entry/copy behavior. The
source package and any outside-stage consumers have not been proved
free of further fixed references. This note does not assign new
addresses or assert firmware image completion.

The isolated `probe_xip_size_variants.py` target receipt records `-O2`,
`-O1`, `-Os`, `-Os -fno-inline-functions`, and `-Os` with jump tables
disabled for these three providers. Neither extra option reduced
them below plain `-Os`; target GCC rejects `-Oz`. The broader
`probe_xip_overflow_os.py`/`select_xip_os_sources.py` probes support
the separate 35-file per-source `-Os` policy used by the builder.
# Current overflowing-provider address escape audit

The source-coherent `codec-xip-os-policy-round` target build passed with 230
image-A inputs and the known-data placement gate. Its target object has 249
size-eligible direct XIP slots and 62 overflows (1,150 aggregate excess bytes).
The build applied the SHA-guarded `-Os` policy to 35 source files; no policy
sources were stale. The three firmware contracts remain the FPU rounding and
inexact hooks and the ambient KWS task words. The relocatable ELF additionally
lists two compiler shift helpers, which require target runtime linkage and are
not evidence for FPU/product semantics.

`audit_xip_address_escapes.py` and `xip-overflow-address-escapes.json` scan
both authenticated BINH-A loaded regions for exact little-endian 32-bit words
equal to each of the 62 overflowing XIP entry addresses. Thirteen entries have
one or more raw address hits. Of sixteen total hits, five are in initialized
SRAM tables, ten are in catalogued XIP inter-function gaps, and the TWS
initializer at `0x10208670`
also has one XIP body-region hit at `0x1020b208`. These hits require symbolic
relocation or a proven fixed entry if any entry moves. The source-owned AOUT
product table and sample-app tail account for the five SRAM hits. The TWS
mode descriptor at the XIP body hit is source-owned by
`resident_xip_mode_initialize.c`: its target object has
`.rela.rodata.gx8002_xip_tws_descriptor` offset 4 as `R_CKCORE_ADDR32`
against `gx8002_xip_tws_initialize_10208670`. Thus the candidate expresses
this pointer symbolically. A movable XIP link still needs a proven descriptor
placement and full reference/branch checks.

The five raw SRAM hits also have source-owned typed pointer sections in the
current image-A object. `.rela.gx8002.sram.aout_operations` has `R_CKCORE_ADDR32`
entries for allocator `0x10205254` at table offset 0, DAC config `0x10204c90`
at offset `0x24`, and dB getter `0x10204ff0` at offset `0x3c`.
`.rela.gx8002.sample_registration.26d30` has corresponding relocations for
sample init `0x10208e4c` at offset `0x10` and I2S request tick `0x102091bc`
at offset `0x18`. These five product pointers are relocatable in selected C;
the authenticated SRAM section placement gate checks their containing extents.

The other 49 overflowing entries have no *raw word* match in these two loaded
regions. That is not a no-reference proof: native PC-relative branches,
computed addresses, image-B or ROM references, and external callers are beyond
this audit. The selected relocatable object's per-section relocation entries
establish symbolic C references; a final link must choose an authenticated
XIP allocation, preserve 24 checked startup/data sections, and validate every
branch range, literal pool, external entry, scatter copy, and alias. Fixed
stock entry slots cannot accommodate the current 62 overflows even after the
qualified target size policy.

The `audit_xip_overflow_relocations.py` crosswalk counted 58 native direct
caller edges into those 62 entries and 273 selected C relocations naming 60
of their provider symbols. The two without selected incoming relocations are
`0x1020470c` and `0x102055dc`; absence does not rule out native indirect or
outside-stage references. The `image_a_xip_packed_probe.ld` and
`check_xip_packed_probe.py` target link placed every one of the 311 direct
native-bound source symbols plus two additional source functions in a
contiguous relocatable section at `[0x10203004,0x10209848)`, 26,692 bytes.
That leaves 4,194 bytes to the native code-span end `0x1020a8aa` before
placing 27 other source-bound labels, helper code, rodata, and native literal
tails. The ten measured pinned arithmetic/CRC function bodies alone total
4,208 bytes at `-O2`, already 14 bytes beyond that headroom, so this probe
does **not** establish a complete packed image inside the stock code span.
The source linker needs qualified code-size reduction or a proven additional
XIP region, and final address/reference checks in either case.

An isolated CK804EF target probe on the ten arithmetic/CRC functions found
that `-Os` changes their summed body size from 4,208 to 3,536 bytes, a 672-byte
reduction. This is a code-size result only. The fixed-slot overflows and the
other 17 source-bound labels still require whole-graph placement and native
runtime qualification. The pinned LLVM 20.1.8 `__ashldi3` and `__lshrdi3`
sources also compile as 44-byte standalone target providers without further
imports; they are recorded in the existing LLVM provenance file and can close
the two target compiler-runtime imports after current source snapshot settles.

The image-A FENV bridge now uses the pinned C-SKY glibc FPUv2 register
contract with the same `-mcpu=ck804ef -mhard-float` target flags as image-B.
An isolated target disassembly shows `mfcr ..., cr<1, 2>` for the live rounding
mode and a runtime `fdivs` for the inexact exception path. The current image-A
relocatable object resolves both compiler-rt FENV imports; its only remaining
semantic import is `gx8002_xip_kws_ambient_task_words`. Linking the two pinned
LLVM shift objects to that current candidate in an isolated relocatable link
also removes `__ashldi3` and `__lshrdi3`, leaving only that ambient task-word
contract. This proves target symbol closure for those lowers, not real-device
directed rounding or the source of the ambient words.

`audit_xip_packed_lower_bound.py` now accounts for more than the direct
function slots using the coherent 233-input image-A candidate. In the native
36,484-byte XIP payload, the packed direct named text is 26,692 bytes;
18 distinct, mapped but previously unplaced helper bodies contribute 4,776
bytes; 59 named XIP read-only sections contribute 4,184 bytes; and three
sample-name sections contribute 44 bytes. The conservative subtotal is
35,696 bytes, leaving **788 bytes** of the original payload size before
other mapped helpers, FENV/shift providers, alignment, other tables, native
literal tails, and veneers. This is a size floor conditional on keeping these
sections in image-A XIP; moving them to an authenticated other region could
change the allocation. It is not an image-size fit or final linker proof.

The canonical image splitter fixes the stock XIP payload at package offsets
`[50576,87060)`, exactly 36,484 bytes loaded at
`[0x10203004,0x1020be88)`. The adjacent stage-2 SRAM source is 14,716
bytes at package offsets `[87060,101776)` and its initialized tail is
already address-constrained. There is no authenticated unused executable
region or expanded package capacity in the retained layout evidence. A source
link that places extra text in SRAM, extends the XIP payload, or changes the
container must first establish the loader and storage contract for that
allocation; the packed probe does not do so.

An additional 18 source-bound non-suffix files were target-compiled with the
selected command line changed only from `-O2` to `-Os`. Their aggregate object
text shrank from 6,274 to 5,374 bytes, and none of their direct native-named
sections grew. The SHA-guarded build policy now covers 53 files. On its new
image-A object, 249/62/28 fixed-slot statuses remain unchanged; the packed
direct text is 26,632 bytes, mapped helper-body floor 4,020 bytes, named XIP
read-only sections 3,848 bytes, and sample names 44 bytes. The conditional
XIP payload floor is **34,544 of 36,484 bytes**, leaving 1,940 bytes before
other source code/data, alignment, and veneers. This is an actual 1,152-byte
reduction from the previous measured floor. The full combined receipt and
image-B coherence are tracked separately from this image-A size observation.

## Complete selected relocation-closure capacity probe (2026-10-11)

The coherent 233-input image-A object from
`g2/build/c-firmware/20261011/codec-xip-unbound-os-round/receipt.json`
(SHA-256 `3060f87ab1719228b1f58fb6ebe8ae8170934d17ee274f395ea1de047e2e0911`)
now has a reproducible section-level relocation audit in
`xip-relocation-closure-unbound-os.json`. Its graph starts at all selected
`gx8002_xip` text/rodata and the authenticated sample-name XIP data, then
follows every defined target section relocation. It reaches 577 allocatable
PROGBITS sections, 51,681 raw bytes. Exactly one target remains undefined in
that graph: `gx8002_xip_kws_ambient_task_words`, whose native producer leaves
three stack words unspecified. No default provider is supplied.

Section names with native `0x1002xxxx` identity and resident code provenance
account for 14,534 reachable bytes; the prospective XIP allocation is 442
sections and 37,147 raw bytes. This includes the newly selected FENV and
64-bit shift helpers, the full 1,024-byte CRC table, named XIP data, literal
strings, and other source helpers. The explicit linker-section probe
`xip-relocation-capacity-unbound-os/receipt.json` packs those 442 sections at
`0x10203004` and measures **37,340 bytes including alignment**. The native
loaded XIP payload is exactly **36,484 bytes** through `0x1020be88`, so the
current source closure **exceeds its authenticated payload by 856 bytes**.
This probe does not add branch veneers or unreferenced but required product
sections, so 856 bytes is a current-candidate minimum placement deficit under
the recorded section classification, not a final firmware size estimate.

The fixed native package maps the adjacent 14,716-byte stage-2 SRAM source at
package offsets 87,060..101,776; its current source-owned executable and
initialized sections already have their own address/copy constraints. No
additional executable loaded region or increased loader copy length is
established by this receipt. A larger replacement XIP container, a proven
alternate placement for selected helpers, or at least 856 bytes of qualified
source/compiler reduction (plus any later layout overhead) remains necessary.
The candidate object does compile and link relocatably; final image placement
and native runtime equality remain open.

## Source-qualified `-Os` continuation

A target compiler probe across all 95 selected XIP translation units still
using `-O2` found 37 whose XIP text sections shrink at `-Os`. The exact
source-hash/object receipt is `xip-remaining-os-all-probe/receipt.json`.
The sum of those XIP section changes is **−1,016 bytes**. Three of the
37 shrink as whole translation units but contain one or more individual
sections that grow (VAD curve/weight/chipping, GPIO disable, DMA clear).
Those three have **relocatable packed-layout qualification only**; fixed
stock address-slot admission and native runtime equality are still open.
The remaining 34 show no individual XIP section growth. The SHA-guarded
selection policy now lists 90 `-Os` source units.

An isolated relink replacing only those 37 objects succeeds. Its complete
relocation closure has 580 allocatable sections and 50,705 raw bytes.
The exact same section classifier and packed linker probe place 445 XIP
sections in **36,368 bytes**, leaving **116 bytes** within the 36,484-byte
native XIP payload. The receipt is `xip-os-all-variant/capacity/receipt.json`.
This is a provisional packed candidate: the link remains relocatable,
indirectly referenced sections and any final veneers have not been proved
absent, and the loader/scatter contract has not been rewritten to this
placement. The selected `-Os` policy is being checked in a fresh coherent
Codec build.

The selected ELF also contains 40 allocatable sections totaling **8,945
bytes** outside the direct-XIP relocation closure. Most are the pinned
NationalChip FFT source bodies; some are resident product data and arithmetic
helpers. They must be classified by actual startup roots or native placement
before a full image link can discard or place them. The 116-byte margin is
therefore not final firmware capacity.

## Paired SRAM source capacity probe

The same candidate requires a separate check for the authenticated loaded
stage-2 SRAM source `[0x10023400,0x10026d7c)`, 14,716 bytes. The initial
source-hash-coherent XIP-90 variant still packed all native-address resident
code and initialized-data sections to **15,020 bytes**, a **304-byte
resident overflow** (`resident-capacity-os-all/receipt.json`).

A target `-Os` probe of all remaining native-address resident C units found
35 smaller units, reducing their resident text sections by **1,074 bytes**.
Two units contain growing individual resident sections and therefore have
relocatable-only qualification. Combining those 35 with the 37 additional
XIP `-Os` units relinks successfully. The paired section-placement probes
then measure XIP **36,380/36,484 bytes** and stage-2 resident
**13,944/14,716 bytes**, leaving 104 and 772 bytes respectively.
`combined-os-variant/{xip-capacity,resident-capacity}/receipt.json` records
the selected object SHA and linker outputs. Both figures are tentative
source-region allocations: no final copy-length, BSS/stack reservation,
indirect entry, veneer, or runtime equality proof follows from relocatable
section packing. The resident `-Os` source policy awaits a fresh coherent
selected build after the currently running XIP-90 checkpoint settles.

The joint native-root audit found two additional exact XIP product-data sections
(`.gx8002.xip.notification_uart_settings`, 16 bytes, and
`.gx8002.xip.aout_route`, 13 bytes) that are not reached from an XIP code
relocation but have explicit source/native XIP ownership. The capacity probe
now seeds these, plus the stock-address flash-name literals. Recomputed paired
packed sizes for the combined `-Os` object are **36,412/36,484 XIP**
(**72 bytes margin**) and **13,912/14,716 stage-2 resident**
(**804 bytes margin**). These replace the provisional 104/772 margins above.
The joint XIP plus resident source-root relocation closure reaches 595 of
620 selected allocatable sections; 25 sections remain outside it, chiefly
pinned FFT/math bodies. Indirect/runtime reachability of those 25 is a
separate gate before a final linker script can discard them.

The SRAM body now also has a stronger fixed-layout probe:
`resident-fixed-tail-os-paired/receipt.json` consumes the selected Codec A
object (SHA-256 `aa9e3dcae207de8f903b7f3f140665fb0ca732849614b8c114feba57e361e0d3`).
It pins the source vector at `0x10023400` and all 22 previously attributed
initialized tail sections at their exact native addresses through
`0x10026d7c`; the other 124 native-address resident sections pack into
`0x10023500..0x100261be`. Thus **806 bytes** remain before the fixed tail
begins at `0x100264e4`. This is a successful target relocatable layout
assertion for all presently classified resident sections, still subject to
indirect code roots, aliases, BSS/stack, final loader copy, and runtime proof.

The selected paired-`-Os` `candidate.o` matches the isolated object byte for
byte (SHA-256 above). Re-running the corrected XIP closure and capacity
scripts against that selected object gives the same 448 XIP sections and
36,412-byte packed size (`xip-selected-paired-{closure.json,capacity/receipt.json}`).
The existing independent known-data checker also passes on it: 24 pinned
vector/tail/BSS sections, including the 2,200-byte initialized tail and
console BSS cell (`known-data-paired-check/receipt.json`). A fresh combined
Codec source-coherent receipt including separate image-B is still pending.

The full selected allocatable PROGBITS set is **58,576 raw bytes**, while the
two authenticated load sources total **51,200 bytes**. The difference
(**7,376 bytes before alignment**) is chiefly the 25 code sections outside
all named XIP/resident source roots, totaling 8,494 bytes. Consequently a
final image must establish that those sections are excluded by source-root
and native-entry provenance, or identify another authenticated destination;
the paired-fit result cannot justify blindly retaining all selected objects.
In particular, the large pinned FFT functions are present as candidate
providers but have no incoming relocation from current image-A source roots.
Their native image-A membership remains a separate evidence question.

## Rooted section-GC and compiler-copy import

The current source root set includes every selected named XIP and resident
body, reset/vector, XIP product literals, and source-owned registration/API
and initialized data sections. `check_image_a_root_gc.py` links the selected
object with `--gc-sections` and those exact KEEP roots. On the ABI-correct
copy-alias candidate, it discards exactly 25 sections/8,494 raw bytes,
retains all 311 direct native-bound XIP symbols, and leaves only the ambient
KWS task-word input undefined. The 25 are 17 pinned FFT/utility sections,
seven uncalled compiler arithmetic sections, and one inlined-out CRC
wrapper. `root-gc-memcpy-probe/receipt.json` has the full section list and
output SHA. Source-root GC eligibility does not itself exclude an unknown
stock indirect entry or library ABI consumer; final admission needs the
native entry/pointer census. The largest authenticated unnamed XIP gap is
138 bytes and the largest SRAM residual code/data gap is 244 bytes, so the
2,506/2,528-byte FFT source bodies cannot each be hidden intact in such a
gap.

The coherent 125-`-Os` Codec A link unexpectedly exposed compiler-emitted
`memcpy` calls in the audio input/output body. Native SRAM `0x10025738`
preserves original destination register `r0` while using `r12` as its moving
copy cursor. The source-owned forward-copy function now returns that
original pointer, and a target-only `memcpy` alias shares its exact code
address. Target compile and 144 bounded host nonoverlap-copy/return vectors
pass (`memcpy-alias-probe/receipt.json`). An isolated replaced-object relink
then has only the ambient KWS import; XIP packed size remains 36,412 bytes
and the fixed SRAM body ends at `0x100261ca`, leaving 794 bytes before the
stock initialized tail. A fresh selected-source combined build is pending.
