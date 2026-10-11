/* Pinned LittleFS block-device erase, stock 0x4cad2e. */
#include <stdint.h>
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);
int32_t g2_lfs_bd_erase(void *filesystem,uint32_t block) {
    uint8_t *fs=(uint8_t *)filesystem;
    if(block>=*(uint32_t *)(void *)(fs+0x6cu))
        g2_file_close_error((const char *)(uintptr_t)0x76bed8u,
                            (const char *)(uintptr_t)0x70c264u,276u);
    uint8_t *cfg=*(uint8_t **)(void *)(fs+0x68u);
    int32_t (*erase)(void *,uint32_t)=
        *(int32_t (**)(void *,uint32_t))(void *)(cfg+0x0cu);
    int32_t err=erase(cfg,block);
    if(err>=1)
        g2_file_close_error((const char *)(uintptr_t)0x78ab74u,
                            (const char *)(uintptr_t)0x70c264u,278u);
    return err;
}
