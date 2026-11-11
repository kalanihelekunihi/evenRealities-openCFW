# RTC2 interrupt C source route and stock span correction

The stock RTC2 IRQ at `0x31750` now routes to the existing pinned Nordic SDK
`nrfx_rtc.c` symbol `RTC2_IRQHandler`. No driver implementation, source unit,
firmware state owner, compiler configuration or manifest is added or changed.

REA confirms a ten-byte stock stub: RTC2 base `0x40024000`, handler index zero,
four compare channels, and a tail branch to `0x7294c`. Two padding bytes and a
four-byte literal follow. The working frontier's previous 162-byte span included
unrelated subsequent routines; it is corrected to ten code bytes. Authenticated
inventories and historical receipts remain unchanged. The locked application
vector at index 52 independently contains `0x31751`. The shared native dispatcher
has 154 code bytes; the fixture executes the complete stub and dispatcher.

The source fixture links the actual existing SDK object and its four-byte static
handler slot at native `0x20007954`. This is controlled placement, not proof of the
final firmware linker binding. Both implementations perform the same ordered
MMIO reads/writes for the tested domains: compare events disable event routing
and interrupts before clearing and calling back; tick and overflow clear pending
state without disabling their interrupts. Compare callbacks report 0 through 3,
tick reports 4, and overflow reports 5. The handler pointer is reloaded at each
handoff.

10,752 paired sequences each deliver two IRQs: 8,192 base sequences cover all
64 enabled-mask and 64 pending-mask combinations with raw pending values 1 and
`0xffffffff`. Another 2,560 sequences change interrupt masks, pending events, or
the handler pointer during callbacks. Tests include enabling later events,
disabling all later interrupts, re-enabling an earlier compare for the next IRQ,
raising overflow from tick, and changing callbacks mid-dispatch. Ordered MMIO,
callback events and mapped peripheral snapshots match. Callee registers on return,
SP, interrupt masks and adjacent handler-slot guards match.

The stock compare/tick callback frame is 32 bytes versus C's 40. Their live
provider registers and private frames are not claimed equal. Overflow restores
the incoming SP and callee registers and forwards caller LR in both implementations;
this is a tail handoff checked with an ordinary return target, not an actual
exception return. Five negative controls reject missing compare interrupt-disable,
missing event-route disable, wrong compare/overflow event codes, and a cached
handler pointer.

MMIO uses emulated memory with modeled INTENCLR and EVTENCLR aliases. Autonomous
RTC events, clock behavior, real interrupt delivery, faults, arbitrary aliases and
concurrency remain unproven. No claim of physical hardware validation is made.

Qualification compiles the unit and selects no exact regions. All 589 normal
source/object hashes and the manifest were revalidated against the prior successful
R1 report; firmware code is unchanged. Its imports remain 164 application / 34
bootloader, with no compile failures or duplicate strong symbols. The source plan
and retained canonical hybrid artifact were revalidated: 4,245 source-built,
641,915 executable fallback and 248 resource bytes. Source-built includes admitted
assembly/data and is not a pure-C coverage metric. The locked application hash
is retained; complete source-only rebuilding and byte-identical C reconstruction
remain unproven.

Machine-readable evidence: `rtc2-irq-c-review.json`. Reproducible ignored probes:
`build/goal-r1-rtc2-irq-c/`.

A subsequent [bounded observer replay](irq-observer-review.md) passes the full
original matrix with MMIO hooks restricted to their register ranges.
