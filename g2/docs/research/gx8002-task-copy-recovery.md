# GX8002 saved-task copy recovery

The model setter at package `0x121A0` saves LR, moves the incoming pointer to
argument 1, supplies length 32 and destination `0x2002E85C`, calls a copy
routine, and restores LR. This matches the `LvpSetSnpuTask` implementation
in pinned NationalChip SDK commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`,
`lvp/vui/kws/models/alexa/v0.2.0/ctc_model.c`. No SDK implementation was copied
into this source candidate.

Using the existing, hardware-gated XIP translation, its call resolves to
`0x10025738`. The authenticated image-A SRAM mapping places that address at
package `0x1774C`. The 126-byte body has no calls and returns the original
argument 0. If either pointer is unaligned, it copies bytes. Otherwise it
copies groups of 16 bytes, then words, then remaining bytes. The next two
bytes are alignment fill, followed by a different function.

`runtime_gx8002_memcpy.c` reconstructs the alignment dispatch, 16-byte groups,
word loop and byte tail in C. Volatile loads/stores preserve the observed
memory access order; the GCC `may_alias` word type avoids effective-type
assumptions for ordinary RAM. Source and destination must not overlap.
This does not establish a general MMIO-copy contract.

The macOS host test passes 4,128 combinations of pointer alignment and lengths
0 through 257, checking guards, return pointer, contents and source preservation.
The restricted target verifier decodes both the compiled object and the
SHA-authenticated stock body. All 4,128 comparisons match final RAM and return
pointer, plus the complete sequence of memory access addresses, widths and
order. Unsupported instructions and out-of-bounds accesses fail closed.
Stack save/restore is abstract, and finite cases do not prove all-input CPU
or ABI equivalence. Four focused host/interpreter tests pass.

The native macOS C-SKY compiler emits 96 bytes with `-Os` and
`-fno-tree-loop-optimize`. Disabling loop rewriting avoids additional induction
variables while preserving all 4,128 exact access-trace comparisons. The
relocation-free section fits the original 126-byte body at package `0x1774C`.
The experimental builder now emits it at that same entry, with 30 trailing
bytes counted separately as unreachable fill. The existing following alignment
word is untouched. Every compiled branch stays within the 96-byte function;
its return is before the fill. Hardware timing remains unqualified.

This replaces the earlier 210-byte default-optimization candidate and admits
96 compiled bytes to the experimental hybrid, removing 126 retained bytes.
The saved-task setter is now also source-built as described below. No complete source-only or
hardware qualification is claimed.

The [target report](gx8002-memcpy-source-verification.json) records the current
source/object hashes and flags. The [recovery record](gx8002-task-copy-recovery.json)
pins the stock ranges. GCC's pinned `csky.cc` and `csky.md`, alongside the local
Sleigh definitions, support the post-increment store and decrement-branch
semantics used by the interpreter.

## Saved-task setter integration

`runtime_gx8002_model_set_task.c` calls the recovered copy routine with the
pinned upstream task structure and fixed destination. The verifier compiles
and links it at `0x10208C14`, resolving the source copy routine at `0x10025738`.
All 20 linked bytes match stock at package `0x121A0`, including the call and
literal pool. No unresolved relocation remains. This corroborates the existing
runtime translation without claiming hardware boot qualification.

The experimental builder includes both source providers. Another 1,024 host
cases exercise setter copy followed by model task translation and check source
preservation. Twelve relevant tests pass. Because the setter bytes are exact,
the package hash is unchanged while 20 more bytes move from retained stock to
compiled source. Hardware timing and the remaining model runtime stay open.
