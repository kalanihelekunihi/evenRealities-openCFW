/* TLSF pool free composition, stock 0x4d0808, pinned tlsf.c. */
#include <stdint.h>
extern void *g2_tlsf_block_from_ptr(void *pointer); /* 0x4cfe04 */
extern int32_t g2_tlsf_block_is_free(void *block);  /* 0x4cfdb4 */
extern void g2_tlsf_block_mark_free(void *block);  /* 0x4cfe96 */
extern void *g2_tlsf_block_merge_prev(void *pool,void *block); /* 0x4d02d6 */
extern void *g2_tlsf_block_merge_next(void *pool,void *block); /* 0x4d033a */
extern void g2_tlsf_block_insert(void *pool,void *block);      /* 0x4d019a */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
void g2_file_pool_free(void *pool,void *pointer) {
    if(!pointer) return;
    void *block=g2_tlsf_block_from_ptr(pointer);
    if(g2_tlsf_block_is_free(block)!=0)
        g2_file_close_error((const char *)(uintptr_t)0x724b90u,
                            (const char *)(uintptr_t)0x71a23cu,1188u);
    g2_tlsf_block_mark_free(block);
    block=g2_tlsf_block_merge_prev(pool,block);
    block=g2_tlsf_block_merge_next(pool,block);
    g2_tlsf_block_insert(pool,block);
}
