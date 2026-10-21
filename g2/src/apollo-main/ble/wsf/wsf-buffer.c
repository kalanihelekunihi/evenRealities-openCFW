#include <stdint.h>

/* Locked literals: 0x530514 -> table pointer cell, 0x530518 -> pool count. */
#define POOL_TABLE (*(volatile uint32_t *)(uintptr_t)0x20074eecu)
#define POOL_COUNT (*(volatile uint8_t *)(uintptr_t)0x20075044u)
#define FREE_MARKER 0xfaabd00du

typedef struct {
    uint16_t size;
    uint8_t count;
    uint8_t reserved;
    uint32_t start;
    uint32_t free_head;
} g2_wsf_pool;

extern void g2_wsf_candidate_cs_enter(void);
extern void g2_wsf_candidate_cs_exit(void);

/* Stock 0x5304d4..0x530512: lower-bound pool selection only. */
void g2_smp_candidate_buffer_free(void *context, uint32_t block_word)
{
    (void)context;
    uint32_t table_word = POOL_TABLE;
    uint32_t count = POOL_COUNT;
    while (count != 0u) {
        --count;
        volatile g2_wsf_pool *pool =
            (volatile g2_wsf_pool *)(uintptr_t)(table_word + 12u * count);
        if (block_word >= pool->start) {
            g2_wsf_candidate_cs_enter();
            *(volatile uint32_t *)(uintptr_t)(block_word + 4u) = FREE_MARKER;
            *(volatile uint32_t *)(uintptr_t)block_word = pool->free_head;
            pool->free_head = block_word;
            g2_wsf_candidate_cs_exit();
            return;
        }
    }
}

/* Direct one-word adapter for the WsfMsgFree provider table. */
void g2_wsf_candidate_buffer_free_word(uint32_t block_word)
{
    g2_smp_candidate_buffer_free((void *)0, block_word);
}
