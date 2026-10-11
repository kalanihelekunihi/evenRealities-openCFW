/* LittleFS block-device sync composition, stock 0x4cabbc. */
#include <stdint.h>
extern int32_t g2_lfs_cache_drop(void *filesystem,void *read_cache); /* 0x4ca81a */
extern int32_t g2_lfs_bd_flush(void *filesystem,void *program_cache,
                              void *read_cache,uint32_t validate); /* 0x4caafa */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
int32_t g2_lfs_bd_sync(void *filesystem,void *program_cache,
                        void *read_cache,uint32_t validate) {
    (void)g2_lfs_cache_drop(filesystem,read_cache);
    int32_t err=g2_lfs_bd_flush(filesystem,program_cache,read_cache,
                                (uint8_t)validate);
    if(err) return err;
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    int32_t (*sync)(void *)=*(int32_t (**)(void *))(void *)(cfg+0x10u);
    err=sync(cfg);
    if(err>=1)
        g2_file_close_error((const char *)(uintptr_t)0x78ab74u,
                            (const char *)(uintptr_t)0x70c264u,221u);
    return err;
}
