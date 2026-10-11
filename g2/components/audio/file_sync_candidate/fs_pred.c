/* Pinned LittleFS directory predecessor search, stock 0x4cf40a. */
#include <stdint.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
extern int32_t g2_lfs_tortoise_detectcycles(void *,void *);
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *);
static int32_t overlap(const uint32_t *a,const uint32_t *b) {
    return a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0];
}
int32_t g2_lfs_fs_pred(void *filesystem,const uint32_t *pair,void *output) {
    g2_mdir *pdir=(g2_mdir *)output;
    pdir->tail[0]=0u;pdir->tail[1]=1u;
    uint32_t tortoise[4]={UINT32_MAX,UINT32_MAX,1u,1u};
    while(pdir->tail[0]!=UINT32_MAX && pdir->tail[1]!=UINT32_MAX) {
        if(g2_lfs_tortoise_detectcycles(pdir,tortoise)<0) return -84;
        if(overlap(pdir->tail,pair)) return 0;
        int32_t err=g2_lfs_dir_fetch(filesystem,pdir,pdir->tail);
        if(err) return err;
    }
    return -2;
}
