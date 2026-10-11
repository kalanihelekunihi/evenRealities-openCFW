/* Pinned lfs_fs_demove, native 0x4cf6e8. */
#include <stdint.h>
struct attr {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *); /* selected 0x4cbedc */
extern void g2_lfs_fs_prepmove(void *,uint32_t,const uint32_t *); /* selected 0x4cf5ec */
extern int32_t g2_lfs_dir_commit(void *,void *,const struct attr *,uint32_t); /* selected 0x4cd388 */
extern int32_t g2_log_transport_queue_failure(const char *,...); /* selected diagnostic */
extern void g2_file_close_error(const char *,const char *,uint32_t); /* selected assertion */
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char debug[]="%s:%d:debug: Fixing move {0x%x, 0x%x} 0x%hx%s\n";
static const char assertion[]="lfs_tag_type3(lfs->gdisk.tag) == LFS_TYPE_DELETE";
int32_t audio_file_lfs_consistency_move(void *filesystem) {
    uint8_t *fs=(uint8_t *)filesystem;
    uint32_t tag=*(uint32_t *)(void *)(fs+0x3cu);
    if(((tag>>20u)&0x700u)==0u) return 0;
    uint32_t *pair=(uint32_t *)(void *)(fs+0x40u);
    uint16_t id=(uint16_t)((tag>>10u)&0x3ffu);
    (void)g2_log_transport_queue_failure(debug,path,4961u,pair[0],pair[1],id,"");
    if(((tag>>20u)&0x7ffu)!=0x4ffu)
        g2_file_close_error(assertion,path,4965u);
    uint8_t dir[32];
    int32_t err=g2_lfs_dir_fetch(filesystem,dir,pair);
    if(err!=0) return err;
    g2_lfs_fs_prepmove(filesystem,0x3ffu,0);
    struct attr deleted={0x4ff00000u|((uint32_t)id<<10u),0};
    return g2_lfs_dir_commit(filesystem,dir,&deleted,1u);
}
