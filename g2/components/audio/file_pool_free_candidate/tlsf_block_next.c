/* TLSF physical next-block calculation, stock 0x4cfe44. */
#include <stdint.h>
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
void *g2_tlsf_block_next(void *block) {
    uint32_t value=*(uint32_t *)((uint8_t *)block+4u);
    uint32_t free_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b4u;
    uint32_t prev_flag=*(volatile const uint32_t *)(uintptr_t)0x78f4b8u;
    uint32_t size=value&~(free_flag|prev_flag);
    uint32_t offset=*(volatile const uint32_t *)(uintptr_t)0x78f4c0u;
    uint32_t overhead=*(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    void *next=(void *)((uintptr_t)block+offset+size-overhead);
    if(size==0u)
        g2_file_close_error((const char *)(uintptr_t)0x77cd0cu,
                            (const char *)(uintptr_t)0x71a23cu,442u);
    return next;
}
