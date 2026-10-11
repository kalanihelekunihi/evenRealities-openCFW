/* TLSF physical block absorption, stock 0x4d0294. */
#include <stdint.h>
extern int32_t g2_tlsf_block_is_last(void *block);
extern uint32_t g2_tlsf_block_size(void *block); /* 0x4cfd70 */
extern void *g2_tlsf_block_link_next(void *block); /* 0x4cfe88 */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
void *g2_tlsf_block_absorb(void *left,void *right) {
    if(g2_tlsf_block_is_last(left)!=0)
        g2_file_close_error((const char *)(uintptr_t)0x724b20u,
                            (const char *)(uintptr_t)0x71a23cu,672u);
    uint32_t size=g2_tlsf_block_size(right);
    uint32_t overhead=*(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    *(uint32_t *)((uint8_t *)left+4u)+=size+overhead;
    (void)g2_tlsf_block_link_next(left);
    return left;
}
