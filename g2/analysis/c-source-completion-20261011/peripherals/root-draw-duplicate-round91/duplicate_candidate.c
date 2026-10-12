#include <stdint.h>
extern void *audio_uart_lv_draw_buf_create_ex_48b010(void *,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
/* Full native48b134..48b196; preserve fresh loads after allocation and flag writes. */
void *audio_uart_lv_draw_buf_duplicate_ex_48b134(void *handlers,const void *source)
{
    const volatile uint32_t *src=source;
    volatile uint32_t *dst=audio_uart_lv_draw_buf_create_ex_48b010(handlers,(uint16_t)src[1],src[1]>>16u,(uint8_t)(src[0]>>8u),(uint16_t)src[2]);
    if(dst==0) return 0;
    uint32_t flags=src[0]>>16u;
    dst[0]=(dst[0]&0xffffu)|(flags<<16u);
    flags=(dst[0]>>16u)|48u;
    dst[0]=(dst[0]&0xffffu)|(flags<<16u);
    uint32_t size;
    if(src[3]<dst[3]) size=src[3];else size=dst[3];
    audio_uart_lv_grid_copy_454738((void *)(uintptr_t)dst[4],(const void *)(uintptr_t)src[4],size);
    return (void *)dst;
}
