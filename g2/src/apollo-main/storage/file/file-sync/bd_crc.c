/* Pinned LittleFS chunked block CRC, stock 0x4caa88. */
#include <stdint.h>
#include <stddef.h>
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
static uint32_t crc32(uint32_t crc,const void *buffer,uint32_t size) {
    static const uint32_t tab[16]={0,0x1db71064,0x3b6e20c8,0x26d930ac,
        0x76dc4190,0x6b6b51f4,0x4db26158,0x5005713c,
        0xedb88320,0xf00f9344,0xd6d6a3e8,0xcb61b38c,
        0x9b64c2b0,0x86d3d2d4,0xa00ae278,0xbdbdf21c};
    const uint8_t *p=(const uint8_t *)buffer;
    for(uint32_t i=0;i<size;i++) {
        crc=(crc>>4u)^tab[(crc^p[i])&15u];
        crc=(crc>>4u)^tab[(crc^(p[i]>>4u))&15u];
    }
    return crc;
}
int32_t g2_lfs_bd_crc(void *filesystem,const void *program_cache,
                       void *read_cache,uint32_t hint,uint32_t block,
                       uint32_t offset,uint32_t size,uint32_t *crc) {
    for(uint32_t index=0;index<size;) {
        uint8_t data[8];
        uint32_t diff=size-index;
        if(diff>8u) diff=8u;
        int32_t err=g2_lfs_bd_read(filesystem,program_cache,read_cache,
                                    hint-index,block,offset+index,data,diff);
        if(err) return err;
        *crc=crc32(*crc,data,diff);
        index+=diff;
    }
    return 0;
}
