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
            g2_flashdb_candidate_log(1u,"driver.jbd4010" /* stock 0x785c90 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
                "am_devices_jbd4010_status_check_and_recovery" /* stock 0x733734 */,0x332u,
                "jdb4010 status is abnormal, recovery" /* stock 0x74995c */);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                "[driver.jbd4010]jdb4010 status is abnormal, recovery" /* stock 0x71e3a8 */,
                "[driver.jbd4010]jdb4010 status is abnormal, recovery" /* stock 0x71e3a8 */);
        display_driver_uled_type0_aux_recover_593528();
        result=0u;
    } else {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(4u,"driver.jbd4010" /* stock 0x785c90 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
                "am_devices_jbd4010_status_check_and_recovery" /* stock 0x733734 */,0x336u,
                "jdb4010 status is normal" /* stock 0x76b1f0 */);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x10000000u,
                "[driver.jbd4010]jdb4010 status is normal" /* stock 0x73e5dc */,
                "[driver.jbd4010]jdb4010 status is normal" /* stock 0x73e5dc */);
        result=1u;
    }
    display_driver_uled_type0_aux_complete_593660();
    return result;
}
