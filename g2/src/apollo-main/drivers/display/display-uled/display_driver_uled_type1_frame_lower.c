/* Apollo S200 Hongshi partial-refresh wrapper at 0x5bcd44. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
/* Fix 48: stock flash 0x76b164, 28-byte MSPI transfer template (copy loop bound; stock image bytes). */
static const uint8_t g2_uled_mspi_template_76b164[28]={0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x2cu, 0x00u, 0x32u, 0x00u, 0x00u, 0x00u, 0x00u, 0x02u, 0x58u, 0x02u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u};
extern unsigned char g2ref_g2_a6ng_framebuffer[] __asm__("g2_a6ng_framebuffer");
extern unsigned char g2ref_g2_a6ng_mspi_handle[] __asm__("g2_a6ng_mspi_handle");

extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);
extern uint32_t display_driver_uled_qspi_write_async_59ce1e(const void *);

uint32_t display_driver_uled_type1_frame_lower_5bcd44(
        uint32_t x,uint32_t y,uint32_t a,uint32_t b,uint32_t width,uint32_t height) {
    (void)x;(void)y;(void)a;(void)b;
    /* The native routine clips its stack arguments, but copies a fixed
       descriptor template; the clipped values do not enter that descriptor. */
    if (width >= 640u) width=639u;
    if (height >= 480u) height=479u;
    (void)width;(void)height;
    uint32_t handle=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_mspi_handle);
    if (handle==0u) {
        if ((g2_flashdb_candidate_flags()&2u)!=0u)
            g2_flashdb_candidate_log(1u,"driver.a6n-g" /* stock 0x785c80 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\hongshi_a6ng\\drv_mspi_a6ng.c" /* stock 0x6ecca8 */,
                "am_devices_hongshi_QSPI_PartialReflash_async" /* stock 0x733614 */,0x339u,
                "Error - pMspiHandle is NULL\r\n" /* stock 0x75f7d0 */);
        if ((g2_flashdb_candidate_flags()&1u)!=0u ||
            (g2_flashdb_candidate_flags()&4u)!=0u)
            (void)audio_log_simple(0x04000000u,
                "[driver.a6n-g]Error - pMspiHandle is NULL\r\n" /* stock 0x73e424 */,
                "[driver.a6n-g]Error - pMspiHandle is NULL\r\n" /* stock 0x73e424 */);
        return UINT32_MAX;
    }
    uint8_t descriptor[28];
    const uint8_t *template=g2_uled_mspi_template_76b164;
    for (uint32_t i=0;i<28u;i++) descriptor[i]=template[i];
    uint32_t payload=*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_framebuffer);
    for (uint32_t i=0;i<4u;i++) {
        descriptor[20u+i]=(uint8_t)(payload>>(8u*i));
        descriptor[24u+i]=(uint8_t)(handle>>(8u*i));
    }
    (void)display_driver_uled_qspi_write_async_59ce1e(descriptor);
    return 0u;
}
