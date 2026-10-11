/* ARM forward-copy side effects at stock 0x439be4. */
#include <stdint.h>
void g2_lfs_memcpy(void *destination,const void *source,uint32_t count) {
    uint8_t *to=(uint8_t *)destination;
    const uint8_t *from=(const uint8_t *)source;
    for(uint32_t i=0;i<count;i++) to[i]=from[i];
}
