/* Apollo S200 type-0 option callback at 0x5936a4. */
#include <stdint.h>

extern uint32_t display_driver_uled_type0_aux_status_593398(uint32_t);
extern void display_driver_uled_type0_aux_recover_593528(void);
extern void display_driver_uled_type0_aux_complete_593660(void);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_aux_finish_5936a4(void) {
    uint32_t status=display_driver_uled_type0_aux_status_593398(1u);
    uint32_t result;
    if (status != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x785c90u,
                (const char *)(uintptr_t)0x6f313cu,
                (const char *)(uintptr_t)0x733734u,0x332u,
                (const char *)(uintptr_t)0x74995cu);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x71e3a8u,
                (const char *)(uintptr_t)0x71e3a8u);
        display_driver_uled_type0_aux_recover_593528();
        result=0u;
    } else {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(4u,(const char *)(uintptr_t)0x785c90u,
                (const char *)(uintptr_t)0x6f313cu,
                (const char *)(uintptr_t)0x733734u,0x336u,
                (const char *)(uintptr_t)0x76b1f0u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x10000000u,
                (const char *)(uintptr_t)0x73e5dcu,
                (const char *)(uintptr_t)0x73e5dcu);
        result=1u;
    }
    display_driver_uled_type0_aux_complete_593660();
    return result;
}
