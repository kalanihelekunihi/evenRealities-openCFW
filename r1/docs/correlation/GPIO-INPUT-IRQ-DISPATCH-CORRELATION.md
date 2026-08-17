# GPIO-input IRQ dispatch correlation

The product GPIO-input registry callback at
`0x0006ED94..<0x0006EDC8` is a 52-byte function with SHA-256
`cce6c3331bbeeb45f432ebab1e540905c2b218d10db5ae0a655641d844a82692`.
Ghidra's function inventory omitted this entry, so the exact executable extent
is recorded as a manual provenance supplement.

The function has no direct branch caller. Its Thumb pointer `0x0006ED95` is
stored at flash address `0x00054C20` and supplied to the Nordic GPIOTE setup
path. The literal immediately after the body is the recovered input-registry
base `0x200070C0`.

The dispatcher walks exactly seven 44-byte records. It compares the provider's
linear pin with the word at record offset 8 and invokes the non-null callback at
offset 40 with the pin truncated to `uint8_t` and the provider action unchanged.
The recovered pin sequence is `15, 21, 17, 18, 33, 3, 33`; therefore the scan
must continue after a match so both records for linear pin 33 are notified.

`r1_gpio_input_irq_dispatch` implements only that bounded product registry
policy and returns the number of callbacks invoked for test observability. It
does not read, configure, or acknowledge GPIO hardware and does not reproduce
Nordic GPIOTE. The Nordic provider remains responsible for interrupt and pin
mechanics.

Reproduce the image hash, exact extent, registration pointer, registry literal,
record geometry, and pin-topology checks with:

```sh
python3 tools/evidence/summarize_r1_gpio_input_irq_dispatch.py
```
