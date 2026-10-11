#include <stdint.h>

/* Stock 0x00509024..0x00509130. The shared mask's original pointer
 * literal is 0x2007436c; its initializer is a product-data contract. */
extern volatile uint32_t g2_codec_shared_enable_mask;
uint32_t g2_gpio_critical_save(void);

extern int32_t g2_gpio_hal_write(uint32_t pin, uint32_t mode);

/* Stock 0x0053a5be: normalize the value byte and the HAL result. */
__attribute__((noinline)) uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value) {
    return g2_gpio_hal_write(pin, (uint8_t)value == 1u) == 0 ? 0u : 0xffffffffu;
}

/* Exact stock 0x00473940: MRS R0,PRIMASK; CPSID I; BX LR. */
uint32_t g2_gpio_critical_save(void) {
    uint32_t prior;
    __asm volatile("mrs %0, primask\n\tcpsid i" : "=r"(prior) : : "memory");
    return prior;
}

uint32_t g2_codec_gpio_write(uint32_t channel, uint32_t value,
                             uint32_t unused_r2, uint32_t passthrough_r3) {
    (void)unused_r2;
    uint32_t pin;
    switch ((uint8_t)channel) {
    case 1u: pin = 0x81u; break;
    case 2u: pin = 9u; break;
    case 3u: pin = 0x80u; break;
    case 4u: pin = 0x8eu; break;
    case 7u: pin = 0x8fu; break;
    case 8u: pin = 0x92u; break;
    case 6u:
    case 9u: {
        uint32_t prior = g2_gpio_critical_save();
        if ((uint8_t)value == 1u)
            g2_codec_shared_enable_mask |= 1u << (uint8_t)channel;
        else if ((uint8_t)value == 0u)
            g2_codec_shared_enable_mask &= ~(1u << (uint8_t)channel);
        g2_codec_pin_write(0x86u, g2_codec_shared_enable_mask != 0u);
        __asm volatile("msr primask, %0" : : "r"(prior) : "memory");
        return prior;
    }
    default: return passthrough_r3;
    }
    g2_codec_pin_write(pin, (uint8_t)value == 1u);
    return passthrough_r3;
}
