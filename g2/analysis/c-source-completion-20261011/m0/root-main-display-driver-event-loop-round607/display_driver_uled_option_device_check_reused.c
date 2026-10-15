/* Apollo S200 uLED device gate at 0x59c876. */
#include <stdint.h>

extern uint32_t g2_norflash_disable_mspi_4c0ea8(uint32_t);
extern uint32_t display_driver_uled_device_bind_4c099c(uint32_t,uint32_t);
extern uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t);
extern void display_driver_uled_device_select_4c32b4(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void device_check_error(uint32_t line,const char *detail,
                               const char *short_detail) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
            (const char *)(uintptr_t)0x6f9fd4u,
            (const char *)(uintptr_t)0x753d08u,line,detail);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u,short_detail,short_detail);
}

uint32_t display_driver_uled_device_check_59c876(const uint8_t *context,
                                                   uint32_t device) {
    if (g2_norflash_disable_mspi_4c0ea8(device) != 0u) {
        device_check_error(0x3du,(const char *)(uintptr_t)0x753d2cu,
                          (const char *)(uintptr_t)0x71e4f8u);
        return UINT32_MAX;
    }
    if (display_driver_uled_device_bind_4c099c(device,
                                                 (uint32_t)(uintptr_t)context) != 0u) {
        device_check_error(0x45u,(const char *)(uintptr_t)0x753d50u,
                          (const char *)(uintptr_t)0x71e530u);
        return UINT32_MAX;
    }
    if (g2_norflash_enable_mspi_4c0e1e(device) != 0u) {
        device_check_error(0x4du,(const char *)(uintptr_t)0x753d50u,
                          (const char *)(uintptr_t)0x71e530u);
        return UINT32_MAX;
    }
    display_driver_uled_device_select_4c32b4(0u,context[8]);
    return 0u;
}
