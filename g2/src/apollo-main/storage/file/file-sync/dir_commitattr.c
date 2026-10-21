/* Pinned LittleFS directory commitprog/commitattr, stock 0x4cc200/0x4cc23c. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t block,off,ptag,crc,begin,end;} g2_commit;
extern int32_t g2_lfs_bd_program(void *,void *,void *,uint32_t,uint32_t,
                                  uint32_t,const void *,uint32_t);
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
int32_t g2_lfs_dir_commitprog(void *filesystem,g2_commit *commit,
                               const void *buffer,uint32_t size) {
    int32_t err=g2_lfs_bd_program(filesystem,(uint8_t *)filesystem+0x10u,
                                   filesystem,0u,commit->block,commit->off,
                                   buffer,size);
    if(err) return err;
    commit->crc=crc32(commit->crc,buffer,size);
    commit->off+=size;
    return 0;
}
int32_t g2_lfs_dir_commitattr(void *filesystem,g2_commit *commit,
                               uint32_t tag,const void *buffer) {
    uint32_t size=tag&0x3ffu;
    uint32_t dsize=4u+((size==0x3ffu) ? 0u : size);
    if(commit->off+dsize>commit->end) return -28;
    uint32_t encoded=__builtin_bswap32((tag&0x7fffffffu)^commit->ptag);
    int32_t err=g2_lfs_dir_commitprog(filesystem,commit,&encoded,4u);
    if(err) return err;
    if((tag&0x80000000u)==0u) {
        err=g2_lfs_dir_commitprog(filesystem,commit,buffer,dsize-4u);
        if(err) return err;
    } else {
        const uint32_t *disk=(const uint32_t *)buffer;
        for(uint32_t i=0;i<dsize-4u;i++) {
            uint8_t value;
            err=g2_lfs_bd_read(filesystem,NULL,filesystem,dsize-4u-i,
                                disk[0],disk[1]+i,&value,1u);
            if(err) return err;
            err=g2_lfs_dir_commitprog(filesystem,commit,&value,1u);
            if(err) return err;
        }
    }
    commit->ptag=tag&0x7fffffffu;
    return 0;
}
