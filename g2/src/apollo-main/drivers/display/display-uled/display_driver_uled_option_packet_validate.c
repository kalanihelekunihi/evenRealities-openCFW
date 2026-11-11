/* Apollo S200 packet descriptor validator at 0x59cb42. */
#include <stdint.h>

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_packet_validate_59cb42(const void *packet,
                                                      const char *caller) {
    uint32_t line;
    const char *detail;
    if (packet == 0) {
        line=0x98u;
        detail="Error - %s: param is NULL\r\n" /* stock 0x76b2d0 */;
    } else if (((const uint32_t *)packet)[6] == 0u) {
        line=0x9du;
        detail="Error - %s: pHandle is NULL\r\n" /* stock 0x75f8f0 */;
    } else if (((const uint32_t *)packet)[5] == 0u) {
        line=0xa2u;
        detail="Error - %s: pData is NULL\r\n" /* stock 0x76b2ec */;
    } else {
        return 0u;
    }
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
            "uled_rw_param_validate" /* stock 0x776e2c */,line,detail,caller);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u)) {
        const char *short_detail=line==0x98u
            ? "[driver.uled_common]Error - %s: param is NULL\r\n" /* stock 0x733794 */: line==0x9du ? "[driver.uled_common]Error - %s: pHandle is NULL\r\n" /* stock 0x729078 */: "[driver.uled_common]Error - %s: pData is NULL\r\n" /* stock 0x7337c4 */;
        (void)audio_log_simple(0x04400000u,short_detail,short_detail,caller);
    }
    return UINT32_MAX;
}
