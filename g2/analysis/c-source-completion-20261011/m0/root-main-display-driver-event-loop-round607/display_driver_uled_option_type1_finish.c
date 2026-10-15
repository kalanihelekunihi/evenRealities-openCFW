/* Apollo type-1 uLED finish callback at 0x5bcbb4. */
#include <stdint.h>

extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t);
extern void display_driver_uled_flash_bus_prepare_4c3500(uint32_t,uint32_t);
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern void display_driver_uled_type1_pin_prepare_5bc690(void);
extern uint32_t audio_delay(uint32_t);
extern void display_driver_uled_buck0_enable_512410(void);

uint32_t display_driver_uled_type1_finish_5bcbb4(void) {
    void *device=(void *)(uintptr_t)
        *(volatile const uint32_t *)(uintptr_t)0x20074510u;
    (void)audio_uart_font_flash_power(device,2u,1u);
    display_driver_uled_flash_bus_prepare_4c3500(0u,16u);
    (void)audio_ble_hci_radio_mode_state_50938e(1u);
    display_driver_uled_type1_pin_prepare_5bc690();
    *(volatile uint32_t *)(uintptr_t)0x40010468u=0x4000u;
    (void)audio_delay(1u);
    *(volatile uint32_t *)(uintptr_t)0x40010468u=1u;
    (void)audio_delay(1u);
    display_driver_uled_buck0_enable_512410();
    (void)audio_delay(10u);
    return 0u;
}
