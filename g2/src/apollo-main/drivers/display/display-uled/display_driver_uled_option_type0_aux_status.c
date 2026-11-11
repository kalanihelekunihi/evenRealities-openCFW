/* Apollo S200 type-0 auxiliary status check at 0x593398. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type0_read_59275e(uint32_t,void *,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void report(uint32_t line,const char *detail,const char *short_detail,
                   uint32_t value) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(2u,"driver.jbd4010" /* stock 0x785c90 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
            "jdb4010_status_check" /* stock 0x776d24 */,line,detail,value);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x08400000u,short_detail,short_detail,value);
}

uint32_t display_driver_uled_type0_aux_status_593398(uint32_t unused) {
    (void)unused;
    uint8_t reply[8];
    audio_uart_buffer_zero(reply,8u,0u);
    uint32_t status=display_driver_uled_type0_read_59275e(5u,reply,1u);
    if (status != 0u) {
        report(0x2dau,"read status reg1 failed,errno number = %d" /* stock 0x73e52c */,
            "[driver.jbd4010]read status reg1 failed,errno number = %d" /* stock 0x714800 */,status);
        return UINT32_MAX;
    }
    if (reply[0] == 0x90u) {
        report(0x2ddu,"read status reg failed,status reg1 = 0x%02x" /* stock 0x73e558 */,
            "[driver.jbd4010]read status reg failed,status reg1 = 0x%02x" /* stock 0x71483c */,reply[0]);
        return UINT32_MAX;
    }
    status=display_driver_uled_type0_read_59275e(0x35u,reply,1u);
    if (status != 0u) {
        report(0x2e3u,"read status reg2 failed,errno number = %d" /* stock 0x73e584 */,
            "[driver.jbd4010]read status reg2 failed,errno number = %d" /* stock 0x714878 */,status);
        return UINT32_MAX;
    }
    if (reply[0] == 0u) {
        report(0x2e6u,"read status reg failed,status reg2 = 0x%02x" /* stock 0x73e5b0 */,
            "[driver.jbd4010]read status reg failed,status reg2 = 0x%02x" /* stock 0x7148b4 */,reply[0]);
        return UINT32_MAX;
    }
    return 0u;
}
