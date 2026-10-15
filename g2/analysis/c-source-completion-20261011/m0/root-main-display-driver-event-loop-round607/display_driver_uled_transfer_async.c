/* Apollo S200 MSPI transfer-async wrapper at 0x4c2208. */
#include <stdint.h>

extern uint32_t display_driver_uled_mspi_queue_prepare_4bfcc0(
    uint32_t, const void *, uint32_t, uint32_t, uint32_t);
extern uint32_t display_driver_uled_irq_save_473940(void);
extern uint32_t g2_main_cq_commit_538fb4(uint32_t, uint32_t);
extern void g2_main_cq_rollback_538f82(uint32_t);
extern uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t);

static uint32_t read_word(const uint8_t *base, uint32_t offset) {
    return *(const uint32_t *)(const void *)(base + offset);
}

static void write_word(uint8_t *base, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(base + offset) = value;
}

uint32_t display_driver_uled_transfer_async_4c2208(
    uint32_t handle, const void *transfer, uint32_t priority,
    void *callback, void *context) {
    uint8_t *const h = (uint8_t *)(uintptr_t)handle;
    if (h == 0 || (read_word(h, 0) & 0x01ffffffu) != 0x01bebebeu)
        return 2u;
    if (read_word(h, 24) == 0 || h[0x82c] == 2u)
        return 7u;
    if ((h[10] == 10u || h[10] == 11u) &&
        ((((const uint8_t *)transfer)[8] & 3u) != 0u))
        return 7u;

    uint32_t selected_callback = (uint32_t)(uintptr_t)callback;
    if (selected_callback == 0 && read_word(h, 0x838) == 0 &&
        h[0x82c] == 0 &&
        (read_word(h, 0x858) >> 1) <= read_word(h, 0x85c))
        selected_callback = 0x004c072du;

    uint32_t result = display_driver_uled_mspi_queue_prepare_4bfcc0(
        handle, transfer, priority & 0xffu, selected_callback,
        (uint32_t)(uintptr_t)context);
    if (result != 0) return result;

    const uint32_t saved_primask = display_driver_uled_irq_save_473940();
    const uint32_t queue = read_word(h, 0x828);
    result = g2_main_cq_commit_538fb4(queue, selected_callback != 0);
    if (result != 0) {
        __asm__ volatile("msr primask, %0" :: "r"(saved_primask) : "memory");
        g2_main_cq_rollback_538f82(queue);
        return result;
    }

    const uint32_t prior = read_word(h, 32);
    write_word(h, 32, prior + 1u);
    write_word(h, 0x830, read_word(h, 0x830) + 1u);
    if (callback != 0) {
        h[0x82d] = 0;
        write_word(h, 0x85c, 0);
    } else if (selected_callback != 0) {
        write_word(h, 0x85c, 0);
    } else {
        write_word(h, 0x85c, read_word(h, 0x85c) + 1u);
    }
    __asm__ volatile("msr primask, %0" :: "r"(saved_primask) : "memory");
    if (prior == 0) result = display_driver_uled_mspi_dma_start_4bfd44(handle);
    return result;
}
