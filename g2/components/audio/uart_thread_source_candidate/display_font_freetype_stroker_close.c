/* Native FT_Stroker_EndSubPath 0x5695f8. Geometry children have explicit
 * source contracts and preserve the native call/error order. */
#include <stdint.h>
extern int32_t audio_uart_font_stroker_arc(void *,uint32_t,uint32_t); /* 0x5688b8 */
extern int32_t audio_uart_font_stroker_reverse(void *,uint32_t); /* 0x569532 */
extern void audio_uart_font_stroker_border_close(void *,uint32_t); /* 0x56834a */
extern int32_t audio_uart_font_stroker_line(void *,const void *); /* 0x568d86 */
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_stroker_cap_first(void *,uint8_t,uint32_t); /* 0x5689e6 */
extern int32_t audio_uart_font_stroker_cap_second(void *,uint8_t,uint32_t); /* 0x568abe */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
int32_t audio_uart_font_stroker_close(void *stroker) {
    if(stroker==0) return 6;
    uint8_t *s=(uint8_t *)stroker;
    if(s[21u]!=0u) {
        int32_t error=audio_uart_font_stroker_arc(s,word(s,0u),0u);
        if(error!=0) return error;
        error=audio_uart_font_stroker_reverse(s,1u);
        if(error!=0) return error;
        store(s,8u,word(s,28u));store(s,12u,word(s,32u));
        error=audio_uart_font_stroker_arc(s,word(s,24u)+0xb40000u,0u);
        if(error!=0) return error;
        audio_uart_font_stroker_border_close(s+0x34u,0u);
        return 0;
    }
    if(word(s,8u)!=word(s,28u)||word(s,12u)!=word(s,32u)) {
        int32_t error=audio_uart_font_stroker_line(s,s+28u);
        if(error!=0) return error;
    }
    store(s,4u,word(s,24u));
    int32_t direction=audio_uart_font_stroker_angle_diff((int32_t)word(s,0u),
                                                           (int32_t)word(s,4u));
    if(direction!=0) {
        uint8_t side=(uint8_t)(direction<0?1u:0u);
        int32_t error=audio_uart_font_stroker_cap_first(s,side,word(s,36u));
        if(error!=0) return error;
        error=audio_uart_font_stroker_cap_second(s,(uint8_t)(side==0u?1u:0u),word(s,36u));
        if(error!=0) return error;
    }
    audio_uart_font_stroker_border_close(s+0x34u,0u);
    audio_uart_font_stroker_border_close(s+0x54u,1u);
    return 0;
}
