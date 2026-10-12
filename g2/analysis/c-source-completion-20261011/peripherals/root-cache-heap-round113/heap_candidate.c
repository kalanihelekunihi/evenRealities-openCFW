/* Native LV heap wrappers and pool accounting; no executable data retained. */
#include <stdint.h>
extern uint8_t audio_uart_lv_heap_pool[],audio_uart_lv_static_slot[];
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *g2_file_pool_allocate(void *,uint32_t);
extern void g2_file_pool_free(void *,void *);
extern void *g2_tlsf_block_from_ptr(void *);
extern uint32_t g2_tlsf_block_size(void *);
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
uint32_t audio_uart_lv_allocation_size_4d05e4(void *pointer) {
    return pointer==0?0u:g2_tlsf_block_size(g2_tlsf_block_from_ptr(pointer));
}
void *audio_uart_lv_pool_allocate_484180(void *cell,uint32_t bytes) {
    volatile uint32_t *pool=cell;
    if(bytes==0u)return 0;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)!=1)return 0;
    void *result=g2_file_pool_allocate((void *)(uintptr_t)pool[1],bytes);
    if(result!=0) {
        uint32_t amount=audio_uart_lv_allocation_size_4d05e4(result);
        pool[2]=amount+pool[2];
        uint32_t high=pool[3];
        if(high<pool[2])high=pool[2];else high=pool[3];
        pool[3]=high;
    }
    (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0,0);
    return result;
}
void *audio_uart_lv_pool_allocate_48431e(uint32_t bytes) {
    return audio_uart_lv_pool_allocate_484180(audio_uart_lv_heap_pool,bytes);
}
void audio_uart_lv_heap_zero_44f70c(void *pointer,uint32_t bytes) {
    audio_uart_lv_basic_box_clear_454746(pointer,0u,bytes);
}
void *audio_uart_lv_malloc(uint32_t bytes) {
    if(bytes==0u)return audio_uart_lv_static_slot;
    return audio_uart_lv_pool_allocate_48431e(bytes);
}
void *audio_uart_lv_heap_alloc(uint32_t bytes) {
    if(bytes==0u)return audio_uart_lv_static_slot;
    void *result=audio_uart_lv_pool_allocate_48431e(bytes);
    if(result!=0)audio_uart_lv_heap_zero_44f70c(result,bytes);
    return result;
}
void audio_uart_lv_pool_free_48429e(void *cell,void *pointer) {
    volatile uint32_t *pool=cell;
    if(pointer==0)return;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)!=1)return;
    uint32_t amount=audio_uart_lv_allocation_size_4d05e4(pointer);
    g2_file_pool_free((void *)(uintptr_t)pool[1],pointer);
    if(amount<pool[2])pool[2]=pool[2]-amount;else pool[2]=0u;
    (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0,0);
}
void audio_uart_lv_pool_free_484338(void *pointer) {
    audio_uart_lv_pool_free_48429e(audio_uart_lv_heap_pool,pointer);
}
void audio_uart_lv_heap_free(void *pointer) {
    if(pointer==audio_uart_lv_static_slot||pointer==0)return;
    audio_uart_lv_pool_free_484338(pointer);
}
