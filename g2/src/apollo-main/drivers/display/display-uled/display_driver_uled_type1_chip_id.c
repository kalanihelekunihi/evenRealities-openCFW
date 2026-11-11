/* Apollo S200 Hongshi chip-ID read at 0x5bc76e. */
#include <stdint.h>

extern uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t,uint32_t);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern void display_driver_uled_type1_read_sn_5bc8b4(void);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type1_get_5bc76e(uint16_t *chip_id) {
    uint32_t value=display_driver_uled_type1_read_bank_5bbe80(6u,0u)&0xffu;
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(3u,"driver.a6n-g" /* stock 0x785c80 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
            "am_devices_mspi_hongshi_read_chipId" /* stock 0x753bc4 */,0x27cu,
            "read bank0 chip id : %02X \r\n" /* stock 0x75f770 */,value);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x0c400000u,
            "[driver.a6n-g]read bank0 chip id : %02X \r\n" /* stock 0x73e3f8 */,
            "[driver.a6n-g]read bank0 chip id : %02X \r\n" /* stock 0x73e3f8 */,value);
    if (value!=1u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,"driver.a6n-g" /* stock 0x785c80 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
                "am_devices_mspi_hongshi_read_chipId" /* stock 0x753bc4 */,0x27fu,
                "Error - Failed to read chip id ,Erro number = %d\r\n" /* stock 0x728e3c */,value);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04400000u,
                "[driver.a6n-g]Error - Failed to read chip id ,Erro number = %d\r\n" /* stock 0x70236c */,
                "[driver.a6n-g]Error - Failed to read chip id ,Erro number = %d\r\n" /* stock 0x70236c */,value);
        return UINT32_MAX;
    }
    audio_ble_hci_boot_delay_491102(100u);
    if (chip_id!=0) *chip_id=1u;
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(4u,"driver.a6n-g" /* stock 0x785c80 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
            "am_devices_mspi_hongshi_read_chipId" /* stock 0x753bc4 */,0x289u,
            "hongshi panel devicve id:  %04x" /* stock 0x75f790 */,*chip_id);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x10400000u,
            "[driver.a6n-g]hongshi panel devicve id:  %04x" /* stock 0x7335e4 */,
            "[driver.a6n-g]hongshi panel devicve id:  %04x" /* stock 0x7335e4 */,*chip_id);
    display_driver_uled_type1_read_sn_5bc8b4();
    return 0u;
}
