/* Apollo type-0 uLED finish callback at 0x59328c. */
#include <stdint.h>

extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t);
extern uint32_t display_driver_uled_flash_bus_prepare_4c3500(uint32_t,uint32_t);
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern void display_driver_uled_type0_pin_prepare_592c78(void);
extern uint32_t audio_delay(uint32_t);
extern void display_driver_uled_buck0_enable_512410(void);
extern void display_driver_uled_type0_mode4_finish_5125a8(void);

uint32_t display_driver_uled_type0_finish_59328c(void) {
    void *device=(void *)(uintptr_t)
        *(volatile const uint32_t *)(uintptr_t)0x20074524u;
    (void)audio_uart_font_flash_power(device,2u,1u);
    (void)display_driver_uled_flash_bus_prepare_4c3500(0u,16u);
    const uint8_t *mode=audio_ble_hci_radio_mode_state_50938e(1u);
    display_driver_uled_type0_pin_prepare_592c78();
    *(volatile uint32_t *)(uintptr_t)0x40010468u=0x4000u;
    (void)audio_delay(3u);
    if (mode[0]>=3u) display_driver_uled_buck0_enable_512410();
    else *(volatile uint32_t *)(uintptr_t)0x40010468u=0x8000u;
    (void)audio_delay(3u);
    if (mode[0]>=4u) display_driver_uled_type0_mode4_finish_5125a8();
    else *(volatile uint32_t *)(uintptr_t)0x40010468u=1u;
    (void)audio_delay(10u);
    *(volatile uint32_t *)(uintptr_t)0x40010460u=0x10u;
    return 0u;
}
