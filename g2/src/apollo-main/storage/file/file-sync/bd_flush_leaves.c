/* LittleFS geometry/cache helpers, stock 0x4ca708/0x4ca714/0x4ca822. */
#include <stdint.h>
extern void *g2_lfs_cache_fill(void *buffer,uint32_t length,uint32_t value);
uint32_t g2_lfs_aligndown(uint32_t size,uint32_t align) {
    return (size/align)*align;
}
uint32_t g2_lfs_alignup(uint32_t size,uint32_t align) {
    return g2_lfs_aligndown(size+align-1u,align);
}
void g2_lfs_cache_zero(void *filesystem,void *cache) {
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    uint32_t size=*(uint32_t *)(void *)(cfg+0x28u);
    void *buffer=*(void **)((uint8_t *)cache+12u);
    (void)g2_lfs_cache_fill(buffer,size,0xffu);
    *(uint32_t *)cache=UINT32_MAX;
}
