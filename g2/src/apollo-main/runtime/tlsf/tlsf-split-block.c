#include <stdint.h>

extern uint32_t g2_tlsf_block_size(void *block); /* 0x4cfd70 */
extern void *g2_tlsf_block_to_ptr(void *block); /* 0x4cfe10 */
extern void *g2_tlsf_align_ptr(void *ptr, uint32_t alignment); /* 0x4cff18 */
extern void g2_tlsf_block_mark_free(void *block); /* 0x4cfe96 */
extern void g2_file_close_error(const char *message,
                                const char *file, uint32_t line);

/* Native 0x4cfd84: replace size, preserving two flag bits. */
void g2_tlsf_block_set_size(void *block, uint32_t size) {
    uint32_t const flags =
        *(volatile const uint32_t *)(uintptr_t)0x78f4b4u |
        *(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    uint32_t *const word = (uint32_t *)((uint8_t *)block + 4u);
    *word = size | (*word & flags);
}

/* Native 0x4d01bc..0x4d01d3. */
uint32_t g2_tlsf_block_can_split(void *block, uint32_t size) {
    return g2_tlsf_block_size(block) >= size + 16u ? 1u : 0u;
}

/* Native 0x4d01d4..0x4d0293. Pinned TLSF block layout. */
void *g2_tlsf_block_split(void *block, uint32_t size) {
    void *const block_pointer = g2_tlsf_block_to_ptr(block);
    const uint32_t overhead =
        *(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    void *const remaining = (void *)((uintptr_t)block_pointer + size - overhead);
    const uint32_t old_size = g2_tlsf_block_size(block);
    const uint32_t remaining_overhead =
        *(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    const uint32_t remain_size = old_size - size - remaining_overhead;
    void *const remainder_ptr = g2_tlsf_block_to_ptr(remaining);
    if (remainder_ptr != g2_tlsf_align_ptr(
            g2_tlsf_block_to_ptr(remaining), 4u))
        g2_file_close_error((const char *)(uintptr_t)0x6a5034u,
                            (const char *)(uintptr_t)0x71a23cu, 657u);
    const uint32_t asserted_size = g2_tlsf_block_size(block);
    const uint32_t assertion_overhead =
        *(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    if (asserted_size != size + remain_size + assertion_overhead)
        g2_file_close_error((const char *)(uintptr_t)0x710724u,
                            (const char *)(uintptr_t)0x71a23cu, 659u);
    g2_tlsf_block_set_size(remaining, remain_size);
    const uint32_t actual_remaining = g2_tlsf_block_size(remaining);
    const uint32_t minimum =
        *(volatile const uint32_t *)(uintptr_t)0x78f4c4u;
    if (actual_remaining < minimum)
        g2_file_close_error((const char *)(uintptr_t)0x6f6eb0u,
                            (const char *)(uintptr_t)0x71a23cu, 661u);
    g2_tlsf_block_set_size(block, size);
    g2_tlsf_block_mark_free(remaining);
    return remaining;
}
