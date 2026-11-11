/* Apollo S200 JBD4010 MSPI device reconfiguration at 0x59c876. */
#include <stdint.h>

extern uint32_t g2_norflash_disable_mspi_4c0ea8(uint32_t);
extern uint32_t g2_norflash_configure_mspi_4c099c(uint32_t,const void *);
extern uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t);
extern void g2_norflash_clock_select_4c32b4(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static void reconfigure_error(uint32_t line,uint32_t detail,
                              uint32_t short_detail) {
    if (g2_flashdb_candidate_flags() & 2u)
        g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
            "am_devices_mspi_device_reconfigure" /* stock 0x753d08 */,line,
            (const char *)(uintptr_t)detail);
    if ((g2_flashdb_candidate_flags() & 1u) ||
        (g2_flashdb_candidate_flags() & 4u))
        (void)audio_log_simple(0x04000000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail);
}

uint32_t display_driver_uled_device_reconfigure_59c876(const void *configuration,
                                                          uint32_t handle) {
    if (g2_norflash_disable_mspi_4c0ea8(handle)!=0u) {
        reconfigure_error(0x3du,(uint32_t)(uintptr_t)"Error - Failed to disable mspi.\n" /* stock 0x753d2c */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to disable mspi.\n" /* stock 0x71e4f8 */);
        return UINT32_MAX;
    }
    if (g2_norflash_configure_mspi_4c099c(handle,configuration)!=0u) {
        reconfigure_error(0x45u,(uint32_t)(uintptr_t)"Error - Failed to configure mspi.\n" /* stock 0x753d50 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to configure mspi.\n" /* stock 0x71e530 */);
        return UINT32_MAX;
    }
    if (g2_norflash_enable_mspi_4c0e1e(handle)!=0u) {
        reconfigure_error(0x4du,(uint32_t)(uintptr_t)"Error - Failed to configure mspi.\n" /* stock 0x753d50 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to configure mspi.\n" /* stock 0x71e530 */);
        return UINT32_MAX;
    }
    g2_norflash_clock_select_4c32b4(0u,
        ((const uint8_t *)configuration)[8]);
    return 0u;
}
