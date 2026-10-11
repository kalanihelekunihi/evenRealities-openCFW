/* Native FT_Angle_Diff0x52910e and FT_StrokeBorder_Close0x56834a. */
#include <stdint.h>
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=value;
}
int32_t audio_uart_font_stroker_angle_diff(int32_t first,int32_t second) {
    uint32_t difference=(uint32_t)second-(uint32_t)first;
    while((int32_t)difference<(int32_t)0xff4c0001u) difference+=0x1680000u;
    while((int32_t)difference>=(int32_t)0x00b40001u) difference-=0x1680000u;
    return (int32_t)difference;
}
void audio_uart_font_stroker_border_close(void *border,uint32_t reverse) {
    uint8_t *b=(uint8_t *)border;
    uint32_t start=word(b,20u),count=word(b,0u);
    if(start+1u>=count) {
        store(b,0u,start);
    } else {
        uint32_t last=count-1u;
        store(b,0u,last);
        uint8_t *points=(uint8_t *)(uintptr_t)word(b,8u);
        store(points,start*8u,word(points,last*8u));
        store(points,start*8u+4u,word(points,last*8u+4u));
        uint8_t *tags=(uint8_t *)(uintptr_t)word(b,12u);
        if((uint8_t)reverse!=0u) {
            uint32_t left=start+1u,right=last-1u;
            while(left<right) {
                uint32_t lx=word(points,left*8u),ly=word(points,left*8u+4u);
                store(points,left*8u,word(points,right*8u));
                store(points,left*8u+4u,word(points,right*8u+4u));
                store(points,right*8u,lx);store(points,right*8u+4u,ly);
                uint8_t tag=tags[left];tags[left]=tags[right];tags[right]=tag;
                left++;right--;
            }
        }
        tags[start]|=4u;
        tags[last-1u]|=8u;
    }
    store(b,20u,0xffffffffu);
    b[16u]=0u;
}
