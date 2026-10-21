/* Littlefs file close worker, stock 0x4cdce4; pinned upstream lfs.c. */
#include <stdint.h>
extern int32_t g2_lfs_file_sync(void *filesystem,void *file); /* 0x4cdf74 */
extern void g2_lfs_mlist_remove(void *filesystem,void *file); /* 0x4cb0a0 */
extern void g2_lfs_free(void *buffer); /* 0x4ca812 */
int32_t g2_lfs_file_close(void *filesystem,void *file) {
    int32_t result=g2_lfs_file_sync(filesystem,file);
    g2_lfs_mlist_remove(filesystem,file);
    void *configuration=*(void **)((uint8_t *)file+0x50u);
    if(*(void **)configuration==0)
        g2_lfs_free(*(void **)((uint8_t *)file+0x4cu));
    return result;
}
