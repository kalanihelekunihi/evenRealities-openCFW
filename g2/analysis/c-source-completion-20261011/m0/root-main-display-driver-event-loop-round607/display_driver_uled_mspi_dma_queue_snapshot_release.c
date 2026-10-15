/* Apollo DMA queue snapshot 0x53901a and release 0x5390fc. Candidate. */
#include <stdint.h>

#define DMA_QUEUE_MAGIC 0x01cdcdcdu
extern uint32_t display_driver_uled_mspi_dma_queue_lock_538d18(uint32_t *);

uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t queue_address,
                                                            uint32_t *out) {
    uint32_t *q = (uint32_t *)(uintptr_t)queue_address;
    if (q == 0 || (q[0] & 0x01ffffffu) != DMA_QUEUE_MAGIC) return 2u;
    if (out == 0) return 6u;
    (void)display_driver_uled_mspi_dma_queue_lock_538d18(q);
    out[0] = q[7];
    out[2] = q[8];
    out[1] = q[8] - (uint32_t)(q[5] != q[4]);
    const uint32_t *meta = (const uint32_t *)(uintptr_t)q[9];
    uint32_t status = *(const volatile uint32_t *)(uintptr_t)meta[6];
    ((uint8_t *)out)[12] = (uint8_t)((status & meta[7]) != 0u);
    ((uint8_t *)out)[13] = (uint8_t)((status & meta[9]) != 0u);
    ((uint8_t *)out)[14] = (uint8_t)((status & meta[8]) != 0u);
    return 0u;
}

uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t queue_address) {
    uint32_t *q = (uint32_t *)(uintptr_t)queue_address;
    if (q == 0 || (q[0] & 0x01ffffffu) != DMA_QUEUE_MAGIC) return 2u;
    if ((q[0] & 0x02000000u) == 0u) return 0u;
    uint32_t *meta = (uint32_t *)(uintptr_t)q[9];
    uint32_t *reg_address_cell = (uint32_t *)(uintptr_t)meta[0];
    *reg_address_cell &= ~1u;
    uint32_t *cursor_cell = (uint32_t *)(uintptr_t)meta[1];
    uint32_t *cursor = (uint32_t *)(uintptr_t)*cursor_cell;
    while ((cursor[0] & ~1u) != meta[2]) {
        if (cursor[0] == meta[1])
            cursor = (uint32_t *)(uintptr_t)cursor[1];
        else
            cursor += 2;
    }
    cursor[0] = meta[2];
    *cursor_cell = (uint32_t)(uintptr_t)cursor;
    q[0] &= ~0x02000000u;
    return 0u;
}
