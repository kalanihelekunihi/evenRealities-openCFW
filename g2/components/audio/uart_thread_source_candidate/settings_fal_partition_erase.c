/* Native fal_partition_erase 0x597db0. */
#include <stdint.h>
extern uint32_t g2_fal_device_for_partition(uint32_t); /* native 0x597d10 */
static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
int32_t audio_fal_partition_erase(uint32_t partition,uint32_t address,uint32_t size) {
    const uint8_t *part=(const uint8_t *)(uintptr_t)partition;
    if(address+size>word(part+0x38u)) return -1;
    uint32_t device=g2_fal_device_for_partition(partition);
    if(device==0u) return -1;
    const uint8_t *dev=(const uint8_t *)(uintptr_t)device;
    int32_t (*erase_fn)(uint32_t,uint32_t)=
        (int32_t (*)(uint32_t,uint32_t))(uintptr_t)word(dev+0x30u);
    return erase_fn(word(part+0x34u)+address,size);
}
