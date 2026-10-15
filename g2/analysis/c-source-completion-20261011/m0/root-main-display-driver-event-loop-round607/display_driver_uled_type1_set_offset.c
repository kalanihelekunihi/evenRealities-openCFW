/* Apollo S200 Hongshi display offsets at 0x5bc4c0. */
#include <stdint.h>

extern uint32_t display_driver_uled_mode_45a568(void);
extern uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t,
                                                              uint32_t);
extern uint32_t display_driver_uled_type1_write_register_5bbdf0(
    uint32_t,uint32_t,uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void log_offset(uint32_t value,uint32_t line,uint32_t detail,
                       uint32_t compact) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,
            (const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x7496dcu,line,
            (const char *)(uintptr_t)detail,value);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c400000u,
            (const char *)(uintptr_t)compact,
            (const char *)(uintptr_t)compact,value);
}

uint32_t display_driver_uled_type1_set_offset_5bc4c0(uint32_t x,
                                                        uint32_t y) {
    uint8_t horizontal = (uint8_t)x;
    uint8_t vertical = (uint8_t)y;
    if (*(volatile const uint8_t *)(uintptr_t)0x2007501au != 0u &&
        display_driver_uled_mode_45a568() == 2u)
        horizontal = (uint8_t)(horizontal + 5u);
    if (horizontal > 16u) horizontal = 16u;
    if (vertical > 16u) vertical = 16u;

    const uint32_t xbank = display_driver_uled_type1_read_bank_5bbe80(
        0xefu,0u) & 0xffu;
    log_offset(xbank,0x214u,0x749704u,0x728dd4u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(
        0xefu,(uint8_t)(horizontal + (xbank & 0xe0u)),0u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd9u,0xbfu,0u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd9u,0xffu,0u);
    audio_ble_hci_boot_delay_491102(100u);

    const uint32_t ybank = display_driver_uled_type1_read_bank_5bbe80(
        0xf0u,0u) & 0xffu;
    log_offset(ybank,0x221u,0x74972cu,0x728e08u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(
        0xf0u,(uint8_t)(vertical + (ybank & 0xe0u)),0u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd9u,0xbfu,0u);
    audio_ble_hci_boot_delay_491102(100u);
    (void)display_driver_uled_type1_write_register_5bbdf0(0xd9u,0xffu,0u);
    audio_ble_hci_boot_delay_491102(100u);
    audio_ble_hci_radio_reset_4910f4(1u);
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,
            (const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x7496dcu,0x235u,
            (const char *)(uintptr_t)0x73e3a0u,horizontal,vertical);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c800000u,
            (const char *)(uintptr_t)0x71474cu,
            (const char *)(uintptr_t)0x71474cu,horizontal,vertical);
    return 0u;
}
