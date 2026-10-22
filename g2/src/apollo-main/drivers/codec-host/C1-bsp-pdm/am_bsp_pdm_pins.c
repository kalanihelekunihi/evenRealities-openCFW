/* Board support: PDM0 pin release (AmbiqSuite am_bsp.c shape; the G2 board
 * BSP is not in any pinned upstream). Native 0x4c3204..0x4c3223, in the BSP
 * object whose literal pool starts at 0x4c3224 (word 0x78ee48 there).
 *
 * am_bsp_pdm_pins_disable(module): modules >= 4 and modules other than 0 are
 * ignored; PDM0 CLK (GPIO 50) and DATA (GPIO 51) are put back on the ROM pad
 * configuration at 0x78ee48 (value 3, the disabled/default pincfg). The
 * pinconfig statuses are discarded. Callers: drivers/codec-host/drv-pdm. */
#include <stdint.h>

#define AM_REG_PDM_NUM_MODULES 4u
#define BSP_GPIO_PDM0_CLK  50u
#define BSP_GPIO_PDM0_DATA 51u

extern const uint32_t g2_audio_clock_pin_config; /* ROM 0x78ee48 (value 3) */
extern uint32_t am_hal_gpio_pinconfig_480f0c(uint32_t pin, uint32_t config);

void am_bsp_pdm_pins_disable_4c3204(uint32_t module);

/* Stock 0x4c3204. */
void am_bsp_pdm_pins_disable_4c3204(uint32_t module)
{
    if (module >= AM_REG_PDM_NUM_MODULES)
        return;
    switch (module) {
    case 0u:
        (void)am_hal_gpio_pinconfig_480f0c(BSP_GPIO_PDM0_CLK, g2_audio_clock_pin_config);
        (void)am_hal_gpio_pinconfig_480f0c(BSP_GPIO_PDM0_DATA, g2_audio_clock_pin_config);
        break;
    default:
        break;
    }
}
