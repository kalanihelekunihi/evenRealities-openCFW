#include <stdint.h>

extern uint32_t g2_gpio_critical_save(void);

/* Stock Apollo GPIO HAL 0x00480fd6..0x004810af. The six GPIO aliases
 * are architectural MMIO ports read from authenticated stock literals. */
__attribute__((noinline)) int32_t g2_gpio_hal_write(uint32_t pin, uint32_t mode) {
    uint32_t bank = ((uint8_t)pin) >> 5;
    uint32_t bit = 1u << (pin & 31u);
    uint32_t prior;
    volatile uint32_t *reg;
    switch ((uint8_t)mode) {
    case 0u:
        reg = (volatile uint32_t *)(uintptr_t)0x40010458u;
        reg[bank] = bit;
        break;
    case 1u:
        reg = (volatile uint32_t *)(uintptr_t)0x4001043cu;
        reg[bank] = bit;
        break;
    case 2u:
        prior = g2_gpio_critical_save();
        reg = (volatile uint32_t *)(uintptr_t)0x40010420u;
        reg[bank] ^= bit;
        __asm volatile("msr primask, %0" : : "r"(prior) : "memory");
        break;
    case 3u:
        reg = (volatile uint32_t *)(uintptr_t)0x400104acu;
        reg[bank] = bit;
        break;
    case 4u:
        reg = (volatile uint32_t *)(uintptr_t)0x40010490u;
        reg[bank] = bit;
        break;
    case 5u:
        prior = g2_gpio_critical_save();
        reg = (volatile uint32_t *)(uintptr_t)0x40010474u;
        reg[bank] ^= bit;
        __asm volatile("msr primask, %0" : : "r"(prior) : "memory");
        break;
    default:
        break;
    }
    return 0;
}

