# TWI packet writes: direct C with the native 16-byte frame

Current implementation: [ordinary C packet-write status ABI](twi-write-pure-c-review.md). Scratch-register/frame preservation described below is historical.

`application/board/native_hw_twi_operations.c` now implements both packet-write
entries directly in C. Their assembly bridges and separate helper kernels
were removed. Packet reads and the register-transfer adapters are unchanged,
including the [register-write length-80 overlap](twi-legacy-tx-c-review.md).

REA read the complete native windows at `0x55ce0` and `0x55d50`. Primary has
106 code bytes, two padding bytes and a four-byte literal; secondary has 104
code bytes and a four-byte literal. The initialized operation tables also
identify these entry points. Both expose a 16-byte frame. Its first word
starts with incoming R2, then becomes the bulk instance argument or zero for
short TX. The second word starts with opaque incoming R3; short TX replaces
only its low two bytes with register/value. Both words are restored on return.

The C implementation retains those overlays with a volatile word and short,
inlined frame-word accessors. Each accessor captures SP at its use; retaining
a frame pointer across providers added another saved register and broke the
native layout in the initial probe. Empty R4 constraints retain the request
pointer at provider entry. Empty return constraints retain R0/R2/R3. No authored
assembly instructions were added to the write paths.

Primary bulk writes forward a halfword register and length. Secondary bulk
writes use the byte register and truncate the halfword length to a byte.
Bulk status mapping tests the full result. Short TX waits only for full-width
zero, then maps the low byte of the TX/wait result; TX `0x100` therefore skips
the wait and maps to success. Timeouts remain 500/100 for primary/secondary.
The unit's SRAM flag preserves native unaligned halfword/word request loads.

The actual normal Clang object passes 26,064 pairs in each of two modes:
modeled legacy TX and actual native/C short-TX wrappers. The latter verifies
the 32-byte SDK TX depth, including the packet and legacy wrapper frames.
Coverage includes:

- Null/closed guards, raw status patterns, length/register boundaries and
  unaligned requests.
- Partial saved-word replacement, mutated frame words, six input-pointer
  locations including the exposed frame, and 384 request/frame alias cases.
- Provider arguments/order, R4–R11 at provider entry, returned R0/R2/R3, shared
  state, final saved registers, SP and interrupt masks.

Six mutation controls reject incorrect short/bulk status mapping, opaque-word
loss, stale word restoration, swapped transfer bytes and register truncation.
A seventh rejects the previous packet-write bridges: their bulk-provider
depth is 40 bytes rather than the native 16. Bulk register-write adapters,
SDK operations and waits remain modeled in these tests. Actual-wrapper mode
executes only the short-write legacy TX code. It does not establish physical
bus, DMA or IRQ behavior. Arbitrary private-stack destinations, unmodeled
faults, concurrent access, APSR and other raw caller-clobbered values remain
outside this proof.

The SP annotation is compiler-specific. The initial GCC probe emitted moves
into reserved SP for the empty output and faulted. The helpers now use GCC's
`__builtin_stack_save` for a read-only capture, leaving the Clang object
identical. GCC `Os`/`O2` diagnostic probes compile but use 32-byte frames, so
they still fail the ABI checks and do not inherit Clang validation. Their
probe-only `-Wno-error=unused-parameter` accommodates pinned SDK SVC
declarations; product warning policy is unchanged. Strict GCC qualification
fails on those declarations.

All 577 R1 units compile without failures or duplicate strong symbols. The
other 576 objects and strong symbol sets are unchanged. Packet-read code and
relocations are identical; register-transfer adapters are unchanged. Imports
remain 164 application and 34 bootloader symbols. The manifest changes only
the target unit's SRAM flag and note.

Official qualification compiles all 20 generic variants but selects no
regions; all 12 strict GCC variants fail. The source plan is unchanged. The
canonical hybrid retains locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,035 source-built bytes, 642,125 retained executable bytes and 248
resource bytes. Source-built totals include assembly/data. Complete source
firmware and packet-write byte identity remain unproven.

The [machine-readable receipt](twi-packet-write-c-review.json) records REA,
execution, compiler failures, controls, qualification and audits. Probes are
under `build/goal-r1-twi-packet-write-c/`.

The subsequent [shared SP observation review](native-stack-c-review.md) centralizes read-only SP capture and removes the unsafe GCC output form. Normal Clang objects remain identical; this does not close the GCC consumer frame gap.

The subsequent [register-write C review](twi-register-write-c-review.md) replaces both register-write bridges while preserving the length-80 overlap. Read function bytes and relocations are unchanged. The actual bulk packet/register/legacy-TX C chain passes 9,000 comparisons at native SDK depth 136.
