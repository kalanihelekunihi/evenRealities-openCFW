# gxDNN command-model reference

Official repository: https://github.com/NationalChip/gxDNN
Pinned commit: 0637b47c8fa0031f8f5651a903cd7d14716382fd.

inspect_gxdnn_cmodel.py authenticates grus/lib/libcmodel.a against the Git
blob and records member hashes in gx8002-gxdnn-cmodel-inventory.json. Native
macOS LLVM tools disassemble its ELF64 x86-64 objects under build/gxdnn-analysis.
These objects are inspection references only; none is executed or linked into
firmware. This discovery does not establish macOS support for upstream tools.

Initial decoded evidence in cmd_parse.o: get_cmd_type classifies low-byte
opcodes 0x80..0x8f as base commands. parse_base_cmd subtracts 0x80 to obtain
a base slot and stores its payload pointer in the context base table. This
supports interpreting TCB words 0x10080..0x10088 as base-slot commands 0..8.

parse_next_cmd extracts header bits 22, 16 and 17. Bit 17 selects sequential
advancement versus an explicit link. In the linked path, bit 16 selects a
host absolute pointer versus a 32-bit relative value transformed to an
absolute address. This is a host model with 64-bit pointers: payload offsets
and command sizes must not be copied into the 32-bit target format.

Bit 22 and opcode 0xff still need interpretation. Next inspect cmd_process.o,
cmd_link.o and transform_rel_to_abs, then corroborate against target descriptor
writes before introducing semantic encoders. The TCB candidate remains
unqualified; this evidence is not complete command/model source recovery.


## Execution-model corroboration

cmd_process.o offsets 0xa7..0xd3 test context byte 0 (header bit 22),
record the current command with cm_set_over_addr, and call cm_send_int with
argument 1. Thus bit 22 requests a command-completion interrupt. The model
suppresses that repeated notification when parse_next_cmd reports the same
command address. At 0x140 it recognizes enum 9 (opcode 0xff); the self-link
path at 0x3c0 queries idle type, sends interrupt 0x10 and either waits or
sends interrupt 8 and returns. Opcode 0xff has no arithmetic dispatch.
The name IDLE in the TCB candidate describes this observed behavior, not
an asserted upstream identifier. Other effects on physical silicon remain
unqualified.

transform_rel_to_abs uses the high four bits as a base-slot index and adds
the low 28 bits to that host base pointer. This is distinct from the target
initializer's absolute-link bus-address masking; do not reinterpret the
latter as a relative link simply because both use a 28-bit mask.

The candidate now names base-slot opcode, absolute-link bit, completion
interrupt bit and idle opcode. Its native macOS build remains 108 bytes in
a 124-byte envelope. It is still not admitted: ordered target writes,
untouched memory and ABI require qualification. No gxDNN binary is included.

## Immediate-operand sentinel evidence

calc.o calc_op_copy offsets16..2c resolve source and destination, then compare
the resolved source pointer with host-width -2. Normal path8b loads a16-bit
source element. Sentinel path102..14c instead loads the16-bit immediate at
parsed-command+24hex and writes it to destination. The source is not read.

calc_op_tensor_tensor independently compares both resolved source pointers
against -2 at a1 and b4. Branches170 and160 load the16-bit command immediate
at+2chex into the corresponding operand register instead of reading memory.
This supports an immediate-operand sentinel rather than a null/error pointer.

The target run_task stores0xfffffffe as base-slot8's payload. Combined with
base-index addressing, the natural interpretation is that slot8+offset0
selects the immediate operand. This target mapping is an inference: the host
model compares64-bit -2, while target payloads are32-bit. Do not claim that
this proves conversion/sign-extension in the host driver or silicon. Future
model-command decoding should corroborate slot8 references (0x80000000) and
embedded constants before declaring the descriptor fully explained.

## Shipped model chain corroboration

analyze_gx8002_model_command_chain.py authenticates the9164-byte block at
package18d90 (SHA c38ed6d22c7c0b6178288678364acd10bd5730aa382c1e19a32f6cf2bd1430b9).
The upstream sequential command sizes walk211 commands, followed by a final
48-byte linked opcode1 command at239chex. Its relative link70000000 resolves
to base slot7 offset0. That slot is assigned the completion descriptor by
run_task. Total212 commands cover the block exactly:185 opcode1, five41hex,
four40hex, four42hex and fourteen43hex. Full rows are recorded in
 gx8002-model-command-chain.json. No firmware data is produced.

No aligned word equals80000000 in this model block. Thus this model does not
directly corroborate the inferred slot8 immediate sentinel. Words whose top
nibble is8 can also be packed parameters; do not classify them as addresses
without decoding their command field. Command payloads and weights still
require semantic recovery; exact boundary coverage is not source completion.

## General-operation subtypes and copy fields

cmd_process reads low4bits at payload+10hex for opcode1. Branches160..1d4
and678..7a3 map0 active,1 pool,2 copy,3 reduce,4 tensor_vector,5 tensor_tensor,
6 tensor_scalar,7 format,8 bn. Shipped counts are123copy,20tensor_vector,
18bn,13active,9tensor_tensor,1reduce,1format. Other27 commands remain grouped
by top-level opcode; no general-operation subtype is inferred for them.

parse_op_copy_cmd reads source word atpayload0, destination atchex;
payload14hex contains extents12/12/8bits. Halfwords1a/18 and1e/1c are source
and destination outer/middle element strides; inner stride1 is explicit in
calc_op_copy. Halfword20hex is the immediate16bit value. calc_op_copy's
indexed loads/stores multiply element indices by2. The analyzer now records
these fields for all123copies. Example: firstcopy transfers extents1,1,64
fromslot1+256 toslot1+2816, source strides896,896,1 and destination1024,1024,1.

This is read-only semantic extraction for reconstruction evidence. No arrays
of copied command bytes are added to firmware. Reserved fields, other numeric
operators, tensor lifetime/aliasing, weights and whole-model behavior still
need recovery before a source-authored model can be admitted.

## Copy access geometry

analyze_gx8002_model_copy_ranges.py enumerates each two-byte element in the
123 decoded copies (at most64 elements per command). Slot pairs:55 from1to1,
10 from3to1,58 from1to4. Maximum accessed byte ends imply copy-only minimum
slot sizes: slot1=13056,slot3=8464,slot4=7424. These are lower bounds, not
allocation proofs; other operators can access larger ranges.

No same-slot destination write overlaps any later source read. The check
uses byte intersections, including odd offsets, and preserves element order.
Five tests cover forward/backward/odd overlap, separate-slot treatment and
shipped counts. Distinct slots may alias in real task pointers; this analysis
does not rule out that case. Report gx8002-model-copy-ranges.json remains
source_admitted=false. No firmware bytes or model replacement are produced.

## Tensor operand fields

parse_op_tensor_vector_cmd and parse_op_tensor_tensor_cmd both extract
sourceA atpayload0, sourceB at4, destination atchex; extents from14hex as
12/12/8bits; stride halfwords1a/18 and1e/1c; immediate at20hex. Their operation
selectors differ: vector uses controlword10hex bits9..10, tensor uses11..12.
All29 shipped operations now carry these decoded fields in the chain report.
Vector selectors:18zero,1one,1three. Tensor selectors:8zero,1two.

The report deliberately calls stride values fields until each operation's
indexing/broadcast behavior is traced. calc_op_tensor_tensor resolves three
relative operands and calls choose_calc_func with the parsed selector. The
latter uses a relocation-backed jump table: do not assign arithmetic names
from familiar ordering without decoding that table. Arithmetic precision,
broadcasting, flags and remaining payload bits remain unresolved.

## Arithmetic dispatch resolved

analyze_gxdnn_arithmetic_dispatch.py authenticates calc.o and resolves its
seven PC-relative jump-table relocations. Because execution adds the table
base, target offset equals relocation addend minus entry offset. Targets
70,80,20,30,40,50,60hex return calc_add/sub/mul/div/pow/exp/log respectively.
Selectors0..6 therefore map add,sub,mul,div,pow,exp,log. Evidence rows saved
in gx8002-gxdnn-arithmetic-dispatch.json; chain analyzer consumes this mapping.

The29 shipped tensor operations now classify as26add,1sub,1mul,1div. These
are host-model operation identities, not numerical-equivalence proofs. The
half_float16 helper implementations, rounding/overflow and hardware behavior
remain to be recovered and qualified. No upstream binary enters firmware.

## Tensor indexing and broadcast

calc_op_tensor_vector at91..b9 computes sourceA element index i*stride0 +
j*stride1 + k. SourceB atce uses k alone, broadcasting over i,j. Destination
d3..ed uses its own two outer strides plus k. Each element is two bytes.
calc_op_tensor_tensor uses the source-stride expression for both operands.
The chain report now records explicit three-dimensional strides.

Tensor-only range analysis reports slot3 minimum1040 bytes, slot1 minimum7380
and slot6 minimum120800. The latter exactly equals the declared weight block
size, corroborating the addressing interpretation without proving numeric
behavior. Two tests check multidimensional broadcast and the shipped extent.
No new payload is generated; runtime aliasing and other operation ranges
remain unresolved. See gx8002-model-tensor-ranges.json.

## Half arithmetic upstream lead

float16.o is compiled from float16.cpp and contains half_float::detail
half2float_impl and float2half_impl template symbols, including conversion
mantissa/exponent/offset tables. half_float16_add decodes both half operands
through those tables, performs x86 ADDSS (binary32), and calls
float2half_impl<float_round_style1>. This is a concrete library fingerprint,
not proof of exact release or numerical equivalence on target hardware.

Primary upstream documentation: https://half.sourceforge.net/ and
https://half.sourceforge.net/half_8hpp_source.html (2.2.1, Christian Rau,
MIT-style license). The current header shares namespace/function names;
exact historical matching is pending. Current release is not automatically
a compatible replacement: pin and compare conversions/rounding/NaNs before
using it as a model oracle or source dependency. The host archive also has
131072-byte exp_lut and ln_lut tables; these remain reference-only and must
not be pulled through as opaque model data. No new dependency is integrated.

## Pinned half source table match

Fetched https://github.com/ROCm/half at
207ee58595a64b5c4a70df221f1e6e704b807811 (header identifies1.12.0).
analyze_gxdnn_half_tables.py checks checkout bytes against the pinned Git
blob and authenticates reference float16.o. All five conversion tables match:
base1024bytes,shift512,mantissa8192,exponent256,offset128. Individual hashes
and header hash are in gx8002-half-table-matches.json. Source is a concrete
match for tables, not proof of the exact original release or rounding flags.

Next compare conversion code, especially HALF_ROUND_TIES_TO_EVEN and NaN,
subnormal, overflow behavior, using source built on macOS. No library or table
has been added to firmware; reference blobs remain inspection-only.

## Conversion rounding configuration verified on macOS

The reference float2half routine at5a..6e computes discarded-low-bit or odd
retained-bit gating, matching HALF_ROUND_TIES_TO_EVEN=1. The pinned header's
default is0 (ties away), so its default configuration is not equivalent.
verify_gxdnn_half_rounding.py builds a native macOS clang++ probe with the
explicit setting and compares104556 inputs against the decoded instruction
formula and already-matched tables. Inputs include all signed exponent
encodings, rounding-boundary neighbors, special-value patterns and100000
reproducible pseudorandom bit patterns. All match.

This does not execute the x86 archive, nor prove all2^32 conversions or NPU
silicon behavior. It validates the configured upstream conversion source as
a reference lead. No probe/library bytes enter firmware. Arithmetic, exp/ln
lookup generation and whole-model numerical behavior remain unresolved.

## Exhaustive half expansion

verify_gxdnn_half_expansion.py builds the pinned half source with native
macOS clang++ and compares all65536 input encodings against the authenticated
reference table formula. Every binary32 result bit matches, including signed
zero, subnormals, infinities and NaN payloads. Report saved as
 gx8002-half-expansion-verification.json. The comparison is exhaustive for
conversion inputs, not for arithmetic or physical NPU behavior. No opaque
archive is executed or included in firmware.

## Native source arithmetic reference

reference_gxdnn_half_arithmetic.cpp supplies a macOS stdin/stdout reference
for selectors0..3. It uses the pinned conversion source, binary32 intermediate
operations, explicit ties-to-even, and no fast-math or contraction. Build:

    xcrun clang++ -std=c++11 -O2 -ffp-contract=off -fno-fast-math -Ibuild/upstream-rocm-half/include tools/reference_gxdnn_half_arithmetic.cpp -o build/gxdnn-analysis/half-arithmetic-reference

Input records are three native uint16 words (selector,A,B), output oneuint16.
Both the current Mac and recorded binary inputs are little endian. Sub/div
reference disassembly decodes A fromrdi into the first binary32 temporary
and B fromrsi into the second: operand order is A-B and A/B. calc_sub/div do
not swap arguments. Eight known-answer tests passed for1+2,1-2,1*2,1/2,
two tie cases, signedzero multiplication and smallest-subnormal addition.
These are smoke checks, not exhaustive arithmetic equivalence. NaN payload
selection can be CPU-dependent; hardware NPU behavior remains unresolved.
No reference program/library bytes are part of the firmware package.

## Finite arithmetic comparison

verify_gxdnn_half_arithmetic.py builds the native reference reproducibly and
checks113072 operation/input cases against Python IEEE pack/unpack conversion
through binary32 and binary16. All match. Samples include signed zeros,
subnormal transitions, values around1, maximum finite values, half overflow
and reproducible pseudorandom finite pairs. Division by zero and NaN operands
are excluded. This finite comparison does not prove all pairs or NPU results;
Python binary64 arithmetic is an independent check with stated precision
limits. No library is admitted to firmware on this evidence alone.

## Special-value observation boundary

observe_gxdnn_half_specials.py authenticates/rebuilds the native reference,
reruns the finite baseline and records324 special-value combinations. Four
signed nonzero divided by signedzero results independently match signed
infinity. NaN-containing cases are observations only, not verified expected
outputs. Their payload/sign propagation is architecture dependent; no NPU
compatibility is inferred. Sourcehash and upstreamcommit accompany the report.
