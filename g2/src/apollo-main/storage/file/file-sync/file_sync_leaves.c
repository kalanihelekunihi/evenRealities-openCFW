/* LittleFS pair-null and CTZ endian leaves, stock 0x4cadd0/0x4cb000. */
#include <stdint.h>
int32_t g2_lfs_pair_isnull(const void *pair) {
    const uint32_t *p=(const uint32_t *)pair;
    return p[0]==UINT32_MAX || p[1]==UINT32_MAX;
}
void g2_lfs_ctz_tole32(void *ctz) {
    /* Match pinned little-endian conversion's byte ordering explicitly. */
    uint32_t *p=(uint32_t *)ctz;
    for(uint32_t i=0;i<2u;i++) {
        uint32_t v=p[i];
        p[i]=(v&0xffu)|((v>>8u&0xffu)<<8u)|
             ((v>>16u&0xffu)<<16u)|((v>>24u&0xffu)<<24u);
    }
}
