/* Pinned LittleFS metadata pair allocation, stock 0x4cc502. */
#include <stdint.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
extern int32_t g2_lfs_alloc(void *,uint32_t *);
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
static uint32_t rd32(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}
int32_t g2_lfs_dir_alloc(void *filesystem,void *directory) {
    g2_mdir *dir=(g2_mdir *)directory;
    for(uint32_t i=0;i<2u;i++) {
        int32_t err=g2_lfs_alloc(filesystem,&dir->pair[(i+1u)&1u]);
        if(err) return err;
    }
    dir->rev=0u;
    int32_t err=g2_lfs_bd_read(filesystem,0,filesystem,4u,
                                dir->pair[0],0u,&dir->rev,4u);
    if(err && err!=-84) return err;
    uint8_t *cfg=(uint8_t *)(uintptr_t)rd32(filesystem,0x68u);
    int32_t cycles=(int32_t)rd32(cfg,0x24u);
    if(cycles>0) {
        uint32_t alignment=((uint32_t)cycles+1u)|1u;
        dir->rev=(dir->rev+alignment-1u)/alignment*alignment;
    }
    dir->off=4u;dir->etag=UINT32_MAX;dir->count=0u;
    dir->tail[0]=UINT32_MAX;dir->tail[1]=UINT32_MAX;
    dir->erased=0u;dir->split=0u;
    return 0;
}
