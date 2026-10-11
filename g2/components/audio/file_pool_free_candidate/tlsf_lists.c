/* TLSF size-class list wrappers, stock 0x4d0178/0x4d019a. */
#include <stdint.h>
extern uint32_t g2_tlsf_block_size(void *block);
extern void g2_tlsf_mapping_insert(uint32_t size,uint32_t *fl,uint32_t *sl);
extern void g2_tlsf_remove_free_block(void *pool,void *block,
                                       uint32_t fl,uint32_t sl);
extern void g2_tlsf_insert_free_block(void *pool,void *block,
                                       uint32_t fl,uint32_t sl);
void g2_tlsf_block_remove(void *pool,void *block) {
    uint32_t fl,sl;
    g2_tlsf_mapping_insert(g2_tlsf_block_size(block),&fl,&sl);
    g2_tlsf_remove_free_block(pool,block,fl,sl);
}
void g2_tlsf_block_insert(void *pool,void *block) {
    uint32_t fl,sl;
    g2_tlsf_mapping_insert(g2_tlsf_block_size(block),&fl,&sl);
    g2_tlsf_insert_free_block(pool,block,fl,sl);
}
