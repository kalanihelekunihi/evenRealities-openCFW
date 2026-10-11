/* TLSF previous/next coalescing, stock 0x4d02d6/0x4d033a. */
#include <stdint.h>
extern int32_t g2_tlsf_block_is_prev_free(void *block); /* 0x4cfddc */
extern void *g2_tlsf_block_prev(void *block);            /* 0x4cfe1e */
extern int32_t g2_tlsf_block_is_free(void *block);
extern void *g2_tlsf_block_next(void *block);
extern int32_t g2_tlsf_block_is_last(void *block);      /* 0x4cfda0 */
extern void g2_tlsf_block_remove(void *pool,void *block); /* 0x4d0178 */
extern void *g2_tlsf_block_absorb(void *left,void *right); /* 0x4d0294 */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
static const char *const tlsf_file=(const char *)(uintptr_t)0x71a23cu;
void *g2_tlsf_block_merge_prev(void *pool,void *block) {
    if(g2_tlsf_block_is_prev_free(block)!=0) {
        void *prev=g2_tlsf_block_prev(block);
        if(!prev) g2_file_close_error((const char *)(uintptr_t)0x74574cu,
                                      tlsf_file,685u);
        if(g2_tlsf_block_is_free(prev)==0)
            g2_file_close_error((const char *)(uintptr_t)0x6fe4bcu,
                                tlsf_file,686u);
        g2_tlsf_block_remove(pool,prev);
        block=g2_tlsf_block_absorb(prev,block);
    }
    return block;
}
void *g2_tlsf_block_merge_next(void *pool,void *block) {
    void *next=g2_tlsf_block_next(block);
    if(!next) g2_file_close_error((const char *)(uintptr_t)0x745778u,
                                  tlsf_file,698u);
    if(g2_tlsf_block_is_free(next)!=0) {
        if(g2_tlsf_block_is_last(block)!=0)
            g2_file_close_error((const char *)(uintptr_t)0x724b58u,
                                tlsf_file,702u);
        g2_tlsf_block_remove(pool,next);
        block=g2_tlsf_block_absorb(block,next);
    }
    return block;
}
