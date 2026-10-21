/* Pinned LittleFS directory parent search, stock 0x4cf4da. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
typedef struct {void *filesystem;uint32_t pair[2];} g2_parent_match;
extern int32_t g2_lfs_tortoise_detectcycles(void *,void *);
extern int32_t g2_lfs_dir_fetchmatch(void *,void *,const uint32_t *,uint32_t,
                                      uint32_t,uint16_t *,
                                      int32_t (*)(void *,uint32_t,const void *),void *);
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
static uint32_t rd32(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}
static int32_t overlap(const uint32_t *a,const uint32_t *b) {
    return a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0];
}
static int32_t parent_match(void *context,uint32_t tag,const void *diskoff) {
    (void)tag;
    g2_parent_match *find=(g2_parent_match *)context;
    void *fs=find->filesystem;
    const uint32_t *disk=(const uint32_t *)diskoff;
    uint32_t *cfg=(uint32_t *)(uintptr_t)rd32(fs,0x68u);
    uint32_t child[2];
    int32_t err=g2_lfs_bd_read(fs,(uint8_t *)fs+0x10u,fs,cfg[7],
                                disk[0],disk[1],child,8u);
    if(err) return err;
    return overlap(child,find->pair) ? 0 : 1;
}
int32_t g2_lfs_fs_parent(void *filesystem,const uint32_t *pair,void *output) {
    g2_mdir *parent=(g2_mdir *)output;
    parent->tail[0]=0u;parent->tail[1]=1u;
    uint32_t tortoise[4]={UINT32_MAX,UINT32_MAX,1u,1u};
    while(parent->tail[0]!=UINT32_MAX && parent->tail[1]!=UINT32_MAX) {
        int32_t err=g2_lfs_tortoise_detectcycles(parent,tortoise);
        if(err<0) return err;
        g2_parent_match match={filesystem,{pair[0],pair[1]}};
        int32_t tag=g2_lfs_dir_fetchmatch(filesystem,parent,parent->tail,
                                           0x7ff003ffu,0x20000008u,NULL,
                                           parent_match,&match);
        if(tag!=0 && tag!=-2) return tag;
    }
    return -2;
}
