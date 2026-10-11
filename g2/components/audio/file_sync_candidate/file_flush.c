/* Pinned LittleFS file_flush state machine, stock 0x4cde54. */
#include <stdint.h>
extern int32_t g2_lfs_cache_drop(void *filesystem,void *cache);
extern int32_t g2_lfs_bd_flush(void *filesystem,void *program_cache,
                                void *read_cache,uint32_t validate);
extern int32_t g2_lfs_file_flushedread(void *filesystem,void *file,
                                        void *buffer,uint32_t size);
extern int32_t g2_lfs_file_flushedwrite(void *filesystem,void *file,
                                         const void *buffer,uint32_t size);
extern int32_t g2_lfs_file_relocate(void *filesystem,void *file);
extern void g2_lfs_debug_bad_block(uint32_t block,uint32_t line);
static uint32_t *word_at(void *base,uint32_t offset) {
    return (uint32_t *)((uint8_t *)base+offset);
}
int32_t g2_lfs_file_flush(void *filesystem,void *file) {
    uint32_t *flags=word_at(file,0x30u);
    if(*flags&0x40000u) {
        if((*flags&0x100000u)==0u)
            (void)g2_lfs_cache_drop(filesystem,(uint8_t *)file+0x40u);
        *flags&=~0x40000u;
    }
    if(*flags&0x20000u) {
        uint32_t pos=*word_at(file,0x34u);
        if((*flags&0x100000u)==0u) {
            uint32_t original[21];
            volatile uint32_t *initialize=original;
            for(uint32_t i=0;i<21u;i++) initialize[i]=0u;
            original[10]=*word_at(file,0x28u);
            original[11]=*word_at(file,0x2cu);
            original[12]=1u; /* LFS_O_RDONLY in the authenticated template. */
            original[13]=*word_at(file,0x34u);
            for(uint32_t i=0;i<4u;i++) original[16u+i]=*word_at(filesystem,i*4u);
            (void)g2_lfs_cache_drop(filesystem,filesystem);
            while(*word_at(file,0x34u)<*word_at(file,0x2cu)) {
                uint8_t data;
                int32_t result=g2_lfs_file_flushedread(filesystem,original,&data,1u);
                if(result<0) return result;
                result=g2_lfs_file_flushedwrite(filesystem,file,&data,1u);
                if(result<0) return result;
                if(*word_at(filesystem,0u)!=UINT32_MAX) {
                    (void)g2_lfs_cache_drop(filesystem,&original[16]);
                    (void)g2_lfs_cache_drop(filesystem,filesystem);
                }
            }
            for(;;) {
                int32_t err=g2_lfs_bd_flush(filesystem,(uint8_t *)file+0x40u,
                                               filesystem,1u);
                if(err==0) break;
                if(err!=-84) return err;
                g2_lfs_debug_bad_block(*word_at(file,0x38u),3408u);
                err=g2_lfs_file_relocate(filesystem,file);
                if(err) return err;
            }
        } else {
            uint32_t size=*word_at(file,0x2cu);
            if(*word_at(file,0x34u)<size) *word_at(file,0x34u)=size;
        }
        *word_at(file,0x28u)=*word_at(file,0x38u);
        *word_at(file,0x2cu)=*word_at(file,0x34u);
        *flags=(*flags&~0x20000u)|0x10000u;
        *word_at(file,0x34u)=pos;
    }
    return 0;
}
