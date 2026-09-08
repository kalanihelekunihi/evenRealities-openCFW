# GRUS asynchronous task submission candidate

The original routine at package0xf2ec / runtime0x10205d60 occupies200 bytes.
The candidate uses the authenticated NationalChip SDK GX_SNPU_TASK and
GX_SNPU_CALLBACK declarations, with assertions for the32-byte GRUS layout.
The native macOS build now emits188 bytes. It is not qualified or admitted.
The initial304-byte array-index version and276-byte address version were
replaced by a single record pointer, allowing compact constant-offset stores.

The function rejects a null task, uninitialized register pointer at5c4, or
full ten-entry ring: signed remainder of wrapping(end+1) equals start.
It reloads end before selecting record=end*144. At record+90 it stores callback,
reads module_id, stores private_data at98, and then transfers task fields in
the exact observed order. Base payload slots0..6 contain ops,data,cmd,input,
output,tmp_mem,weight. Slot7 stores the masked address of record+16; slot8
stores0xfffffffe. Slot8's full purpose remains to be explained; it is not
counted as understood model data merely because its value is reproduced.

The command at record+16 is completion-interrupt+absolute-link+idle and its
link points to itself. The final base command's link at84 points to task.cmd.
After stores it reloads end, advances modulo10, checks state, conditionally
calls internal resume, and submits record+16. Helper results are ignored;
success returns0, failure returns-1. Source pushes8 bytes only on success;
stock pushes8 on entry. Both preserve callee registers and original SP.

Next qualify decoded stock/source reads, writes, all valid ring indices,
null/uninitialized/full rejection, state values, wrapping, callbacks and
private-data bit patterns, helper clobbers/state mutations and untouched
memory. Task pointers currently use ordinary upstream fields; emitted load
order is visible and must be tested. Invalid pointers/indices do not acquire
validity merely through an interpreter. submit_task at10205a00 still needs
separate recovery. No firmware package change from this candidate.

## Initial target qualification

model_gx8002_snpu_run_task.py provides an independent ordered read/write
model with guarded driver memory and distinct task fields. The decoded
verifier passes1,802 cases: all100 valid ring positions, three states,
helper mutation on/off and three seed patterns, plus null/uninitialized
rejection. Six model tests and seven target tests pass, including callback
and private-data bit patterns and mutations of descriptor offset, helper,
frame and write location. Source and stock failure-frame differences are
accepted only when the callee-preserved ABI and final SP agree.

Report saved but no integration yet. Helper calls currently use modeled
boundaries: composed execution with decoded submit/cache routines remains
pending. Slot8 payload0xfffffffe still requires full semantic explanation.
The finite valid-ring model does not claim behavior for corrupted indices,
invalid task pointers or asynchronous memory changes between ordinary reads.

## Shared-state outer/publication composition

The decoded run_task and submit_task interpreters now accept injected memory
models; submit_task also accepts the caller's nested stack location. Existing
default qualifications still pass. verify_gx8002_run_submit_composition.py
checks 9,600 cases: all valid start/end ring indices, three states, previous
link presence, completion presence, two seeds and four stock/source pairings.
Descriptor construction and publication share the same driver/task words and
ordered trace. The independent outer and submission models compose against
the same memory layout for comparison.

Five focused tests check shared descriptor/tail contents, appended link writes,
full-ring rejection, modeled resume clearing and a mutated nested head pointer.
Resume's driver-word clears are modeled; its hardware body and the publication
hardware helpers are not decoded in this composition. Asynchronous mutation
and hardware cache coherence remain separate. This evidence does not admit
the outer function into the firmware build by itself.

## Decoded cache composition and integration admission

verify_gx8002_run_submit_cache_composition.py passes 38,400 cases across all
sixteen stock/source combinations of run_task, submit_task, descriptor-cache
wrapper and lower cleaner. Task/driver memory is shared; nested SP values are
passed through all calls; ordered MMIO is compared alongside descriptor and
link writes. Four focused tests check flush-before-enable, prior-link store
before clean, full-ring suppression and corrupted cache opcode detection.
The three composition suites pass all 15 tests. Existing 9,600 outer/submit
and 2,304 submit/cache baselines were rerun and their hash pins refreshed.

Resume's state effects and NPU register helpers remain modeled here; physical
cache coherency is not simulated. The 188-byte recovered outer function is
now registered for the integration build, occupying its 200-byte original
envelope. Full macOS integration is running; the previous 571-test package
remains the last verified packaged artifact until that run completes.

Integration completed: all 593 native macOS tests pass. Full EVENOTA build
and verify-artifacts succeed with apple-clang; package size 4,750,780 bytes,
7,822 placed flash regions and zero unresolved regions. Codec SHA-256:
9b199559385fb15ce974cb4242d4c60463b6a4f3e129449957e86d60e7c656f0.
Package SHA-256:
61264d20a0fc02827014e408fb14269516f1c7104247e8416b49d12a7bf78683.
The artifact remains hybrid and hardware-unqualified.
