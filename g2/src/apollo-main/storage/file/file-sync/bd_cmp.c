/* Pinned LittleFS block comparison, stock 0x4caa04. */
#include <stdint.h>
extern int32_t g2_lfs_bd_read(void *filesystem,const void *program_cache,
                              void *read_cache,uint32_t hint,uint32_t block,
                              uint32_t offset,void *buffer,uint32_t size);
extern int32_t g2_lfs_memcmp(const void *a,const void *b,uint32_t size);
int32_t g2_lfs_bd_cmp(void *filesystem,void *program_cache,void *read_cache,
                       uint32_t hint,uint32_t block,uint32_t offset,
                       const void *buffer,uint32_t size) {
    const uint8_t *bytes=(const uint8_t *)buffer;
    uint32_t index=0;
    while(index<size) {
        uint8_t data[8];
        uint32_t diff=size-index;
        if(diff>sizeof(data)) diff=sizeof(data);
        int32_t err=g2_lfs_bd_read(filesystem,program_cache,read_cache,
                                    hint-index,block,offset+index,data,diff);
        if(err) return err;
        int32_t cmp=g2_lfs_memcmp(data,bytes+index,diff);
        if(cmp) return cmp<0 ? 1 : 2;
        index+=diff;
    }
    return 0;
}
