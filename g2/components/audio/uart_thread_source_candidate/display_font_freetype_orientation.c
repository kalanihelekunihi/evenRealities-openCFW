/* Native FT_Outline_Get_Orientation 0x527e0a, using signed area from the
 * authenticated FreeType outline layout. */
#include <stdint.h>
extern void audio_uart_font_outline_cbox(void *,void *); /* 0x527ace */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static uint32_t msb(uint32_t value) {
    uint32_t index=0u;
    while(value>>=1u) index++;
    return index;
}
static uint32_t abs_bits(int32_t value) {
    return value<0?(uint32_t)(-(int64_t)value):(uint32_t)value;
}
uint32_t audio_uart_font_outline_orientation(void *outline) {
    if(outline==0 || *(int16_t *)(void *)((uint8_t *)outline+2u)<1) return 0u;
    int32_t box[4];
    audio_uart_font_outline_cbox(outline,box);
    if(box[0]==box[2] || box[1]==box[3]) return 2u;
    uint32_t sx=msb(abs_bits(box[0])|abs_bits(box[2]));
    uint32_t sy=msb((uint32_t)box[3]-(uint32_t)box[1]);
    sx=sx>14u?sx-14u:0u;
    sy=sy>14u?sy-14u:0u;
    const int32_t *points=(const int32_t *)(uintptr_t)word(outline,4u);
    const int16_t *contours=(const int16_t *)(uintptr_t)word(outline,0x0cu);
    uint32_t area=0u;
    int32_t first=0;
    int32_t count=*(int16_t *)(void *)outline;
    for(int32_t contour=0;contour<count;contour++) {
        int32_t last=contours[contour];
        int32_t px=points[last*2]>>(sx&0xffu);
        int32_t py=points[last*2+1]>>(sy&0xffu);
        for(int32_t i=first;i<=last;i++) {
            int32_t x=points[i*2]>>(sx&0xffu);
            int32_t y=points[i*2+1]>>(sy&0xffu);
            area+=((uint32_t)px+(uint32_t)x)*((uint32_t)y-(uint32_t)py);
            px=x;py=y;
        }
        first=last+1;
    }
    return (int32_t)area<0?0u:area==0u?2u:1u;
}
