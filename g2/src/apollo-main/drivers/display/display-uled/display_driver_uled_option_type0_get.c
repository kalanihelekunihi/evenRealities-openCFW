/* Apollo S200 type-0 option register getter at 0x592f9a. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type0_read_59275e(uint32_t,void *,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

uint32_t display_driver_uled_type0_get_592f9a(uint16_t *value) {
    uint8_t reply[36];
    audio_uart_buffer_zero(reply,36u,0u);
    uint32_t status=display_driver_uled_type0_read_59275e(0x9fu,reply,4u);
    if (status != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(2u,"driver.jbd4010" /* stock 0x785c90 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
                "am_devices_mspi_jbd4010_read_chipId" /* stock 0x753c9c */,0x256u,
                "read chip id failed,errno number = %d\r\n" /* stock 0x749894 */,status);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x08400000u,
                "[driver.jbd4010]read chip id failed,errno number = %d\r\n" /* stock 0x71e338 */,
                "[driver.jbd4010]read chip id failed,errno number = %d\r\n" /* stock 0x71e338 */,status);
        return UINT32_MAX;
    }
    uint32_t result=((uint32_t)reply[1]<<8) | reply[2];
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(3u,"driver.jbd4010" /* stock 0x785c90 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
            "am_devices_mspi_jbd4010_read_chipId" /* stock 0x753c9c */,0x259u,
            "jbd panel devicve id:  %04x" /* stock 0x76b1d4 */,result);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x0c400000u,
            "[driver.jbd4010]jbd panel devicve id:  %04x" /* stock 0x73e500 */,
            "[driver.jbd4010]jbd panel devicve id:  %04x" /* stock 0x73e500 */,result);
    if (value != 0) *value=(uint16_t)result;
    return 0u;
}
