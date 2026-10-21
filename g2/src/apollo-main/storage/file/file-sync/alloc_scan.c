/* Pinned LittleFS lookahead callback/drop/scan, stock 0x4cb0f6/0x4cb0e6/0x4cb12e. */
#include <stdint.h>
extern void g2_lfs_cache_fill(void *buffer,uint32_t length,uint32_t value);
extern int32_t g2_lfs_fs_traverse(void *filesystem,
                                  int32_t (*visit)(void *,uint32_t),
                                  void *context,uint32_t include_orphans);
extern void g2_lfs_alloc_checkpoint(void *filesystem);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_alloc_lookahead(void *filesystem,uint32_t block) {
    uint32_t count=*word_at(filesystem,0x6cu);
    uint32_t off=((block-*word_at(filesystem,0x54u))+count)%count;
    if(off<*word_at(filesystem,0x58u)) {
        uint8_t *buffer=(uint8_t *)(uintptr_t)*word_at(filesystem,0x64u);
        buffer[off/8u]|=(uint8_t)(1u<<(off%8u));
    }
    return 0;
}
void g2_lfs_alloc_drop(void *filesystem) {
    *word_at(filesystem,0x58u)=0;
    *word_at(filesystem,0x5cu)=0;
    g2_lfs_alloc_checkpoint(filesystem);
}
int32_t g2_lfs_alloc_scan(void *filesystem) {
    uint32_t count=*word_at(filesystem,0x6cu);
    *word_at(filesystem,0x54u)=
        (*word_at(filesystem,0x54u)+*word_at(filesystem,0x5cu))%count;
    *word_at(filesystem,0x5cu)=0;
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    uint32_t capacity=*word_at(cfg,0x2cu)*8u;
    uint32_t checkpoint=*word_at(filesystem,0x60u);
    *word_at(filesystem,0x58u)=capacity<checkpoint?capacity:checkpoint;
    g2_lfs_cache_fill((void *)(uintptr_t)*word_at(filesystem,0x64u),
                      *word_at(cfg,0x2cu),0u);
    int32_t err=g2_lfs_fs_traverse(filesystem,g2_lfs_alloc_lookahead,
                                   filesystem,1u);
    if(err) {g2_lfs_alloc_drop(filesystem);return err;}
    return 0;
}
