# uLED callback shared-handle review

REA/Ghidra 12.1.4 checked the locked Apollo main callbacks at 0x592658
(type 0) and 0x5BBD48 (type 1), 40 instruction bytes each. Their handle
cells are 0x20074524 and 0x20074510. Each body follows this sequence:

```text
saved_status := entry_r2               // pushed stack word, not an API argument
saved_r3 := entry_r3
if load_u32(cell) != 0:
    status_get(load_u32(cell), &saved_status, false)
    interrupt_clear(load_u32(cell), saved_status)
    interrupt_service(load_u32(cell), saved_status)
machine_exit_r0 := saved_status
machine_exit_r1 := saved_r3
```

All four handle reads are distinct. The status/clear helpers can change
the shared cell before the next call, and the cell can change between the
initial guard and the status call. The retained candidate
`display_driver_uled_option_irq_pair.c` now preserves the missing second
read instead of caching the first value. It remains excluded from qualified
linking (`link: false`). The unused `display_driver_uled_vendor_shutdown.c`
candidate was removed: it duplicated both entries, cached the handle for all
three calls, and introduced separate unbound globals for the handle cells.
No other source consumed those globals or shutdown names.

The raw decompiler invents apparent parameters and an `undefined8` result
from `push {r2,r3,r4,lr}` / `pop {r0,r1,r4,pc}`. These instructions do have
machine-level input/output effects; they do not establish a four-argument
public API. The option records use the existing void callback interface.

## Evidence and limits

An isolated Unicorn comparison recorded the ordered shared-cell reads and
helper arguments for both panels. The original candidate matched only the
two NULL-cell cases out of 18 when read events were included; the corrected
candidate matches all 18. Cases include zero/all-bit interrupt status,
cell changes after individual reads, and cell changes after status/clear
helper calls. Two additional counterexamples show that the superseded
candidate continues passing the old handle after the status helper changes
the shared cell. The helpers are controlled mocks, not peripheral emulators.

One unresolved boundary remains explicit. If a nonzero handle fails the
status helper's validity check, stock leaves the saved entry-r2 word
unchanged and still calls clear/service. The retained C initializes status
to zero and therefore does not reproduce that malformed-handle path. Two
counterexamples preserve this limitation. Proving the handle-validity
invariant, or admitting a faithful interface for the machine-state dependency,
is required before complete pseudocode/C qualification; this review does not
silently claim that boundary is solved.

The updated Apollo-main manifest compiles all 2,836 remaining units, has no
expected failures or duplicate strong symbols, and composes successfully.
That build's object-level census was 1,456 before linker aliases; it was not
the remaining composed-object frontier. The current post-alias count is
131, as recorded in `source-build-goal-validation.json`. No gate advanced. The surrounding publication
path is analyzed in [the initialization review](uled-mspi-init-review.md).

The raw REA observations, identities, before/after traces and counterexamples
are retained in
[`uled-irq-handle-review.json`](../../evidence/uled-irq-handle-review.json).
Analysis wrappers, original candidate snapshots and probes are under
`build/goal-uled-irq/`. These results do not prove physical timing, interrupt
concurrency, independent review, whole-image completeness or byte equality.
