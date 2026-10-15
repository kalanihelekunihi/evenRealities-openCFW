/* Native FlashDB partition erase wrapper 0x585a32. */
#include <stdint.h>
extern int32_t audio_fal_partition_erase(uint32_t); /* native 0x597db0 */
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
uint32_t audio_flashdb_partition_erase(uint32_t database,uint32_t address,uint32_t size) {
    (void)address;(void)size;
    const uint8_t *db=(const uint8_t *)(uintptr_t)database;
    if(db[25u]!=0u) return 1u;
    return audio_fal_partition_erase(word(db+8u))<0 ? 1u : 0u;
}
