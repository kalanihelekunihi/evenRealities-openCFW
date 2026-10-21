/* Native area outset 0x450b98 and ancestor scrollbar predicate 0x440a18. */
#include <stdint.h>
void audio_uart_lv_area_expand_450b98(int32_t *area,int32_t x,int32_t y) {
    area[0]=(int32_t)((uint32_t)area[0]-(uint32_t)x);
    area[2]=(int32_t)((uint32_t)area[2]+(uint32_t)x);
    area[1]=(int32_t)((uint32_t)area[1]-(uint32_t)y);
    area[3]=(int32_t)((uint32_t)area[3]+(uint32_t)y);
}
uint32_t audio_uart_lv_object_scrollbar_visible_440a18(void *object) {
    for(uint8_t *p=(uint8_t *)object;p!=0;p=*(uint8_t **)(void *)(p+4u)) {
        uint8_t *spec=*(uint8_t **)(void *)(p+8u);
        if(spec!=0 && ((*(uint16_t *)(void *)(spec+0x32u)>>10u)&3u)==2u)return 1u;
    }
    return 0u;
}
