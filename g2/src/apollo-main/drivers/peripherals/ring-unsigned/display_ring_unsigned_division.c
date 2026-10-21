/* Native 64-bit unsigned division helper at 0x47cc60.  Its zero divisor
 * path returns the dividend.  A restoring divide expresses the same quotient
 * without depending on a compiler-provided __aeabi_uldivmod implementation. */
#include <stdint.h>
uint64_t audio_uart_ring_u64_div_47cc60(uint32_t low,uint32_t high,
                                         uint32_t divisor_low,uint32_t divisor_high) {
    uint64_t dividend=((uint64_t)high<<32)|low;
    uint64_t divisor=((uint64_t)divisor_high<<32)|divisor_low;
    if(divisor==0u)return dividend;
    uint64_t quotient=0u,remainder=0u;
    for(unsigned bit=64u;bit!=0u;) {
        --bit;
        uint64_t carry=remainder>>63;
        remainder=(remainder<<1)|((dividend>>bit)&1u);
        if(carry!=0u || remainder>=divisor) {
            remainder-=divisor;
            quotient|=(uint64_t)1u<<bit;
        }
    }
    return quotient;
}
