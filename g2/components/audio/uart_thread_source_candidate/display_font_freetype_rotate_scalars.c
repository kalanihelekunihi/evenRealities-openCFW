/* Native FT_Vector_NormLen scaling0x528e18 and CORDIC shrink0x528db8. */
#include <stdint.h>
static uint32_t abs_bits(int32_t value) {
    return value<0?0u-(uint32_t)value:(uint32_t)value;
}
int32_t audio_uart_font_vector_normalize(void *vector) {
    int32_t *v=(int32_t *)vector;
    uint32_t combined=abs_bits(v[0])|abs_bits(v[1]);
    uint32_t msb=0u;
    for(uint32_t n=combined;n>1u;n>>=1u) msb++;
    if(msb<30u) {
        uint32_t left=29u-msb;
        v[0]=(int32_t)((uint32_t)v[0]<<left);
        v[1]=(int32_t)((uint32_t)v[1]<<left);
        return (int32_t)left;
    }
    uint32_t right=msb-29u;
    v[0]>>=right;v[1]>>=right;
    return -(int32_t)right;
}
int32_t audio_uart_font_vector_shrink(int32_t value) {
    uint32_t magnitude=abs_bits(value);
    uint64_t product=(uint64_t)magnitude*0xdbd95b16ull+0x40000000ull;
    uint32_t result=(uint32_t)(product>>32u);
    return (int32_t)(value<0?0u-result:result);
}
