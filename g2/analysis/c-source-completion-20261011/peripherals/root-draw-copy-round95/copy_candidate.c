#include <stdint.h>
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern void *audio_uart_lv_draw_buf_goto_xy_48b2aa(const void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *,const void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native48ad42..48aef8, including custom-copy dispatch and assertions. */
void audio_uart_lv_draw_buf_copy_48ad42(void *destination,const void *destination_area,const void *source,const void *source_area)
{
    volatile uint32_t *d=destination;
    const volatile uint32_t *s=source;
    const volatile uint32_t *handlers=(const volatile uint32_t *)(uintptr_t)d[6];
    if(handlers[7]!=0u) {
        ((void (*)(void *,const void *,const void *,const void *))(uintptr_t)handlers[7])(destination,destination_area,source,source_area);return;
    }
    static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_copy";
    if((uint8_t)(d[0]>>8u)!=(uint8_t)(s[0]>>8u)) {
        audio_uart_lvgl_log(3u,file,235u,function,"Asserted at expression: %s Color format mismatch: %d != %d","dest->header.cf == src->header.cf",(uint32_t)(uint8_t)(d[0]>>8u),(uint32_t)(uint8_t)(s[0]>>8u));
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    uint32_t width=destination_area==0 ? (uint16_t)d[1] : audio_uart_lv_area_width_451598(destination_area);
    if((destination_area==0 || source_area==0) && (uint32_t)(uint8_t)(d[0]>>8u)-7u<4u) {
        uint32_t palette;
        if((uint8_t)(d[0]>>8u)==7u) palette=2u;
        else if((uint8_t)(d[0]>>8u)==8u) palette=4u;
        else if((uint8_t)(d[0]>>8u)==9u) palette=16u;
        else if((uint8_t)(d[0]>>8u)==10u) palette=256u;
        else palette=0u;
        audio_uart_lv_grid_copy_454738((void *)(uintptr_t)d[4],(void *)(uintptr_t)s[4],palette*4u);
    }
    if((source_area==0 && width!=(uint16_t)s[1]) || (source_area!=0 && width!=audio_uart_lv_area_width_451598(source_area))) {
        audio_uart_lvgl_log(3u,file,250u,function,"Asserted at expression: %s (%s)","0","Source and destination areas have different width");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    const volatile uint32_t *sa=source_area,*da=destination_area;
    uint32_t src=source_area!=0 ? (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(source,sa[0],sa[1]) : (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(source,0u,0u);
    uint32_t dst=destination_area!=0 ? (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(destination,da[0],da[1]) : (uint32_t)(uintptr_t)audio_uart_lv_draw_buf_goto_xy_48b2aa(destination,0u,0u);
    uint32_t y,end;
    if(destination_area!=0) {y=da[1];end=da[3];}
    else {y=0u;end=(d[1]>>16u)-1u;}
    uint32_t dest_stride=(uint16_t)d[2],src_stride=(uint16_t)s[2];
    uint32_t bytes=(width*audio_uart_lv_color_bpp_440f44((uint8_t)(d[0]>>8u))+7u);
    bytes=(bytes>>3u)|((bytes&0x80000000u)!=0u?0xe0000000u:0u);
    while((int32_t)y<=(int32_t)end) {
        audio_uart_lv_grid_copy_454738((void *)(uintptr_t)dst,(void *)(uintptr_t)src,bytes);
        dst+=dest_stride;src+=src_stride;y+=1u;
    }
}
