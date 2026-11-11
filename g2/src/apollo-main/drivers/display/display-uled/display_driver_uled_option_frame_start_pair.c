/* Apollo S200 option frame-start callbacks 0x5931c0 and 0x5bcb28.
 * The saved optional callback comes from the matching setup option.
 */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_20074518[] __asm__("g2_stock_ram_20074518");

typedef uint32_t (*uled_frame_hook)(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type0_frame_lower_592dea(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t display_driver_uled_type1_frame_lower_5bcd44(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);

uint32_t display_driver_uled_type0_frame_start_5931c0(void) {
    uled_frame_hook hook=(uled_frame_hook)(uintptr_t)
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074518+0x14u);
    if (hook != 0) (void)hook(0u,0u,0u,0x280u,0x1e0u);
    (void)display_driver_uled_type0_frame_lower_592dea(0u,0u,0u,0u,0x280u,0x1e0u);
    return 0u;
}

uint32_t display_driver_uled_type1_frame_start_5bcb28(void) {
    uled_frame_hook hook=(uled_frame_hook)(uintptr_t)
        *(volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074518);
    if (hook != 0) (void)hook(0u,0u,0u,0x280u,0x1e0u);
    (void)display_driver_uled_type1_frame_lower_5bcd44(0u,0u,0u,0u,0x280u,0x1e0u);
    return 0u;
}
