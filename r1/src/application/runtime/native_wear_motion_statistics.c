#include <stdint.h>
#include "../board/native_battery_memory.h"
#pragma STDC FP_CONTRACT OFF

static float sample_axis(uint32_t packet,uint32_t offset)
{
    return (float)(int16_t)read16((const volatile uint8_t *)(uintptr_t)(packet+offset));
}

void r1_wear_motion_statistics(uint32_t packet,void *destination)
{
    volatile float *out=(volatile float *)destination;
    uint32_t index=0,count;
    float sum_x;
    for (;;) {
        count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
        sum_x=out[0];
        if (count<=index) break;
        uint32_t offset=index*6u;
        float x=sample_axis(packet,offset);
        index=(uint8_t)(index+1u);
        out[0]=sum_x+x;
        float y=sample_axis(packet,offset+2u),sum_y=out[1];
        out[1]=sum_y+y;
        float z=sample_axis(packet,offset+4u),sum_z=out[2];
        out[2]=sum_z+z;
    }
    float mean_x=sum_x/(float)count;
    out[0]=mean_x;
    count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
    float sum_y=out[1],mean_y=sum_y/(float)count;
    out[1]=mean_y;
    count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
    float sum_z=out[2],mean_z=sum_z/(float)count;
    out[2]=mean_z;
    index=0;
    for (;;) {
        count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
        if (count<=index) break;
        uint32_t offset=index*6u;
        float x=sample_axis(packet,offset);
        index=(uint8_t)(index+1u);
        float dx=x-mean_x,variance_x=out[3];
        out[3]=variance_x+dx*dx;
        float y=sample_axis(packet,offset+2u),dy=y-mean_y,variance_y=out[4];
        out[4]=variance_y+dy*dy;
        float z=sample_axis(packet,offset+4u),dz=z-mean_z,variance_z=out[5];
        out[5]=variance_z+dz*dz;
    }
    float variance_x=out[3];
    out[3]=variance_x/(float)count;
    count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
    float variance_y=out[4];
    out[4]=variance_y/(float)count;
    count=read16((const volatile uint8_t *)(uintptr_t)(packet+180u));
    float variance_z=out[5];
    out[5]=variance_z/(float)count;
}
