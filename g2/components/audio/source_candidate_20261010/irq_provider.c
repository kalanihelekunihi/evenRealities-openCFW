#include <stdint.h>

/* Original Apollo MAIN helper 0x473940: read PRIMASK, then disable IRQs.
 * The instruction contract and both initial masks are covered by the
 * audio-clock-timing-closure receipt. This is a named source provider for
 * existing `stock_save_irq` callers, not an executable-byte copy. */
uint32_t stock_save_irq(void) {
    uint32_t saved;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(saved) :: "memory");
    return saved;
}

/* The I2S clock release receipt binds this name to the same original entry. */
uint32_t audio_clock_save_disable_irq(void) __attribute__((alias("stock_save_irq")));
