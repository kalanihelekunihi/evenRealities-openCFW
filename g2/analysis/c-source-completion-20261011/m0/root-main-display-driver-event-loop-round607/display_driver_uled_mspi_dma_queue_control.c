/* Apollo DMA queue start/stop 0x538e3c and 0x538e8c. Candidate. */
#include <stdint.h>

#define DMA_QUEUE_MAGIC 0x01cdcdcdu

uint32_t display_driver_uled_mspi_dma_queue_start_538e3c(uint32_t *queue) {
    if (queue == 0 || (queue[0] & 0x01ffffffu) != DMA_QUEUE_MAGIC) return 2u;
    if ((queue[0] & 0x02000000u) != 0u) return 0u;
    if (queue[2] >= 0x20080000u) __asm__ volatile("dmb sy" ::: "memory");
    volatile uint32_t *reg = *(volatile uint32_t **)(uintptr_t)queue[9];
    *reg |= 1u;
    queue[0] |= 0x02000000u;
    return 0u;
}

uint32_t display_driver_uled_mspi_dma_queue_stop_538e8c(uint32_t *queue) {
    if (queue == 0 || (queue[0] & 0x01ffffffu) != DMA_QUEUE_MAGIC) return 2u;
    if ((queue[0] & 0x02000000u) == 0u) return 0u;
    volatile uint32_t *reg = *(volatile uint32_t **)(uintptr_t)queue[9];
    *reg &= ~1u;
    queue[0] &= ~0x02000000u;
    return 0u;
}
