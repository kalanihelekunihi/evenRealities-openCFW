/* Native LittleFS public wrappers 0x4cfa94/0x4cfb40/0x4cfbb2/0x4cfbe8;
 * membership checks and diagnostics follow the pinned lfs.c ABI. */
#include <stdint.h>
extern int32_t g2_lfs_mlist_isopen(void *,void *); /* selected 0x4cb082 */
extern void g2_file_close_error(const char *,const char *,uint32_t); /* 0x4d09b4 */
int32_t audio_file_lfs_open_core(void *,void *,const char *,uint32_t); /* 0x4cdcc8 */
int32_t audio_file_lfs_read_core(void *,void *,void *,uint32_t); /* 0x4ce158 */
int32_t audio_file_lfs_seek_core(void *,void *,int32_t,uint32_t); /* 0x4ce3bc */
int32_t audio_file_lfs_tell_core(void *,void *); /* 0x4ce45c */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char must_be_open[]="lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)file)";
static const char must_be_closed[]="!lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)file)";
static void *list(void *filesystem) {
    return *(void **)(void *)((uint8_t *)filesystem+0x28u);
}
int32_t audio_file_lfs_open(void *filesystem,void *file,const char *path,uint32_t flags) {
    if(g2_lfs_mlist_isopen(list(filesystem),file)!=0)
        g2_file_close_error(must_be_closed,source,0x17e7u);
    return audio_file_lfs_open_core(filesystem,file,path,flags);
}
int32_t audio_file_lfs_read(void *filesystem,void *file,void *buffer,uint32_t size) {
    if(g2_lfs_mlist_isopen(list(filesystem),file)==0)
        g2_file_close_error(must_be_open,source,0x182du);
    return audio_file_lfs_read_core(filesystem,file,buffer,size);
}
int32_t audio_file_lfs_seek(void *filesystem,void *file,int32_t offset,uint32_t whence) {
    if(g2_lfs_mlist_isopen(list(filesystem),file)==0)
        g2_file_close_error(must_be_open,source,0x1851u);
    return audio_file_lfs_seek_core(filesystem,file,offset,whence);
}
int32_t audio_file_lfs_tell(void *filesystem,void *file) {
    if(g2_lfs_mlist_isopen(list(filesystem),file)==0)
        g2_file_close_error(must_be_open,source,0x1872u);
    return audio_file_lfs_tell_core(filesystem,file);
}
int32_t audio_file_lfs_tell_core(void *filesystem,void *file) { /* 0x4ce45c */
    (void)filesystem;
    return *(int32_t *)(void *)((uint8_t *)file+0x34u);
}
