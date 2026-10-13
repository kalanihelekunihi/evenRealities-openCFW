#include <stdint.h>
extern void *audio_uart_nema_pool_select_514050(uint32_t);
extern void *audio_uart_lv_pool_allocate_484180(void *,uint32_t);
extern void *audio_uart_lv_pool_aligned_allocate_4841d8(void *,uint32_t,uint32_t);
extern void audio_uart_checksum_copy(void *,const void *,uint32_t);
/* Native514070..5140c6: hidden descriptor output, original full-width pool ID. */
void audio_uart_nema_buffer_create_514070(uint32_t *out,uint32_t id,uint32_t size) {
    void *pool=audio_uart_nema_pool_select_514050(id);
    void *pointer;
    if(((const volatile uint8_t *)pool)[24]!=0u) {
        size=(size+31u)&~31u;
        pointer=audio_uart_lv_pool_aligned_allocate_4841d8(pool,size,32u);
    } else if(id<=2u) pointer=audio_uart_lv_pool_aligned_allocate_4841d8(pool,size,8u);
    else pointer=audio_uart_lv_pool_allocate_484180(pool,size);
    uint32_t descriptor[4]={size,id,(uint32_t)(uintptr_t)pointer,(uint32_t)(uintptr_t)pointer};
    audio_uart_checksum_copy(out,descriptor,16u);
}
