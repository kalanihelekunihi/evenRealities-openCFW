/* Native CORDIC pseudo-polarize 0x528ee4, with authenticated ROM
 * angle table at 0x6e35c0. Output vector stores radius and angle. */
#include <stdint.h>
static const uint32_t angles[22]={
    0x1a90a7u,0xe0947u,0x72001u,0x3938bu,0x1ca38u,0xe52au,
    0x7297u,0x394cu,0x1ca6u,0xe53u,0x729u,0x395u,
    0x1cau,0xe5u,0x73u,0x39u,0x1du,0xeu,0x7u,0x4u,0x2u,0x1u};
void audio_uart_font_vector_angle_core(void *vector) {
    uint32_t *v=(uint32_t *)vector;
    uint32_t x=v[0],y=v[1],angle;
    if((int32_t)x<(int32_t)y) {
        if((int32_t)(0u-x)<(int32_t)y) {
            angle=0x5a0000u;uint32_t t=x;x=y;y=0u-t;
        } else {
            angle=(int32_t)y>=1?0xb40000u:0xff4c0000u;
            x=0u-x;y=0u-y;
        }
    } else if((int32_t)(x+y)<0) {
        angle=0xffa60000u;uint32_t t=y;y=x;x=0u-t;
    } else angle=0u;
    uint32_t power=1u;
    for(uint32_t shift=1u;shift<23u;++shift) {
        uint32_t dx=(uint32_t)((int32_t)(power+x)>>shift);
        uint32_t dy=(uint32_t)((int32_t)(power+y)>>shift);
        if((int32_t)y<1) {
            x-=dy;y+=dx;angle-=angles[shift-1u];
        } else {
            x+=dy;y-=dx;angle+=angles[shift-1u];
        }
        power<<=1u;
    }
    if((int32_t)angle>=0) angle=(angle+8u)&~15u;
    else angle=0u-((8u-angle)&~15u);
    v[0]=x;v[1]=angle;
}
