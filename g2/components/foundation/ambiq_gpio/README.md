# Bounded GPIO IRQ source module

Four unchanged function bodies from pinned Ambiq HAL commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` implement individual IRQ status,
clear, callback registration and dispatch. The retained source notice is
BSD-3-Clause (Ambiq2025). `SOURCE_PROVENANCE.json` authenticates pinned Git
blobs, exact excerpts and stock adaptations. This is not the full GPIO driver.

`ambiq_gpio.h` declares APIs and caller obligations. `ambiq_gpio_compat.h`
represents only proven ARM32 registers/IRQ numbers/table slots. IRQ56..62 and
125..131 select seven32-bit banks in each of two channels; EN/STAT/CLR begin at
0x40010530/534/538 with0x10 bank stride and0x70 channel stride. Callback and
argument tables are separate448-word arrays at0x20068228 and0x20068928.

Status uses the real PRIMASK provider, masks reads, and restores the old mask.
Clear writes the mask once, without waiting. Service visits ascending set bits,
reads the current callback/argument slots, invokes non-null callbacks, continues
after missing entries and returns7 if any callback was absent. Registration
validates channel0/1/2 only. Caller must validate pin/bank, maintain callback and
argument lifetimes, and prevent publication/dispatch races. No allocator, release,
GPIO configuration, NVIC/clock setup or physical interrupt delivery is supplied.

`make -C g2 ambiq-gpio-simulator` builds a callable isolated source module.
`GPIO_SIM_CFLAGS` deliberately selects a Cortex-M4 Thumb-2 subset valid on M55:
Unicorn rejects the CSEL instruction emitted by the M55 optimizer. `-fwrapv`
defines the wrapped signed negation in the unchanged upstream first-set-bit
expression, including bit31. Claims are for this tested target/flags and ARM32
ABI, not portable source/compiler-byte equality.

Run original/source tests with:

```
make -C g2 ambiq-gpio-simulator-test \
 SCB_SIM_PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python \
 GPIO_SIM_REPORT=build/foundation/ambiq-gpio-simulator/new-comparison.json
```

Reports are created exclusively; choose a new report path for each rerun. The
verifier executes four original bodies and the actual critical provider. Only
fixture callbacks are intercepted; W1C behavior is a synthetic MMIO model.
Source/original state, output writes, MMIO operations, mask state, callbacks and
live-table mutation match independent expected behavior. Six service bytes are
provably unreachable after the original IRQ guard and are separately reported.

Concrete stock consumer: radio boot registers channel0/pin117/handler0x4b4a99/
argument0; GPIO0_607F_IRQHandler reads raw pending bits for IRQ59, clears, then
services bank3, where pin117 is bit21. Hardware callback body/pinmux/NVIC setup
remain separate analysis boundaries. See
`g2/analysis/ambiq-gpio-irq-2026-10-05/REPORT.md` and `original/README.md`.
