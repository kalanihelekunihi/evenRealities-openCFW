# DW SPI quick-transfer recovery

The authenticated SDK section `.text.dw_spi_quick_transfer` matches all 634
stock bytes at package 0xf790 / runtime 0x10206204 after relocating its two
calls to `gx_clock_set_module_enable` at 0x10025080. The source object is pinned
to SDK commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 and blob
600d763a219007e2af7b5006989d44984abf0861. The relocation list has exactly two
PC-relative calls, at section offsets 24 and 100. No BSS binding is required.
`analyze_gx8002_dw_spi_quick_transfer.py` reproduces full identity on macOS;
its linked SDK output is comparison-only and is not a firmware provider.

Initial decoded state findings to preserve during C reconstruction:

- Load device->master->driver_data and zero message.actual_length before
  testing private state offset 0x10 for an active message. Store message.spi.
- The already-active branch skips clock enable and goes directly to the shared
  return path, which clears private words at 0x10 and 0x14 and returns zero.
  This is observed behavior, not an inferred successful transfer or a proposed
  concurrency guarantee. Do not silently replace it with a busy error.
- The idle path records the message, enables clock module 14, and writes 2 to
  absolute 0xa030008c. The normal/error clock shutdown path writes 3 there and
  disables module 14 before clearing those private words.
- Transfer-list entries use a 24-byte list-node offset. Buffer and length
  alignment failures converge on return -22 with clock shutdown.
- The tail contains byte, halfword and word receive stores from controller
  offset 0x60. Their post-increment instructions must be modeled explicitly.

These are partial semantic findings, not source admission. Full send/receive
loops, FIFO behavior, transfer defaults, malformed lists and hardware effects
still require reconstruction and qualification. No C replacement is emitted
by the attribution tool.

## Exhaustive width-selection evidence

`analyze_gx8002_spi_transfer_width.py` executes the attributed width-selection
instructions for all 256 possible input bytes and checks an independently
expressed arithmetic mapping. Zero selects/stores 8 bits and one byte. Inputs
1–8 use one byte; 9–16 use two; 17–32 use four (the rounded 24-bit case is
explicitly remapped to 32 bits). Inputs 33–248 produce widths 5–31, for which
the later transfer loop has no matching byte/halfword/word data-access branch.
Inputs 249–255 produce zero and can reach division by zero. The JSON records
all 256 mappings. This is baseline behavior evidence, not an endorsement of
these inputs or admission of a complete transfer replacement.

Additional loop observations: TX waits for status bit 2 and then waits for bit
0 to clear before advancing the transfer list. RX reads the FIFO-level word
at controller +0x24, masks it using twice the private RX-depth word minus one,
and performs width-specific post-increment stores. There is no inferred
software timeout in these observed loops; complete MMIO execution modeling
must distinguish hardware progress from an infinite wait.

## First complete C candidate

The source candidate now builds natively on macOS to 602 bytes within the
634-byte stock envelope. It contains message/transfer traversal, width/default
handling, controller programming, TX FIFO submission and readiness waits, RX
chunking and width-specific stores, alignment failure and common clock/state
cleanup. SDK public types are used with recovered private prefixes. The builder
pins source, SDK headers, stock identity and clock-helper address.

This is a compilation checkpoint only. The candidate is unregistered and has
no decoded transaction/ABI qualification. C expression evaluation order around
volatile controller/configuration reads and data-port accesses must be checked
against stock; do not assume source statement order alone proves those traces.
Malformed widths, non-progressing FIFO states and arithmetic boundary cases
also need explicit modeling. No original code bytes are imported by the C
candidate, but its clock helper remains an external binding.

## Controller-access ordering corrections

Inspection of the first compiled candidate found two trace differences from
stock. The transfer-mode configuration read preceded the controller-pointer
read, and the private word at +0x20 was cleared before loading the controller
pointer used for the following disable. Explicit local controller pointers
now impose the recovered ordering. The regenerated instructions at 0x1020629a
load private +4 before reading config +0x0c and writing controller +0xf0. The
aligned-setup path similarly loads the controller pointer before clearing
private +0x20. Candidate size remains 602 bytes, SHA-256
`0b4d660a735fc0a65583db96567d17f5d5a64d394c62377835ce469f0b1e59d2`.
These inspected corrections do not qualify the remaining transfer paths;
a complete decoded transaction model is still required before admission.

## Scoped lifecycle qualification

The independent lifecycle model and decoded runner now verify busy-entry and
empty-list paths, including message metadata writes, clock/absolute-control
sequencing, common state clearing, return zero and the fixed 28-byte frame.
Four stock/C cases pass. Three focused tests cover these paths and mutations
of the initial message write and clock module. This evidence does not admit
the complete function: nonempty transfer lists, FIFO progress, alignment errors
and data-access ordering remain outside this initial verifier's scope.

The independent alignment-error model now specifies nonempty setup through
controller configuration and common error shutdown, with TX/RX buffer choice,
16-bit divider truncation/clamping and return -22. Four model tests pass.
Aligned requests explicitly require a FIFO model rather than being accepted
by this scoped model. Decoded stock/C comparison for this path is still pending.

Decoded alignment-error verification now passes 280 stock/C cases covering
TX/RX selection, 9/16/17/24/32-bit widths, misaligned lengths and buffer addresses,
and divider truncation/clamping. The common interpreter gained byte accesses,
extensions, arithmetic, division, conditional increments and unsigned maximum.
The earlier four lifecycle cases and seven lifecycle/alignment-model tests
still pass. These scoped proofs remain insufficient for whole-function
admission: aligned FIFO processing, data movement and readiness waits need
independent modeled execution.

Aligned TX replay now passes 12 decoded cases across three widths, FIFO
backpressure and readiness delays. It exposed a byte-buffer read occurring
before the controller-pointer read; an explicit volatile byte access after
the pointer load corrects that difference. Size remains 602 bytes, SHA-256
`964b5afa5ff89a937beda755efe5e1558d669c00643b24796e6ee25cd19a5e8b`.

An independent aligned RX model now specifies receive chunking, empty FIFO
polls, data-port reads and width-truncated stores with advancing buffer
addresses. Five tests pass for 8/16/32-bit stores, multiple chunks, delayed
data, missing data and overrun rejection. This initial model excludes FIFO
overrun behavior rather than interpreting it as success. Decoded RX replay,
multiple transfers per message and whole-function qualification remain open.

Decoded FIFO coverage now passes 160 TX and 160 RX cases. Both cover widths
0/1/8/9/16/17/24/32 bits, element counts 0/1/2/3/17, depths 2/16, and immediate
or delayed FIFO progress. RX includes width-specific post-increment stores and
multi-chunk reads. Sixteen focused lifecycle/model tests pass after extending
the interpreter. Multiple transfers within one message, helper state changes,
and unsupported-input behavior still need qualification before full admission.

Mixed-message replay now passes 252 two/three-transfer combinations of TX,
RX, zero-length and alignment-error transfers. The composed independent trace
keeps message clock setup/shutdown once, remaps distinct list nodes, and stops
at the first error. Three model tests check those boundaries. Each transfer
uses distinct buffer storage: aliased RX/TX buffers require a shared-memory
model and are explicitly rejected, preventing scripted TX reads from assuming
stale data after an earlier RX write. No full-function admission is made yet.

Shared-buffer message coverage now brings the decoded matrix to 270 cases.
An explicit byte-memory model applies RX stores before constructing later TX
reads, including partial overlap and changes of transfer width. Five message
model tests pass, with exact expected bytes for full/partial RX-to-TX overlap.
Shared buffers are kept separate from metadata; conflicting declarations of
initial TX bytes are rejected. This does not establish concurrency, arbitrary
metadata aliasing or helper-induced state mutation.

Five FIFO target-mutation tests now pass: wrong receive store width,
destination and FIFO count, wrong transmit free-space selection, and removed
readiness-mask behavior all fail the independent transaction checks. These
complement the valid TX/RX/message replay rather than merely counting cases.
The clock binding resolves to the already-reconstructed upstream-backed
platform gate; its existing qualification models the separately qualified
lookup. Whole transfer/gate composition remains to be checked explicitly.

Call-boundary transfer/gate composition now passes 36 combinations (stock/C
transfer × stock/C gate × TX/RX/error messages × three source-register values),
executing 72 gate calls. Each gate MMIO trace matches its existing oracle and
writes only the admitted clock-control addresses. Ten lifecycle/FIFO target
tests pass, including hook invocation and propagation of injected helper
failure. This is explicitly not shared nested-stack execution: the gate uses
its existing abstract stack and modeled lookup/table, and transfer caller
register clobbers remain modeled. Hardware clock side effects are unproven.

The aggregate source-qualification report now pins all transfer models,
verifiers, builder, attribution and gate-comparison/link scripts. It reproduces
874 decoded transfer cases and 36 gate-composition combinations and requires
identical candidate evidence across each run. All 28 focused tests pass. The
602-byte C candidate is registered for integration, replacing its complete
634-byte region with separately counted unreachable fill. Source admission
retains the documented valid-buffer/list contract and finite-replay limits;
it does not establish complete firmware functionality or hardware readiness.
