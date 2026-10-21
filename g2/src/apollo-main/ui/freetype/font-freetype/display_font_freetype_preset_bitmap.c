/* Native FT_Outline_Render bitmap preset0x5250de and LCD adjust0x524f36. */
#include <stdint.h>
extern void audio_uart_font_outline_cbox(void *,void *); /* 0x527ace */
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void s(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static uint32_t floor64(uint32_t n) { return n&~63u; }
static uint32_t ceil64(uint32_t n) { return (n+63u)&~63u; }
void audio_uart_font_preset_bitmap(void *slot,uint32_t mode,const void *origin) {
    uint8_t *internal=(uint8_t *)(uintptr_t)w(slot,0x9cu);
    if(internal!=0 && (internal[4u]&1u)!=0u) return;
    uint32_t dx=origin==0?0u:w(origin,0u);
    uint32_t dy=origin==0?0u:w(origin,4u);
    uint32_t box[4];
    audio_uart_font_outline_cbox((uint8_t *)slot+0x6cu,box);
    box[0]+=dx;box[1]+=dy;box[2]+=dx;box[3]+=dy;
    uint8_t pixel_mode=(uint8_t)mode;
    if(pixel_mode==2u) {
        pixel_mode=1u;
        for(uint32_t axis=0u;axis<2u;axis++) {
            if((int32_t)(box[axis+2u]-box[axis])<64) {
                box[axis]=floor64(box[axis]);box[axis+2u]=ceil64(box[axis+2u]);
            } else {
                box[axis]=floor64(box[axis]+32u);
                box[axis+2u]=floor64(box[axis+2u]+32u);
            }
        }
    } else {
        if(pixel_mode==3u) {pixel_mode=5u;box[0]-=21u;box[2]+=21u;}
        else if(pixel_mode==4u) {pixel_mode=6u;box[1]-=21u;box[3]+=21u;}
        else pixel_mode=2u;
        for(uint32_t i=0u;i<2u;i++) box[i]=floor64(box[i]);
        for(uint32_t i=2u;i<4u;i++) box[i]=ceil64(box[i]);
    }
    uint32_t width=(box[2]-box[0])>>6u;
    uint32_t rows=(box[3]-box[1])>>6u;
    uint32_t pitch=width;
    if(pixel_mode==1u) pitch=((width+15u)>>4u)<<1u;
    else if(pixel_mode==5u) {width*=3u;pitch=(width+3u)&~3u;}
    else if(pixel_mode==6u) rows*=3u;
    s(slot,0x64u,(uint32_t)((int32_t)box[0]>>6));
    s(slot,0x68u,(uint32_t)((int32_t)box[3]>>6));
    uint8_t *bitmap=(uint8_t *)slot+0x4cu;
    bitmap[18u]=pixel_mode;
    *(uint16_t *)(void *)(bitmap+16u)=256u;
    s(bitmap,4u,width);s(bitmap,0u,rows);s(bitmap,8u,pitch);
}
