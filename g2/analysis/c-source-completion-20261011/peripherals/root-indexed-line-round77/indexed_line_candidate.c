#include <stdint.h>
/* Full native4c8c94..4c8d3c. Signed x division truncates toward zero;
 * loop width is signed and shift tests use the native low signed byte. */
uint32_t audio_uart_lv_bin_decode_indexed_line_4c8c94(uint32_t format,void *palette,uint32_t x_bits,uint32_t width_bits,const void *input,void *output)
{
    uint32_t bits,shift;
    int32_t x=(int32_t)x_bits;
    uintptr_t address=(uintptr_t)input;
    switch((uint8_t)format) {
    case 7: bits=1u;address+=(uint32_t)(x/8);shift=7u-(x_bits&7u);break;
    case 8: bits=2u;address+=(uint32_t)(x/4);shift=6u-((x_bits<<1u)&6u);break;
    case 9: bits=4u;address+=(uint32_t)(x/2);shift=4u-((x_bits<<2u)&4u);break;
    case 10: bits=8u;address+=x_bits;shift=0u;break;
    default: return 0u;
    }
    uint32_t mask=(1u<<bits)-1u;
    for(uint32_t i=0u;(int32_t)i<(int32_t)width_bits;++i) {
        uint32_t index=(*(const uint8_t *)address>>shift)&mask;
        ((uint32_t *)output)[i]=((const uint32_t *)palette)[index];
        shift-=bits;
        if((int8_t)(uint8_t)shift<0) {shift=8u-bits;++address;}
    }
    return 1u;
}
