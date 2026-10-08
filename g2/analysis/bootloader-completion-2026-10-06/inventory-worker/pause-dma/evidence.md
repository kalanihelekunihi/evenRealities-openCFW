# MSPI command-queue pause and DMA continuation

The source in `g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c`
combines stock `0x4240aa`, its split continuation through `0x42411f`, the CQ
pause/poll routine `0x423fb8`, and DMA setup `0x42403e`. The caller saves and
updates `state+0x840` under PRIMASK, restores the saved mask, and skips the
pause/DMA path when the previous value was nonzero. Otherwise it requests CQ
pause by writing `0x800000` to `MSPI+0x2b4`; the loop tests bit 0 at `+0x2a0`,
then uses bit 3 at `+0x2ac` and bit 7 at `+0x2b8` as the alternate ready path.
The loop limit is the pinned literal `0x186a0` (100000 raw delay iterations;
this does not assert elapsed microseconds). Once the pause gate clears, the
stock status-check routine polls `MSPI+0x104` for bit 0 equal to zero. Pause
timeout returns 4. On success, the helper updates `state+0x24`, MSPI control
registers `+0x208/+0x200`, and byte `state+0x83c`, then requests clock 4 for
user `(module+16)&0xff`. A nonzero clock status is returned. On success it
selects the next 24-byte DMA descriptor and writes its four words to `+0x108`,
`+0x10c`, `+0x110`, and `+0x100`.

Original/source comparison passes 7 fixtures over 422 distinct stock
instruction bytes. Fixtures cover the prior-timeout fast path, immediate
pause readiness, the alternate ready bits, status changes from the delay
provider, the 100000-iteration timeout, clock-request failure, and zero-sized
DMA rings. The exact stock ranges and SHA-256 values, source hashes, instruction
trace, and cases are in `result.json`.

The delay provider is intercepted and may change synthetic MMIO values at
specified callback counts. Clock requests also return an injected status. This
validates control flow against the original instructions but does not assert
real timing, physical CQ behavior, DMA completion, or flash effects. No device
was accessed.
