# TWIM0/1 interrupt and completeness C source routes

Both stock TWIM IRQ entries now route to the existing, unchanged pinned Nordic
SDK `nrfx_twim.c` vector symbols. Their common dispatcher `0x939a0` and transfer
completeness helper `0x98dc0` also have tested C source routes. REA covers the
8/10-byte stubs, 400-byte dispatcher and 98-byte helper. Application vectors
19/20 contain `0x31a75`/`0x31a85`. No firmware source unit, implementation, state
owner, compiler flag or manifest is added or changed.

Assertions compiled against the actual SDK types confirm two 52-byte control
blocks, indices zero/one, all fourteen field offsets and a 24-byte event. The
fixture links the existing C object and its static array at native `0x2002c1e8`
(second instance `0x2002c21c`). This controlled binding does not prove a final
firmware link address. The actual native/C dispatcher and completeness helper
execute; event-clear, copy and NVIC instructions are not replaced by helper stubs.

The checks cover error-to-STOP recovery, STOPPED completion and the suspended
TX/TXTX paths. Incomplete EasyDMA byte counts reset ENABLE from zero to six and
set the software error. TXTX amount selection follows its stage interrupt mask.
Error priority matches address NACK, data NACK, overrun, software bus error, then
DONE. Repeated transfers retain busy; ordinary completion releases it. Suppressed
success callbacks remain suppressed, while errors can still invoke the handler.
Callback changes to handler/context, busy, repeat flags and pending error/STOPPED
state are observed on the next manually delivered IRQ.

86,528 paired two-IRQ sequences pass (173,056 invocations): 81,920 base sequences
and 4,608 callback-mutation sequences. Domains span both instances, all sixteen
combinations of ERROR/STOPPED/SUSPENDED/LASTTX inputs, all four transfer types,
handler-suppression/spurious-stop flags, prior error/repeated states, four DMA
count pairs, five ERRORSRC values and LASTTX_STOP shortcut presence. Another 512
two-IRQ sequences (1,024 invocations) exercise the second TXTX stage explicitly.
Total: 174,080 paired IRQ invocations.

Ordered peripheral/NVIC reads and writes, meaningful callback data, callback
control-block snapshots, final driver/register memory, callee registers on return,
SP, interrupt masks and state guards match. Six negative controls reject retained
busy, missing error STOP, wrong NACK event type, missing incomplete-transfer reset,
wrong copied length and the wrong TXTX secondary-stage length test.

Stock callback frames are 64 bytes versus C's 48 bytes. Private event addresses,
padding and live provider registers are not treated as equal. When successful
handlers are suppressed but an error forces a callback, stock and SDK do not
initialize the event descriptor; those private bytes are excluded. Event type,
context and driver state are still compared. This does not prove complete raw ABI
identity. Controlled register inputs include unusual combinations; they do not
claim that real hardware autonomously produces every combination.

INTENSET/CLR and ERRORSRC aliases are modeled. Later STOPPED is delivered by the
fixture for recovery sequences. Physical I2C/EasyDMA traffic, peripheral timing,
actual interrupt/exception delivery, arbitrary aliases, faults and concurrency
remain unproven. Memory hooks are restricted to MMIO/NVIC: a global-hook observer
effect and independent checks without memory hooks are documented in
[the IRQ observer review](irq-observer-review.md). Full bounded-hook replays of
the prior four IRQ matrices also pass there.

Qualification compiles the SDK unit and selects no exact regions. All 589 normal
source/object hashes and the manifest were revalidated against the prior passing
R1 report, with 164 application / 34 bootloader imports and no compile failures or
duplicate strong symbols. The existing canonical hybrid and source-plan hash are
unchanged: 4,245 source-built, 641,915 executable fallback and 248 resource bytes.
Source-built includes admitted assembly/data. The locked application SHA remains
intact; complete source-only rebuilding and byte-identical C reconstruction are
unproven.

Machine-readable evidence: `twim-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-twim-irq-c/`.
