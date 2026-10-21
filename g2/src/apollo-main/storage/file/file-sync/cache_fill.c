/* Source equivalent of stock reverse-fill memset body at 0x43c0e4. */
#include <stdint.h>
void *g2_lfs_cache_fill(void *buffer,uint32_t length,uint32_t value) {
    volatile uint8_t *bytes=(volatile uint8_t *)buffer;
    uint8_t fill=(uint8_t)value;
    for(uint32_t i=length;i!=0u;--i) bytes[i-1u]=fill;
    return buffer;
}
