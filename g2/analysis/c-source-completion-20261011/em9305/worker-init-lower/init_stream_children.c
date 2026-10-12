#include "init_lower_native.h"

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

/* Native 0x307980..0x3079c2. The product pointer table is the same
 * 0x3357a8 three-record table already identified by selected stream code.
 * A zero entry is explicitly skipped, including its 704-byte clear. */
uint32_t opencfw_em9305_init_child_307980(void)
{
    uint32_t result = 0x802a54u;
    init_write32(0x802a5cu, 0u);
    init_write32(0x802a58u, 0u);
    init_write32(0x802a54u, 0u);
    *(volatile uint8_t *)0x805a7cu = 1u;
    *(volatile uint8_t *)0x802a5eu = 1u;
    for (uint32_t index = 0; index < 3u; ++index) {
        uintptr_t context = (uintptr_t)init_read32(0x3357a8u + 4u * index);
        if (context != 0u) {
            result = (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)context, 0u, 704u);
            *(volatile uint8_t *)(context + 16u) = (uint8_t)index;
        }
    }
    return result;
}

/* Native 0x307a68..0x307af6. Unlike 307980, the three pointers in the
 * 0x3357b4 table are dereferenced unconditionally by the stock loop. */
uint32_t opencfw_em9305_init_child_307a68(void)
{
    (void)opencfw_em9305_memset((void *)0x803560u, 0u, 124u);
    for (uint32_t index = 0; index < 3u; ++index) {
        uintptr_t context = (uintptr_t)init_read32(0x3357b4u + 4u * index);
        (void)opencfw_em9305_memset((void *)context, 0u, 704u);
        uint32_t slot = init_read32(0x803b5cu + 4u * index);
        *(volatile uint8_t *)(context + 16u) = (uint8_t)index;
        init_write32(context + 148u, slot);
    }
    init_write32(0x8035e4u, 0x00100010u);
    init_write32(0x8035e8u, 0u);
    uint8_t task = init_read8(0x805b18u);
    *(volatile uint8_t *)0x803560u = 1u;
    *(volatile uint8_t *)0x805a7cu = 1u;
    init_write16(0x8035c2u, 1287u);
    init_write16(0x8035d2u, 1543u);
    *(volatile uint8_t *)0x8019f8u = 0u;
    *(volatile uint8_t *)0x8035c8u = task;
    *(volatile uint8_t *)0x8035d8u = task;
    return task;
}
