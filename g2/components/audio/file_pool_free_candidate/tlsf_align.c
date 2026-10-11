/* TLSF block pointer and alignment helpers, stock 0x4cfe10/0x4cff18. */
#include <stdint.h>
extern void g2_file_close_error(const char *,const char *,uint32_t);
void *g2_tlsf_block_to_ptr(void *block) {
    uint32_t offset=*(volatile const uint32_t *)(uintptr_t)0x78f4c0u;
    return (void *)((uintptr_t)block+offset);
}
void *g2_tlsf_align_ptr(void *ptr,uint32_t align) {
    uintptr_t rounded=((uintptr_t)ptr+align-1u)&~((uintptr_t)align-1u);
    if((align&(align-1u))!=0u)
        g2_file_close_error((const char *)(uintptr_t)0x7106e4u,
                            (const char *)(uintptr_t)0x71a23cu,485u);
    return (void *)rounded;
}
