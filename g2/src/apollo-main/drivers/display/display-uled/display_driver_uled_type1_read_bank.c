/* Apollo S200 Hongshi bank read with three-attempt retry at 0x5bbe80. */
#include <stdint.h>

extern uint32_t display_driver_uled_type1_read_register_5bbe3e(uint32_t,
                                                                 uint32_t *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_delay_449376(uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type1_read_bank_5bbe80(uint32_t bank,
                                                      uint32_t mode) {
    uint32_t word=0u,attempts=0u,result;
    do {
        result=display_driver_uled_type1_read_register_5bbe3e(
            (uint8_t)bank,&word,1u,(uint8_t)mode);
        if (result==0u) break;
        attempts=(uint8_t)(attempts+1u);
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(2u,"driver.a6n-g" /* stock 0x785c80 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
                "am_devices_mspi_hongshi_read_bank" /* stock 0x753b34 */,0x140u,
                "Error - Failed to read bank, resend times %d  ui32Status %d \r\n" /* stock 0x70af64 */,attempts,result);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x08800000u,
                "[driver.a6n-g]Error - Failed to read bank, resend times %d  ui32Status %d \r\n" /* stock 0x6eccf8 */,
                "[driver.a6n-g]Error - Failed to read bank, resend times %d  ui32Status %d \r\n" /* stock 0x6eccf8 */,attempts,result);
        (void)display_driver_uled_delay_449376(2u);
    } while (attempts<3u);
    if (attempts==3u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,"driver.a6n-g" /* stock 0x785c80 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
                "am_devices_mspi_hongshi_read_bank" /* stock 0x753b34 */,0x148u,
                "Error - Failed to read bank resending exceeds %d times \r\n" /* stock 0x71465c */,attempts);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04400000u,
                "[driver.a6n-g]Error - Failed to read bank resending exceeds %d times \r\n" /* stock 0x6f9d94 */,
                "[driver.a6n-g]Error - Failed to read bank resending exceeds %d times \r\n" /* stock 0x6f9d94 */,attempts);
        return 0xffu;
    }
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(4u,"driver.a6n-g" /* stock 0x785c80 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
            "am_devices_mspi_hongshi_read_bank" /* stock 0x753b34 */,0x150u,
            "am_devices_mspi_hongshi_read ui32Status: 0x%04x  %02x %02x %02x %02x \r\n" /* stock 0x6f9ddc */,result,
            (word>>24)&0xffu,(word>>16)&0xffu,(word>>8)&0xffu,word&0xffu);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x11400000u,
            "[driver.a6n-g]am_devices_mspi_hongshi_read ui32Status: 0x%04x  %02x %02x %02x %02x \r\n" /* stock 0x6e2fe8 */,
            "[driver.a6n-g]am_devices_mspi_hongshi_read ui32Status: 0x%04x  %02x %02x %02x %02x \r\n" /* stock 0x6e2fe8 */,result,
            (word>>24)&0xffu,(word>>16)&0xffu,(word>>8)&0xffu,word&0xffu);
    return word&0xffu;
}
