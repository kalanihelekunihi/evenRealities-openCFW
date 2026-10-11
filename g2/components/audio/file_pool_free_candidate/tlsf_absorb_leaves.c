/* TLSF block size and physical link, stock 0x4cfd70/0x4cfe88. */
#include <stdint.h>
extern void *g2_tlsf_block_next(void *block);
uint32_t g2_tlsf_block_size(void *block) {
    uint32_t flags=*(volatile const uint32_t *)(uintptr_t)0x78f4b4u|
                   *(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    return *(uint32_t *)((uint8_t *)block+4u)&~flags;
}
void *g2_tlsf_block_link_next(void *block) {
    void *next=g2_tlsf_block_next(block);
    *(void **)next=block;
    return next;
}
