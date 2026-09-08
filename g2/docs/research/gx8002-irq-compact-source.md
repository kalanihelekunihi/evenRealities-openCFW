# Compact source IRQ entry

runtime_gx8002_irq_compact_entry.S is explicit architecture assembly implementing
the C dispatcher's vector/slot/call behavior within the original interrupt
frame. It assembles to the exact80 shipped bytes. The build records it as
compiled_assembly, separately from compiled_c: this is not a claim of pure C
interrupt entry, and it contains no extracted machine-code array.

The92-byte software frame saves extended caller-clobbered registers, FPU state
and the interrupted link register. NIE/IPUSH add32 bytes, for124 bytes before
the registered callback's own stack use. Ordinary callbacks preserve r4-r11
and r16/r17 under the reviewed C-SKY ABI.768 complete decoded cases cover all
valid external vectors, high status bits, missing/present handlers and varied
register patterns, checking the original frame and complete restored context.

Nested qualification uses shared stack storage and inherited interrupted
registers. A nested exception explicitly overwrites outer EPC/EPSR; outer NIR
must recover the original values from its NIE frame.225 cases cover25 post-NIE
instruction boundaries at three nested depths with three seeds. Seven tests
exercise malformed restores/frames/slot addressing and nested outer-stack
preservation. Build ownership tests separately ensure assembly is not counted
as C. The full integration includes the new entry and these tests.

An earlier conservative model also injected before NIE while leaving outer
control-register variables untouched. That was stack-layout evidence only,
not evidence that nested exception entry preserves unsaved EPC/EPSR. The compact
model now rejects that injection point. Pre-NIE acceptance depends on exception
entry enable rules; no such acceptance is asserted. This correction supersedes
any broader interpretation of the earlier all-boundary control-state results.

Admission requires the pinned ISA hash, compiler/SDK ABI audit, exact stock
bytes and the complete decoded/nested evidence. No additional stack growth is
introduced. Physical stack capacity, arbitrary callback depths, priority timing,
invalid vectors and instruction faults remain whole-device qualification work.
Source-only firmware completion is not claimed.

Compact IRQ integration passed274 tests. Ownership now separates8428 compiled
C bytes (121 functions /137 occurrences) and80 compiled architecture-assembly
bytes (one IRQ entry), with2216 source data,80 metadata,326 fill and314962
retained bytes. There are162 replacement regions. Codec hash is unchanged:
d226af97d7bb35b46852bf1d4bd839eb5bb6228e16eb3e91747e4efc0b35ad54.
This replaces the IRQ executable region without increasing its original frame.
Complete source-only firmware and hardware qualification remain unfinished.
