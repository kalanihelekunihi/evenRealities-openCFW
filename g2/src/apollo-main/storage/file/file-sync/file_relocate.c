/* Pinned LittleFS file relocation, stock 0x4cdd0e. */
#include <stdint.h>
extern int32_t g2_lfs_alloc(void *filesystem,uint32_t *block);
extern int32_t g2_lfs_bd_erase(void *filesystem,uint32_t block);
extern int32_t g2_lfs_dir_getread(void *fs,void *directory,
                                   const void *pcache,void *rcache,
                                   uint32_t hint,uint32_t tagmask,
                                   uint32_t tag,uint32_t offset,
                                   void *buffer,uint32_t size);
extern int32_t g2_lfs_bd_read(void *fs,const void *pcache,void *rcache,
                               uint32_t hint,uint32_t block,uint32_t offset,
                               void *buffer,uint32_t size);
extern int32_t g2_lfs_bd_program(void *filesystem,void *program_cache,
                                  void *read_cache,uint32_t validate,
                                  uint32_t block,uint32_t offset,
                                  const void *buffer,uint32_t size);
extern void g2_lfs_memcpy(void *destination,const void *source,uint32_t count);
extern void g2_lfs_cache_zero(void *filesystem,void *cache);
extern int32_t g2_lfs_cache_drop(void *filesystem,void *cache);
extern void g2_lfs_debug_bad_block(uint32_t block,uint32_t line);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_file_relocate(void *filesystem,void *file) {
    uint8_t *fs=(uint8_t *)filesystem,*f=(uint8_t *)file;
    for(;;) {
        uint32_t new_block;
        int32_t err=g2_lfs_alloc(filesystem,&new_block);
        if(err) return err;
        err=g2_lfs_bd_erase(filesystem,new_block);
        if(err) {
            if(err==-84) goto relocate;
            return err;
        }
        for(uint32_t i=0;i<*word_at(file,0x3cu);i++) {
            uint8_t data;
            if(*word_at(file,0x30u)&0x100000u) {
                uint16_t id=*(uint16_t *)(void *)(f+4u);
                err=g2_lfs_dir_getread(filesystem,f+8u,0,f+0x40u,
                     *word_at(file,0x3cu)-i,0xfff7fc00u,
                     0x20100000u|((uint32_t)id<<10),i,&data,1u);
            } else {
                err=g2_lfs_bd_read(filesystem,f+0x40u,filesystem,
                     *word_at(file,0x3cu)-i,*word_at(file,0x38u),i,&data,1u);
            }
            if(err) return err;
            err=g2_lfs_bd_program(filesystem,fs+0x10u,filesystem,1u,
                                    new_block,i,&data,1u);
            if(err) {
                if(err==-84) goto relocate;
                return err;
            }
        }
        uint8_t *cfg=*(uint8_t **)(void *)(fs+0x68u);
        g2_lfs_memcpy((void *)(uintptr_t)*word_at(file,0x4cu),
                      (const void *)(uintptr_t)*word_at(fs,0x1cu),
                      *word_at(cfg,0x28u));
        for(uint32_t i=0;i<3u;i++) *word_at(file,0x40u+i*4u)=*word_at(fs,0x10u+i*4u);
        g2_lfs_cache_zero(filesystem,fs+0x10u);
        *word_at(file,0x38u)=new_block;
        *word_at(file,0x30u)|=0x20000u;
        return 0;
relocate:
        g2_lfs_debug_bad_block(new_block,3329u);
        (void)g2_lfs_cache_drop(filesystem,fs+0x10u);
    }
}
