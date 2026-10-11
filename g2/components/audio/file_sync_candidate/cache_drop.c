/* LittleFS cache_drop, stock 0x4ca81a. */
#include <stdint.h>
int32_t g2_lfs_cache_drop(void *filesystem,void *read_cache) {
    (void)filesystem;
    *(uint32_t *)read_cache=UINT32_MAX;
    return -1;
}
