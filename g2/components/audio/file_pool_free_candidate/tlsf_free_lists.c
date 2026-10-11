/* Pinned TLSF free-list operations, stock 0x4d003a/0x4d00d0. */
#include <stdint.h>
extern void g2_file_close_error(const char *,const char *,uint32_t);
extern void *g2_tlsf_block_to_ptr(void *block); /* stock 0x4cfe10 */
extern void *g2_tlsf_align_ptr(void *ptr,uint32_t align); /* stock 0x4cff18 */

static uint32_t *word_at(void *p,uint32_t offset) {
    return (uint32_t *)((uint8_t *)p+offset);
}
static uint32_t *head_at(void *pool,uint32_t fl,uint32_t sl) {
    return word_at(pool,0x74u+fl*128u+sl*4u);
}
void g2_tlsf_remove_free_block(void *pool,void *block,uint32_t fl,uint32_t sl) {
    uint32_t prev=*word_at(block,12),next=*word_at(block,8);
    if(!prev) g2_file_close_error((const char *)(uintptr_t)0x7456f4u,
                                  (const char *)(uintptr_t)0x71a23cu,581u);
    if(!next) g2_file_close_error((const char *)(uintptr_t)0x745720u,
                                  (const char *)(uintptr_t)0x71a23cu,582u);
    *word_at((void *)(uintptr_t)next,12)=prev;
    *word_at((void *)(uintptr_t)prev,8)=next;
    uint32_t *head=head_at(pool,fl,sl);
    if(*head==(uint32_t)(uintptr_t)block) {
        *head=next;
        if(next==(uint32_t)(uintptr_t)pool) {
            uint32_t *sl_map=word_at(pool,20u+fl*4u);
            *sl_map &= ~(1u << (sl&31u));
            if(!*sl_map) *word_at(pool,16u) &= ~(1u << (fl&31u));
        }
    }
}
void g2_tlsf_insert_free_block(void *pool,void *block,uint32_t fl,uint32_t sl) {
    uint32_t *head=head_at(pool,fl,sl);
    uint32_t current=*head;
    if(!current) g2_file_close_error((const char *)(uintptr_t)0x73a034u,
                                     (const char *)(uintptr_t)0x71a23cu,609u);
    if(!block) g2_file_close_error((const char *)(uintptr_t)0x71a2b4u,
                                   (const char *)(uintptr_t)0x71a23cu,610u);
    *word_at(block,8)=current;
    *word_at(block,12)=(uint32_t)(uintptr_t)pool;
    *word_at((void *)(uintptr_t)current,12)=(uint32_t)(uintptr_t)block;
    void *ptr=g2_tlsf_block_to_ptr(block);
    if(ptr!=g2_tlsf_align_ptr(g2_tlsf_block_to_ptr(block),4u))
        g2_file_close_error((const char *)(uintptr_t)0x6dbbf0u,
                            (const char *)(uintptr_t)0x71a23cu,616u);
    *head=(uint32_t)(uintptr_t)block;
    *word_at(pool,16u) |= 1u << (fl&31u);
    *word_at(pool,20u+fl*4u) |= 1u << (sl&31u);
}
