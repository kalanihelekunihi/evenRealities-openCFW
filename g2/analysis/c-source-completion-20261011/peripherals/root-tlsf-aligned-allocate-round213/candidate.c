#include <stdint.h>
extern uint32_t g2_tlsf_adjust_request(uint32_t,uint32_t);
extern void *g2_tlsf_find_suitable(void *,uint32_t);
extern void *g2_tlsf_block_to_ptr(void *);
extern void *g2_tlsf_align_ptr(void *,uint32_t);
extern void *g2_tlsf_trim_free_leading_4d0444(void *,void *,uint32_t);
extern void *g2_tlsf_prepare_allocation(void *,void *,uint32_t);
extern void g2_file_close_error(const char *,const char *,uint32_t);
/* Native4d0744..4d0802, pinned TLSF alignment policy with native gap16. */
void *audio_uart_lv_tlsf_aligned_allocate_4d0744(void *pool,uint32_t alignment,uint32_t size) {
    uint32_t adjusted=g2_tlsf_adjust_request(size,4u);
    uint32_t requested=g2_tlsf_adjust_request(alignment+adjusted+16u,alignment);
    if(adjusted==0u || alignment<5u)requested=adjusted;
    void *block=g2_tlsf_find_suitable(pool,requested);
    uint32_t minimum=*(const volatile uint32_t *)(uintptr_t)0x78f4c4u;
    uint32_t overhead=*(const volatile uint32_t *)(uintptr_t)0x78f4bcu;
    if(minimum+overhead!=16u)g2_file_close_error("sizeof(block_header_t) == block_size_min + block_header_overhead","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf.c",1149u);
    if(block) {
        void *ptr=g2_tlsf_block_to_ptr(block);
        void *aligned=g2_tlsf_align_ptr(ptr,alignment);
        uint32_t gap=(uint32_t)(uintptr_t)aligned-(uint32_t)(uintptr_t)ptr;
        if(gap!=0u && gap<16u) {
            uint32_t offset=16u-gap;
            if(alignment>=offset)offset=alignment;
            aligned=g2_tlsf_align_ptr((void *)(uintptr_t)((uint32_t)(uintptr_t)aligned+offset),alignment);
            gap=(uint32_t)(uintptr_t)aligned-(uint32_t)(uintptr_t)ptr;
        }
        if(gap) {
            if(gap<16u)g2_file_close_error("gap >= gap_minimum && \"gap size too small\"","D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\tlsf\\tlsf.c",1173u);
            block=g2_tlsf_trim_free_leading_4d0444(pool,block,gap);
        }
    }
    return g2_tlsf_prepare_allocation(pool,block,adjusted);
}
