/* Native FT_MulFix0x5246f8, FT_Vector_Transform0x527b60,
 * FT_Outline_Transform0x527ba0, with 32-bit arithmetic/rounding. */
#include <stdint.h>
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
extern int32_t audio_uart_font_scale_metric(uint32_t,int32_t); /* selected 0x5246f8 */
void audio_uart_font_vector_transform(void *vector,const void *matrix) {
    if(vector==0||matrix==0) return;
    int32_t x=(int32_t)word(vector,0u),y=(int32_t)word(vector,4u);
    uint32_t out_x=(uint32_t)audio_uart_font_scale_metric((uint32_t)x,(int32_t)word(matrix,0u))+
                   (uint32_t)audio_uart_font_scale_metric((uint32_t)y,(int32_t)word(matrix,4u));
    uint32_t out_y=(uint32_t)audio_uart_font_scale_metric((uint32_t)x,(int32_t)word(matrix,8u))+
                   (uint32_t)audio_uart_font_scale_metric((uint32_t)y,(int32_t)word(matrix,12u));
    store(vector,0u,out_x);store(vector,4u,out_y);
}
void audio_uart_font_outline_transform(void *outline,const void *matrix) {
    if(outline==0||matrix==0) return;
    int32_t count=*(const int16_t *)(const void *)((const uint8_t *)outline+2u);
    uint8_t *points=(uint8_t *)(uintptr_t)word(outline,4u);
    for(int32_t i=0;i<count;i++)
        audio_uart_font_vector_transform(points+(uint32_t)i*8u,matrix);
}
