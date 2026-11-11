/* SPDX-License-Identifier: MIT
 * BINH A stage-1 boot setup at stock 0x10000acc..0x10000af8.
 * Calls and the NOR boot-device branch follow the locked C-SKY body.
 */
#include <stdint.h>

extern void gx8002_image_a_stage1_boot_mode_10000a04(void);
extern void gx8002_image_a_stage1_clock_setup_10000f14(void);
extern void gx8002_image_a_stage1_clock_init_1000092c(void);
extern void gx8002_image_a_stage1_timer_start_10000f04(uint32_t, uint32_t);
extern int32_t gx8002_image_a_stage1_loader_10000a2c(void);

__attribute__((noinline, used, section(".spl_a.return_leaf")))
void gx8002_image_a_stage1_return_leaf_10000134(void)
{
    __asm__ volatile ("" ::: "memory");
}

__attribute__((used, section(".spl_a.boot_setup")))
void gx8002_image_a_stage1_boot_setup_10000acc(void)
{
    gx8002_image_a_stage1_boot_mode_10000a04();
    gx8002_image_a_stage1_clock_setup_10000f14();
    gx8002_image_a_stage1_clock_init_1000092c();
    gx8002_image_a_stage1_return_leaf_10000134();
    gx8002_image_a_stage1_timer_start_10000f04(1u, 0u);
    /* Keep the stock literal-pool load of the boot-info word. */
    volatile uint32_t *boot_device;
    __asm__ volatile ("lrw %0, 0x20001280" : "=r"(boot_device));
    if (*boot_device == 2u)
        (void)gx8002_image_a_stage1_loader_10000a2c();
}
