/* Apollo S200 Hongshi brightness at 0x5bc6ae; the settings config getter
 * 0x46b44c is audio_settings_get_config_46b44c (app/silent-mode). */
#include <stdint.h>

extern uint32_t display_driver_brightness_ratio_cell_4af73a(uint32_t);
extern uint32_t display_driver_uled_mode_45a568(void);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);
extern uint32_t display_driver_uled_type1_write_register_5bbdf0(
    uint32_t,uint32_t,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint8_t *audio_settings_get_config_46b44c(void); /* 0x46b44c */

void display_driver_uled_type1_set_brightness_5bc6ae(int32_t level,
                                                        uint32_t unused1,
                                                        uint32_t unused2) {
    (void)unused1;
    (void)unused2;
    int32_t mapped;
    if (level < 2) mapped = 5;
    else if (level < 101) mapped = (level * 250 - 451) / 98 + 5;
    else mapped = 255;
    const volatile uint8_t *const nvdb =
        (const volatile uint8_t *)(uintptr_t)
        display_driver_brightness_ratio_cell_4af73a(5u);
    const uint32_t base = *nvdb;
    const volatile uint8_t *const config =
        audio_settings_get_config_46b44c();
    uint32_t reduction = config[display_driver_uled_mode_45a568() == 1u ?
                                23u : 22u];
    if (reduction > 10u) reduction = 10u;
    const uint32_t current =
        (20u - reduction) * ((base * (uint32_t)mapped) / 100u) / 20u;
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(4u,
            (const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x749754u,0x271u,
            (const char *)(uintptr_t)0x73e3ccu,level,current);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x10800000u,
            (const char *)(uintptr_t)0x71e220u,
            (const char *)(uintptr_t)0x71e220u,level,current);
    (void)display_driver_uled_type1_write_register_5bbdf0(
        0xe2u,current & 0xffu,0u);
    audio_ble_hci_radio_reset_4910f4(1u);
}
