/* Native FT_Vector_Rotate CORDIC core 0x528e5a. Table values are the
 * authenticated 22 words at stock ROM 0x6e35c0, not opaque code bytes. */
#include <stdint.h>
static const uint32_t angles[22]={
    0x1a90a7u,0xe0947u,0x72001u,0x3938bu,0x1ca38u,0xe52au,
    0x7297u,0x394cu,0x1ca6u,0xe53u,0x729u,0x395u,
    0x1cau,0xe5u,0x73u,0x39u,0x1du,0xeu,0x7u,0x4u,0x2u,0x1u};
void audio_uart_font_vector_rotate_core(void *vector,uint32_t raw_angle) {
    int32_t *v=(int32_t *)vector;
    uint32_t x=(uint32_t)v[0],y=(uint32_t)v[1],angle=raw_angle;
    while((int32_t)(angle+0x2d0000u)<0) {
        uint32_t old=y;y=0u-x;x=old;angle+=0x5a0000u;
    }
    while((int32_t)angle>=0x2d0001) {
        uint32_t old=x;x=0u-y;y=old;angle-=0x5a0000u;
    }
    uint32_t power=1u;
    for(uint32_t shift=1u;shift<23u;shift++) {
        int32_t dy=(int32_t)(y+power)>>shift;
        int32_t dx=(int32_t)(x+power)>>shift;
        if((int32_t)angle>=0) {
            x-= (uint32_t)dy;
            y+= (uint32_t)dx;
            angle-=angles[shift-1u];
        } else {
            x+= (uint32_t)dy;
            y-= (uint32_t)dx;
            angle+=angles[shift-1u];
        }
        power<<=1u;
    }
    v[0]=(int32_t)x;v[1]=(int32_t)y;
}
