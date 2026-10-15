/* Apollo type-0 uLED mode-4 PMIC sequence at 0x5124fc. */
#include <stdint.h>

extern uint32_t display_driver_uled_pmic_ldo_find_55face(uint32_t,uint32_t);
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t);
extern uint32_t display_driver_uled_pmic_ldo_switch_55fb7c(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pmic_ldo_config_55fae2(uint32_t,const void *);
extern uint32_t display_driver_uled_pmic_ldo_commit_55fad8(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_type0_mode4_5124fc(void) {
    uint32_t ldo = display_driver_uled_pmic_ldo_find_55face(0x20070f78u,1u);
    if (ldo == 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x78b618u,
                (const char *)(uintptr_t)0x6e103cu,
                (const char *)(uintptr_t)0x779becu,0x3ebu,
                (const char *)(uintptr_t)0x7814f8u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x762990u,
                (const char *)(uintptr_t)0x762990u);
        return;
    }
    const uint8_t *mode = audio_ble_hci_radio_mode_state_50938e(1u);
    if (mode[0] < 4u) return;
    uint32_t config[2];
    const volatile uint32_t *stock=(const volatile uint32_t *)(uintptr_t)0x78de24u;
    config[0]=stock[0];config[1]=stock[1];
    (void)display_driver_uled_pmic_ldo_switch_55fb7c(ldo,0u);
    (void)display_driver_uled_pmic_ldo_config_55fae2(ldo,config);
    (void)display_driver_uled_pmic_ldo_commit_55fad8(ldo,0u);
}
