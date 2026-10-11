# Apollo MAIN UART IRQ source candidate

`irq_service.c` is the source projection of authenticated entry `0x58e860`,
originally developed at `g2/analysis/audio-source-candidate-20261010/uart_irq_local_candidate.c`.
The pinned Ambiq Apollo510 `am_hal_uart_interrupt_service` is its attributable
source lead; the candidate follows observed stock handle layout and return
semantics where they differ from the generic upstream SDK.

It compiles as a Cortex-M55 EABI relocatable C unit. Its six typed lower
imports are unresolved contracts: RX abort, DMA abort, error status, DMA
complete, read state machine, and write state machine. The prior 360/360
stock/source fixture comparisons cut at those child calls. This object is not
selected into the audio archive until those children and callback/MMIO effects
are composed. No production handler, interrupt delivery, or firmware link is
claimed.

The experimental child composition adds stock-corrected DMA/error, RX abort,
read state machine, and direct source bridges for static RX FIFO/TX state
machine bodies. The bridges embed their original translation units and are
mutually exclusive with normal archive objects. After isolated `ld -r`, the
only imports are queue init/add/get and source-backed microsecond delay, all
present in the admitted audio archive. This does not promote the composition
to validated production behavior.

Run `python3 build_experimental.py OUTPUT --audio-archive ARCHIVE` to produce
an isolated link receipt and verify the admitted Audio archive resolves every
IRQ child import. `--main-object` accepts a freshly rebuilt combined Apollo
object for a later collision check.
