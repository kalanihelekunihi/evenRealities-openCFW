/* Pinned lfs_fs_desuperblock, native 0x4cf648. */
#include <stdint.h>
struct attr {uint32_t tag;const void *buffer;};
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *); /* selected 0x4cbedc */
extern int32_t g2_lfs_dir_commit(void *,void *,const struct attr *,uint32_t); /* selected 0x4cd388 */
extern int32_t g2_log_transport_queue_failure(const char *,...); /* selected diagnostic */
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char debug[]="%s:%d:debug: Rewriting superblock {0x%x, 0x%x}%s\n";
static uint32_t rd32(const uint8_t *p,uint32_t off) {
    return *(const uint32_t *)(const void *)(p+off);
}
int32_t audio_file_lfs_consistency_recover(void *filesystem) {
    uint8_t *fs=(uint8_t *)filesystem;
    uint32_t state=rd32(fs,0x30u);
    if((state&0x200u)==0u) return 0;
    uint32_t *root=(uint32_t *)(void *)(fs+0x20u);
    (void)g2_log_transport_queue_failure(debug,path,4920u,root[0],root[1],"");
    uint8_t dir[32];
    int32_t err=g2_lfs_dir_fetch(filesystem,dir,root);
    if(err!=0) return err;
    uint8_t *cfg=(uint8_t *)(uintptr_t)rd32(fs,0x68u);
    uint32_t superblock[6]={0x00020001u,rd32(cfg,0x1cu),rd32(fs,0x6cu),
                            rd32(fs,0x70u),rd32(fs,0x74u),rd32(fs,0x78u)};
    struct attr entry={0x20100018u,superblock};
    err=g2_lfs_dir_commit(filesystem,dir,&entry,1u);
    if(err!=0) return err;
    *(uint32_t *)(void *)(fs+0x30u)=state&~0x200u;
    return 0;
}
