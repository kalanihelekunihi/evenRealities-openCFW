/* Native 0x4d3dda radio region read and ITCM copy dispatch. */
#include <stdint.h>

extern uint32_t platform_copy_words(uint32_t,uint32_t *,uint32_t);

uint32_t audio_ble_hci_radio_read_region_4d3dda(uint8_t region,uint32_t offset,
                                                  uint32_t words,uint32_t *output)
{
    uint32_t mode=*(volatile const uint32_t *)0x400201bcu;
    uint32_t source_ready=(*(volatile const uint32_t *)0x40021008u>>27u)&1u;
    uint32_t direct=(mode>>4u)&1u;
    uint32_t alternate=(mode>>3u)&1u;
    if (output==0) return 6u;
    uint32_t limit;
    switch (region) {
        case 0u: limit=direct?0x40u:0x200u;break;
        case 1u: limit=alternate?0x2c0u:0x600u;break;
        case 2u: limit=0x40u;break;
        case 3u: limit=0x2c0u;break;
        case 4u: limit=0x200u;break;
        case 5u: limit=0x600u;break;
        default:return 6u;
    }
    if (limit < words+offset) return 5u;
    uint32_t source;
    switch (region) {
        case 0u:
            if (direct) {
                if (!source_ready) return 9u;
                source=0x42004000u+offset*4u;
            } else {
                source=0x42000000u+offset*4u;
            }
            break;
        case 1u:
            if (alternate) {
                if (!source_ready) return 9u;
                source=0x42006000u+offset*4u;
            } else {
                uint32_t adjusted=offset>0x1ffu?offset+0x280u:offset;
                source=0x42002000u+adjusted*4u;
            }
            break;
        case 2u:
            if (!source_ready) return 9u;
            source=0x42004000u+offset*4u;
            break;
        case 3u:
            if (!source_ready) return 9u;
            source=0x42006000u+offset*4u;
            break;
        case 4u:source=0x42000000u+offset*4u;break;
        default:source=0x42002000u+offset*4u;break;
    }
    platform_copy_words(source,output,words);
    return 0u;
}
