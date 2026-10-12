/* Native image-B cache control leaves at 0x10004fac, 0x10004db4,
 * and 0x10004d94. The C-SKY sync instructions and unbounded hardware
 * completion poll are native behavior, not substitute success paths.
 */
#include <stdint.h>

static volatile uint32_t *const cache =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);

void gx8002_image_b_cache_stage_10004fac(void)
{
    volatile uint32_t *const controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xb0000000);
    controller[0] = 0u;
    controller[0] = controller[0] | 1u;
    while ((controller[1] & 3u) != 2u) {
    }
}

void gx8002_image_b_cache_stage_10004db4(void)
{
    __asm__ volatile("sync\nsync" ::: "memory");
    cache[0] = cache[0] & ~1u;
    cache[1] = 1u;
    __asm__ volatile("sync\nsync" ::: "memory");
}

void gx8002_image_b_cache_stage_10004d94(void)
{
    __asm__ volatile("sync\nsync" ::: "memory");
    cache[1] = 1u;
    cache[0] = 21u;
    __asm__ volatile("sync\nsync" ::: "memory");
}
