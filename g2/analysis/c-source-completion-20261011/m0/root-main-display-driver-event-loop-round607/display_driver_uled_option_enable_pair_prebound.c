/* Apollo S200 uLED option enable callbacks at 0x5926b4 and 0x5bbda4.
 * Direct callees remain explicit imports until source-owned implementations
 * and a whole-chain comparison are available.
 */
#include <stdint.h>

extern void display_driver_uled_type0_pre_593200(void);
extern void display_driver_uled_type0_step_5927ca(void);
extern uint32_t display_driver_uled_type0_get_592f9a(uint32_t);
extern void display_driver_uled_type0_start_5931c0(void);
extern void display_driver_uled_type0_finish_59328c(void);
extern uint32_t display_driver_uled_type1_pre_5bcb6c(void);
extern uint32_t display_driver_uled_type1_get_5bc76e(uint16_t *);
extern void display_driver_uled_type1_step_5bbff2(void);
extern void display_driver_uled_type1_post_5bcb28(void);
extern void display_driver_uled_type1_finish_5bcbb4(void);
extern void audio_delay(uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);

uint32_t display_driver_uled_option_type0_enable_5926b4(uint32_t enabled) {
    if ((uint8_t)enabled != 0u) display_driver_uled_type0_pre_593200();
    display_driver_uled_type0_step_5927ca();
    uint32_t result = display_driver_uled_type0_get_592f9a(0u);
    if ((uint8_t)enabled != 0u) {
        display_driver_uled_type0_start_5931c0();
        audio_ble_hci_radio_reset_4910f4(5u);
        display_driver_uled_type0_finish_59328c();
    }
    audio_delay(10u);
    return result;
}

uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t enabled) {
    if ((uint8_t)enabled != 0u) display_driver_uled_type1_pre_5bcb6c();
    uint16_t argument = 0u;
    uint32_t result = display_driver_uled_type1_get_5bc76e(&argument);
    display_driver_uled_type1_step_5bbff2();
    display_driver_uled_type1_post_5bcb28();
    if ((uint8_t)enabled != 0u) {
        audio_ble_hci_radio_reset_4910f4(5u);
        display_driver_uled_type1_finish_5bcbb4();
    } else {
        audio_delay(50u);
        *(volatile uint32_t *)(uintptr_t)0x4001044cu = 0x4000u;
    }
    return result;
}
