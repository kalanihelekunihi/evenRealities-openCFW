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
        g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
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
        error_log(0x5au,(uint32_t)(uintptr_t)"Failed to reconfigure serail mode\n" /* stock 0x753d74 */,(uint32_t)(uintptr_t)"[driver.uled_common]Failed to reconfigure serail mode\n" /* stock 0x71e568 */,(uint32_t)(uintptr_t)"am_devices_mspi_set_serail_mode" /* stock 0x75f870 */);
        return;
    }
    uint8_t mode=0u;
    if (g2_norflash_config_transfer_4c0f78(handle,0x18u,&mode)!=0u)
        error_log(0x60u,(uint32_t)(uintptr_t)"Failed to control serail mode\n" /* stock 0x75f890 */,(uint32_t)(uintptr_t)"[driver.uled_common]Failed to control serail mode\n" /* stock 0x729010 */,(uint32_t)(uintptr_t)"am_devices_mspi_set_serail_mode" /* stock 0x75f870 */);
}

void display_driver_uled_quad_mode_59ca2c(const void *configuration,
                                            uint32_t handle) {
    uint8_t changed[24];
    const uint8_t *original=(const uint8_t *)configuration;
    for (uint32_t i=0;i<24u;i++) changed[i]=original[i];
    changed[0]=1u;changed[8]=0x10u;changed[15]=1u;
    if (display_driver_uled_device_reconfigure_59c876(changed,handle)!=0u) {
        error_log(0x6fu,(uint32_t)(uintptr_t)"Failed to reconfigure quad mode\n" /* stock 0x753d98 */,(uint32_t)(uintptr_t)"[driver.uled_common]Failed to reconfigure quad mode\n" /* stock 0x71e5a0 */,(uint32_t)(uintptr_t)"am_devices_mspi_set_quad_mode" /* stock 0x75f8b0 */);
        return;
    }
    uint8_t mode=0x10u;
    if (g2_norflash_config_transfer_4c0f78(handle,0x18u,&mode)!=0u)
        error_log(0x75u,(uint32_t)(uintptr_t)"Failed to control quad mode\n" /* stock 0x75f8d0 */,(uint32_t)(uintptr_t)"[driver.uled_common]Failed to control quad mode\n" /* stock 0x729044 */,(uint32_t)(uintptr_t)"am_devices_mspi_set_quad_mode" /* stock 0x75f8b0 */);
}
