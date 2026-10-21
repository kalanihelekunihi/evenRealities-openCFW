/* Native FreeType 16.16 fixed-point multiplication 0x5246f8. */
#include <stdint.h>
int32_t audio_uart_font_scale_metric(uint32_t first,int32_t second) {
    uint32_t left=first;
    uint32_t right=(uint32_t)second;
    int32_t sign=1;
    if((int32_t)left<0) {left=0u-left;sign=-1;}
    if((int32_t)right<0) {right=0u-right;sign=-sign;}
    uint32_t result;
    if(left+(right>>8u)<0x1fffu)
        result=(right*left+0x8000u)>>16u;
    else
        result=right*(left>>16u)+(right>>16u)*(left&0xffffu)+
               (((right&0xffffu)*(left&0xffffu)+0x8000u)>>16u);
    if(sign<0) result=0u-result;
    return (int32_t)result;
}
