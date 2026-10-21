/* Pinned LittleFS directory commit wrapper, stock 0x4cd388. */
#include <stdint.h>
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_orphaningcommit(void *filesystem,void *directory,
                                          const struct g2_lfs_attr *attrs,
                                          uint32_t count);
extern int32_t g2_lfs_fs_deorphan(void *filesystem,uint32_t powerloss);
int32_t g2_lfs_dir_commit(void *filesystem,void *directory,
                           const struct g2_lfs_attr *attrs,uint32_t count) {
    int32_t orphans=g2_lfs_dir_orphaningcommit(filesystem,directory,attrs,count);
    if(orphans<0) return orphans;
    if(orphans!=0) {
        int32_t err=g2_lfs_fs_deorphan(filesystem,0u);
        if(err) return err;
    }
    return 0;
}
