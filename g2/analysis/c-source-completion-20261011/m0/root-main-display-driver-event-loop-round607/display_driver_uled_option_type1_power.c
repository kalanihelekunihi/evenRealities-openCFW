/* Apollo 0x5122ec buck-1 configuration; PMIC callees remain source gates.
 * Diagnostic strings are authenticated ROM addresses in the S200 image.
 */
#include <stdint.h>

extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern uint32_t display_driver_uled_pmic_find_55fa0e(uint32_t,uint32_t);
extern void display_driver_uled_pmic_enable_55fa40(uint32_t,uint32_t);
extern void display_driver_uled_pmic_voltage_55fa22(uint32_t,uint32_t);
extern void display_driver_uled_pmic_commit_55fa18(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_type1_power_5122ec(void) {
    const uint8_t *mode = audio_ble_hci_radio_mode_state_50938e(1u);
    uint32_t buck = display_driver_uled_pmic_find_55fa0e(0x20070f78u,0u);
    if (buck == 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x78b618u,
                (const char *)(uintptr_t)0x6e103cu,
                (const char *)(uintptr_t)0x779b8cu,0x399u,
                (const char *)(uintptr_t)0x7814bcu);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x762930u,
                (const char *)(uintptr_t)0x762930u);
        return;
    }
    display_driver_uled_pmic_enable_55fa40(buck,1u);
    display_driver_uled_pmic_voltage_55fa22(buck,mode[0]==6u ? 8u : 1u);
    display_driver_uled_pmic_commit_55fa18(buck,0u);
}
