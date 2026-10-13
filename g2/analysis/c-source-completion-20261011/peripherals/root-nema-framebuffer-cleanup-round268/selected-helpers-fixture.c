#include <stdint.h>
extern void audio_uart_lv_pool_free_48429e(void *,void *);
void *audio_uart_nema_pool_select_514050(uint32_t pool_id) {
    if(pool_id==2u)return (void *)(uintptr_t)0x20000370u;
    if(pool_id==3u)return (void *)(uintptr_t)0x20000338u;
    return (void *)(uintptr_t)0x20000354u;
}
void audio_uart_nema_cl_buffer_destroy_5140c6(void *buffer) {
    volatile uint32_t *b=buffer;
    void *pool=audio_uart_nema_pool_select_514050(b[1]);
    void *data=(void *)(uintptr_t)b[2];
    audio_uart_lv_pool_free_48429e(pool,data);
    b[2]=0u;b[3]=0u;b[0]=0u;b[1]=UINT32_MAX;
}