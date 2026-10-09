/* Reconstructed quotient-only support for GCC division call sites selected in
 * config_baudrate. This is not a complete __aeabi_uldivmod ABI implementation:
 * remainder registers are not supplied. Denominators tested here fit32bits.
 * No executable library archive or original opcode body is retained. */
#include <stdint.h>
uint64_t __aeabi_uldivmod(uint64_t n,uint64_t d) {
    uint64_t q=0,r=0;
    if(d==0)return 0; /* Not validated as a stock zero-divisor behavior. */
    for(unsigned i=0;i<64;i++) {
        uint64_t bit=n>>63;n<<=1;r=(r<<1)|bit;q<<=1;
        if(r>=d){r-=d;q|=1;}
    }
    return q;
}
