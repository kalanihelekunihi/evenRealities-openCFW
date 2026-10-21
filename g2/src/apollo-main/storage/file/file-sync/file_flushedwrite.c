/* Pinned LittleFS flushedwrite worker, stock 0x4ce1a0. */
#include <stdint.h>
extern int32_t g2_lfs_file_outline(void *filesystem,void *file);
extern int32_t g2_lfs_ctz_find(void *filesystem,const void *pcache,void *rcache,
                                uint32_t head,uint32_t size,uint32_t position,
                                uint32_t *block,uint32_t *offset);
extern void g2_lfs_cache_zero(void *filesystem,void *cache);
extern void g2_lfs_alloc_checkpoint(void *filesystem);
extern int32_t g2_lfs_ctz_extend(void *filesystem,void *program_cache,
                                  void *read_cache,uint32_t block,
                                  uint32_t position,uint32_t *new_block,
                                  uint32_t *new_offset);
extern int32_t g2_lfs_bd_program(void *filesystem,void *program_cache,
                                  void *read_cache,uint32_t validate,
                                  uint32_t block,uint32_t offset,
                                  const void *buffer,uint32_t size);
extern int32_t g2_lfs_file_relocate(void *filesystem,void *file);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_file_flushedwrite(void *filesystem,void *file,
                                  const void *buffer,uint32_t size) {
    uint8_t *fs=(uint8_t *)filesystem,*f=(uint8_t *)file;
    uint32_t *flags=word_at(file,0x30u),remaining=size;
    const uint8_t *data=(const uint8_t *)buffer;
    if((*flags&0x100000u) &&
       ((*word_at(file,0x34u)+remaining>*word_at(file,0x2cu) ?
         *word_at(file,0x34u)+remaining:*word_at(file,0x2cu))>
        *word_at(filesystem,0x7cu))) {
        int32_t err=g2_lfs_file_outline(filesystem,file);
        if(err) {*flags|=0x80000u;return err;}
    }
    uint8_t *cfg=*(uint8_t **)(void *)(fs+0x68u);
    uint32_t block_size=*word_at(cfg,0x1cu);
    while(remaining) {
        if((*flags&0x20000u)==0u || *word_at(file,0x3cu)==block_size) {
            if((*flags&0x100000u)==0u) {
                if((*flags&0x20000u)==0u && *word_at(file,0x34u)>0u) {
                    uint32_t ignored_offset=0;
                    int32_t err=g2_lfs_ctz_find(filesystem,0,f+0x40u,
                         *word_at(file,0x28u),*word_at(file,0x2cu),
                         *word_at(file,0x34u)-1u,word_at(file,0x38u),
                         &ignored_offset);
                    if(err) {*flags|=0x80000u;return err;}
                    g2_lfs_cache_zero(filesystem,f+0x40u);
                }
                g2_lfs_alloc_checkpoint(filesystem);
                int32_t err=g2_lfs_ctz_extend(filesystem,f+0x40u,filesystem,
                         *word_at(file,0x38u),*word_at(file,0x34u),
                         word_at(file,0x38u),word_at(file,0x3cu));
                if(err) {*flags|=0x80000u;return err;}
            } else {
                *word_at(file,0x38u)=UINT32_MAX-1u;
                *word_at(file,0x3cu)=*word_at(file,0x34u);
            }
            *flags|=0x20000u;
        }
        uint32_t diff=block_size-*word_at(file,0x3cu);
        if(diff>remaining) diff=remaining;
        for(;;) {
            int32_t err=g2_lfs_bd_program(filesystem,f+0x40u,filesystem,1u,
                           *word_at(file,0x38u),*word_at(file,0x3cu),data,diff);
            if(err==0) break;
            if(err!=-84) {*flags|=0x80000u;return err;}
            err=g2_lfs_file_relocate(filesystem,file);
            if(err) {*flags|=0x80000u;return err;}
        }
        *word_at(file,0x34u)+=diff;
        *word_at(file,0x3cu)+=diff;
        data+=diff;remaining-=diff;
        g2_lfs_alloc_checkpoint(filesystem);
    }
    return (int32_t)size;
}
