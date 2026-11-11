# R1 accelerometer/raw-HR adapters and readiness gate in C

Follow-up: [sensor-update coordination](gomore-sensor-update-c-review.md)
now has a C implementation and actual idle-callback replay. Counts below
describe the preceding stream-adapter build.

`native_gomore_stream_adapters.c` implements stock accelerometer callback
`0x6b114`, raw-HR callback `0x6b228` and readiness gate `0x6b0d4`. The
[receipt](gomore-stream-adapters-c-review.json) binds REA bytes, production
objects, independent replay/oracle results, negative controls and qualification.
No state owner, RAM or inline assembly is added.

Both callbacks read the count **before checking the payload for null**. The
count is at byte 180 for accelerometer packets and byte zero for raw-HR. The
native count-read fault therefore remains possible even for null callbacks.
`-fno-delete-null-pointer-checks` is required: the first compiler probe removed
raw-HR's later null check. The final object retains both the read and check;
null inputs return the incoming context only when that read succeeds. Counts
are capped at 25 and recorded without rewriting the packet count.

Accelerometer samples are processed in native order: signed Y halfword first
with scale -125/128, then signed X with +125/128, then signed Z with +125/128.
Each source read precedes its fresh destination-pointer load; stores occur
before the next axis is read. Pointer fields are reloaded each iteration, so
payload/destination/pointer-field overlaps retain native effects. Raw-HR loads
each word's bits through a volatile float lvalue, interprets them as unsigned
integer and converts them to binary32. The compiler emits the native VFP load,
unsigned conversion and store directly from C. This avoids treating incoming
word encodings as floating-point sample values.

The callbacks OR pending bits 1/2 and enter the C gate. It scans all seven
shared authorization entries for accelerometer/raw-HR users. When both are
required, both pending bits are required; otherwise the relevant single bit is
sufficient. Output dispatch runs before a late clear of **all** pending bits.
No-dispatch returns the raw-HR predicate; dispatch returns zero. The lower
output lifecycle remains modeled/unresolved.

**13,080 paired native/C/oracle cases** pass: 6,496 accelerometer, 4,024 raw-HR
and 2,560 gate cases, including **45 expected faults**. Tests exhaust all
**65,536 signed halfword values under every rounding mode**, plus 6,400 seeded
unsigned words under all four rounding modes. Exact-rational conversion
rounding and inexact flags are checked independently. Coverage includes all
pending byte values, last-entry users, cap boundaries, pointer/payload aliases,
provider mutations, signed zero, FPSCR and vector memory mapped or unmapped.
The normal emulator access mode permits the tested misaligned VFP accesses;
this does not establish physical alignment-trap behavior.

Completed calls check return, guarded state/workspace/buffers, provider order,
FPSCR, preserved registers, SP and masks. Faults compare native/C error,
fault locations and partial memory/FP state; interrupted register/stack frames
are excluded. Eleven compiled defects are rejected, including wrong axis/sign,
signed raw conversion, cached pointers, premature null checks and pending logic.
The authorization dispatcher separately passes its **2,026 paired cases** with
updated callback declarations.

All **676 units** compile with no duplicate strong symbols. All **675 prior
objects** remain unchanged; the sole prior source change updates authorization
callback prototypes without changing its object. Application imports fall from
165 to **164** and bootloader imports remain **34**. Two adapter imports are
resolved and `r1_gomore_sensor_output_dispatch_native` is exposed. Sensor update
`0x94384`, output lifecycle `0x6c294` and lifecycle initialization remain source
reconstruction dependencies.

None of the three functions qualifies as instruction-identical. The canonical
plan remains **4,369 source-built bytes**, and the fresh hybrid matches the
locked application through executable pull-through. Full source-only linking,
byte identity, concurrent access, first-use FP and physical hardware operation
remain unproven. Exception and memory behavior is verified for the pinned
compiler/target and emulator configuration, not arbitrary C implementations.
