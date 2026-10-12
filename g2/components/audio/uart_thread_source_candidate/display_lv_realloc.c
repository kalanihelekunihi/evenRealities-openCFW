/* Native LVGL realloc 0x44f76a and pool layer 0x48432a/0x484234.
 * Product mutex/pool cells remain authenticated live RAM contracts. */
#include <stdint.h>
extern uint8_t audio_uart_lv_heap_pool[];
extern uint8_t audio_uart_lv_static_slot[];
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *g2_tlsf_reallocate_4d0868(void *,void *,uint32_t);
extern uint32_t g2_tlsf_block_size(void *); /* selected 0x4cfd70 */
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void *audio_uart_lv_malloc(uint32_t); /* selected 0x44f718 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\stdlib\\lv_mem.c";
static uint32_t allocation_size(void *ptr) {
    return ptr==0 ? 0u : g2_tlsf_block_size((uint8_t *)ptr-8u);
}
void *audio_uart_lv_pool_realloc_484234(void *pool_cell,void *ptr,uint32_t size) {
    uint32_t *pool=(uint32_t *)pool_cell;
    void *mutex=(void *)(uintptr_t)pool[0];
    if(xQueueSemaphoreTake(mutex,UINT32_MAX)!=1)return 0;
    uint32_t before=allocation_size(ptr);
    void *result=g2_tlsf_reallocate_4d0868((void *)(uintptr_t)pool[1],ptr,size);
    if(result!=0) {
        uint32_t after=allocation_size(result);
        pool[2]=pool[2]-before+after;
        if(pool[3]<pool[2])pool[3]=pool[2];
    }
    (void)audio_uart_queue_send(mutex,0,0u,0u);
    return result;
}
__attribute__((noinline)) void *audio_uart_lv_pool_realloc_48432a(void *ptr,uint32_t size) {
    return audio_uart_lv_pool_realloc_484234(audio_uart_lv_heap_pool,ptr,size);
}
void *audio_uart_lv_realloc_44f76a(void *ptr,uint32_t size) {
    if(size==0u) {
        audio_uart_lv_heap_free(ptr);
        return audio_uart_lv_static_slot;
    }
    if(ptr==audio_uart_lv_static_slot)return audio_uart_lv_malloc(size);
    void *result=audio_uart_lv_pool_realloc_48432a(ptr,size);
    if(result==0)
        audio_uart_lvgl_log(3u,path,0xa2u,"lv_realloc","couldn't reallocate memory");
    return result;
}
