/* TLSF physical next-block calculation, stock 0x4cfe44. */
#include <stdint.h>
extern uint32_t g2_tlsf_block_size(void *block);
extern void *g2_tlsf_block_to_ptr(void *block);
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
void *g2_tlsf_block_next(void *block) {
    uint32_t size=g2_tlsf_block_size(block);
    void *pointer=g2_tlsf_block_to_ptr(block);
    uint32_t overhead=*(volatile const uint32_t *)(uintptr_t)0x78f4bcu;
    void *next=(void *)((uintptr_t)pointer+size-overhead);
    if(g2_tlsf_block_size(block)==0u)
        g2_file_close_error((const char *)(uintptr_t)0x77cd0cu,
                            (const char *)(uintptr_t)0x71a23cu,442u);
    return next;
}
