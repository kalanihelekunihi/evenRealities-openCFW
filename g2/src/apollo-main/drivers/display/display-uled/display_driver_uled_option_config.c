/* Apollo S200 uLED MSPI initialization at 0x59cf1a. */
#include <stdint.h>

extern uint32_t audio_uart_sync_sem_new(uint32_t,uint32_t,const void *);
extern uint32_t g2_main_mspi_handle_init_4c0812(uint32_t,uint32_t *);
extern int32_t audio_uart_font_flash_power(void *,uint8_t,uint8_t);
extern uint32_t g2_main_mspi_handle_config_4c08a8(uint32_t,const void *);
extern uint32_t g2_norflash_configure_mspi_4c099c(uint32_t,const void *);
extern uint32_t g2_norflash_enable_mspi_4c0e1e(uint32_t);
extern void g2_norflash_clock_select_4c32b4(uint32_t,uint32_t);
extern uint32_t display_driver_uled_interrupt_clear_4c23de(uint32_t,uint32_t);
extern uint32_t display_driver_uled_interrupt_enable_4c2328(uint32_t,uint32_t);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint8_t,const char *,const char *,
                                     const char *,uint32_t,const char *,...);
extern uint32_t audio_log_simple(uint32_t,const char *,const char *,...);

static uint32_t mspi_init_failed(uint32_t line,uint32_t detail,uint32_t short_detail) {
    if ((g2_flashdb_candidate_flags()&2u)!=0u)
        g2_flashdb_candidate_log(1u,(const char *)(uintptr_t)0x77f0a4u,
            (const char *)(uintptr_t)0x6f9fd4u,
            (const char *)(uintptr_t)0x776e74u,line,
            (const char *)(uintptr_t)detail);
    if ((g2_flashdb_candidate_flags()&1u)!=0u ||
        (g2_flashdb_candidate_flags()&4u)!=0u)
        (void)audio_log_simple(0x04000000u,
            (const char *)(uintptr_t)short_detail,
            (const char *)(uintptr_t)short_detail);
    return UINT32_MAX;
}

uint32_t display_driver_uled_option_config_59cf1a(uint32_t *output,
                uint32_t mode,uint32_t serial_config,uint32_t quad_config) {
    *(volatile uint32_t *)(uintptr_t)0x20074538u=serial_config;
    *(volatile uint32_t *)(uintptr_t)0x2007453cu=quad_config;
    *(volatile uint32_t *)(uintptr_t)0x20074534u=
        audio_uart_sync_sem_new(1u,0u,0);
    uint32_t handle=0u;
    if (g2_main_mspi_handle_init_4c0812(0u,&handle)!=0u)
        return mspi_init_failed(0x141u,0x7499fcu,0x7148f0u);
    if (audio_uart_font_flash_power((void *)(uintptr_t)handle,0u,0u)!=0)
        return mspi_init_failed(0x147u,0x753de0u,0x71e5d8u);
    uint32_t configuration[3]={0x100u,mode,
        *(volatile const uint32_t *)(uintptr_t)0x20074004u};
    if (g2_main_mspi_handle_config_4c08a8(handle,configuration)!=0u)
        return mspi_init_failed(0x150u,0x73e6b8u,0x70b124u);
    if (g2_norflash_configure_mspi_4c099c(handle,
            (const void *)(uintptr_t)serial_config)!=0u)
        return mspi_init_failed(0x156u,0x753e04u,0x71e610u);
    if (g2_norflash_enable_mspi_4c0e1e(handle)!=0u)
        return mspi_init_failed(0x15cu,0x75f910u,0x7290acu);
    g2_norflash_clock_select_4c32b4(0u,0u);
    if (display_driver_uled_interrupt_clear_4c23de(handle,0x1a80u)!=0u)
        return UINT32_MAX;
    if (display_driver_uled_interrupt_enable_4c2328(handle,0x1a80u)!=0u)
        return mspi_init_failed(0x16bu,0x749a24u,0x71492cu);
    *(volatile uint8_t *)(uintptr_t)0xe000e414u=0x40u;
    *(volatile uint32_t *)(uintptr_t)0xe000e100u=0x00100000u;
    (void)audio_uart_font_flash_power((void *)(uintptr_t)handle,2u,1u);
    *output=handle;
    return 0u;
}
