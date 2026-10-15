/* Apollo S200 JBD4010 MSPI serial and quad transitions. */
#include <stdint.h>

extern uint32_t display_driver_uled_device_reconfigure_59c876(const void *,uint32_t);
extern uint32_t g2_norflash_config_transfer_4c0f78(uint32_t,uint32_t,const void *);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void error_log(uint32_t line,uint32_t detail,uint32_t short_detail,
                      uint32_t function) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
            (const char *)(uintptr_t)0x6f9fd4u,
            (const char *)(uintptr_t)function,line,
            (const char *)(uintptr_t)detail);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail);
}

void display_driver_uled_serial_mode_59c980(const void *configuration,
                                              uint32_t handle) {
    if (display_driver_uled_device_reconfigure_59c876(configuration,handle)!=0u) {
        error_log(0x5au,0x753d74u,0x71e568u,0x75f870u);
        return;
    }
    uint8_t mode=0u;
    if (g2_norflash_config_transfer_4c0f78(handle,0x18u,&mode)!=0u)
        error_log(0x60u,0x75f890u,0x729010u,0x75f870u);
}

void display_driver_uled_quad_mode_59ca2c(const void *configuration,
                                            uint32_t handle) {
    uint8_t changed[24];
    const uint8_t *original=(const uint8_t *)configuration;
    for (uint32_t i=0;i<24u;i++) changed[i]=original[i];
    changed[0]=1u;changed[8]=0x10u;changed[15]=1u;
    if (display_driver_uled_device_reconfigure_59c876(changed,handle)!=0u) {
        error_log(0x6fu,0x753d98u,0x71e5a0u,0x75f8b0u);
        return;
    }
    uint8_t mode=0x10u;
    if (g2_norflash_config_transfer_4c0f78(handle,0x18u,&mode)!=0u)
        error_log(0x75u,0x75f8d0u,0x729044u,0x75f8b0u);
}
