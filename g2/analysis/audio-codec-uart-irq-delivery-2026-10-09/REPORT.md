# Codec UART IRQ receive and callback delivery

**112 original/source comparisons PASS** for the channel-3 wrapper at locked
address `0x55E2CE`. [Results](results.json), [ELF/source hashes](reproduction-receipt.json),
and [reconstructed source](../../components/audio/codec_uart_irq_offline/irq.c)
are retained for reproduction.

The wrapper obtains status, clears that same status, and calls the HAL service
provider before interpreting individual bits. Status bit `0x10` requests up to
15 FIFO bytes and only accumulates them. Bit `0x40` requests up to 16 bytes,
invokes the registered callback with `(staging_buffer, accumulated_count)`, and
then resets the accumulated count to zero. When both bits are set, the 15-byte
read precedes the 16-byte read and the callback sees their combined accepted
count. Bit `0x01` independently sets descriptor completion byte `+25`.

The locked helper instructions at `0x55E50C`/`0x55E516` and
`0x55E52C`–`0x55E53C` establish the RX object layout: accumulated count is at
offset `+8`, and staging-buffer pointer is at `+12`. Callback setup at
descriptor offset `+20` and the stock codec callback at `0x58FB1C` route the
delivered bytes into the 64-byte UART3 ring at `0x20073ED4`. The comparisons
exercise FIFO accept counts 0/1/3/16, prior accumulated counts 0/2, callback
absent/present, and statuses 0, 1, `0x10`, `0x40`, `0x41`, `0x50`, and `0x51`.

HAL status/clear/service/FIFO operations are supplied software providers. The
fixture directly invokes the wrapper; it does not model vector registration,
NVIC state, exception entry/return, electrical UART behavior, or real interrupt
timing. Thus it proves delivery semantics once the wrapper runs, without making
a physical-state or live scheduler claim.

The GPIO frontend and generic GPIO registration/service paths are already
source-backed in `ambiq-gpio-config-2026-10-05` and
`ambiq-gpio-irq-2026-10-05`; duplicating them would add no evidence. Static
audio-task initialization is already bounded in
`audio-task-configuration-closure-2026-10-08`. The remaining boundary for a
real block-to-interrupt-to-resume claim is initialized whole-system vector,
NVIC, scheduler, and peripheral state or a device/runtime trace. Available
static provider source cannot prove that external state.
