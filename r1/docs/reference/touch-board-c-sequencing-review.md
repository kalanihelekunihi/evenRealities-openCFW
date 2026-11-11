# Touch board sequencing and ready callback reconstructed in C

`native_touch_board.c` now supplies five stock entry contracts, with one new
owner for the observed active byte (`0x200067f8`) and one for the ready callback
word (`0x20006808`). Existing bus/output/input cached handles and task/thread
state retain their original C owners; intervening context bytes are not claimed.

| Entry | C symbol | Observed policy |
| --- | --- | --- |
| `0x93404` | `r1_touch_ready_callback_setter` | Reject zero without changing the old word; otherwise store input and return one |
| `0x933fc` | `r1_touch_ready_irq_callback` | Tail-forward event flag one through the existing task-event provider |
| `0x4eb80` | `r1_touch_board_open` | Skip setup for any nonzero active byte; otherwise run the full line/delay/registration sequence and set active one last |
| `0x4ebdc` | `r1_touch_power_on_step` | Historical name: actual native operations release the LDO then select output slot `0x18` zero |
| `0x4eb60` | `r1_touch_pending_flag_consume` | For nonzero active, clear it first, stop input and tail-enter the power step; otherwise preserve the context-address return role |

REA and raw instructions establish these policies. The IRQ wrapper's old
eight-byte envelope includes padding; its executed body is six bytes, now
recorded as a manual frontier supplement. Decompiler void return annotations
do not capture all observable R0 words: open returns the original nonzero byte
or one after setup; inactive consume returns the context address. C retains
that address as its relocated active-byte owner, without claiming final placement.

Cold open performs LDO acquire, RTOS delay ten, input stop, output selector one,
output selector zero, delay 130, output selector one, delay ten, output close,
delay twenty, input open, fresh input/callback reads and slot `0x20` registration
with selector one, then delay twenty. Only after that does it store active one.
Method/OS results do not short-circuit this sequence. IRQ forwarding reuses the
existing C task-event routine and thread-handle owner.

The probe passes 12,800 paired stock/C cases (25,600 executions), covering all
five contracts, active bytes 0/1/2/255, four callback input kinds, sequential
mutations, null/non-null thread and input handles, missing device methods and
full result words. It executes actual setter, board policy, registry dispatcher,
IRQ wrapper and task-event forwarder; device/line helpers and OS calls are
modeled. When registration receives the known ready IRQ target, the probe
also delivers it through actual native/C forwarding to the modeled OS flag API.
It compares ordered state/handle/callback accesses, complete call arguments,
return roles/words and preserved registers/stack/masks. Modeled helper entries
use emulator-only BX-LR return stubs to avoid a Unicorn hook/Thumb-IT redirection
artifact; firmware evidence and produced source ELF files remain unmodified.

Negative controls for null-clearing the setter, marking active before setup,
and hoisting callback before input open all fail. The normal report
`build/sources-goal-r1-touch-board/report.json` compiles 573 R1 units without
failures or duplicate strong symbols. Imports remain 197 application and
34 bootloader. `make sources-check` passes.
[Machine evidence](touch-board-c-sequencing-review.json) binds REA, C owners,
probe, negative controls and normal build by hash.

A material remaining gap is explicit: native input/callback capture uses one
LDRD instruction, while the separate C fields currently produce separate loads.
Sequential callback mutations are covered; equivalent behavior under concurrent
updates is not established. This must be resolved or proved irrelevant before
claiming full hardware equivalence. Concrete callback validity, private frames/
caller-clobbered flags/registers, actual IRQ exception behavior, electrical/RTOS
timing and startup placement also remain unverified.

Default C sizes are 22/6/108/14/36 bytes for setter/IRQ/open/power-step/consume,
versus native 12/6/86/14/28 instruction bytes. No byte qualification was performed.
The canonical plan remains at 3,827 source-built bytes in the last verified
hybrid. Complete source-only byte identity and G2 corpus gates remain outstanding.
