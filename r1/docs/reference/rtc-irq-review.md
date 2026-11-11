# R1 RTC2 SDK dispatcher and vector reference

The pinned SDK's compiled RTC2 dispatcher matches stock in 4,243 controlled
MMIO comparisons. Its object was already in composition and is unchanged.
The checked source vector reference now also participates, resolving to that
SDK handler. The locked application word at offset `0xD0` is `0x31751`, the
Thumb entry at `0x31750`; the isolated linked candidate vector resolves to
its own SDK handler's Thumb symbol. This does not place a full executable
vector table at the native runtime address.

The static sweep covers all 4,096 combinations of six enabled and six pending
event flags. Another 147 cases change the handler slot, disable subsequent
interrupts or inject pending events/enables during the first callback. Checks
compare complete ordered MMIO reads/writes, callback identity/order/event
arguments and final modeled state. Compare events disable EVTEN and INTEN,
clear the event with readback, then dispatch in channel order. Tick and
overflow follow. All r4–r11 and entry SP values are preserved; callback SP
alignment passes. Actual callback stack depths differ between compilers and
are recorded separately, so private stack identity is not claimed.

The MMIO model implements INTENCLR/EVTENCLR alias effects. Callbacks are
controlled mocks and the handler slot is seeded directly. No hardware timer,
NVIC entry/return, actual startup installation, clock drift or complete fault
state is validated. The subsequent [initialization-to-IRQ review](rtc-init-irq-review.md)
checks actual SDK handler installation in 432 additional modeled sequences.

REA observes a 10-byte entry at `0x31750..0x31759`. The dispatcher has 152
analyzed instruction bytes in two ranges, `0x7294C..0x72965` and
`0x72968..0x729E5`: its 154-byte span includes an unexecuted NOP between those
ranges. This distinguishes body bytes from span size without changing
canonical ledgers or accepted coverage.

All 561 R1 units compile and both compositions pass, with unchanged 238
application and 34 bootloader imports. No duplicate strong symbols,
source-plan selections or workflow gates were added. Exact instruction and
timing identity, full startup and physical interrupt delivery remain open.

[rtc-irq-review.json](rtc-irq-review.json) binds SDK/vector source hashes,
report identity, modeled MMIO cases, private-stack observations and REA data.
Probes remain under ignored `build/goal-r1-rtc-irq/`.
