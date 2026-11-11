/* Apollo type-0 uLED mode-4 PMIC sequence at 0x5124fc. */
#include <stdint.h>
/* Fix 48: stock flash 0x78de24, 2 words (stock image bytes). */
static const uint32_t g2_uled_ldo_config_78de24[2]={0x00000001u, 0x00000003u};

/* Sim-test fix (2026-10-26): stock literal 0x20070f78 is the npmx_instance
 * that npmx_main_driver.c defines as g2_npmx_instance; our link places it
 * elsewhere, so the literal read zero (Renode HardFault blx 0 in the kick). */
struct npmx_instance;
extern struct npmx_instance g2_npmx_instance; /* RAM 0x20070f78 */

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
    uint32_t ldo = display_driver_uled_pmic_ldo_find_55face(((uint32_t)(uintptr_t)&g2_npmx_instance),1u);
    if (ldo == 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,"npmx_driver" /* stock 0x78b618 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\npmx_driver_transplant\\src\\npmx_main_driver.c" /* stock 0x6e103c */,
                "configure_lsdw2_voltage" /* stock 0x779bec */,0x3ebu,
                "p_ldsw2 is null!\n" /* stock 0x7814f8 */);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                "[npmx_driver]p_ldsw2 is null!\n" /* stock 0x762990 */,
                "[npmx_driver]p_ldsw2 is null!\n" /* stock 0x762990 */);
        return;
    }
    const uint8_t *mode = audio_ble_hci_radio_mode_state_50938e(1u);
    if (mode[0] < 4u) return;
    uint32_t config[2];
    const volatile uint32_t *stock=g2_uled_ldo_config_78de24;
    config[0]=stock[0];config[1]=stock[1];
    (void)display_driver_uled_pmic_ldo_switch_55fb7c(ldo,0u);
    (void)display_driver_uled_pmic_ldo_config_55fae2(ldo,config);
    (void)display_driver_uled_pmic_ldo_commit_55fad8(ldo,0u);
}
