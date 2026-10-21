/* LittleFS allocation checkpoint, stock 0x4cb0e0. */
#include <stdint.h>
void g2_lfs_alloc_checkpoint(void *filesystem) {
    uint8_t *fs=(uint8_t *)filesystem;
    *(uint32_t *)(void *)(fs+0x60u)=*(uint32_t *)(void *)(fs+0x6cu);
}
