/* Experimental littlefs backend close wrapper, stock 0x4cfad0. */
#include <stdint.h>
extern int32_t g2_lfs_mlist_isopen(void *list,void *file);
extern int32_t g2_lfs_file_close(void *filesystem,void *file);
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
int32_t audio_file_backend_close(void *filesystem,void *file) {
    void *list=*(void **)((uint8_t *)filesystem+0x28u);
    if(g2_lfs_mlist_isopen(list,file)==0)
        g2_file_close_error((const char *)(uintptr_t)0x71f8e0u,
                             (const char *)(uintptr_t)0x70c264u,0x180bu);
    return g2_lfs_file_close(filesystem,file);
}
