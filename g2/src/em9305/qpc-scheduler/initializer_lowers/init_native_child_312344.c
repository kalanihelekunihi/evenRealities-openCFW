#include <stdint.h>

/* Native 0x312344..0x31235e: program the radio whitening seed for a
 * channel and set the enable bit. The seed register 0xf04044 receives
 * bit-reversed channel bits 0..5 (APEX bswp8, bits 2..7 of the result)
 * shifted down by one with bit 0 set; then 312330 applies `enabled`. */
extern uint32_t opencfw_em9305_radio_enable_312330(uint32_t value);

#ifdef OPENCFW_QEMU_SOFT_BSWP8
/* Test-harness only: QEMU-ARC lacks the APEX bswp8 extension; model it as
 * a bit reversal of the low byte (the harness applies the same model to
 * the stock side). */
static inline uint32_t opencfw_em9305_bswp8(uint32_t value)
{
    uint32_t result = 0u;
    for (uint32_t i = 0u; i < 8u; i++) {
        result = (result << 1) | (value & 1u);
        value >>= 1;
    }
    return result;
}
#else
__asm__(".extInstruction bswp8,7,14,SUFFIX_NONE,SYNTAX_2OP");
static inline uint32_t opencfw_em9305_bswp8(uint32_t value)
{
    uint32_t result;
    __asm__ volatile("bswp8 %0,%1" : "=r"(result) : "r"(value));
    return result;
}
#endif

uint32_t opencfw_em9305_radio_finish_mode_312344(uint32_t channel, uint32_t enabled)
{
    *(volatile uint32_t *)(uintptr_t)0xf04044u =
        ((opencfw_em9305_bswp8(channel) & 252u) >> 1) | 1u;
    return opencfw_em9305_radio_enable_312330(enabled);
}
