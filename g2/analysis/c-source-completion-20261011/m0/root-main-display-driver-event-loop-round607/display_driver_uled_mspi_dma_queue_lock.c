/* Apollo DMA queue snapshot lock 0x538d18. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_irq_save_473940(void);

uint32_t display_driver_uled_mspi_dma_queue_lock_538d18(uint32_t *q) {
    uint32_t prior_mask = display_driver_uled_irq_save_473940();
    const uint32_t *meta = (const uint32_t *)(uintptr_t)q[9];
    uint32_t producer = *(const volatile uint32_t *)(uintptr_t)meta[2];
    uint32_t cursor = (producer & 0xffu) | (q[8] & 0xffffff00u);
    q[7] = cursor;
    if ((int32_t)(q[8] - cursor) < 0) q[7] = cursor - 0x100u;
    q[3] = *(const volatile uint32_t *)(uintptr_t)meta[1];
    __asm__ volatile("msr primask, %0" :: "r"(prior_mask) : "memory");
    return prior_mask;
}
