/* Apollo S200 Hongshi serial-number read/log sequence at 0x5bc8b4. */
#include <stdint.h>

extern uint32_t display_driver_uled_type1_write_register_5bbdf0(uint32_t,
                                                                  uint32_t,uint32_t);
extern uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t,uint32_t);
extern void audio_ble_hci_radio_reset_4910f4(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_type1_read_sn_5bc8b4(void) {
    uint8_t serial[19];
    for (uint32_t page=0;page<5u;page++) {
        (void)display_driver_uled_type1_write_register_5bbdf0(0x65u,
                                                                page==4u?1u:0u,0u);
        (void)display_driver_uled_type1_write_register_5bbdf0(0x66u,2u,0u);
        (void)display_driver_uled_type1_write_register_5bbdf0(0x67u,
                                                                page==4u?0u:page,0u);
        (void)display_driver_uled_type1_write_register_5bbdf0(0x64u,0x85u,0u);
        audio_ble_hci_radio_reset_4910f4(1u);
        for (uint32_t offset=0;offset<(page==4u?3u:4u);offset++)
            serial[page*4u+offset]=(uint8_t)
                display_driver_uled_type1_read_bank_5bbe80(0x6cu+offset,0u);
        (void)display_driver_uled_type1_write_register_5bbdf0(0x64u,0u,0u);
        audio_ble_hci_radio_reset_4910f4(1u);
    }
    for (uint32_t i=0;i<19u;i++) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(3u,"driver.a6n-g" /* stock 0x785c80 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
                "am_device_mspi_hongshi_read_sn" /* stock 0x75f7b0 */,0x2d3u,
                " %02X " /* stock 0x78d47c */,serial[i]);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x0c400000u,
                "[driver.a6n-g] %02X " /* stock 0x776cdc */,
                "[driver.a6n-g] %02X " /* stock 0x776cdc */,serial[i]);
    }
}
