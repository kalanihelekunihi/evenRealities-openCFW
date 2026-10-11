/* Native FT_Stroker_LineTo, 0x568d86.  The corner and subpath helpers
 * retain their separate native identities and error propagation. */
#include <stdint.h>

typedef struct { int32_t x, y; } Vector;
extern int32_t audio_uart_font_vector_length(const Vector *); /* 0x529086 */
extern int32_t audio_uart_font_vector_angle(int32_t, int32_t); /* 0x528fbc */
extern void audio_uart_font_vector_from_polar(Vector *, uint32_t, uint32_t); /* 0x5290fa */
extern int32_t audio_uart_font_stroker_process_corner(void *, int32_t, int32_t); /* 0x568d2a */
extern int32_t audio_uart_font_stroker_subpath_start(void *, int32_t); /* 0x568ce2 */
extern int32_t audio_uart_font_stroker_border_add(void *, const Vector *, uint32_t); /* 0x5683f2 */

static uint32_t word(const void *p, uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p + offset);
}
static void store(void *p, uint32_t offset, uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p + offset) = v;
}

int32_t audio_uart_font_stroker_line(void *stroker, const Vector *to) {
    if (stroker == 0 || to == 0) return 6;
    uint8_t *s = (uint8_t *)stroker;
    Vector offset = {(int32_t)((uint32_t)to->x - word(s,8u)),
                     (int32_t)((uint32_t)to->y - word(s,12u))};
    if (offset.x == 0 && offset.y == 0) return 0;
    int32_t length = audio_uart_font_vector_length(&offset);
    int32_t angle = audio_uart_font_vector_angle(offset.x, offset.y);
    audio_uart_font_vector_from_polar(&offset, word(s,0x30u),
                                      (uint32_t)angle + 0x5a0000u);
    int32_t error;
    if (s[20u] != 0u) {
        error = audio_uart_font_stroker_process_corner(s, angle, length);
        if (error != 0) return error;
    } else {
        store(s,4u,(uint32_t)angle);
        error = audio_uart_font_stroker_subpath_start(s,length);
        if (error != 0) return error;
    }
    for (uint32_t side=0;side<2u;++side) {
        Vector point = {(int32_t)((uint32_t)to->x+(uint32_t)offset.x),
                        (int32_t)((uint32_t)to->y+(uint32_t)offset.y)};
        error = audio_uart_font_stroker_border_add(s+0x34u+side*0x20u,&point,1u);
        if (error != 0) return error;
        offset.x=(int32_t)(-(uint32_t)offset.x);
        offset.y=(int32_t)(-(uint32_t)offset.y);
    }
    store(s,0u,(uint32_t)angle);
    store(s,8u,(uint32_t)to->x);
    store(s,12u,(uint32_t)to->y);
    store(s,16u,(uint32_t)length);
    return 0;
}
