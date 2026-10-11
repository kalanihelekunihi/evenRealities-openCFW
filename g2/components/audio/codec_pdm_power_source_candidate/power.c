#include <stdint.h>

/* Complete stock 0x00592046..0x005920cb, with existing power-domain
 * children at 0x47f5b8 and 0x47f7ae. */
extern uint32_t audio_power_peripheral_on(uint32_t peripheral);
extern uint32_t audio_power_peripheral_off(uint32_t peripheral);
extern uint32_t g2_gpio_critical_save(void);

uint32_t g2_pdm_disable(void *handle, uint32_t mode, uint32_t backup) {
    volatile uint32_t *const row = (volatile uint32_t *)handle;
    if (handle == 0 || (row[0] & 0x01ffffffu) != 0x01f956e2u)
        return 2u;
    uint32_t const peripheral = (uint8_t)(row[2] + 30u);
    mode = (uint8_t)mode;
    backup = (uint8_t)backup;
    if (mode == 0u) {
        if (backup != 0u && ((volatile uint8_t *)handle)[4] == 0u)
            return 7u;
        (void)audio_power_peripheral_on(peripheral);
        if (backup != 0u) {
            uint32_t const prior = g2_gpio_critical_save();
            ((volatile uint8_t *)handle)[4] = 0u;
            __asm__ volatile("msr PRIMASK, %0" :: "r"(prior) : "memory");
        }
        return 0u;
    }
    if (mode == 1u || mode == 2u) {
        if (backup != 0u) {
            uint32_t const prior = g2_gpio_critical_save();
            ((volatile uint8_t *)handle)[4] = 1u;
            __asm__ volatile("msr PRIMASK, %0" :: "r"(prior) : "memory");
        }
        (void)audio_power_peripheral_off(peripheral);
        return 0u;
    }
    return 6u;
}
