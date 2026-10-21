/* Native 0x44b5a0: bounded NUL-terminated copy, zero-filling the tail.
 * The native alignment fast path changes throughput, not defined bytes. */
#include <stdint.h>
void *audio_dashboard_copy_limited(void *dst,const void *src,uint32_t count) {
    uint8_t *d=(uint8_t *)dst;
    const uint8_t *s=(const uint8_t *)src;
    uint32_t i=0;
    while(i<count) {
        uint8_t v=s[i];
        d[i++]=v;
        if(v==0u) break;
    }
    while(i<count) d[i++]=0u;
    return dst;
}
