/* Small LittleFS opencfg descendants from pinned lfs.c and native
 * 0x4cad76/80/ac, 0x4cb0bc, 0x4cafea, 0x4ca80a, 0x4cf9e0. */
#include <stdint.h>
extern void *codec_allocate(uint32_t); /* selected 0x474cd2 */
extern int32_t g2_lfs_dir_getslice(void *,void *,uint32_t,uint32_t,uint32_t,
                                    void *,uint32_t); /* selected 0x4cb23a */
extern int32_t audio_file_lfs_consistency_recover(void *); /* 0x4cf648 */
extern int32_t audio_file_lfs_consistency_move(void *); /* 0x4cf6e8 */
extern int32_t g2_lfs_fs_deorphan(void *,uint32_t); /* selected 0x4cf7ac */
uint32_t audio_file_lfs_path_namelen(const char *path) {
    uint32_t n=0u;
    while(path[n]!=0 && path[n]!='/') n++;
    return n;
}
int32_t audio_file_lfs_path_islast(const char *path) {
    path+=audio_file_lfs_path_namelen(path);
    while(*path=='/') path++;
    return *path==0;
}
int32_t audio_file_lfs_path_isdir(const char *path) {
    return path[audio_file_lfs_path_namelen(path)]!=0;
}
void audio_file_lfs_mlist_append(void *filesystem,void *file) {
    uint32_t *head=(uint32_t *)(void *)((uint8_t *)filesystem+0x28u);
    *(uint32_t *)file=*head;
    *head=(uint32_t)(uintptr_t)file;
}
void audio_file_lfs_ctz_fromle32(void *ctz) {
    uint8_t *p=(uint8_t *)ctz;
    for(uint32_t i=0u;i<2u;i++) {
        uint8_t *b=p+i*4u;
        uint32_t value=(uint32_t)b[0]|((uint32_t)b[1]<<8u)|
                       ((uint32_t)b[2]<<16u)|((uint32_t)b[3]<<24u);
        *(uint32_t *)(void *)b=value;
    }
}
void *audio_file_lfs_malloc(uint32_t bytes) {
    return codec_allocate(bytes);
}
int32_t audio_file_lfs_dir_get(void *filesystem,void *directory,
                                uint32_t mask,uint32_t tag,void *buffer) {
    return g2_lfs_dir_getslice(filesystem,directory,mask,tag,0u,
                               buffer,tag&0x3ffu);
}
int32_t audio_file_lfs_forceconsistency(void *filesystem) {
    int32_t err=audio_file_lfs_consistency_recover(filesystem);
    if(err!=0) return err;
    err=audio_file_lfs_consistency_move(filesystem);
    if(err!=0) return err;
    return g2_lfs_fs_deorphan(filesystem,1u);
}
