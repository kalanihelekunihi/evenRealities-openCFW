/* Pinned LittleFS CCRC/FCRC finalization, stock 0x4cc2f2. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t block,off,ptag,crc,begin,end;} g2_commit;
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
extern int32_t g2_lfs_bd_crc(void *,const void *,void *,uint32_t,uint32_t,
                              uint32_t,uint32_t,uint32_t *);
extern int32_t g2_lfs_bd_program(void *,void *,void *,uint32_t,uint32_t,
                                  uint32_t,const void *,uint32_t);
extern int32_t g2_lfs_bd_sync(void *,void *,void *,uint32_t);
extern int32_t g2_lfs_dir_commitattr(void *,g2_commit *,uint32_t,const void *);
static uint32_t rd32(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}
static uint32_t min(uint32_t a,uint32_t b) {return a<b?a:b;}
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
int32_t g2_lfs_dir_commitcrc(void *filesystem,g2_commit *commit) {
    uint8_t *fs=(uint8_t *)filesystem;
    uint8_t *cfg=(uint8_t *)(uintptr_t)rd32(fs,0x68u);
    uint32_t block_size=rd32(cfg,0x1cu),prog_size=rd32(cfg,0x18u);
    uint32_t unaligned=min(commit->off+20u,block_size);
    uint32_t end=(unaligned+prog_size-1u)/prog_size*prog_size;
    uint32_t off1=0u,crc1=0u;
    while(commit->off<end) {
        uint32_t noff=min(end-(commit->off+4u),0x3feu)+commit->off+4u;
        if(noff<end) noff=min(noff,end-20u);
        uint8_t eperturb=0xffu;
        if(noff>=end && noff<=block_size-prog_size) {
            int32_t err=g2_lfs_bd_read(fs,NULL,fs,prog_size,commit->block,
                                        noff,&eperturb,1u);
            if(err && err!=-84) return err;
            uint32_t fcrc[2]={prog_size,UINT32_MAX};
            err=g2_lfs_bd_crc(fs,NULL,fs,prog_size,commit->block,noff,
                               fcrc[0],&fcrc[1]);
            if(err && err!=-84) return err;
            err=g2_lfs_dir_commitattr(fs,commit,0x5ffffc08u,fcrc);
            if(err) return err;
        }
        uint32_t tag=((0x500u+((uint32_t)(uint8_t)~eperturb>>7u))<<20u)|
                      (0x3ffu<<10u)|(noff-(commit->off+4u));
        uint32_t ccrc[2];
        ccrc[0]=__builtin_bswap32(tag^commit->ptag);
        commit->crc=crc32(commit->crc,&ccrc[0],4u);
        ccrc[1]=commit->crc;
        int32_t err=g2_lfs_bd_program(fs,fs+0x10u,fs,0u,commit->block,
                                       commit->off,ccrc,8u);
        if(err) return err;
        if(off1==0u) {off1=commit->off+4u;crc1=commit->crc;}
        commit->off=noff;
        commit->ptag=tag^((uint32_t)(0x80u&~eperturb)<<24u);
        commit->crc=UINT32_MAX;
        if(noff>=end || noff>=rd32(fs+0x10u,4u)+rd32(cfg,0x28u)) {
            err=g2_lfs_bd_sync(fs,fs+0x10u,fs,0u);
            if(err) return err;
        }
    }
    uint32_t off=commit->begin,crc=UINT32_MAX;
    int32_t err=g2_lfs_bd_crc(fs,NULL,fs,off1+4u,commit->block,
                               off,off1-off,&crc);
    if(err) return err;
    if(crc!=crc1) return -84;
    err=g2_lfs_bd_crc(fs,NULL,fs,4u,commit->block,off1,4u,&crc);
    if(err) return err;
    return crc==0u ? 0 : -84;
}
