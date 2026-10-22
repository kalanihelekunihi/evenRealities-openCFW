/* SPDX-License-Identifier: MIT
 * Image-A SRAM native cache command variants 0x10025608 (invalidate) and
 * 0x100256c0 (clean+invalidate), sharing the 128-byte unrolled line walk.
 */
#include <stdint.h>

/* Native 0x100255c4/0x100255e4 place two C-SKY sync operations on
 * each side of the cache-control register sequence. */
static inline void gx8002_cache_sync_pair(void)
{
    __asm__ volatile("sync\n\tsync" ::: "memory");
}

/* Stock 0x100255C4 (gx_dcache_enable) */
void gx8002_resident_dcache_enable_255c4(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    gx8002_cache_sync_pair();
    control[1] = 1u;
    control[0] = 21u;
    gx8002_cache_sync_pair();
}

/* Stock 0x100255E4 (gx_dcache_disable) */
void gx8002_resident_dcache_disable_255e4(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f000);
    gx8002_cache_sync_pair();
    control[0] = control[0] & ~UINT32_C(1);
    control[1] = 1u;
    gx8002_cache_sync_pair();
}

static void gx8002_cache_lines(uintptr_t address, int32_t bytes, uint32_t op)
{
    volatile uint32_t *const command =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004);
    uint32_t line = ((uint32_t)address & ~UINT32_C(15)) | op;
    while (bytes >= 128) {
        command[0] = line;
        command[0] = line + 16u;
        command[0] = line + 32u;
        command[0] = line + 48u;
        command[0] = line + 64u;
        command[0] = line + 80u;
        command[0] = line + 96u;
        command[0] = line + 112u;
        line += 128u;
        bytes -= 128;
    }
    while (bytes > 0) {
        command[0] = line;
        line += 16u;
        bytes -= 16;
    }
}

/* Stock 0x10025608 (gx_dcache_invalid_range) */
void gx8002_resident_cache_invalidate_25608(void *address, int32_t bytes)
{
    gx8002_cache_lines((uintptr_t)address, bytes, 2u);
}

/* Stock 0x100256C0 (gx_dcache_clean_invalid_range) */
void gx8002_resident_cache_clean_invalidate_256c0(
    void *address, int32_t bytes)
{
    gx8002_cache_lines((uintptr_t)address, bytes, 10u);
}

/* Stock 0x1002571C (gx_icache_enable) */
void gx8002_resident_icache_enable_2571c(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xb0000000);
    control[0] = 0u;
    control[0] = control[0] | 1u;
    while ((control[1] & 3u) != 2u) { }
}
