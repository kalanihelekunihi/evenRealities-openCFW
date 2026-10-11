/* LittleFS lfs_file_read native 0x4ce158; pinned lfs.c public core. */
#include <stdint.h>
extern void g2_file_close_error(const char *,const char *,uint32_t); /* 0x4d09b4 */
extern int32_t g2_lfs_file_flush(void *,void *); /* selected 0x4cde54 */
extern int32_t g2_lfs_file_flushedread(void *,void *,void *,uint32_t); /* selected 0x4ce042 */
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char read_assert[]="(file->flags & LFS_O_RDONLY) == LFS_O_RDONLY"; /* ROM0x7348d4 */
int32_t audio_file_lfs_read_core(void *filesystem,void *file,void *buffer,uint32_t size) {
    uint32_t flags=*(uint32_t *)(void *)((uint8_t *)file+0x30u);
    if((flags&1u)==0u)
        g2_file_close_error(read_assert,source,0xde4u);
    if((flags&0x20000u)!=0u) {
        int32_t err=g2_lfs_file_flush(filesystem,file);
        if(err!=0) return err;
    }
    return g2_lfs_file_flushedread(filesystem,file,buffer,size);
}
