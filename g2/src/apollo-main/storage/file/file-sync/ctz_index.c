/* Pinned LittleFS CTZ index conversion, stock 0x4cd6e4. */
#include <stdint.h>
static uint32_t popcount(uint32_t value) {
    uint32_t count=0;
    while(value) {count+=value&1u;value>>=1u;}
    return count;
}
uint32_t g2_lfs_ctz_index(void *filesystem,uint32_t *offset) {
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    uint32_t size=*offset;
    uint32_t block_data=*(uint32_t *)(void *)(cfg+0x1cu)-8u;
    uint32_t index=size/block_data;
    if(index==0u) return 0;
    index=(size-4u*(popcount(index-1u)+2u))/block_data;
    *offset=size-block_data*index-4u*popcount(index);
    return index;
}
