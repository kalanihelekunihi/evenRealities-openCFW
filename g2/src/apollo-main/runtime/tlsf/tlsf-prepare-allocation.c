#include <stdint.h>

extern int32_t g2_tlsf_block_is_free(void *block);       /* 0x4cfdb4 */
extern uint32_t g2_tlsf_block_can_split(void *block,
                                        uint32_t size);  /* 0x4d01bc */
extern void *g2_tlsf_block_split(void *block,
                                 uint32_t size);          /* 0x4d01d4 */
extern void *g2_tlsf_block_link_next(void *block);        /* 0x4cfe88 */
extern void g2_tlsf_block_insert(void *pool, void *block);/* 0x4d019a */
extern void *g2_tlsf_block_next(void *block);             /* 0x4cfe44 */
extern void *g2_tlsf_block_to_ptr(void *block);           /* 0x4cfe10 */
extern void g2_file_close_error(const char *message,
                                const char *file, uint32_t line);

/* Native 0x4cfde8: set the previous-free flag in a block header. */
__attribute__((noinline))
void g2_tlsf_block_set_prev_free(void *block) {
    uint32_t const flag = *(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    *(uint32_t *)((uint8_t *)block + 4u) |= flag;
}

/* Native 0x4cfeac..0x4cfec1. */
__attribute__((noinline))
void g2_tlsf_block_mark_used(void *block) {
    void *const next = g2_tlsf_block_next(block);
    uint32_t const prev_flag = *(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    *(uint32_t *)((uint8_t *)next + 4u) &= ~prev_flag;
    uint32_t const free_flag = *(volatile const uint32_t *)(uintptr_t)0x78f4b4u;
    *(uint32_t *)((uint8_t *)block + 4u) &= ~free_flag;
}

/* Native 0x4d039e..0x4d03ef. */
__attribute__((noinline))
void g2_tlsf_block_trim_free(void *pool, void *block, uint32_t size) {
    if (g2_tlsf_block_is_free(block) == 0)
        g2_file_close_error((const char *)(uintptr_t)0x73a064u,
                            (const char *)(uintptr_t)0x71a23cu, 713u);
    if (g2_tlsf_block_can_split(block, size) != 0u) {
        void *const remainder = g2_tlsf_block_split(block, size);
        (void)g2_tlsf_block_link_next(block);
        g2_tlsf_block_set_prev_free(remainder);
        g2_tlsf_block_insert(pool, remainder);
    }
}

/* Native 0x4d04e6..0x4d0523. */
void *g2_tlsf_prepare_allocation(void *pool, void *block, uint32_t size) {
    if (block == 0)
        return 0;
    if (size == 0u)
        g2_file_close_error((const char *)(uintptr_t)0x766d50u,
                            (const char *)(uintptr_t)0x71a23cu, 789u);
    g2_tlsf_block_trim_free(pool, block, size);
    g2_tlsf_block_mark_used(block);
    return g2_tlsf_block_to_ptr(block);
}
