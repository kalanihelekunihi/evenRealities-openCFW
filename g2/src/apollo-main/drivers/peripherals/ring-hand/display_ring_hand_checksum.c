/* Native 0x49acd4 uses the authenticated CCITT table at ROM 0x6c0b50.
 * The polynomial form below generates the same 256 table entries in C. */
#include <stdint.h>
uint16_t audio_uart_hand_checksum_49acd4(const void *bytes,uint32_t length,
                                        const uint16_t *seed) {
    uint16_t crc=seed!=0?*seed:0xffffu;
    const uint8_t *p=(const uint8_t *)bytes;
    for(uint32_t i=0;i<length;i++) {
        uint16_t table=(uint16_t)((uint16_t)(p[i]^(crc>>8))<<8);
        for(uint32_t bit=0;bit<8u;bit++)
            table=(uint16_t)((table&0x8000u)?((table<<1)^0x1021u):(table<<1));
        crc=(uint16_t)(table^(uint16_t)(crc<<8));
    }
    return crc;
}
