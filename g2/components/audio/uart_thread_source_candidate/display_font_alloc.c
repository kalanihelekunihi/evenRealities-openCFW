/* Native LVGL malloc/calloc wrappers 0x44f718/0x44f730 and pool 0x484180. */
#include <stdint.h>
extern uint8_t audio_uart_lv_heap_pool[]; /* RAM0x20000338 */
extern uint8_t audio_uart_lv_static_slot[]; /* RAM0x2006f5ac */
extern int32_t xQueueSemaphoreTake(void *,uint32_t); /* selected 0x441c44 */
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t); /* selected 0x4417ee */
extern void *g2_file_pool_allocate(void *,uint32_t); /* selected 0x4d0722 */
extern uint32_t g2_tlsf_block_size(void *); /* selected 0x4cfd70 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
static void *font_pool_allocate(uint32_t bytes) {
    if(bytes==0u) return 0;
    uint32_t *pool=(uint32_t *)(void *)audio_uart_lv_heap_pool;
    void *mutex=(void *)(uintptr_t)pool[0];
    if(xQueueSemaphoreTake(mutex,UINT32_MAX)!=1) return 0;
    void *result=g2_file_pool_allocate((void *)(uintptr_t)pool[1],bytes);
    if(result!=0) {
        uint32_t amount=g2_tlsf_block_size((uint8_t *)result-8u);
        pool[2]+=amount;
        if(pool[3]<pool[2]) pool[3]=pool[2];
    }
    (void)audio_uart_queue_send(mutex,0,0u,0u);
    return result;
}
void *audio_uart_lv_malloc(uint32_t bytes) {
    if(bytes==0u) return audio_uart_lv_static_slot;
    return font_pool_allocate(bytes);
}
void *audio_uart_lv_heap_alloc(uint32_t bytes) {
    if(bytes==0u) return audio_uart_lv_static_slot;
    void *result=font_pool_allocate(bytes);
    if(result!=0) audio_uart_buffer_zero(result,bytes,0u);
    return result;
}
