# R1 GoMore HR and HRV sensor adapters in C

Follow-up: [idle callback/workspace consolidation](gomore-idle-c-review.md)
relocates the shared sample view into its full owner and reruns these adapter
checks. Counts below describe the preceding adapter build.

`native_gomore_hr_adapters.c` replaces the native HR adapter at `0x6b1b8`
(60-byte inventory extent) and HRV adapter at `0x6b1f4` (52 bytes). The
[receipt](gomore-hr-adapters-c-review.json) binds REA bytes, production objects,
replay/oracle checks, qualification and normal composition. Both functions
reuse the existing shared authorization state and add no RAM or assembly.

HR reads the first payload byte, converts it exactly to binary32 and stores its
bits at `0x2001a594`. It ORs pending bit 4 into state byte +1, then reads entry
5's enable flag. When set, it calls the actual authorization dispatcher with
`(5,0)` and forwards its return. Otherwise it returns zero. Null payloads return
the incoming context word. Length is ignored as in stock.

HRV reads payload byte 9 and clamps values above four by writing four back into
the payload. It stores that count at `0x2001a590`, clears the two state words
at offsets 28/32, then **rereads payload byte 9** to determine copy length.
The copy uses the existing native-return memory-move wrapper and upstream
memmove/memcpy. Consequently aliases with the cleared words, overlapping source
and destination, payload mutation and source/destination-end returns follow the
stock behavior. Null payloads preserve the context return; length is ignored.

**10,323 paired native/C cases** pass, including **1,200 expected payload faults**
and **720 cases through actual native/C authorization**. Direct cases use an
independent memory/result oracle. Coverage includes null and unmapped payloads,
shared-state/sample aliases, count 0/1/4/5/255, all sample-byte boundaries,
signed/sticky FP state and rounding/FZ/DN modes. Exact state snapshots, observed
provider order, returns, FPSCR, preserved registers, SP and masks match. The
linked C authorization path executes with modeled lower stream, timer, log and
user callback providers. The C memory helpers execute, including overlap cases.
The authorization unit separately passes its existing **2,026 paired cases**.
Eight compiled defective variants are rejected, including wrong float storage,
pending/auth bits, null returns, omitted count rewrite, cached copy count,
missing clears and ISO copy return behavior.

The authorization unit's callback declarations now match these three-argument,
word-returning adapters; its production object is unchanged. All **673 prior
objects** remain unchanged, and **672 prior source/object pairs** are unchanged.
The new normal build compiles **674 units** with no duplicate strong symbols.
Application imports fall from 167 to **165**; bootloader imports remain **34**.
The unresolved accelerometer, raw-HR and idle-timer callbacks remain the next
interfaces in this authorization path. Parameterized frozen GoMore routines are
not substituted for these native ABIs.

Neither adapter qualifies as instruction-identical. The canonical plan remains
**4,369 source-built bytes**; the fresh hybrid matches the locked application
through executable pull-through. First-use FP activation, concurrent state,
physical sensors, complete source-only firmware linking and byte identity remain
unproven.
