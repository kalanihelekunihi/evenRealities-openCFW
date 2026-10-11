/* TLSF mark-free/link-next composition, stock 0x4cfe96. */
#include <stdint.h>
extern void *g2_tlsf_block_next(void *block); /* 0x4cfe44 */
void g2_tlsf_block_mark_free(void *block) {
    uint8_t *next=(uint8_t *)g2_tlsf_block_next(block);
    *(void **)(void *)next=block;
    uint32_t prev_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    *(uint32_t *)(void *)(next+4u)|=prev_flag;
    uint32_t free_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b4u;
    *(uint32_t *)((uint8_t *)block+4u)|=free_flag;
}
