/* Apollo S200 type-0 uLED pre-enable sequence at 0x593200. */
#include <stdint.h>

extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern void display_driver_uled_type0_pin_prepare_592c78(void);
extern void display_driver_uled_type0_mode4_5124fc(void);
extern void display_driver_uled_type1_power_5122ec(void);
extern uint32_t audio_delay(uint32_t);
extern void g2_norflash_clock_select_4c32b4(uint32_t,uint32_t);
extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t);
extern uint32_t g2_norflash_disable_mspi_4c0ea8(uint32_t);
extern uint32_t g2_norflash_configure_mspi_4c099c(uint32_t,const void *);
extern uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t);

uint32_t display_driver_uled_type0_pre_593200(void) {
    const uint8_t *mode = audio_ble_hci_radio_mode_state_50938e(1u);
    display_driver_uled_type0_pin_prepare_592c78();
    if (mode[0] >= 4u) display_driver_uled_type0_mode4_5124fc();
    else *(volatile uint32_t *)(uintptr_t)0x4001044cu = 1u;
    (void)audio_delay(3u);
    if (mode[0] >= 3u) display_driver_uled_type1_power_5122ec();
    else *(volatile uint32_t *)(uintptr_t)0x4001044cu = 0x8000u;
    (void)audio_delay(3u);
    *(volatile uint32_t *)(uintptr_t)0x4001044cu = 0x4000u;
    (void)audio_delay(10u);
    g2_norflash_clock_select_4c32b4(0u,0u);
    uint32_t handle = *(volatile const uint32_t *)(uintptr_t)0x20074524u;
    (void)audio_uart_font_flash_power((void *)(uintptr_t)handle,0u,1u);
    (void)g2_norflash_disable_mspi_4c0ea8(handle);
    (void)g2_norflash_configure_mspi_4c099c(handle,
                                              (const void *)(uintptr_t)0x200007a0u);
    (void)g2_norflash_enable_mspi_4c0e1e(handle);
    *(volatile uint32_t *)(uintptr_t)0x40010444u = 0x10u;
    return 0u;
}
