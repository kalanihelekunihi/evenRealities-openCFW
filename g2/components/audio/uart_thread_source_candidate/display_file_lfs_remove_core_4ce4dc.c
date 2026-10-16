/* Stock Main 0x4ce4dc, traced to pinned littlefs lfs_remove_.
 * The 32-bit directory/list layout and helper calls follow the original
 * Apollo image. This source is a candidate until its native oracle passes. */
#include <stdint.h>

struct lfs_mdir32 {
    uint32_t pair[2], rev, off, etag;
    uint16_t count;
    uint8_t erased, split;
    uint32_t tail[2];
};
struct lfs_mlist32 {
    uint32_t next;
    uint16_t id;
    uint8_t type, pad;
    struct lfs_mdir32 m;
};
struct lfs_attr32 {uint32_t tag; const void *buffer;};

extern int32_t audio_file_lfs_forceconsistency(void *); /* 0x4cf9e0 */
extern int32_t audio_file_lfs_dir_find(void *,void *,const char **,uint16_t *); /* 0x4cc04a */
extern int32_t audio_file_lfs_dir_get(void *,void *,uint32_t,uint32_t,void *); /* 0x4cb3c8 */
extern void audio_file_lfs_ctz_fromle32(void *); /* 0x4cae3e/0x4cafea */
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *); /* 0x4cbedc */
extern int32_t g2_lfs_fs_preporphans(void *,int8_t); /* 0x4cf570 */
extern int32_t g2_lfs_dir_commit(void *,void *,const struct lfs_attr32 *,uint32_t); /* 0x4cd388 */
extern int32_t g2_lfs_fs_pred(void *,const uint32_t *,void *); /* 0x4cf40a */
extern int32_t audio_file_lfs_dir_drop_4cc5a2(void *,void *,void *);

static uint32_t tag_id(uint32_t tag) {return (tag>>10u)&0x3ffu;}
static uint32_t tag_type3(uint32_t tag) {return (tag>>20u)&0x7ffu;}
static uint32_t read_mlist(const void *filesystem) {
    return *(const uint32_t *)(const void *)((const uint8_t *)filesystem+0x28u);
}
static void write_mlist(void *filesystem,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)filesystem+0x28u)=value;
}

int32_t audio_file_lfs_remove_core_4ce4dc(void *filesystem,const char *path,uint32_t option) {
    (void)option; /* the stock public wrapper passes zero */
    int32_t err=audio_file_lfs_forceconsistency(filesystem);
    if(err!=0) return err;

    struct lfs_mdir32 cwd;
    int32_t found=audio_file_lfs_dir_find(filesystem,&cwd,&path,0);
    if(found<0 || tag_id((uint32_t)found)==0x3ffu)
        return found<0 ? found : -22;

    struct lfs_mlist32 dir;
    dir.next=read_mlist(filesystem);
    if(tag_type3((uint32_t)found)==2u) {
        uint32_t pair[2];
        int32_t result=audio_file_lfs_dir_get(filesystem,&cwd,0x700ffc00u,
                0x20000008u|(tag_id((uint32_t)found)<<10u),pair);
        if(result<0) return result;
        audio_file_lfs_ctz_fromle32(pair);
        err=g2_lfs_dir_fetch(filesystem,&dir.m,pair);
        if(err!=0) return err;
        if(dir.m.count>0u || dir.m.split!=0u) return -39;
        err=g2_lfs_fs_preporphans(filesystem,1);
        if(err!=0) return err;
        dir.type=0;
        dir.id=0;
        write_mlist(filesystem,(uint32_t)(uintptr_t)&dir);
    }

    struct lfs_attr32 deleted={0x4ff00000u|(tag_id((uint32_t)found)<<10u),0};
    err=g2_lfs_dir_commit(filesystem,&cwd,&deleted,1u);
    write_mlist(filesystem,dir.next);
    if(err!=0) return err;

    if(tag_type3((uint32_t)found)==2u) {
        err=g2_lfs_fs_preporphans(filesystem,-1);
        if(err!=0) return err;
        err=g2_lfs_fs_pred(filesystem,dir.m.pair,&cwd);
        if(err!=0) return err;
        err=audio_file_lfs_dir_drop_4cc5a2(filesystem,&cwd,&dir.m);
        if(err!=0) return err;
    }
    return 0;
}
