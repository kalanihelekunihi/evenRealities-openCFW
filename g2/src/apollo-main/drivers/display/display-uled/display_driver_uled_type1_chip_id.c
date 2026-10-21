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
        g2_flashdb_candidate_log(3u,(const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x753bc4u,0x27cu,
            (const char *)(uintptr_t)0x75f770u,value);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x0c400000u,
            (const char *)(uintptr_t)0x73e3f8u,
            (const char *)(uintptr_t)0x73e3f8u,value);
    if (value!=1u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x785c80u,
                (const char *)(uintptr_t)0x6ecca8u,
                (const char *)(uintptr_t)0x753bc4u,0x27fu,
                (const char *)(uintptr_t)0x728e3cu,value);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04400000u,
                (const char *)(uintptr_t)0x70236cu,
                (const char *)(uintptr_t)0x70236cu,value);
        return UINT32_MAX;
    }
    audio_ble_hci_boot_delay_491102(100u);
    if (chip_id!=0) *chip_id=1u;
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(4u,(const char *)(uintptr_t)0x785c80u,
            (const char *)(uintptr_t)0x6ecca8u,
            (const char *)(uintptr_t)0x753bc4u,0x289u,
            (const char *)(uintptr_t)0x75f790u,*chip_id);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x10400000u,
            (const char *)(uintptr_t)0x7335e4u,
            (const char *)(uintptr_t)0x7335e4u,*chip_id);
    display_driver_uled_type1_read_sn_5bc8b4();
    return 0u;
}
