/* Native 0x568ce2 joins an existing corner; 0x568d2a opens the first
 * border pair. The selected symbol aliases predate that source mapping. */
#include <stdint.h>
typedef struct { int32_t x,y; } Vector;
extern int32_t audio_uart_font_stroker_angle_diff(int32_t,int32_t); /* 0x52910e */
extern int32_t audio_uart_font_stroker_cap_first(void *,uint8_t,uint32_t); /* 0x5689e6 */
extern int32_t audio_uart_font_stroker_cap_second(void *,uint8_t,uint32_t); /* 0x568abe */
extern void audio_uart_font_vector_from_polar(Vector *,uint32_t,uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_border_move(void *,const Vector *); /* 0x568636 */

static uint32_t word(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void store(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}

int32_t audio_uart_font_stroker_subpath_start(void *stroker,int32_t length) {
    int32_t turn=audio_uart_font_stroker_angle_diff((int32_t)word(stroker,0u),
                                                     (int32_t)word(stroker,4u));
    if(turn==0) return 0;
    uint8_t side=(uint8_t)(turn<0?1u:0u);
    int32_t error=audio_uart_font_stroker_cap_first(stroker,side,(uint32_t)length);
    if(error!=0) return error;
    return audio_uart_font_stroker_cap_second(stroker,(uint8_t)(side==0u?1u:0u),
                                               (uint32_t)length);
}

int32_t audio_uart_font_stroker_process_corner(void *stroker,int32_t angle,
                                                int32_t length) {
    uint8_t *s=(uint8_t *)stroker;
    Vector offset,point;
    audio_uart_font_vector_from_polar(&offset,word(s,0x30u),
                                       (uint32_t)angle+0x5a0000u);
    point.x=(int32_t)(word(s,8u)+(uint32_t)offset.x);
    point.y=(int32_t)(word(s,12u)+(uint32_t)offset.y);
    int32_t error=audio_uart_font_stroker_border_move(s+0x34u,&point);
    if(error!=0) return error;
    point.x=(int32_t)(word(s,8u)-(uint32_t)offset.x);
    point.y=(int32_t)(word(s,12u)-(uint32_t)offset.y);
    error=audio_uart_font_stroker_border_move(s+0x54u,&point);
    store(s,24u,(uint32_t)angle);
    s[20u]=0;
    store(s,36u,(uint32_t)length);
    return error;
}
