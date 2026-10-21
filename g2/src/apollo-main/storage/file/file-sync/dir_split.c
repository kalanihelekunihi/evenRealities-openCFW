/* Pinned LittleFS metadata pair split, stock 0x4cc600. */
#include <stdint.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_alloc(void *,void *);
extern int32_t g2_lfs_dir_compact(void *,void *,const struct g2_lfs_attr *,
                                   uint32_t,void *,uint32_t,uint32_t);
static int32_t overlap(const uint32_t *a,const uint32_t *b) {
    return a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0];
}
int32_t g2_lfs_dir_split(void *filesystem,void *directory,
                          const struct g2_lfs_attr *attrs,uint32_t count,
                          void *source,uint32_t split,uint32_t end) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory,tail;
    int32_t err=g2_lfs_dir_alloc(fs,&tail);
    if(err) return err;
    tail.split=dir->split;
    tail.tail[0]=dir->tail[0];tail.tail[1]=dir->tail[1];
    int32_t compact=g2_lfs_dir_compact(fs,&tail,attrs,count,source,split,end);
    if(compact<0) return compact;
    dir->tail[0]=tail.pair[0];dir->tail[1]=tail.pair[1];dir->split=1u;
    if(overlap(dir->pair,(const uint32_t *)(void *)(fs+0x20u)) && split==0u) {
        *(uint32_t *)(void *)(fs+0x20u)=tail.pair[0];
        *(uint32_t *)(void *)(fs+0x24u)=tail.pair[1];
    }
    return 0;
}
