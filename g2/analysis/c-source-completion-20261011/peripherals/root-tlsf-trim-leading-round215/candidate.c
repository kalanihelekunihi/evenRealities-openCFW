#include <stdint.h>
extern uint32_t g2_tlsf_block_can_split(void *,uint32_t);
extern void *g2_tlsf_block_split(void *,uint32_t);
extern void g2_tlsf_block_set_prev_free(void *);
extern void *g2_tlsf_block_link_next(void *);
extern void g2_tlsf_block_insert(void *,void *);
/* Native4d0444..4d0484: leading free-block split and original-block reinsertion. */
void *g2_tlsf_trim_free_leading_4d0444(void *pool,void *block,uint32_t size) {
    void *result=block;
    if(g2_tlsf_block_can_split(block,size)!=0u) {
        uint32_t overhead=*(const volatile uint32_t *)(uintptr_t)0x78f4bcu;
        result=g2_tlsf_block_split(block,size-overhead);
        g2_tlsf_block_set_prev_free(result);
        (void)g2_tlsf_block_link_next(block);
        g2_tlsf_block_insert(pool,block);
    }
    return result;
}
