/* SPDX-License-Identifier: MIT
 * Image-B data-cache enable/disable 0x10004d94/0x10004db4.
 * Native C-SKY sync instructions bracket the MMIO transitions.
 */
#include <stdint.h>

static void native_double_sync(void)
{
    __asm__ volatile ("sync\n\tsync\n" ::: "memory");
}

/* Stock 0x10004D94 (gx_dcache_enable) */
void gx8002_image_b_dcache_enable_10004d94(void)
{
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    native_double_sync();
    control[1] = 1u;
    control[0] = 21u;
    native_double_sync();
}

/* Stock 0x10004DB4 (gx_dcache_disable) */
void gx8002_image_b_dcache_disable_10004db4(void)
{
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    native_double_sync();
    uint32_t mode = control[0];
    control[0] = mode & ~UINT32_C(1);
    control[1] = 1u;
    native_double_sync();
}
