# Command-chain publication candidates

Original submit_task: package0xef8c, runtime0x10205a00, envelope144 bytes.
The reconstructed C builds natively on macOS in124 bytes. It remains
unqualified and unregistered. Original and source use20-byte frames.

The state tail pointer is at5c0. A zero tail sets state BUSY(1), sets the
hardware head to low28bits(descriptor+16), cleans the new descriptor, enables
NPU through a freshly loaded register pointer5c4, and stores the new tail.

For nonzero tail and STALL(2), read the completed command through the NPU
getter. Zero completion follows the start path. Nonzero completion first
reloads the tail and links its word+4 to the new base-command block, then
loads the restart head at completed+0x20000004. It sets BUSY and follows the
same set-head/clean/enable sequence. Source omits stock's otherwise local
scratch rewrite from completion bus address to mapped address; qualification
must distinguish scratch state from observable memory/calls.

For nonzero tail and any state other than2, clean the new descriptor first,
reload the current tail, update its link word+4, and clean8 bytes of that
previous descriptor. Finally replace state tail with the submitted descriptor.
No extra cache operations or idle waits are inferred. Every helper call can
clobber caller registers; state pointers may change across helper boundaries.

The cache wrapper at package0xef74/runtime0x102059e8 cleans8 bytes at the
supplied descriptor, then108 bytes at descriptor+16 (nine12-byte base
commands). Native source builds22 bytes in24. Its helper is
NationalChip gx_dcache_clean_range at runtime0x10025664, established by SDK
relocations and target branch decoding. Wrapper and helper need separate
qualification before any admission. Physical cache coherence is not proved
by matching wrapper arguments alone.

Files: runtime_gx8002_snpu_submit_task.c,
runtime_gx8002_snpu_task_cmd_cache_flush.c, corresponding build_*_candidate.py
scripts, candidate reports and disassemblies under build/gx8002-board.
Next compare all branches with live state reloads, distinct old/new tails,
completed head memory, helper clobbers, scratch initialization and ABI;
compose with the outer run_task candidate when both are qualified.

## Cache-wrapper qualification

verify_gx8002_snpu_task_cmd_cache_flush.py now passes2,485 decoded comparison
cases and seven tests. It verifies both helper targets, ordered address/length
arguments, observed final r0, conservative caller clobbers and8-byte frame.
Pointer tests include boundary wrapping as arithmetic tests only. Mutation
tests reject incorrect lengths, offsets, targets, frame and saved pointer.
Reviewed report saved; registration/integration remain pending.

The lower helper10025664 maps to package17678 and remains retained stock.
Its92-byte envelope ends176d4. It aligns address down to16, ORs command8,
compares signed size against128, emits eight writes to e000f004 per128-byte
chunk, then emits16-byte steps while signed remaining size is positive.
Upstream include/driver/gx_dcache.h declares size int32_t. Negative sizes
therefore issue no writes. Initial misalignment is discarded rather than
added to the size: do not silently replace this behavior with a generic
round-up-range implementation. The adjacent routine176d4 uses command10;
its identity/ownership needs separate evidence. No hardware coherence claim.

## Publication-helper qualification

The independent model_gx8002_snpu_submit_task.py and decoded target verifier
now pass3,360 cases and eight tests. Cases vary descriptor, tail presence,
state, completion presence, restart-head patterns and live state mutations.
Every helper can replace the register pointer and tail. Ordered model traces
check link reads/writes, start/restart/append calls and final tail publication.
Both target interpreters enforce20-byte frame, initialized scratch output,
helper targets and caller clobbers. Mutation tests cover wrong command offset,
state test, helper target and return frame. Full run_task composition and
physical cache effects remain separate. The reviewed report is saved; this
helper is not registered in the integration build yet.

Cache integration checkpoint: the descriptor-cache wrapper and lower
cache-clean routine are now integrated, with 557 passing native macOS tests.
The publication helper itself remains qualified but unregistered.

## Decoded cache composition

verify_gx8002_descriptor_cache_composition.py now executes the wrapper's
calls through the decoded lower cache-clean loops, using the nested stack
location. All72 combinations pass exact ordered MMIO: stock/source wrapper
crossed with stock/source lower helper, six address cases and three seeds.
Caller-clobbered registers remain conservatively synthesized after each
call, so this is boundary composition rather than instruction-level transfer
of every scratch register. Void returns are excluded. Existing15 cache
unit tests remain the baseline. Physical cache coherence remains unproven.

## Submission through decoded cache loops

The submission/cache composition verifier now passes 2,304 cases: three
valid descriptor locations, tail presence, four state values, completion
presence, live helper mutations and three register seeds, each across all
eight stock/source combinations of submission, descriptor wrapper and lower
cache cleaner. Ordered MMIO is compared together with link writes and final
state. The report pins all participating verifier and state-model sources.
Six additional tests cover enable ordering, live mutation, wrong publication
pointer, wrong descriptor offset, wrong cache operation and wrong MMIO port.
Together with the existing three routine suites, all 29 focused tests pass.

The reconstructed C declaration of the lower cleaner now uses its recovered
signed length type. Both call sites pass positive constant lengths, so this
prototype correction does not change emitted instructions. The submission
helper is registered for integration; the full macOS build must still pass
before a new packaged artifact is reported. Outer run_task composition and
physical cache coherence remain outstanding.

Integration completed: 571 tests pass, and the full 4,750,780-byte EVENOTA
package builds and verifies using apple-clang on macOS. Codec SHA-256:
714a6772dfaf9e6c4fb1edf8674cb01d8dbcc2ee2398dd04c600ad26a00f0082.
Package SHA-256:
46f29763e9a54774bde100ed068f70cfdfbb2cb3b926ebf3d978cc95595783c2.
The helper contributes 124 C bytes and 20 unreachable padding bytes. This
is still an experimental hybrid, with no hardware qualification.
