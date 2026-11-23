#include "init_lower_native.h"
#include "em9305_ram.h"

extern uint8_t *const opencfw_em9305_ext_init_records_3357a8[3];
extern uint8_t *const opencfw_em9305_stream_objects_3357b4[3];

extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);

/* Native 0x307980..0x3079c2. The product pointer table is the same
 * 0x3357a8 three-record table already identified by selected stream code.
 * A zero entry is explicitly skipped, including its 704-byte clear. */
uint32_t opencfw_em9305_init_child_307980(void)
{
    uint32_t result = ((uintptr_t)&em9305_ram_802a2c + 0x28u);
    init_write32(((uintptr_t)&em9305_ram_802a2c + 0x30u), 0u);
    init_write32(((uintptr_t)&em9305_ram_802a2c + 0x2cu), 0u);
    init_write32(((uintptr_t)&em9305_ram_802a2c + 0x28u), 0u);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x10u) = 1u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_802a2c + 0x32u) = 1u;
    for (uint32_t index = 0; index < 3u; ++index) {
        uintptr_t context = (uintptr_t)opencfw_em9305_ext_init_records_3357a8[index];
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
    (void)opencfw_em9305_memset((void *)(uintptr_t)&em9305_ram_803560, 0u, 124u);
    for (uint32_t index = 0; index < 3u; ++index) {
        uintptr_t context = (uintptr_t)opencfw_em9305_stream_objects_3357b4[index];
        (void)opencfw_em9305_memset((void *)context, 0u, 704u);
        uint32_t slot = init_read32((uintptr_t)&em9305_ram_803b5c + 4u * index);
        *(volatile uint8_t *)(context + 16u) = (uint8_t)index;
        init_write32(context + 148u, slot);
    }
    init_write32(0x8035e4u, 0x00100010u);
    init_write32(0x8035e8u, 0u);
    uint8_t task = init_read8(((uintptr_t)&em9305_ram_805af0 + 0x28u));
    *(volatile uint8_t *)(uintptr_t)&em9305_ram_803560 = 1u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_805a6c + 0x10u) = 1u;
    init_write16(((uintptr_t)&em9305_ram_8035c0 + 0x2u), 1287u);
    init_write16(((uintptr_t)&em9305_ram_8035c0 + 0x12u), 1543u);
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_8019e8 + 0x10u) = 0u;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_8035c0 + 0x8u) = task;
    *(volatile uint8_t *)((uintptr_t)&em9305_ram_803560 + 0x78u) = task;
    return task;
}
