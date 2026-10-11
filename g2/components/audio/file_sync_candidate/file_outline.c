/* LittleFS inline-to-block outline, stock 0x4cde2c. */
#include <stdint.h>
extern void g2_lfs_alloc_checkpoint(void *filesystem);
extern int32_t g2_lfs_file_relocate(void *filesystem,void *file);
int32_t g2_lfs_file_outline(void *filesystem,void *file) {
    uint8_t *f=(uint8_t *)file;
    *(uint32_t *)(void *)(f+0x3cu)=*(uint32_t *)(void *)(f+0x34u);
    g2_lfs_alloc_checkpoint(filesystem);
    int32_t err=g2_lfs_file_relocate(filesystem,file);
    if(err) return err;
    *(uint32_t *)(void *)(f+0x30u)&=~0x100000u;
    return 0;
}
