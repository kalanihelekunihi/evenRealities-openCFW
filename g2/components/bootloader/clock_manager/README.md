# Private bootloader clock dispatch

`clock_manager.c` reconstructs the stock `clock_request` and `clock_release`
dispatchers at `0x004222f0` and `0x00422364`, plus the class-0 per-user
bookkeeping provider. `clock_class_providers.c` reconstructs classes 1 and 3
and their directly called register-update helper. `clock_class_provider2.c`
reconstructs class 2 and the mode-apply selectors it uses; class 4 and its
delay path are in `clock_class_provider4.c`; class 5 covers clkgen/dual-switch
ownership; and class 6 covers bounded PLL setup/teardown. The exported
dispatch API accepts raw 32-bit register
arguments and explicitly truncates both to 8 bits, matching the stock `UXTB`
instructions before validation and provider selection.

Both dispatchers return status 6 for user IDs 57 or greater after truncation,
and for clock IDs 7 or greater. Clock IDs 0 through 6 dispatch to provider
functions named in the source. All seven classes have source providers. The
shared mode-apply helper reconstructs all selectors and its original
four-argument/two-register return ABI. Class 2 itself uses selectors 2, 3,
and 4; selectors 5 and 6 call the dispatcher for the nested class-2 user.

The raw arguments use `uint32_t` in the public C prototype so the source can
explicitly reproduce the entry instruction's low-byte truncation even when
upper input-register bits are set. Callers should include this header rather
than use narrower, inconsistent declarations.

Class 0 keeps one bit per user in two words per class at SRAM address
`0x20026e74`. Requests and releases are idempotent per user. A change saves
PRIMASK, disables interrupts, updates the bit, and restores the saved PRIMASK.
No clock-tree MMIO operation occurs in this class-0 provider.

Run the instruction differential from
`g2/analysis/bootloader-completion-2026-10-06/upstream-worker/clock-manager/`
with `make test`. It uses the locked image and synthetic SRAM/MMIO; all class
providers execute as stock and compiled source. Class 2, class 4, and PLL
status polls use synthetic register state. Calibrated waits reach the ROM
target at Thumb address `0x41`, intercepted before any hardware wait.
