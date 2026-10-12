/* Native 0x4d34f8 CRC32. The authenticated table at 0x699fa8 starts
 * 00000000,77073096,ee0e612c,990951ba: reflected 0xedb88320. This C
 * generates each table value instead of carrying the stock table blob. */
#include <stdint.h>
uint32_t audio_ble_radio_crc_local_4d34f8(const void *input,uint32_t length,
                                           const uint32_t *previous) {
    uint32_t crc=previous?~*previous:0xffffffffu;
    const uint8_t *p=(const uint8_t *)input;
    for(uint32_t i=0u;i<length;i++) {
        uint32_t index=(crc^p[i])&0xffu;
        for(unsigned bit=0u;bit<8u;bit++)
            index=(index>>1u)^((index&1u)?0xedb88320u:0u);
        crc=index^(crc>>8u);
    }
    return ~crc;
}
