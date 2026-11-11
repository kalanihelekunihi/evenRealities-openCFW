/* Apollo uLED option setup callbacks 0x592680 and 0x5bbd70. Candidate.
 * Child configuration/enable providers remain independent source gates.
 */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_a6ng_framebuffer[] __asm__("g2_a6ng_framebuffer");
extern unsigned char g2ref_g2_a6ng_mspi_handle[] __asm__("g2_a6ng_mspi_handle");
extern unsigned char g2ref_g2_jbd4010_framebuffer[] __asm__("g2_jbd4010_framebuffer");
extern unsigned char g2ref_g2_jbd4010_mspi_handle[] __asm__("g2_jbd4010_mspi_handle");
extern unsigned char g2ref_g2_stock_ram_20074518[] __asm__("g2_stock_ram_20074518");
/* sim15: MSPI0 device-config records at stock .data 0x20000758..0x200007a0
 * (type1 serial 0x758, type1 quad 0x770, type0 serial 0x788). Evidence: values
 * copied verbatim from .waves/init_20000000.bin offsets 0x758..0x7a0 (no
 * pointers); the stock hook on 0x59cf1a shows r2=0x20000788 reading
 * {0x201,0,0x0f000000,0x01010000,0,0}. 0x200007a0 (type0 quad) is the existing
 * g2_stock_ram_200007a0 cell. Raw addresses made g2_norflash_configure_mspi_4c099c
 * fail, so MSPI0/panel never initialized. */
static uint32_t g2_stock_ram_20000758[18] __attribute__((aligned(8))) = {
    0x00000100u, 0x00000000u, 0x0e000000u, 0x01000000u, 0x00000000u, 0x00000000u,
    0x00000300u, 0x00000000u, 0x10000010u, 0x00000100u, 0x00000000u, 0x00000000u,
    0x00000201u, 0x00000000u, 0x0f000000u, 0x01010000u, 0x00000000u, 0x00000000u,
};
extern uint32_t g2_stock_ram_200007a0[];
#define DEVCFG(a) ((uint32_t)(uintptr_t)&g2_stock_ram_20000758[((a) - 0x20000758u) / 4u])
extern uint32_t display_driver_uled_option_config_59cf1a(uint32_t *,uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_option_type0_enable_5926b4(uint32_t);
extern uint32_t display_driver_uled_option_type1_enable_5bbda4(uint32_t);

uint32_t display_driver_uled_option_type0_setup_592680(uint32_t handle,
                                                         uint32_t argument,
                                                         uint32_t callback) {
    if(handle==0u)return UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074518+0x14u)=handle;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_framebuffer)=argument;
    (void)display_driver_uled_option_config_59cf1a(
        (uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_jbd4010_mspi_handle),callback,DEVCFG(0x20000788u),(uint32_t)(uintptr_t)g2_stock_ram_200007a0);
    return display_driver_uled_option_type0_enable_5926b4(1u);
}

uint32_t display_driver_uled_option_type1_setup_5bbd70(uint32_t handle,
                                                         uint32_t argument,
                                                         uint32_t callback) {
    if(handle==0u)return UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074518)=handle;
    *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_framebuffer)=argument;
    (void)display_driver_uled_option_config_59cf1a(
        (uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_a6ng_mspi_handle),callback,DEVCFG(0x20000758u),DEVCFG(0x20000770u));
    return display_driver_uled_option_type1_enable_5bbda4(1u);
}
