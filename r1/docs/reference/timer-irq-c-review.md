# TIMER2/4 interrupt C source routes

The stock TIMER2 and TIMER4 entries now route to the existing, unchanged pinned
Nordic SDK `nrfx_timer.c` vector symbols. Their shared dispatcher at `0x729ec`
also has a tested C source route. REA covers both stubs and its 70-byte body.
Application vectors 26/43 contain `0x33829`/`0x3383d`. No firmware implementation,
state owner, source unit, compiler flag or manifest is added or changed.

TIMER2's stub passes peripheral `0x4000a000`, control block `0x2002c2a4` and four
channels. TIMER4 passes `0x4001b000`, control block `0x2002c2b0` and six channels.
Both stubs have ten code bytes followed by padding and two literals. TIMER4's
working-frontier span is corrected from 78 to ten code bytes: the old span crossed
into an unrelated routine beginning at `0x33850`. Authenticated inventories and
historical receipts remain unchanged.

Compiled assertions against the actual SDK type confirm two 12-byte control
blocks, indices zero/one, and handler/context/state offsets 0/4/8. The fixture
links the actual existing C object and its static array at the native base. This
controlled placement does not establish the final firmware linker binding.

49,352 paired two-IRQ sequences pass (98,704 paired invocations). There are
49,152 base sequences covering both instances, all 64 pending and enabled-mask
combinations, three context words, and event values one/`0xffffffff`. Another
200 sequences change later masks/events, re-pend an earlier channel, or replace
handler/context during a callback. TIMER2 ignores channels four/five while TIMER4
processes them. Register inputs include reserved/unused bits deliberately; they
do not assert that real TIMER2 hardware generates those events.

The implementation checks each event then its interrupt mask, clears the event,
and calls the current handler with the event offset enum and current context.
It does not disable a compare interrupt on dispatch. Ordered MMIO reads/writes,
callback arguments and control snapshots, final driver/register state, return
callee registers, SP, interrupt masks and adjacent state guards match. Six negative
controls reject ignoring enables, missing event clear, wrong context/event,
truncating TIMER4 to four channels, and caching the callback pointer.

Native callback frames are 24 bytes versus C's 32. Live callback registers,
private frames, caller-clobbered return registers and APSR are excluded. Hooks
are bounded to timer MMIO. Autonomous clocks/compare generation, real interrupt
or exception delivery, null handlers, corrupt state, arbitrary aliases/faults and
concurrency remain unproven.

Two ignored literal-pool probes (`-mno-movt` with recorded size optimization and
with explicit `-Oz`) compile, but their first stub instruction still differs from
stock. Neither is adopted. Production flags and existing source-plan providers
are unchanged. Qualification reproduces the already-admitted eight-byte
`nrfx_timer_clear` region with the same payload bounds and hash; it selects no
new IRQ region. This distinction is recorded in the machine-readable review.

All 590 normal source/object hashes and the manifest were revalidated against
the prior passing R1 report, with 164 application / 34 bootloader imports, no
compile failures and no duplicate strong symbols. The retained canonical hybrid
and current source-plan hash are unchanged: 4,245 source-built, 641,915 executable
fallback and 248 resource bytes. Source-built includes admitted assembly/data.
Complete source-only rebuilding and byte-identical C reconstruction remain
unproven.

Machine-readable evidence: `timer-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-timer-irq-c/`.
