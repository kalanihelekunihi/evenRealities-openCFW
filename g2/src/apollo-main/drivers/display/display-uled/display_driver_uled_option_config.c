/* Apollo S200 uLED MSPI initialization at 0x59cf1a. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074000[] __asm__("g2_stock_ram_20074000"); /* Fix 44: stock owner of blob+offset access */
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20073f30[] __asm__("g2_stock_ram_20073f30");
extern unsigned char g2ref_g2_uled_mspi_quad_config[] __asm__("g2_uled_mspi_quad_config");
extern unsigned char g2ref_g2_uled_mspi_semaphore[] __asm__("g2_uled_mspi_semaphore");
extern unsigned char g2ref_g2_uled_mspi_serial_config[] __asm__("g2_uled_mspi_serial_config");

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
        g2_flashdb_candidate_log(1u,"driver.uled_common" /* stock 0x77f0a4 */,
            "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled_common.c" /* stock 0x6f9fd4 */,
            "am_devices_mspi_init" /* stock 0x776e74 */,line,
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
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_serial_config)=serial_config;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_quad_config)=quad_config;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_uled_mspi_semaphore)=
        audio_uart_sync_sem_new(1u,0u,0);
    uint32_t handle=0u;
    if (g2_main_mspi_handle_init_4c0812(0u,&handle)!=0u)
        return mspi_init_failed(0x141u,(uint32_t)(uintptr_t)"Error - Failed to initialize MSPI.\r\n" /* stock 0x7499fc */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to initialize MSPI.\r\n" /* stock 0x7148f0 */);
    if (audio_uart_font_flash_power((void *)(uintptr_t)handle,0u,0u)!=0)
        return mspi_init_failed(0x147u,(uint32_t)(uintptr_t)"Error - Failed to power on MSPI.\r\n" /* stock 0x753de0 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to power on MSPI.\r\n" /* stock 0x71e5d8 */);
    uint32_t configuration[3]={0x100u,mode,
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074000+0x4u)};
    if (g2_main_mspi_handle_config_4c08a8(handle,configuration)!=0u)
        return mspi_init_failed(0x150u,(uint32_t)(uintptr_t)"Error - Failed to configure MSPI device.\r\n" /* stock 0x73e6b8 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to configure MSPI device.\r\n" /* stock 0x70b124 */);
    if (g2_norflash_configure_mspi_4c099c(handle,
            (const void *)(uintptr_t)serial_config)!=0u)
        return mspi_init_failed(0x156u,(uint32_t)(uintptr_t)"Error - Failed to configure MSPI.\r\n" /* stock 0x753e04 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to configure MSPI.\r\n" /* stock 0x71e610 */);
    if (g2_norflash_enable_mspi_4c0e1e(handle)!=0u)
        return mspi_init_failed(0x15cu,(uint32_t)(uintptr_t)"Error - Failed to enable MSPI.\n" /* stock 0x75f910 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to enable MSPI.\n" /* stock 0x7290ac */);
    g2_norflash_clock_select_4c32b4(0u,0u);
    if (display_driver_uled_interrupt_clear_4c23de(handle,0x1a80u)!=0u)
        return UINT32_MAX;
    if (display_driver_uled_interrupt_enable_4c2328(handle,0x1a80u)!=0u)
        return mspi_init_failed(0x16bu,(uint32_t)(uintptr_t)"Error - Failed to enable interrupt .\n" /* stock 0x749a24 */,(uint32_t)(uintptr_t)"[driver.uled_common]Error - Failed to enable interrupt .\n" /* stock 0x71492c */);
    *(volatile uint8_t *)(uintptr_t)0xe000e414u=0x40u;
    *(volatile uint32_t *)(uintptr_t)0xe000e100u=0x00100000u;
    (void)audio_uart_font_flash_power((void *)(uintptr_t)handle,2u,1u);
    *output=handle;
    return 0u;
}
