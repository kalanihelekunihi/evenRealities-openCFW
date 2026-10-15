/* Apollo S200 JBD4010 MSPI device reconfiguration at 0x59c876. */
#include <stdint.h>

extern uint32_t display_driver_uled_mspi_disable_4c0ea8(uint32_t);
extern uint32_t g2_norflash_configure_mspi_4c099c(uint32_t,const void *);
extern uint32_t display_driver_uled_mspi_enable_4c0e1e(uint32_t);
extern void display_driver_uled_mspi_pin_mode_4c32b4(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void reconfigure_error(uint32_t line,uint32_t detail,
                              uint32_t short_detail) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
            (const char *)(uintptr_t)0x6f9fd4u,
            (const char *)(uintptr_t)0x753d08u,line,
            (const char *)(uintptr_t)detail);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail);
}

uint32_t display_driver_uled_device_reconfigure_59c876(const void *configuration,
                                                          uint32_t handle) {
    if (display_driver_uled_mspi_disable_4c0ea8(handle)!=0u) {
        reconfigure_error(0x3du,0x753d2cu,0x71e4f8u);
        return UINT32_MAX;
    }
    if (g2_norflash_configure_mspi_4c099c(handle,configuration)!=0u) {
        reconfigure_error(0x45u,0x753d50u,0x71e530u);
        return UINT32_MAX;
    }
    if (display_driver_uled_mspi_enable_4c0e1e(handle)!=0u) {
        reconfigure_error(0x4du,0x753d50u,0x71e530u);
        return UINT32_MAX;
    }
    display_driver_uled_mspi_pin_mode_4c32b4(0u,
        ((const uint8_t *)configuration)[8]);
    return 0u;
}
