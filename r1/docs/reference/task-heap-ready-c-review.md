# Native allocator through task readiness in C

Stack initialization now reads the existing source-owned
`r1_native_initial_xpsr` word through a volatile typed C access instead of
hard-coding its initial value. REA confirms that stock entry 0x856c0 loads the
word at 0x9c4cc through a literal pointer; its initial value is 0x01000000.
This restores a real data dependency even though default-value frame tests
could not distinguish the old constant expression. The source constant has
one existing owner in `native_task_construction.c`. No opcode array or
handwritten assembly replacement is introduced.

The ownership entry for `pxPortInitialiseStack` now points to the current
`rtos/task-construction/stack.c`, replacing its removed pre-consolidation path.
Constructor, initializer and ready-handoff entries reference the combined
receipt. [Machine-readable evidence](task-heap-ready-c-review.json) binds the
current sources, REA, probes, earlier component receipts, audit, qualification
and hybrid report by SHA-256. Earlier standalone allocator and constructor
checks remain relevant, including free/coalescing and modeled-null cleanup
branches that these integrated traces do not replace.

The stock and C integration passes 1,288 paired traces containing 1,672 paired
constructor operations (3,344 root executions). Both sides execute their actual
allocator, memory-fill, constructor, initialization, list-item, stack-frame,
ready-insertion and cold list-initialization code. Mixed dynamic/static tasks,
name/depth/priority boundaries and scheduler-state transitions are covered.
Each trace runs at two entry masks and four initial-xPSR word values. The values
are changed only in emulated data memory; the locked artifacts are unchanged.
This tests the stack writer's raw dependency, not whether every test xPSR value
would be valid for starting a physical task.

Complete 51,200-byte heap, heap state/sentinel, scheduler cells, ready lists,
output guards and four static control/stack regions compare. Independent checks
cover task depth/priority/number, names, allocation/notification flags, frame PC
and xPSR, output handles, and fault categories. The matrix checks 16 first-
allocation exhaustion traces, 24 second-allocation exhaustion traces and 16
invalid-priority traces. Actual allocator exhaustion follows the stock fatal
policy, rather than a fabricated null return. Full-pool successful boundary
allocations are included.

Only allocation caller words and task-exit LR words are normalized, after
checking each against its actual allocation-call LR or source-specific exit
function. The C-side instruction hook forbids execution from the mapped stock
code range. Controls that corrupt caller tracking, hard-code xPSR, corrupt its
stored value or lose the task number are rejected. Thus normalization does not
hide those errors.

A further 576 source-only CMSIS traces (704 constructor operations) execute the
actual `osThreadNew` adapter through allocation and task readiness, again with
four xPSR word values. Scheduler-state reads, suspend/resume and critical
boundaries are modeled. In the stock comparisons only suspend/resume and
critical boundaries are modeled; memory fills and allocation execute. Fixed
stock RAM placement is a fixture, not a production linker result. Stable names,
ordinary valid pointers and seeded scheduler state are assumed. Full exception
state, private frames, caller-clobbered words/flags, malformed heap/pointers,
asynchronous context switches and physical scheduling remain unverified.

All 573 R1 units compile without failures or duplicate strong symbols. Only the
stack-initialization object changes; its private task-exit body and every other
object are byte unchanged. Import sets remain 179 application and 34 bootloader.
Five qualification profiles select no exact new region. The unchanged canonical
plan still builds a stock-identical hybrid with 3,857 source-built bytes,
642,303 executable pull-through bytes and 248 resource bytes. Compilation and
bounded source execution do not prove a complete source executable link,
source completeness or hardware operation. No G2 corpus gate advances.
