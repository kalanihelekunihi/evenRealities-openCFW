/* Pinned LittleFS reachable-block count, stock 0x4cfa12. */
#include <stdint.h>
extern int32_t g2_lfs_fs_traverse(void *,int32_t (*)(void *,uint32_t),
                                   void *,uint32_t);
static int32_t count_block(void *context,uint32_t block) {
    (void)block;
    (*(uint32_t *)context)++;
    return 0;
}
int32_t g2_lfs_fs_size(void *filesystem) {
    uint32_t size=0u;
    int32_t err=g2_lfs_fs_traverse(filesystem,count_block,&size,0u);
    if(err) return err;
    return (int32_t)size;
}
