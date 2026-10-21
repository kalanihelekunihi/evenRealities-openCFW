/* TLSF coalescing leaves, stock 0x4cfddc/0x4cfda0/0x4cfe1e. */
#include <stdint.h>
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
int32_t g2_tlsf_block_is_prev_free(void *block) {
    uint32_t mask=*(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    return (int32_t)(*(uint32_t *)((uint8_t *)block+4u)&mask);
}
int32_t g2_tlsf_block_is_last(void *block) {
    uint32_t value=*(uint32_t *)((uint8_t *)block+4u);
    uint32_t free_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b4u;
    uint32_t prev_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    return (value&~(free_flag|prev_flag))==0u;
}
void *g2_tlsf_block_prev(void *block) {
    if(g2_tlsf_block_is_prev_free(block)==0)
        g2_file_close_error((const char *)(uintptr_t)0x71a200u,
                            (const char *)(uintptr_t)0x71a23cu,433u);
    return *(void **)block;
}
