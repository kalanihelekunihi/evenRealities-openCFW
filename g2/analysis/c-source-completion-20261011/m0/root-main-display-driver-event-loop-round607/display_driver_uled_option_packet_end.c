/* Apollo S200 packet end wrapper at 0x59ca2c. */
#include <stdint.h>

extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
extern uint32_t display_driver_uled_device_check_59c876(const void *,uint32_t);
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t,uint32_t,
                                                     const void *);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_packet_end_59ca2c(const void *context,
                                             uint32_t device) {
    uint8_t descriptor[24];
    audio_uart_checksum_copy(descriptor,context,24u);
    descriptor[8]=0x10u;
    descriptor[0]=1u;
    descriptor[15]=1u;
    if (display_driver_uled_device_check_59c876(descriptor,device) != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x75f8b0u,0x6fu,
                (const char *)(uintptr_t)0x753d98u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x71e5a0u,
                (const char *)(uintptr_t)0x71e5a0u);
        return;
    }
    const uint8_t control=0x10u;
    if (g2_norflash_config_transfer_4c0f78(device,24u,&control) != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x75f8b0u,0x75u,
                (const char *)(uintptr_t)0x75f8d0u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x729044u,
                (const char *)(uintptr_t)0x729044u);
    }
}
