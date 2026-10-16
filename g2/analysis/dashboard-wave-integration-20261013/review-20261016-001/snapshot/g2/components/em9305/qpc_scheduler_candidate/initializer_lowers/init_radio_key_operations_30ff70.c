#include <stdint.h>

/* Native 0x30ff70..0x310036. These are firmware-owned byte-order adapters
 * around two resident ROM curve operations. A zero ROM result promises 32
 * bytes for multiply or 64 bytes for base generation; ROM behavior itself
 * remains an external platform contract. */
extern uint32_t opencfw_em9305_vendor_words_3333d0(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_rom_curve_multiply_1081e8(uintptr_t,
                                                            uintptr_t,
                                                            uintptr_t);
extern uint32_t opencfw_em9305_rom_curve_base_108178(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_radio_key_operation_30ff70(uintptr_t point,
                                                     uintptr_t scalar,
                                                     uintptr_t output)
{
    _Alignas(4) uint8_t frame[96];
    (void)opencfw_em9305_vendor_words_3333d0((uintptr_t)frame,point);
    (void)opencfw_em9305_vendor_words_3333d0((uintptr_t)(frame+32u),point+32u);
    uint32_t result=opencfw_em9305_rom_curve_multiply_1081e8(
        (uintptr_t)frame,scalar,(uintptr_t)(frame+64u));
    if(result!=0u)return result;
    for(uint32_t index=0u;index<8u;++index) {
        uint32_t word=*(volatile uint32_t *)(frame+64u+index*4u);
        uintptr_t destination=output+28u-index*4u;
        *(volatile uint8_t *)destination=(uint8_t)word;
        *(volatile uint8_t *)(destination+1u)=(uint8_t)(word>>8u);
        *(volatile uint8_t *)(destination+2u)=(uint8_t)(word>>16u);
        *(volatile uint8_t *)(destination+3u)=(uint8_t)(word>>24u);
        result=word>>24u;
    }
    return result;
}

uint32_t opencfw_em9305_radio_key_operation_30ffbc(uintptr_t scalar,
                                                     uintptr_t output)
{
    _Alignas(4) uint8_t frame[64];
    uint32_t result=opencfw_em9305_rom_curve_base_108178(scalar,
                                                            (uintptr_t)frame);
    if(result!=0u)return result;
    for(uint32_t index=0u;index<8u;++index) {
        uint32_t first=*(volatile uint32_t *)(frame+index*4u);
        uint32_t second=*(volatile uint32_t *)(frame+32u+index*4u);
        uintptr_t destination=output+28u-index*4u;
        *(volatile uint8_t *)destination=(uint8_t)first;
        *(volatile uint8_t *)(destination+3u)=(uint8_t)(first>>24u);
        *(volatile uint8_t *)(destination+1u)=(uint8_t)(first>>8u);
        *(volatile uint8_t *)(destination+2u)=(uint8_t)(first>>16u);
        *(volatile uint8_t *)(destination+32u)=(uint8_t)second;
        *(volatile uint8_t *)(destination+33u)=(uint8_t)(second>>8u);
        *(volatile uint8_t *)(destination+34u)=(uint8_t)(second>>16u);
        *(volatile uint8_t *)(destination+35u)=(uint8_t)(second>>24u);
        result=second;
    }
    return result;
}
