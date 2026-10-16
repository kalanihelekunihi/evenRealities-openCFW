/* Native QF_gc 0x310fb8..0x311014. Pinned QP/C is comparator only.
 * Preserve repeated byte reads, saved IRQ state, narrowed pool index,
 * assertion continuation and actual pool-return child ABI.
 */
#include <stdint.h>
extern void opencfw_em9305_assert(uint32_t module,uint32_t line);
extern void opencfw_em9305_pool_put(void *pool,void *event); /* 0x311798 */
void opencfw_em9305_event_gc(void *event)
{
    volatile uint8_t *const bytes = event;
    if (bytes[2] == 0) return;
    uint32_t irq;
    __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
    if (bytes[3] >= 2) {
        const uint8_t refs = bytes[3];
        bytes[3] = (uint8_t)(refs - 1u);
        __asm__ volatile("seti %0" :: "r"(irq) : "memory");
        return;
    }
    const uint8_t pool_id = bytes[2];
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
    const uint8_t count = *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801360);
    const uint8_t index = (uint8_t)(pool_id - 1u);
    if (index >= count) opencfw_em9305_assert(UINT32_C(0x334520),410);
    void *const pool = (void *)(uintptr_t)(UINT32_C(0x801368) + (uint32_t)index * 20u);
    opencfw_em9305_pool_put(pool,event);
}
