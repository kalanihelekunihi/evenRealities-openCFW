# Private bootloader clock dispatch

`clock_manager.c` reconstructs the stock `clock_request` and `clock_release`
dispatchers at `0x004222f0` and `0x00422364`, plus the class-0 per-user
bookkeeping provider. `clock_class_providers.c` reconstructs classes 1 and 3
and their directly called register-update helper. The exported dispatch API accepts raw 32-bit register
arguments and explicitly truncates both to 8 bits, matching the stock `UXTB`
instructions before validation and provider selection.

Both dispatchers return status 6 for user IDs 57 or greater after truncation,
and for clock IDs 7 or greater. Clock IDs 0 through 6 dispatch to provider
functions named in the source. Classes 0, 1, and 3 are implemented here.
Classes 2, 4, 5, and 6 remain explicit external provider dependencies; the test-only stubs in the
upstream-worker directory are not firmware implementations.

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
with `make test`. It uses the locked image and synthetic SRAM/MMIO; only
classes 2, 4, 5, and 6 are intercepted by test stubs.
