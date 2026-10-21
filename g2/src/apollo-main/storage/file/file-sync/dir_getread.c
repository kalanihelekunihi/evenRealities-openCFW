/* Pinned LittleFS inline directory read/cache worker, stock 0x4cb3f0. */
#include <stdint.h>
extern void g2_lfs_memcpy(void *destination,const void *source,uint32_t size);
extern uint32_t g2_lfs_aligndown(uint32_t value,uint32_t align);
extern uint32_t g2_lfs_alignup(uint32_t value,uint32_t align);
extern int32_t g2_lfs_dir_getslice(void *filesystem,void *directory,
                                    uint32_t mask,uint32_t tag,uint32_t offset,
                                    void *buffer,uint32_t size);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
static uint32_t min_u32(uint32_t a,uint32_t b) {return a<b?a:b;}
int32_t g2_lfs_dir_getread(void *filesystem,void *directory,
                            const void *program_cache,void *read_cache,
                            uint32_t hint,uint32_t mask,uint32_t tag,
                            uint32_t offset,void *buffer,uint32_t size) {
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    if(offset+size>*word_at(cfg,0x1cu)) return -84;
    uint8_t *data=(uint8_t *)buffer;
    while(size) {
        uint32_t diff=size;
        if(program_cache && *word_at((void *)program_cache,0u)==UINT32_MAX-1u &&
           offset<*word_at((void *)program_cache,4u)+*word_at((void *)program_cache,8u)) {
            if(offset>=*word_at((void *)program_cache,4u)) {
                uint32_t displacement=offset-*word_at((void *)program_cache,4u);
                diff=min_u32(diff,*word_at((void *)program_cache,8u)-displacement);
                g2_lfs_memcpy(data,
                    (const uint8_t *)(uintptr_t)*word_at((void *)program_cache,12u)+displacement,diff);
                data+=diff;offset+=diff;size-=diff;continue;
            }
            diff=min_u32(diff,*word_at((void *)program_cache,4u)-offset);
        }
        if(*word_at(read_cache,0u)==UINT32_MAX-1u &&
           offset<*word_at(read_cache,4u)+*word_at(read_cache,8u)) {
            if(offset>=*word_at(read_cache,4u)) {
                uint32_t displacement=offset-*word_at(read_cache,4u);
                diff=min_u32(diff,*word_at(read_cache,8u)-displacement);
                g2_lfs_memcpy(data,
                    (const uint8_t *)(uintptr_t)*word_at(read_cache,12u)+displacement,diff);
                data+=diff;offset+=diff;size-=diff;continue;
            }
            diff=min_u32(diff,*word_at(read_cache,4u)-offset);
        }
        uint32_t read_size=*word_at(cfg,0x14u);
        *word_at(read_cache,0u)=UINT32_MAX-1u;
        *word_at(read_cache,4u)=g2_lfs_aligndown(offset,read_size);
        *word_at(read_cache,8u)=min_u32(g2_lfs_alignup(offset+hint,read_size),
                                        *word_at(cfg,0x28u));
        int32_t err=g2_lfs_dir_getslice(filesystem,directory,mask,tag,
                      *word_at(read_cache,4u),
                      (void *)(uintptr_t)*word_at(read_cache,12u),
                      *word_at(read_cache,8u));
        if(err<0) return err;
    }
    return 0;
}
