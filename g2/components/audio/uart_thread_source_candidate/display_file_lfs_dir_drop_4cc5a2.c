/* Stock Main 0x4cc5a2, pinned LittleFS lfs_dir_drop. */
#include <stdint.h>

struct lfs_attr32 {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_getgstate(void *,void *,void *); /* 0x4cbefc */
extern int32_t g2_lfs_dir_commit(void *,void *,const struct lfs_attr32 *,uint32_t); /* 0x4cd388 */

int32_t audio_file_lfs_dir_drop_4cc5a2(void *filesystem,void *directory,void *tail) {
    uint8_t *t=(uint8_t *)tail;
    int32_t err=g2_lfs_dir_getgstate(filesystem,tail,(uint8_t *)filesystem+0x48u);
    if(err!=0) return err;
    /* Pair conversion is identity on the stock little-endian Cortex-M image. */
    uint32_t type=0x600u+(uint32_t)t[23u];
    struct lfs_attr32 attr={(type<<20u)|0x000ffc08u,t+24u};
    return g2_lfs_dir_commit(filesystem,directory,&attr,1u);
}
