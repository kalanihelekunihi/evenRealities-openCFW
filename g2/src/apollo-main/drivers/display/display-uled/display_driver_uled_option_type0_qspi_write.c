/* Apollo S200 asynchronous JBD4010 QSPI write at 0x59ce1e. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200007a0[] __asm__("g2_stock_ram_200007a0");
extern unsigned char g2ref_g2_uled_mspi_quad_config[] __asm__("g2_uled_mspi_quad_config");
extern unsigned char g2ref_g2_uled_mspi_semaphore[] __asm__("g2_uled_mspi_semaphore");
extern unsigned char g2ref_g2_uled_mspi_serial_config[] __asm__("g2_uled_mspi_serial_config");

extern uint32_t display_driver_uled_packet_validate_59cb42(const void *,const char *);
extern void display_driver_uled_quad_mode_59ca2c(uint32_t,uint32_t);
extern void display_driver_uled_interrupt_clear_4c23de(uint32_t,uint32_t);
extern void display_driver_uled_interrupt_enable_4c2328(uint32_t,uint32_t);
extern void display_driver_uled_prepare_transfer_47510e(const void *);
extern uint32_t display_driver_uled_transfer_async_4c2208(uint32_t,const void *,
                                                           uint32_t,void *,void *);
/* Stock callback 0x59c867 = mspi_transfer_callback (0x59c866, symbols/apollo_main.tsv;
 * same body: *ctx=status; osSemaphoreRelease(g2_uled_mspi_semaphore @0x20074534)). */
extern void mspi_transfer_callback(void *,uint32_t);
extern int32_t audio_semaphore_acquire(void *,uint32_t);
extern void display_driver_uled_serial_mode_59c980(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static uint32_t word(const uint8_t *p,uint32_t offset) {
    const uint8_t *q=p+offset;
    return (uint32_t)q[0]|((uint32_t)q[1]<<8)|
           ((uint32_t)q[2]<<16)|((uint32_t)q[3]<<24);
}
static void put(uint8_t *p,uint32_t offset,uint32_t value) {
    for (uint32_t i=0;i<4u;i++) p[offset+i]=(uint8_t)(value>>(8u*i));
}

uint32_t display_driver_uled_qspi_write_async_59ce1e(const void *descriptor) {
    const uint8_t *input=(const uint8_t *)descriptor;
    const void *validation_context="am_devices_mspi_qspi_write_async" /* stock 0x753dbc */;
    uint32_t validation=display_driver_uled_packet_validate_59cb42(
        descriptor,(const char *)validation_context);
    if (validation!=0u)
        return validation;
    uint32_t handle=word(input,24u);
    display_driver_uled_quad_mode_59ca2c(
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_quad_config),handle);
    display_driver_uled_interrupt_clear_4c23de(handle,0x1a80u);
    display_driver_uled_interrupt_enable_4c2328(handle,0x1a80u);
    uint32_t transfer_info[2]={word(input,20u),word(input,12u)};
    display_driver_uled_prepare_transfer_47510e(transfer_info);
    uint8_t transfer[24]={1u,1u};
    put(transfer,4u,word(input,12u));
    put(transfer,8u,word(input,4u));
    put(transfer,12u,word(input,20u));
    uint32_t queued=display_driver_uled_transfer_async_4c2208(handle,transfer,1u,
        (void *)mspi_transfer_callback,(void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200007a0+0x4cu));
    uint32_t acquired=(uint32_t)audio_semaphore_acquire(
        (void *)(uintptr_t)*(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_semaphore),
        3000u);
    if (acquired!=0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
                "am_devices_mspi_qspi_write_async" /* stock 0x753dbc */,0x12au,
                "Error - Failed to acquire semaphore. code = %d\n" /* stock 0x733854 */,acquired);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04400000u,
                "[driver.uled_common]Error - Failed to acquire semaphore. code = %d\n" /* stock 0x702548 */,
                "[driver.uled_common]Error - Failed to acquire semaphore. code = %d\n" /* stock 0x702548 */,acquired);
    }
    display_driver_uled_serial_mode_59c980(
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_serial_config),handle);
    return acquired==0u ? queued : UINT32_MAX;
}
