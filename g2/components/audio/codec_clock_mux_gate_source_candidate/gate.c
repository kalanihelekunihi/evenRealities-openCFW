#include <stdint.h>

/* Stock 0x0044b0d6..0x0044b157, for path IDs 0..5. Request bytes
 * are product-initialized RAM at authenticated address 0x200740ec. */
extern uint8_t g2_codec_clock_mux_requests[6]; /* 0x200740ec */
extern uint32_t g2_gpio_critical_save(void);    /* 0x473940 */

void g2_clock_mux_gate(uint8_t path, uint8_t request) {
    uint32_t const prior = g2_gpio_critical_save();
    g2_codec_clock_mux_requests[path] = request;
    uint8_t combined = 0u;
    for (uint32_t i = 0u; i < 6u; ++i)
        combined |= g2_codec_clock_mux_requests[i];
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)0x40008858u;
    for (uint32_t bit = 0u; bit < 5u; ++bit) {
        uint32_t const field = 1u << (bit + 1u);
        *control = (*control & ~field) |
                   (((uint32_t)(combined >> bit) & 1u) << (bit + 1u));
    }
    __asm__ volatile("msr PRIMASK, %0" :: "r"(prior) : "memory");
}
