/* Native Main 0x4403e6 and 0x440494, adapted from the pinned LVGL
 * scrollbar clipping path. Coordinates are signed inclusive endpoints. */
#include <stdint.h>

extern void *audio_uart_lv_obj_has_parent_44dca2(void *);
extern void audio_uart_lv_scrollbar_clip_child_440dda(void *,int32_t *,uint32_t,uint32_t);

uint32_t audio_uart_lv_scrollbar_mode_452dd8(void *object) {
    uint8_t *spec=*(uint8_t **)((uint8_t *)object+8u);
    if(spec==0)return 0;
    return ((uint32_t)*(uint16_t *)(spec+0x32u)>>10)&3u;
}

void audio_uart_lv_scrollbar_clip_4403e6(void *object,int32_t *area,
                                          uint32_t part,uint32_t flags) {
    if(object==0)return;
    uint32_t mode=(uint8_t)audio_uart_lv_scrollbar_mode_452dd8(object);
    uint32_t first=(uint8_t)flags&1u;
    uint32_t second=((uint8_t)flags>>1)&1u;
    if(second!=0u) {
        if(first!=0u)
            audio_uart_lv_scrollbar_clip_4403e6(
                audio_uart_lv_obj_has_parent_44dca2(object),area,part,(uint8_t)flags);
        if(mode==2u)
            audio_uart_lv_scrollbar_clip_child_440dda(object,area,part,second);
    } else {
        if(mode==2u)
            audio_uart_lv_scrollbar_clip_child_440dda(object,area,part,second);
        if(first!=0u)
            audio_uart_lv_scrollbar_clip_4403e6(
                audio_uart_lv_obj_has_parent_44dca2(object),area,part,(uint8_t)flags);
    }
}

static int32_t low(int32_t a,int32_t b) {return a<b?a:b;}
static int32_t high(int32_t a,int32_t b) {return a>b?a:b;}

void audio_uart_lv_object_scrollbar_area_440494(void *object,int32_t *area,
                                                  uint32_t flags) {
    int32_t a[8]={area[0],area[1],area[0],
                  (int32_t)((uint32_t)area[3]+1u),
                  (int32_t)((uint32_t)area[2]+1u),area[1],
                  (int32_t)((uint32_t)area[2]+1u),
                  (int32_t)((uint32_t)area[3]+1u)};
    audio_uart_lv_scrollbar_clip_4403e6(object,a,4u,(uint8_t)flags);
    area[0]=low(low(a[0],a[2]),low(a[4],a[6]));
    area[2]=high(high(a[4],a[6]),high(a[2],a[0]));
    area[1]=low(low(a[1],a[3]),low(a[5],a[7]));
    area[3]=high(high(a[7],a[5]),high(a[3],a[1]));
}
