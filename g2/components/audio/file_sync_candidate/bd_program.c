/* Pinned LittleFS cached block program worker, stock 0x4cac04. */
#include <stdint.h>
extern void g2_file_close_error(const char *message,const char *file,uint32_t line);
extern void g2_lfs_memcpy(void *destination,const void *source,uint32_t size);
extern uint32_t g2_lfs_aligndown(uint32_t value,uint32_t align);
extern int32_t g2_lfs_bd_flush(void *filesystem,void *program_cache,
                                void *read_cache,uint32_t validate);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_bd_program(void *filesystem,void *program_cache,
                           void *read_cache,uint32_t validate,
                           uint32_t block,uint32_t offset,
                           const void *buffer,uint32_t size) {
    uint8_t *fs=(uint8_t *)filesystem,*pc=(uint8_t *)program_cache;
    uint8_t *cfg=*(uint8_t **)(void *)(fs+0x68u);
    if(block!=UINT32_MAX-1u && block>=*word_at(fs,0x6cu))
        g2_file_close_error((const char *)(uintptr_t)0x71f758u,
                            (const char *)(uintptr_t)0x70c264u,232u);
    if(offset+size>*word_at(cfg,0x1cu))
        g2_file_close_error((const char *)(uintptr_t)0x754e0cu,
                            (const char *)(uintptr_t)0x70c264u,233u);
    const uint8_t *data=(const uint8_t *)buffer;
    uint32_t cache_size=*word_at(cfg,0x28u);
    while(size) {
        if(block==*word_at(pc,0u) && offset>=*word_at(pc,4u) &&
           offset<*word_at(pc,4u)+cache_size) {
            uint32_t diff=cache_size-(offset-*word_at(pc,4u));
            if(diff>size) diff=size;
            g2_lfs_memcpy((uint8_t *)(uintptr_t)*word_at(pc,12u)+
                          offset-*word_at(pc,4u),data,diff);
            data+=diff;offset+=diff;size-=diff;
            uint32_t occupied=offset-*word_at(pc,4u);
            if(*word_at(pc,8u)<occupied) *word_at(pc,8u)=occupied;
            if(*word_at(pc,8u)==cache_size) {
                int32_t err=g2_lfs_bd_flush(filesystem,program_cache,
                                               read_cache,(uint8_t)validate);
                if(err) return err;
            }
            continue;
        }
        if(*word_at(pc,0u)!=UINT32_MAX)
            g2_file_close_error((const char *)(uintptr_t)0x754e30u,
                                (const char *)(uintptr_t)0x70c264u,262u);
        *word_at(pc,0u)=block;
        *word_at(pc,4u)=g2_lfs_aligndown(offset,*word_at(cfg,0x18u));
        *word_at(pc,8u)=0;
    }
    return 0;
}
