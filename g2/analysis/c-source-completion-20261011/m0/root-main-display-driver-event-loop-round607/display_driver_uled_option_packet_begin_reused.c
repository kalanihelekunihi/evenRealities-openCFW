/* Apollo S200 packet begin wrapper at 0x59c980. */
#include <stdint.h>

extern uint32_t display_driver_uled_device_check_59c876(uint32_t,uint32_t);
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t,uint32_t,
                                                              const void *);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

void display_driver_uled_packet_begin_59c980(uint32_t context,uint32_t device) {
    if (display_driver_uled_device_check_59c876(context,device) != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x75f870u,0x5au,
                (const char *)(uintptr_t)0x753d74u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x71e568u,
                (const char *)(uintptr_t)0x71e568u);
        return;
    }
    const uint8_t control=0u;
    if (g2_norflash_config_transfer_4c0f78(device,24u,&control) != 0u) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
                (const char *)(uintptr_t)0x6f9fd4u,
                (const char *)(uintptr_t)0x75f870u,0x60u,
                (const char *)(uintptr_t)0x75f890u);
        if ((g2_flashdb_candidate_flags() & 1u) ||
            (g2_flashdb_candidate_flags() & 4u))
            (void)audio_log_simple(0x04000000u,
                (const char *)(uintptr_t)0x729010u,
                (const char *)(uintptr_t)0x729010u);
    }
}
