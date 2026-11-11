/* Apollo S200 JBD4010 partial reflash at 0x592dea. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_jbd4010_framebuffer[] __asm__("g2_jbd4010_framebuffer");
extern unsigned char g2ref_g2_jbd4010_mspi_handle[] __asm__("g2_jbd4010_mspi_handle");

extern uint32_t display_driver_uled_qspi_write_async_59ce1e(const void *);
extern uint32_t display_driver_uled_command_5926ee(uint32_t,const void *,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);
extern void display_driver_uled_delay_449376(uint32_t);

uint32_t display_driver_uled_type0_frame_lower_592dea(uint32_t ignored0,
                                                        uint32_t ignored1,
                                                        uint32_t ignored2,
                                                        uint32_t ignored3,
                                                        uint32_t width,
                                                        uint32_t height) {
    (void)ignored0;(void)ignored1;(void)ignored2;(void)ignored3;
    if ((int32_t)width>=640) width=639u;
    if ((int32_t)height>=480) height=479u;
    (void)width;(void)height;
    uint8_t descriptor[28]={1u,0u,0u,0u,0u,0u,0u,0u,
                            0u,0u,0u,0u,2u,0x58u,2u};
    uint32_t context=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_framebuffer);
    for (uint32_t i=0;i<4u;i++) descriptor[20u+i]=(uint8_t)(context>>(8u*i));
    context=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_mspi_handle);
    for (uint32_t i=0;i<4u;i++) descriptor[24u+i]=(uint8_t)(context>>(8u*i));
    if (display_driver_uled_qspi_write_async_59ce1e(descriptor)!=0u)
        return 0u;
    uint32_t zero=0u;
    uint32_t result=display_driver_uled_command_5926ee(0x97u,&zero,0u);
    if (result!=0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,"driver.jbd4010" /* stock 0x785c90 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\jbd4010\\drv_mspi_jbd4010.c" /* stock 0x6f313c */,
                "am_devices_jbd4010_QSPI_PartialReflash_async" /* stock 0x733704 */,0x217u,
                "\r\nam_devices_mspi_jbd4010_QSPI_PartialReflash fail\r\n" /* stock 0x71e300 */);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                "[driver.jbd4010]\r\nam_devices_mspi_jbd4010_QSPI_PartialReflash fail\r\n" /* stock 0x6f9f44 */,
                "[driver.jbd4010]\r\nam_devices_mspi_jbd4010_QSPI_PartialReflash fail\r\n" /* stock 0x6f9f44 */);
    }
    display_driver_uled_delay_449376(2u);
    return result!=0u;
}
