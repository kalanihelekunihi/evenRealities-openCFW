# Recovered three-instance PWM C driver configuration

`r1/src/application/runtime/native_pwm.c` adds the previously unbuilt pinned
Nordic `nrfx_pwm.c` implementation to normal R1 application composition. Its local
configuration enables PWM0/1/2, disables PWM3, disables the DMA anomaly workaround,
and disables logging. Shared SDK configuration and the vendor implementation are
unchanged. Configuration is applied after `nrfx.h` so legacy configuration
translation cannot override the recovered local choices.

REA confirms three eight-byte stock stubs at `0x30ca8`, `0x30cb8`, `0x30cc8`,
using PWM bases `0x4001c000`, `0x40021000`, `0x40022000` and eight-byte control
blocks at `0x2002c2e4`, `0x2002c2ec`, `0x2002c2f4`. Their common dispatcher
`0x72a32` has 156 code bytes. That frontier row previously pointed to the timer
source because of its generic `irq_handler` name; it now points to the PWM wrapper.
Application vectors 44/49/50 corroborate the three entries. PWM3's vector is the
separate default handler `0x274a3`; no fourth instance is introduced.

Assertions compiled against the actual included SDK types confirm three instances,
indices zero through two, and handler/state/flags offsets 0/4/5 in each eight-byte
control block. The fixture binds the actual new C object's 24-byte static array
at the native base. This controlled placement does not establish final linking or
stock cold initialization. No new duplicate state owner is introduced.

12,528 paired two-IRQ sequences pass (25,056 paired invocations): 12,288 base
sequences cover all three instances, all sixteen SEQEND0/SEQEND1/LOOPSDONE/STOPPED
combinations, flags zero through 31, null/non-null handlers, raw event values one
and `0xffffffff`, and initialized/powered states. Another 240 sequences modify
later flags, callback pointers, pending events or state during a callback. They
include STOPPED callbacks re-arming sequence zero for the next IRQ.

Ordered MMIO reads/writes, callback event and control-array snapshots, final
peripheral/driver memory, return callee registers, SP, masks and guards match.
SEQEND callbacks require their signal flag; finished is delivered unless suppressed;
STOPPED sets state initialized and is delivered whenever a handler exists. The
handler pointer is reloaded between events. Six negative controls reject a wrong
sequence flag, inverted finished gate, missing initialized state, wrong STOPPED
event, missing sequence-event clear and a cached callback pointer.

Non-tail callback frames are stock 16 bytes versus C 24 bytes; live callback
registers and private frames are not treated as identical. STOPPED restores incoming
SP and R4-R11 and forwards caller LR in both paths. This is an ordinary-return
fixture, not real exception return. Bounded MMIO hooks avoid the observer issue
documented in `irq-observer-review.md`. Real PWM waveforms, clock behavior,
EasyDMA traffic, physical interrupt delivery, faults, arbitrary aliases and
concurrency remain unproven.

The new unit also compiles init, uninit, simple/complex playback, stop and stopped
query APIs. Their behavior has not been qualified by these IRQ tests. Extra SDK
read-only PWM log metadata is not claimed to match stock data. Neither the vendor
source nor the wrapper introduces executable opcode arrays or inline assembly.

All 590 R1 units compile and compose: 516 application and 74 bootloader. The prior
589 object files are identical; application/bootloader imports remain 164/34 and
there are no duplicate strong symbols. The manifest only adds this one candidate.
Qualification selects no exact regions. A fresh canonical hybrid application
retains its locked SHA with 4,245 source-built, 641,915 executable fallback and
248 resource bytes. Source-built includes admitted assembly/data. The source plan
is unchanged; complete source-only rebuilding and byte-identical C reconstruction
remain unproven.

Machine-readable hashes, observations and pointers: `pwm-c-review.json`.
Reproducible ignored probes: `build/goal-r1-pwm-c/`.
