/* Apollo S200 type-0 LDO mode-4 finish wrapper at 0x5125a8. */
#include <stdint.h>

extern uint32_t display_driver_uled_pmic_ldo_find_55face(uint32_t,uint32_t);
extern uint32_t display_driver_uled_pmic_ldo_commit_55fad8(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                      const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_type0_mode4_finish_5125a8(void) {
    uint32_t ldo=display_driver_uled_pmic_ldo_find_55face(0x20070f78u,1u);
    if (ldo == 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x78b618u,
                (const char *)(uintptr_t)0x6e103cu,
                (const char *)(uintptr_t)0x779c04u,0x41eu,
                (const char *)(uintptr_t)0x7814f8u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x762990u,
                (const char *)(uintptr_t)0x762990u);
        return;
    }
    (void)display_driver_uled_pmic_ldo_commit_55fad8(ldo,1u);
}
