/* Pinned TLSF/native realloc 0x4d0868 and used-block trim 0x4d03f0. */
#include <stdint.h>
#include <stddef.h>

extern void *g2_file_pool_allocate(void *,uint32_t); /* 0x4d0722 */
extern void g2_file_pool_free(void *,void *); /* 0x4d0808 */
extern void *g2_tlsf_block_from_ptr(void *); /* 0x4cfe04 */
extern void *g2_tlsf_block_next(void *); /* 0x4cfe44 */
extern uint32_t g2_tlsf_block_size(void *); /* 0x4cfd70 */
extern int32_t g2_tlsf_block_is_free(void *); /* 0x4cfdb4 */
extern uint32_t g2_tlsf_adjust_request(uint32_t,uint32_t); /* 0x4cff42 */
extern void *g2_tlsf_block_merge_next(void *,void *); /* 0x4d033a */
extern void g2_tlsf_block_mark_used(void *); /* 0x4cfeac */
extern uint32_t g2_tlsf_block_can_split(void *,uint32_t); /* 0x4d01bc */
extern void *g2_tlsf_block_split(void *,uint32_t); /* 0x4d01d4 */
extern void g2_tlsf_block_insert(void *,void *); /* 0x4d019a */
extern void g2_file_close_error(const char *,const char *,uint32_t); /* 0x4d09b4 */
extern void *memcpy(void *,const void *,size_t);

static const char tlsf_file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf.c";
static const char realloc_free_error[]="!block_is_free(block) && \"block already marked as free\"";
static const char trim_used_error[]="!block_is_free(block) && \"block must be used\"";

void g2_tlsf_block_clear_prev_free(void *block) /* native 0x4cfdf6 */
{
    *(uint32_t *)((uint8_t *)block+4u)&=~2u;
}

void g2_tlsf_block_trim_used(void *pool,void *block,uint32_t size) /* 0x4d03f0 */
{
    if (g2_tlsf_block_is_free(block)!=0)
        g2_file_close_error(trim_used_error,tlsf_file,0x2d6u);
    if (g2_tlsf_block_can_split(block,size)!=0u) {
        void *remainder=g2_tlsf_block_split(block,size);
        g2_tlsf_block_clear_prev_free(remainder);
        remainder=g2_tlsf_block_merge_next(pool,remainder);
        g2_tlsf_block_insert(pool,remainder);
    }
}

void *g2_tlsf_reallocate_4d0868(void *pool,void *pointer,uint32_t bytes)
{
    if (pointer==0) return g2_file_pool_allocate(pool,bytes);
    if (bytes==0u) {
        g2_file_pool_free(pool,pointer);
        return 0;
    }
    void *block=g2_tlsf_block_from_ptr(pointer);
    void *next=g2_tlsf_block_next(block);
    uint32_t current_size=g2_tlsf_block_size(block);
    uint32_t next_size=g2_tlsf_block_size(next);
    uint32_t requested=g2_tlsf_adjust_request(bytes,4u);
    if (g2_tlsf_block_is_free(block)!=0)
        g2_file_close_error(realloc_free_error,tlsf_file,0x4d1u);
    if (current_size<requested &&
        (g2_tlsf_block_is_free(next)==0 ||
         4u+next_size+current_size<requested)) {
        void *replacement=g2_file_pool_allocate(pool,bytes);
        if (replacement!=0) {
            uint32_t copied=current_size<bytes?current_size:bytes;
            (void)memcpy(replacement,pointer,copied);
            g2_file_pool_free(pool,pointer);
        }
        return replacement;
    }
    if (current_size<requested) {
        (void)g2_tlsf_block_merge_next(pool,block);
        g2_tlsf_block_mark_used(block);
    }
    g2_tlsf_block_trim_used(pool,block,requested);
    return pointer;
}
