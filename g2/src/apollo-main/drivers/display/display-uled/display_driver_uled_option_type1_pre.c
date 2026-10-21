/* Apollo type-1 uLED option pre-enable sequence at 0x5bcb6c. */
#include <stdint.h>

extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern void display_driver_uled_type1_pin_prepare_5bc690(void);
extern void display_driver_uled_type1_power_5122ec(void);
extern uint32_t audio_delay(uint32_t);
extern void g2_norflash_clock_select_4c32b4(uint32_t,uint32_t);
extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t);

uint32_t display_driver_uled_type1_pre_5bcb6c(void) {
    (void)audio_ble_hci_radio_mode_state_50938e(1u);
    display_driver_uled_type1_pin_prepare_5bc690();
    display_driver_uled_type1_power_5122ec();
    (void)audio_delay(7u);
    g2_norflash_clock_select_4c32b4(0u,0u);
    (void)audio_delay(1u);
    *(volatile uint32_t *)(uintptr_t)0x4001044cu = 1u;
    (void)audio_delay(110u);
    void *device = (void *)(uintptr_t)*(volatile uint32_t *)(uintptr_t)0x20074510u;
    (void)audio_uart_font_flash_power(device,0u,1u);
    return 0u;
}
