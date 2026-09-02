# G2 bootloader retained-event service-loop source closure

The complete 162-byte function at `0x0042E2F8..0x0042E39A` is now
source-owned MIT C. It initializes event/runtime services, selects the retained
context layout, then performs the authenticated 60,000-unit wait/time loop.
Its sole ingress is the stored Thumb entry pointer at `0x0042E48C`.

Apple clang 21 and Homebrew clang 22 reproduce all bytes exactly from
mnemonic-only Arm source under fourteen strict provider relocations. Portable
tests cover both context layouts, callback eligibility, timeout rollover, and
timestamp updates. Live retained RAM, scheduler/event, logging, timing,
interrupt, reset, and cold-boot behavior is blocked by unavailable physical evidence.
