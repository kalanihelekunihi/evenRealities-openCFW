# Bounded IRQ memory observers and execution cross-check

A TWIM fixture exposed an observer effect in Unicorn 2.1.4. A global combined
memory-read/write hook, even with an empty callback, changes execution of the
compiled C Thumb IT sequence: busy remains one although the emitted busy-clear
store is present. The locked native implementation clears busy. Restricting those
hooks to the peripheral/NVIC address ranges restores the clear; execution without
memory hooks also clears busy. Firmware source has not been changed to compensate
for this emulation effect.

`build/goal-r1-twim-irq-c/observer.py` reproduces all three modes. Additional
bounded/no-memory-hook checks independently agree on driver error/busy state and
callback data for complete and incomplete TX, RX, TXRX and both TXTX amount cases
across the two instances. These are controlled execution checks, not proof that
all possible emulator observer effects are eliminated.

The complete earlier SAADC, RTC2, GPIOTE and SPIM2 matrices were replayed with
hooks restricted to their MMIO ranges. Their machine-readable results are
identical to their original receipts: 13,056 SAADC cases, 21,504 RTC2 IRQ
invocations, 137,594 GPIOTE IRQ invocations and 5,760 SPIM2 IRQ invocations. The
existing firmware objects and providers remain unchanged. Original receipts are
retained and link to this supplemental replay.

Machine-readable reproducer values, replay receipts and verifier hashes:
`irq-observer-review.json`. Reproducible ignored scripts are under
`build/goal-r1-twim-irq-c/`, including `setup-regressions.py` and the four generated
`regressions/*/verify.py` files.
