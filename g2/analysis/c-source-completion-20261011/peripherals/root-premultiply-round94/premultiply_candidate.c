#include <stdint.h>
extern void audio_uart_lv_basic_box_clear_454746(void *,uint32_t,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
/* Full native440f38..440f44; return scratch is not a void API contract. */
void audio_uart_lv_color_zero_440f38(void *color,uint32_t size)
{
    audio_uart_lv_basic_box_clear_454746(color,0u,size);
}
/* Full native4410b8..4410ee; RGB channels update red, green, blue in that order. */
void audio_uart_lv_color_premultiply_4410b8(void *color)
{
    volatile uint8_t *c=color;
    if(c[3]==255u) return;
    if(c[3]==0u) {audio_uart_lv_color_zero_440f38(color,4u);return;}
    c[2]=(uint8_t)((uint32_t)c[2]*c[3]>>8u);
    c[1]=(uint8_t)((uint32_t)c[1]*c[3]>>8u);
    c[0]=(uint8_t)((uint32_t)c[0]*c[3]>>8u);
}
struct audio_uart_packed_color16 { uint16_t value; } __attribute__((packed));
/* Full native4410ee..441164; packed accesses support native ARGB8565 pixels. */
void audio_uart_lv_color16_premultiply_4410ee(void *color,uint32_t alpha)
{
    volatile struct audio_uart_packed_color16 *c=color;
    if((uint8_t)alpha==255u) return;
    if((uint8_t)alpha==0u) {audio_uart_lv_color_zero_440f38(color,2u);return;}
    uint32_t red=(((uint32_t)(c->value>>11u)*(uint8_t)alpha)>>8u)&31u;
    c->value=(uint16_t)((c->value&0x7ffu)|(red<<11u));
    uint32_t green=(((uint32_t)((c->value>>5u)&63u)*(uint8_t)alpha)>>8u)&63u;
    c->value=(uint16_t)((c->value&0xf81fu)|(green<<5u));
    uint32_t blue=((uint32_t)(*(volatile uint8_t *)color&31u)*(uint8_t)alpha>>8u)&31u;
    c->value=(uint16_t)((c->value&0xffe0u)|blue);
}
/* Full native48b540..48b722, including unsupported-format diagnostic and flags. */
uint32_t audio_uart_lv_draw_buf_premultiply_48b540(void *buffer)
{
    volatile uint32_t *b=buffer;
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_buf.c";
    static const char function[]="lv_draw_buf_premultiply";
    if(b==0) {
        audio_uart_lvgl_log(3u,source,520u,function,"Asserted at expression: %s (%s)","draw_buf != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    if(b==0) return 0u;
    if(((b[0]>>16u)&1u)!=0u) return 0u;
    if(((b[0]>>16u)&32u)==0u) {
        audio_uart_lvgl_log(2u,source,525u,function,"draw buf is not modifiable: 0x%04x",b[0]>>16u);return 0u;
    }
    uint32_t cf=b[0]>>8u;
    if((uint32_t)(uint8_t)cf-7u<4u) {
        uint32_t n=(uint8_t)cf==7u?2u:(uint8_t)cf==8u?4u:(uint8_t)cf==9u?16u:256u;
        uint32_t data=b[4];
        for(uint32_t i=0u;i<n;i++) audio_uart_lv_color_premultiply_4410b8((void *)(uintptr_t)(data+4u*i));
    } else if((uint8_t)cf==16u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],line=b[4];
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {audio_uart_lv_color_premultiply_4410b8((void *)(uintptr_t)pixel);pixel+=4u;}
            line+=stride;
        }
    } else if((uint8_t)cf==20u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],alpha_stride=stride>>1u,line=b[4];
        uint32_t alpha=line+height*stride;
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {
                audio_uart_lv_color16_premultiply_4410ee((void *)(uintptr_t)pixel,*(volatile uint8_t *)(uintptr_t)(alpha+x));pixel+=2u;
            }
            line+=stride;alpha+=alpha_stride;
        }
    } else if((uint8_t)cf==19u) {
        uint32_t height=b[1]>>16u,width=(uint16_t)b[1],stride=(uint16_t)b[2],line=b[4];
        for(uint32_t y=0u;y<height;y++) {
            uint32_t pixel=line;
            for(uint32_t x=0u;x<width;x++) {
                uint32_t alpha=*(volatile uint8_t *)(uintptr_t)(pixel+2u);
                audio_uart_lv_color16_premultiply_4410ee((void *)(uintptr_t)pixel,alpha);pixel+=3u;
            }
            line+=stride;
        }
    } else if((uint32_t)(uint8_t)cf-11u>=4u) {
        audio_uart_lvgl_log(2u,source,589u,function,"draw buf has no alpha, cf: %d",(uint32_t)(uint8_t)cf);
    }
    uint32_t flags=(b[0]>>16u)|1u;
    b[0]=(b[0]&0xffffu)|(flags<<16u);
    return 1u;
}
