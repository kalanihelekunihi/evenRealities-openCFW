/* LittleFS file sync worker, stock 0x4cdf74, pinned upstream lfs.c. */
#include <stdint.h>
#include <stddef.h>
extern int32_t g2_lfs_file_flush(void *filesystem,void *file); /* 0x4cde54 */
extern int32_t g2_lfs_pair_isnull(const void *pair);          /* 0x4cadd0 */
extern int32_t g2_lfs_bd_sync(void *filesystem,void *pcache,
                               void *rcache,uint32_t validate); /* 0x4cabbc */
extern void g2_lfs_ctz_tole32(void *ctz);                     /* 0x4cb000 */
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_commit(void *filesystem,void *mdir,
                                  const struct g2_lfs_attr *,uint32_t count);
int32_t g2_lfs_file_sync(void *filesystem,void *file) {
    uint8_t *f=(uint8_t *)file;
    uint32_t *flags=(uint32_t *)(void *)(f+0x30u);
    if(*flags&0x80000u) return 0;
    int32_t err=g2_lfs_file_flush(filesystem,file);
    if(err) {*flags|=0x80000u;return err;}
    if((*flags&0x10000u)==0u || g2_lfs_pair_isnull(f+8u)!=0) return 0;
    const uint32_t inline_file=(*flags&0x100000u)!=0u;
    if(!inline_file) {
        err=g2_lfs_bd_sync(filesystem,(uint8_t *)filesystem+0x10u,
                            filesystem,0u);
        if(err) return err;
    }
    uint32_t ctz[2];
    uint16_t id=*(uint16_t *)(void *)(f+4u);
    struct g2_lfs_attr attrs[2];
    if(inline_file) {
        attrs[0].tag=(0x201u<<20)|((uint32_t)id<<10)|
                     *(uint32_t *)(void *)(f+0x2cu);
        attrs[0].buffer=*(void **)(void *)(f+0x4cu);
    } else {
        ctz[0]=*(uint32_t *)(void *)(f+0x28u);
        ctz[1]=*(uint32_t *)(void *)(f+0x2cu);
        g2_lfs_ctz_tole32(ctz);
        attrs[0].tag=(0x202u<<20)|((uint32_t)id<<10)|8u;
        attrs[0].buffer=ctz;
    }
    uint8_t *cfg=*(uint8_t **)(void *)(f+0x50u);
    attrs[1].tag=0x10200000u|((uint32_t)id<<10)|
                 *(uint32_t *)(void *)(cfg+8u);
    attrs[1].buffer=*(void **)(void *)(cfg+4u);
    err=g2_lfs_dir_commit(filesystem,f+8u,attrs,2u);
    if(err) {*flags|=0x80000u;return err;}
    *flags&=~0x10000u;
    return 0;
}
