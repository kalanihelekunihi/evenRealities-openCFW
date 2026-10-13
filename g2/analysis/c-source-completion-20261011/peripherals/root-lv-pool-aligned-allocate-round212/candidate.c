#include <stdint.h>
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *audio_uart_lv_tlsf_aligned_allocate_4d0744(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_allocation_size_4d05e4(void *);
/* Native4841d8..484234: locked allocation and fresh accounting/high-water reads. */
void *audio_uart_lv_pool_aligned_allocate_4841d8(void *cell,uint32_t bytes,uint32_t alignment) {
    volatile uint32_t *pool=cell;
    void *result=0;
    if(bytes==0u)return 0;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)==1) {
        result=audio_uart_lv_tlsf_aligned_allocate_4d0744((void *)(uintptr_t)pool[1],alignment,bytes);
        if(result) {
            uint32_t size=audio_uart_lv_allocation_size_4d05e4(result);
            pool[2]=size+pool[2];
            uint32_t high=pool[3];
            uint32_t current=pool[2];
            if(high<current)high=pool[2];else high=pool[3];
            pool[3]=high;
        }
        (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0u,0u);
    }
    return result;
}
