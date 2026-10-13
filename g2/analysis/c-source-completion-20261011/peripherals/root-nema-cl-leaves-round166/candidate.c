#include <stdint.h>
extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_lv_pool_free_48429e(void *,void *);
/* Native514050..514070, source-owned pool selector literal addresses. */
void *audio_uart_nema_pool_select_514050(uint32_t pool_id) {
    if(pool_id==2u)return (void *)(uintptr_t)0x20000370u;
    if(pool_id==3u)return (void *)(uintptr_t)0x20000338u;
    return (void *)(uintptr_t)0x20000354u;
}
/* Native5140c6..5140ea; poolfree can mutate the owner. */
void audio_uart_nema_cl_buffer_destroy_5140c6(void *buffer) {
    volatile uint32_t *b=buffer;
    void *pool=audio_uart_nema_pool_select_514050(b[1]);
    void *data=(void *)(uintptr_t)b[2];
    audio_uart_lv_pool_free_48429e(pool,data);
    b[2]=0u;b[3]=0u;b[0]=0u;b[1]=UINT32_MAX;
}
/* Native514178..514184. */
void audio_uart_nema_cl_node_release_514178(void *node) {
    audio_uart_lv_pool_free_48429e((void *)(uintptr_t)0x20000338u,node);
}
/* Native4b127c..4b128a; native scratch return ignored by void API. */
void audio_uart_nema_error_set_4b127c(uint32_t error) {
    volatile uint32_t *context=(void *)(uintptr_t)audio_uart_nema_context_cell[0];
    context[8]=context[8]|error;
}
