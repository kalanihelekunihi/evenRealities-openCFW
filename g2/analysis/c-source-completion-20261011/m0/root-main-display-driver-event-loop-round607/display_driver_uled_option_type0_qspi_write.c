/* Apollo S200 asynchronous JBD4010 QSPI write at 0x59ce1e. */
#include <stdint.h>

extern uint32_t display_driver_uled_packet_validate_59cb42(const void *,const char *);
extern void display_driver_uled_quad_mode_59ca2c(uint32_t,uint32_t);
extern void display_driver_uled_interrupt_clear_4c23de(uint32_t,uint32_t);
extern void display_driver_uled_interrupt_enable_4c2328(uint32_t,uint32_t);
extern void display_driver_uled_prepare_transfer_47510e(const void *);
extern uint32_t display_driver_uled_transfer_async_4c2208(uint32_t,const void *,
                                                           uint32_t,void *,void *);
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
    const void *validation_context=(const void *)(uintptr_t)0x753dbcu;
    uint32_t validation=display_driver_uled_packet_validate_59cb42(
        descriptor,(const char *)validation_context);
    if (validation!=0u)
        return validation;
    uint32_t handle=word(input,24u);
    display_driver_uled_quad_mode_59ca2c(
        *(volatile const uint32_t *)(uintptr_t)0x2007453cu,handle);
    display_driver_uled_interrupt_clear_4c23de(handle,0x1a80u);
    display_driver_uled_interrupt_enable_4c2328(handle,0x1a80u);
    uint32_t transfer_info[2]={word(input,20u),word(input,12u)};
    display_driver_uled_prepare_transfer_47510e(transfer_info);
    uint8_t transfer[24]={1u,1u};
    put(transfer,4u,word(input,12u));
    put(transfer,8u,word(input,4u));
    put(transfer,12u,word(input,20u));
    uint32_t queued=display_driver_uled_transfer_async_4c2208(handle,transfer,1u,
        (void *)(uintptr_t)0x59c867u,(void *)(uintptr_t)0x200007ecu);
    uint32_t acquired=(uint32_t)audio_semaphore_acquire(
        (void *)(uintptr_t)*(volatile const uint32_t *)(uintptr_t)0x20074534u,
        3000u);
    if (acquired!=0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x753dbcu,0x12au,
                (const char *)(uintptr_t)0x733854u,acquired);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04400000u,
                (const char *)(uintptr_t)0x702548u,
                (const char *)(uintptr_t)0x702548u,acquired);
    }
    display_driver_uled_serial_mode_59c980(
        *(volatile const uint32_t *)(uintptr_t)0x20074538u,handle);
    return acquired==0u ? queued : UINT32_MAX;
}
