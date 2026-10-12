# Touch reset-copy source reduction

The pinned Touch wrapper is SHA-256
`0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d`.
Its reset descriptor copies 241 words (964 bytes) from ROM `0xb58c` to SRAM
`0x200004c0`. Prior source-owned islands total 25 bytes. This pass adds 68
source-owned bytes in five disjoint islands, for 93/964 bytes and 871
remaining. `reset-descriptor-receipt.json` records exact section, address,
length and SHA-256 comparisons.

Four low-power sensor descriptors at `0x20000808` encode widget 0 with
sensors 0–3. Four active sensor descriptors at `0x20000818` encode widget 1
with sensors 0–3. The LP history and scan consumers establish the role of
these two 16-byte arrays; the stock reset bytes establish their values.
Two context pointer words at `0x2000051c` and `0x20000520` now relocate to
the active and LP arrays respectively. The isolated absolute linker places
the source arrays and pointers at their authenticated SRAM VMAs and ROM LMAs,
and all 40 bytes compare exactly against the official image.

The 28-byte DeepSleep callback descriptor at `0x20000850` uses the recovered
`touch_pm_callback` ABI: source callback `touch_ilo_deep_sleep_callback`,
type 1, skip mask 0, parameter address `0x20000ccc`, null list links and
order `0xff`. Earlier Touch PM analysis identifies this descriptor and
callback through registration/dispatch consumers. This pass links the
source callback at the bounded original entry and compares all 28 descriptor
bytes exactly against the official reset payload. The bounded layout is an
oracle fixture, not the final Touch linker map.

The Touch candidate builder now includes the three new reset-data C units;
its retained function sources and provider set continue to compile. Remaining
initialized data includes the product CapSense context, widget and sensor
configurations, zero-filled members, peripheral descriptor fields and two
GNU CRT callback words. Their source types, pointer relocations, and final
linker placement need further attribution. The missing generated product
`cycfg_capsense.c/.h` and final `.map` have not been acquired. Whole-image
source completeness, byte equality and hardware behavior remain open.

## Attributed vendor LP context and widget runtime initializers

Initialized the existing CapSense submodule at its unchanged3.0.1 commit25fa1cd5... and fetched pinned primary version4/5/6/7 references. Version11's widened LP context does not match native offsets. Versions4-6 supply the native32-byte common-context ABI: tunerCmd2,tunerSt6,status8,lpDataSt22,lpScanSt28. `reset_common_context.c` defines named product fields; all32 compiled data bytes equal stock (`reset-common-context-receipt.json`). Producing SDK version is not uniquely identified.

Version6 reference commit247a9a0f79eb976f144f5fbeb29488c1c2606517 supplies the60-byte LP/fine-CDAC widget ABI, corroborated by native widget stride60,status35,compensation-divider54. `reset_widget_contexts.c` defines three typed product widget contexts and an8-byte slider position, using one true C pointer relocation. Isolated absolute compiled source compares all188 bytes exactly (`reset-widget-context-receipt.json`). No opaque byte array or executable blob.

Cumulative attributed initialized reset bytes now313/964,651remaining. This is bounded data/relocation ownership, not final image layout, complete generated configuration, or physical touch proof. Version6 reference source/header/license files and provenance are retained in `capsense-v6-reference`; version11 comparison in `capsense-v11-reference`, both traced to exact objects in the existing CapSense submodule.

Nine10-byte sensor contexts now named source fields (`reset_sensor_contexts.c`), corroborated by native stride10/status6/raw-baseline-difference0/2/4 and primary vendor LP CDAC9. Product ROM widget descriptors independently bound4+4+1 sensor rows. All90 compiled initialized bytes matchstock; aggregate403/964 bytes,561remaining (`reset-sensor-context-receipt.json`). The all-zero historic region is not promoted to an arbitrary blob/buffer: its exact generated allocation extent remains open.

## LP channel and genuine child data objects

`reset_channel_pending.c` now defines the complete 28-byte LP channel at
RAM `0x2000082c` (ROM `0xb8f8`). The product common configuration at ROM
`0xb2a8+8` points to this address. Native scan preparation reads its hardware
and driver-context pointers at offsets 0/4; native Cmod control reads the
two port/pin pairs at offsets 8/12 and 16/20. These accesses agree with
the pinned CapSense v6 LP channel type.

The referenced MSCLP context is a four-byte middleware lock key, as defined
by PDL commit `69bb46becb33da0215576d6d22f6b225165d4c28`, header retained in
`g2/analysis/source-discovery-parallel-2026-10-09/pdl-history/`.
Two electrode descriptors at ROM `0xb32c` and two pin descriptors at `0xb33c`
are also named C data, with actual pointer relocations between them.
The bounded verifier compares all 28 channel bytes and 32 ROM child bytes
against authenticated stock; the linked fixture has zero undefined symbols.
The candidate builder now selects this source. Its historical `pending` filename
does not imply unresolved providers after this pass.

**Completed scope:** typed channel and its referenced data objects, including
bounded pointer placement. **Remaining reset-copy estimate:** 533/964 bytes;
431 bytes are now closed by attributed source fixtures. The additional 32 ROM
bytes and four-byte driver BSS context are outside that reset-copy census.
Final image placement, history allocation and hardware operation remain open.

## Actual reset helper replaces the offline boundary

The selected `app_event.c` previously defined `touch_reset_boundary` as an
empty infinite loop for earlier offline fixtures. That did not implement the
native reset body. `eeprom_offline/system_reset.c` now owns native
`0x7e14..0x7e26`: DSB, unconditional AIRCR write `0x05fa0004`, DSB, and the
native terminal NOP loop. `app_event.c` calls this real source body; historical
fixture entry cuts remain valid by symbol name.

`verify_system_reset.py` compares authenticated stock and actual compiled C in
Unicorn for four prior AIRCR values. Both produce exactly the two barriers and
one four-byte register write, preserve SP, and reach the loop twice. Run with
`/tmp/iar-c-runtime-venv/bin/python`; the ordinary system Python lacks Unicorn.
No physical reset/device action occurs. Reset-data coverage remains431/964;
this pass fixes executable-body fidelity rather than initialized data coverage.

The candidate builder excludes `lp_history_offline/decoder.c`: its header
explicitly identifies it as a new app analysis API, not a recovered stock body.
Its standalone producer tests remain available. It is not counted as firmware
source recovery.

## Application PM descriptor and threshold

`reset_app_pm.c` defines the 28-byte descriptor at RAM `0x200004cc`, its typed
zero-initialized two-pointer parameter object at `0x200009c0`, and the halfword
threshold at `0x200004e8`. The descriptor layout agrees with the existing PM
registration ABI. Its native callback at `0x3620` is the actual four-byte
return-zero leaf; compiled C matches those four bytes exactly. All descriptor
pointers and 30 initialized data bytes also match stock in the bounded fixture.
The adjacent two bytes after the threshold are not counted without allocation
or padding ownership. Completed scope: descriptor/callback/threshold data
ownership. **Remaining reset-copy estimate:503/964 bytes;461 closed.**
`reset-app-pm-receipt.json` records source and fixture hashes. Full image layout,
all generated product configuration and hardware execution remain open.

## Source-built GCC CRT integration

Freshly reran the authenticated CRT_BEGIN/CRT_END source builds and source-link
checks. All four retained functions (152 bytes), both init/fini array entries
(eight bytes), and the four-byte EH-frame terminator again match stock exactly.
The Touch builder now rebuilds both providers from the exact pinned `crtstuff.c`
commands, hashes consumed inputs before/after compilation, checks expected
source-built object hashes, and adds those freshly compiled objects. It does
not import an installed executable provider. The earlier static global data
that the bounded CRT oracle discarded is not newly claimed as stock-owned.

**Completed scope:** fresh source-provider integration plus eight reset-copy
array bytes. **Remaining reset-copy estimate:495/964 bytes;469 closed.**
Remaining regions are enumerated with stock hashes in
`reset-remaining-regions.json`. Final linker layout, constructor reachability,
the historical buffer allocation and full generated configuration remain open.

`verify_delay_alignment.py` now closes three bytes between the typed MHz and
kHz reset objects. The linked section uses no explicit fill or ALIGN: natural
uint32 object section alignment produces the exact eight stock bytes, five of
which were already closed scalar data. **Current total:472/964 reset bytes;
492 remain.** This does not authorize arbitrary zero gaps or identify the
426-byte historic allocation. The remaining-region inventory excludes these
three proven alignment bytes.

## Slider position-filter history header

The previous slider producer analysis identifies RAM `0x20000848` as widget1's
position-filter header, not libc or a generic PM object. `reset_position_history.c`
defines the vendor-compatible pointer/count header and the selected path's
single position record at `0x200009dc`. Native widget1 ROM `0xb188+60` points
to the header; config `0x00800102` requests one eight-byte history record per
position, and centroidConfig&3==1 produces zero/one positions. All eight compiled
header bytes and the pointer relocation match stock. Wider generated storage
allocation is not claimed from this single-position contract.
Completed scope: typed initialized header. **Current reset closure480/964;
484remaining.** `reset-position-history-receipt.json` records the bounded checks.

## Experimental top-level LP context pointer table

The pinned CapSense v6 LP `cy_stc_capsense_context_t` has fifteen ordered
pointer fields. The stock reset-copy interval RAM `0x200004ec..0x20000528`
contains exactly that 60-byte table. `reset_capsense_context.c` expresses the
vendor field names and keeps unresolved product configuration and generated RAM
pointees as external symbols. A bounded absolute linker fixture binds each
symbol to its authenticated stock address. All 60 compiled bytes match ROM
`0xb5b8..0xb5f4` exactly (`verify_reset_capsense_context.py`). This newly
attributes 52 pointer bytes; the two scan-slot pointers (eight bytes) were
already covered by the selected Touch candidate. The experimental whole-table
unit is not selected because it would overlap those two selected slot-link
units and its remaining pointee definitions are still external contracts.

The final pointer at RAM `0x20000524` names the LP historic context start
`0x2000065e`. It establishes the start, not the 426-byte allocation extent.
A second bounded link places the already selected two-byte application threshold
immediately before the context and emits the two alignment bytes through
`ALIGN(4)`, with no explicit data initializer. The combined 64 bytes match
stock. The four-byte value at `0x20000828` remains unowned. Selected reset
closure is still 480/964 bytes; if the whole pointer table and alignment are
reconciled into the linker graph, attributed closure would be 534/964, leaving
430 bytes (426 history allocation and four-byte value). Pointee contents,
linker allocation, and hardware behavior are not established by the fixture.

## Top-level context selected in the Touch archive

The Touch archive now selects `reset_capsense_context.c` in place of the two
slot-link units. The archive rebuild compiled all 54 Touch C units and reports
nine strong unresolved generated pointee contracts. Five other table pointers
resolve to existing selected source symbols. The typed context model adds
52 pointer bytes and the adjacent source-link alignment adds two bytes to the
reset-copy ownership census. Current selected attributed closure is **534/964
bytes**, with **430 bytes remaining**: the unproven 426-byte LP history
allocation extent and a four-byte value at RAM `0x20000828`. The archive is
compilable; final link placement and generated product pointee definitions are
open. The earlier 480-byte figure above is the pre-integration snapshot.

## Remaining reset allocation gates

`audit_remaining_reset_gates.py` checks the locked payload and selected source
receipts. The vendor v6 LP type declares `ptrLpHistoricContext` elements as
`uint16_t`, and `Cy_CapSense_TransferLpRawCounts` increments the pointer once
per scanned slot per frame. The configured four-slot result window has at most
212 nominal complete words, or 424 bytes of history; the adjacent known object
starts 426 bytes after the pointer target. These facts do not establish the
linker allocation extent. A generated `cycfg_capsense` declaration or official
symbol-size map is required before the entire zero run can be claimed.

The remaining four bytes at RAM `0x20000828` contain little-endian value 2.
The pinned static decomp/source search did not identify a consumer or field
schema for that location; the authenticated image has no absolute pointer
literal to that address. The value remains an explicit product data contract.
The finite audit records the exact hashes and limits. No live Ghidra instance
was available for an interactive xref check.

## Fifth active scan-slot row

The four-byte reset value at RAM `0x20000828` is the fifth
`cy_stc_capsense_scan_slot_t` entry in the active descriptor array, with
`wdId=2` and `snsId=0`. It follows the four `wdId=1` rows at
`0x20000818..0x20000827`; the next named channel descriptor begins at
`0x2000082c`. The pinned v6 vendor type declares two `uint16_t` fields in
this order. `reset_sensor_descriptors.c` now owns five active rows, and the
bounded target compiler/linker check compares all 20 bytes exactly with stock
(`reset-descriptor-receipt.json`). The fresh Touch candidate build passes
with 54 source units and the same nine genuine generated-data imports.
Selected attributed reset-copy closure is now **538/964 bytes**, with the
426-byte LP history extent the sole remaining unowned reset-copy interval.
This does not establish that entire allocation or the generated configuration
pointees.

## Generated LP pin records

The pinned CapSense v6 LP `cy_stc_capsense_pin_config_t` has an eight-byte
record containing a port pointer, pin number, and pad number. The five records
at stock ROM `0xb34c..0xb373` are now expressed as the typed source array
`touch_generated_pin_config`. `verify_reset_pin_config.py` compiles this array
for Cortex-M0+ and compares its complete 40-byte section against the locked
G2 2.2.6.10 Touch image: **40/40 exact bytes**. The selected context refers
to this symbol with the same typed declaration. The fresh experimental Touch
build at `g2/build/c-firmware/20261011/touch-pin-config-round/receipt.json`
passes with **55 C units and eight generated-data imports**; source completion
is still false. The 426-byte LP history reset interval and final source
placement remain open. This source section is relocatable; the bounded byte
comparison does not establish the final firmware link address.

## Active-scan runtime BSS

The v6 LP active-sensor runtime type contains four pointers, two halfwords,
and three state bytes, occupying 24 bytes on Cortex-M0+. The authenticated
context points to RAM `0x20000c38`; the next generated internal context starts
at `0x20000c50`, exactly 24 bytes later. The stock reset zero descriptor clears
`0x200008a8..0x20000f57`, which includes this object. The selected
`touch_generated_active_scan_sns` is now a typed 24-byte NOBITS definition;
target `readelf` confirms section type `NOBITS`, size 24, alignment 4. The
context uses a typed pointer to it. The fresh coherent experimental build at
`g2/build/c-firmware/20261011/touch-active-scan-nobits-round/receipt.json`
passes with **seven generated-data imports**. Its address still requires final
linker placement, and this evidence does not identify the other generated
runtime objects or the 426-byte reset history allocation.

## MSCLP base-frame runtime

The pinned PDL `cy_msclp.h` defines `cy_stc_msclp_base_config_t` as 28 named
register words, eight global switch words, and four seven-word sensing-mode
records. That is exactly 256 bytes. The generated context points to RAM
`0x20000b38`, and the next identified active-scan object begins at
`0x20000c38`, exactly 256 bytes later. Both lie inside the authenticated CRT
zero range. The selected C declares this typed object with all named fields;
the isolated target object is a 256-byte, four-byte-aligned NOBITS section.
The coherent Touch receipt at
`g2/build/c-firmware/20261011/touch-base-frame-final-round/receipt.json`
compiles all **57/57** source units and retains **six** genuine generated-data
imports. This establishes type, size and reset mode; final address placement
and physical MSCLP behavior remain separate obligations.

## Low-power and active sensor-frame storage

The selected scan descriptors contain four low-power slots and five active
slots. The pinned CapSense LP sensing source indexes low-power frames by the
PDL's 11-word sensor register stride. Four such frames occupy exactly the
pointer-bounded `0x200009fc..0x20000aab` interval (176 bytes). The active
sensor-frame interval `0x20000aac..0x20000b37` is 140 bytes, matching five
seven-word frames used by the active frame layout. Both intervals lie inside
the authenticated 1712-byte CRT zero range. The selected C now owns typed
`uint32_t` slot arrays; target object sections are NOBITS with sizes 176 and
140 bytes. The coherent build at
`g2/build/c-firmware/20261011/touch-sensor-frames-round/receipt.json`
compiles **58/58** units and leaves **four** generated-data imports: common
config, widget config, internal context, and LP history. The 426-byte reset
history extent and final addresses remain open.

## Remaining generated-object boundary

Four selected imports remain. `touch_generated_lp_history` starts at reset
RAM `0x2000065e`; the next named object starts at `0x20000808`, leaving 426
zero bytes. Vendor LP history elements are `uint16_t`, but the generated
array dimension and possible two-byte alignment tail are not proven.
`touch_generated_internal_context` starts at zeroed RAM `0x20000c50`; native
code writes through at least offset 117, while a distinct PDL lock object
starts at `0x20000cc8`. Its exact generated type/extent and field-option
configuration still need a producer declaration or equivalent ABI proof.
`touch_generated_common_config` at ROM `0xb2a8` and
`touch_generated_widget_config` at ROM `0xb0f8` require their generated LP
option set and typed field values; nearby pointer tables and stock bytes give
boundaries but do not uniquely establish those full vendor layouts. The
missing `cycfg_capsense.c/.h` or an authenticated generated map remains the
most direct evidence. A final linker/scatter source is also required to place
all owned ROM/BSS objects and establish the executable image. The root Touch
builder's historical “484 reset-copy bytes” gate predates the fifth active
slot attribution; the current unowned reset-copy interval is **426 bytes**.

## Four generated-object boundary recheck

`audit_generated_product_frontier.py` records the locked ROM and RAM boundaries
in `generated-product-frontier.json`. The three native widget records start at
`0xb0f8`, `0xb188`, and `0xb218`, giving an observed 144-byte stride and a
432-byte span before the common configuration at `0xb2a8`. That common region
has 132 observed bytes before the first named electrode descriptor at
`0xb32c`; its LP channel pointer at `0xb2b0` is `0x2000082c`. These are native
byte boundaries, not a recovered product option macro set or generated C
initializer. The pinned v6 PDL declares LP history elements as `uint16_t` and
advances one element per scanned slot per frame. Neither its type nor the
426-byte zero gap proves the generated array count. The internal context
starts at `0x20000c50` with observed native writes through offset 117; the
named lock at `0x20000cc8` bounds 120 available bytes without proving the
object's extent or conditional field layout.

A repository file inventory found no product `cycfg_capsense.c/.h`. The two
`design.modus` files are third-party reference designs for different devices;
their option choices cannot be transferred to this G2 image. A targeted
public search for G2/S200 generated CapSense files found no exact product
artifact. All four strong imports therefore remain source contracts. The
next admissible evidence is the product's generated `cycfg_capsense.c/.h`,
its option-bearing design input plus the matching generator version, or an
authenticated linker map with symbol extents together with a validated PDL
field-layout option set. No 426-byte array or ROM configuration initializer
was fabricated in this pass.
