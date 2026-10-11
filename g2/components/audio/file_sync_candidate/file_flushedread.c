/* Pinned LittleFS flushedread worker, stock 0x4ce042. */
#include <stdint.h>
extern int32_t g2_lfs_ctz_find(void *fs,const void *pcache,void *rcache,
                                uint32_t head,uint32_t size,uint32_t position,
                                uint32_t *block,uint32_t *offset);
extern int32_t g2_lfs_dir_getread(void *fs,void *directory,
                                   const void *pcache,void *rcache,
                                   uint32_t hint,uint32_t tagmask,
                                   uint32_t tag,uint32_t offset,
                                   void *buffer,uint32_t size);
extern int32_t g2_lfs_bd_read(void *fs,const void *pcache,void *rcache,
                               uint32_t hint,uint32_t block,uint32_t offset,
                               void *buffer,uint32_t size);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_file_flushedread(void *filesystem,void *file,
                                 void *buffer,uint32_t size) {
    uint32_t *position=word_at(file,0x34u);
    uint32_t file_size=*word_at(file,0x2cu);
    if(*position>=file_size) return 0;
    uint32_t remaining=file_size-*position;
    if(size<remaining) remaining=size;
    uint32_t total=remaining;
    uint8_t *data=(uint8_t *)buffer;
    uint32_t block_size=*word_at(*(void **)((uint8_t *)filesystem+0x68u),0x1cu);
    while(remaining) {
        uint32_t *flags=word_at(file,0x30u);
        if((*flags&0x40000u)==0u || *word_at(file,0x3cu)==block_size) {
            if((*flags&0x100000u)==0u) {
                int32_t err=g2_lfs_ctz_find(filesystem,0,(uint8_t *)file+0x40u,
                      *word_at(file,0x28u),file_size,*position,
                      word_at(file,0x38u),word_at(file,0x3cu));
                if(err) return err;
            } else {
                *word_at(file,0x38u)=UINT32_MAX-1u;
                *word_at(file,0x3cu)=*position;
            }
            *flags|=0x40000u;
        }
        uint32_t diff=block_size-*word_at(file,0x3cu);
        if(diff>remaining) diff=remaining;
        int32_t err;
        if(*flags&0x100000u) {
            uint16_t id=*(uint16_t *)((uint8_t *)file+4u);
            err=g2_lfs_dir_getread(filesystem,(uint8_t *)file+8u,0,
                  (uint8_t *)file+0x40u,block_size,0xfff7fc00u,
                  0x20100000u|((uint32_t)id<<10),*word_at(file,0x3cu),
                  data,diff);
        } else {
            err=g2_lfs_bd_read(filesystem,0,(uint8_t *)file+0x40u,
                 block_size,*word_at(file,0x38u),*word_at(file,0x3cu),data,diff);
        }
        if(err) return err;
        *position+=diff;
        *word_at(file,0x3cu)+=diff;
        data+=diff;
        remaining-=diff;
    }
    return (int32_t)total;
}
