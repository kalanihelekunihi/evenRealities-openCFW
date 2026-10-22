/* Native QActive_get_ and QMPool_put from authenticated record0x302400.
 * Product layouts are recovered offsets, not inferred upstream ABI padding.
 */
#include <stdint.h>
extern void opencfw_em9305_assert(uint32_t module,uint32_t line);
static uint32_t irq_save(void) { uint32_t state; __asm__ volatile("clri %0\n\tsync" : "=r"(state) :: "memory"); return state; }
static void irq_restore(uint32_t state) { __asm__ volatile("seti %0" :: "r"(state) : "memory"); }
/* Stock 0x00310D38 (QActive_get_) */
void *opencfw_em9305_active_get(void *active)
{
    volatile uint8_t *const bytes = active;
    volatile uint32_t *const words = active;
    const uint32_t irq = irq_save();
    if (words[3] == 0) opencfw_em9305_assert(UINT32_C(0x334538),110);
    const uint32_t event = words[3];
    const uint8_t free_slots = (uint8_t)(bytes[23] + 1u);
    bytes[23] = free_slots;
    const uint8_t end = bytes[20];
    if (end >= free_slots) {
        volatile uint32_t *const ring = (volatile uint32_t *)(uintptr_t)words[4];
        const uint8_t index = bytes[22];
        words[3] = ring[index];
        if (bytes[22] == 0) bytes[22] = end;
        const uint8_t tail = bytes[22];
        bytes[22] = (uint8_t)(tail - 1u);
    } else {
        words[3] = 0;
        if ((uint32_t)end + 1u != free_slots) {
            irq_restore(irq);
            opencfw_em9305_assert(UINT32_C(0x334538),310);
        }
    }
    irq_restore(irq);
    return (void *)(uintptr_t)event;
}
void opencfw_em9305_pool_put(void *pool,void *event)
{
    volatile uint32_t *const words = pool;
    volatile uint16_t *const halves = pool;
    const uint16_t total = halves[7];
    const uint16_t free_blocks = halves[8];
    const uint32_t block = (uint32_t)(uintptr_t)event;
    if (free_blocks >= total || block < words[1] || block > words[2])
        opencfw_em9305_assert(UINT32_C(0x334540),200);
    const uint32_t irq = irq_save();
    const uint32_t head = words[0];
    *(volatile uint32_t *)event = head;
    words[0] = block;
    const uint16_t old_free = halves[8];
    halves[8] = (uint16_t)(old_free + 1u);
    irq_restore(irq);
}
