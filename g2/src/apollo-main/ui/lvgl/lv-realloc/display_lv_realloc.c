/* Native LVGL realloc 0x44f76a and pool layer 0x48432a/0x484234.
 * Product mutex/pool cells remain authenticated live RAM contracts. */
#include <stdint.h>
extern uint8_t audio_uart_lv_heap_pool[];
extern uint8_t audio_uart_lv_static_slot[];
extern int32_t xQueueSemaphoreTake(void *,uint32_t);
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t);
extern void *g2_tlsf_reallocate_4d0868(void *,void *,uint32_t);
extern uint32_t audio_uart_lv_allocation_size_4d05e4(void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void *audio_uart_lv_malloc(uint32_t); /* selected 0x44f718 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\stdlib\\lv_mem.c";
void *audio_uart_lv_pool_realloc_484234(void *pool_cell,void *ptr,uint32_t size) {
    volatile uint32_t *pool=(volatile uint32_t *)pool_cell;
    if(xQueueSemaphoreTake((void *)(uintptr_t)pool[0],UINT32_MAX)!=1)return 0;
    uint32_t before=audio_uart_lv_allocation_size_4d05e4(ptr);
    void *result=g2_tlsf_reallocate_4d0868((void *)(uintptr_t)pool[1],ptr,size);
    if(result!=0) {
        pool[2]=pool[2]-before;
        uint32_t after=audio_uart_lv_allocation_size_4d05e4(result);
        pool[2]=after+pool[2];
        uint32_t high=pool[3];
        if(high<pool[2])high=pool[2];else high=pool[3];
        pool[3]=high;
    }
    (void)audio_uart_queue_send((void *)(uintptr_t)pool[0],0,0u,0u);
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
