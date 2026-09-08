# Flash protection query reconstruction

The candidates in `runtime_gx8002_flash_protection.c` recover package entries
0x15900 (status, 148-byte envelope) and 0x15994 (mode, 36 bytes). Their source
uses the shared flash state and already recovered wait/status entry points.
Neither candidate is admitted to the firmware.

Status first writes zero to its caller's output, then reads the selected
device and its protection profile pointer at device+16. A null profile or
null entry pointer produces UINT32_MAX in the output and returns -1.
Otherwise it waits for readiness, reloads the selected device, and reads the
halfword at device+6. Only manufacturers 0x5e and 0x85 continue. It reads both
status registers, reloads selected device and profile, and snapshots count
from profile+4. Each iteration reloads the entry base from profile+0 and reads
an eight-byte entry in this order: byte1 mask, byte0 expected value, byte2
expected second value, byte3 second mask, word4 protected length. The first
matching pair wins. No match yields UINT32_MAX. A matching UINT32_MAX also
returns -1; every other matching length returns zero.

The mode query returns 1 when both profile and its entry pointer are nonnull,
otherwise -1. It does not inspect entry count or manufacturer. Thus a nonnull
empty profile can report mode 1 while status reports failure.

Native GCC 13 builds are currently 160 bytes for status and 36 for mode.
-O1 produces 172 status bytes, -O2/-O3 168, and -Os/-Oz 160. Disabling TER,
expensive optimizations, dominator optimization, VRP, forward propagation,
CCP, caller saves, instruction scheduling, or shrink wrapping individually
under -Os did not reduce the 160-byte result. Narrow local byte/halfword
types also retained the same size. The disassembly contains redundant
zero extensions after volatile narrow loads and a separate failure return.
These observations guide further source/compiler analysis; they do not
justify removing volatile accesses or weakening the access-order contract.

The analysis builder permits overlapping sections to inspect oversized code,
marks this in its report, and sets source_admitted=false. This ELF must not
be used as a firmware provider. Before admission, remove that allowance,
qualify decoded traces including helper-driven pointer changes and output
aliasing, test ABI preservation, and verify all section envelopes. The actual
protection profile initialization and hardware operations remain unresolved.

Initial decoded qualification passes 49,152 cases for both functions, with
all first-status bytes, complementary second-status bytes, four manufacturer
values, null/empty/populated profiles, empty and matching/sentinel tables,
two caller-clobber seeds, and selected-device/profile changes across helpers.
It checks ordered reads/writes/calls, return values, and preserved r4-r11/SP.
The two overlapping ELF sections are decoded separately to avoid address
collisions in the analysis. Independent status-pair coverage, output aliasing,
and rejection tests remain before admission.

Expanded decoded qualification now passes 114,752 cases. This includes every
independent pair of status bytes (65,536 pairs), rejection of an earlier entry
by status2 followed by a partial-mask match, and 64 alias cases. Alias targets
are the initial device's profile pointer, the initial profile's entry pointer,
and either of two subsequently scanned entry lengths. The oracle applies the
initial zero store to these fields before predicting later reads; it does not
merely replay the nonalias trace with a changed output address. Clearing a
matching UINT32_MAX length changes the result to successful zero, as stock does.
Nine oracle/rejection tests pass, including wrong access width, extra calls,
missing effects, unknown instructions, register corruption, and alias effects.
The status slot remains oversized, so neither query is admitted yet.

## Size resolution

Five source-level CK804 load intrinsics replace the compiler's redundant
extensions: one halfword manufacturer read and four byte entry reads. Each
uses volatile inline assembly with a register base, immediate byte offset,
full-register result, and memory clobber. LD.B/LD.H zero-extend their result;
no encoded instruction bytes are embedded. Fixed immediate offsets avoid
extra address arithmetic. All control flow, matching and state handling
remain C. This explicit assembly is part of the source, like the project's
existing control-register intrinsics, and must not be described as pure C.

The status function now occupies 144/148 bytes; mode occupies 36/36. The
linker overlap allowance has been removed. All 114,752 decoded comparisons
pass for this revised code, including the unchanged 16-byte saved-register
frame, ordered narrow accesses, helper calls and output aliases. Nine tests
pass. An admission adapter is prepared; complete package integration is still
pending. Protection profile initialization and hardware execution remain
unqualified.

Both queries are now integrated through the reviewed admission adapter.
Native codec/package builds and artifact verification pass, together with
137 existing integration tests and nine protection tests. The standard Make
target now includes those nine tests. This admission replaces 184 retained
bytes; protection-profile data initialization and physical execution remain
unqualified. See the source-candidate build report for current ownership.
