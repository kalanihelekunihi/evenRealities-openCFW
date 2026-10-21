/* Native FreeType signed MulDiv 0x524606 and DivFix 0x524754. */
#include <stdint.h>
static uint64_t magnitude(int32_t value) {
    return value<0?(uint64_t)(0u-(uint32_t)value):(uint64_t)(uint32_t)value;
}
static int32_t signed_result(uint64_t value,uint32_t negative) {
    if(value>0xffffffffull) value=0x7fffffffull;
    uint32_t result=(uint32_t)value;
    return (int32_t)(negative?(0u-result):result);
}
int32_t audio_uart_font_mul_div(int32_t a,int32_t b,int32_t c) {
    uint32_t negative=((uint32_t)a^(uint32_t)b^(uint32_t)c)>>31u;
    uint64_t divisor=magnitude(c);
    if(divisor==0u) return signed_result(0x7fffffffu,negative);
    uint64_t numerator=magnitude(a)*magnitude(b)+(divisor>>1u);
    return signed_result(numerator/divisor,negative);
}
int32_t audio_uart_font_divide_metric(int32_t a,int32_t b) {
    uint32_t negative=((uint32_t)a^(uint32_t)b)>>31u;
    uint64_t divisor=magnitude(b);
    if(divisor==0u) return signed_result(0x7fffffffu,negative);
    uint64_t numerator=(magnitude(a)<<16u)+(divisor>>1u);
    return signed_result(numerator/divisor,negative);
}
