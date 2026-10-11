/* Native FreeType kerning lookup 0x4b28ee with inlined comparator semantics. */
#include <stdint.h>
static uint8_t font_u8(uint32_t address) {
    return *(const uint8_t *)(uintptr_t)address;
}
static uint16_t font_u16(uint32_t address) {
    return *(const uint16_t *)(uintptr_t)address;
}
int32_t audio_uart_font_glyph_kerning(void *font,uint32_t left,uint32_t right) {
    const uint8_t *f=(const uint8_t *)font;
    const uint8_t *inner=*(const uint8_t *const *)(const void *)(f+0x18u);
    uint16_t mode=*(const uint16_t *)(const void *)(inner+0x12u);
    const uint32_t *table=*(const uint32_t *const *)(const void *)(inner+0xcu);
    if((mode&0x2000u)==0u) {
        uint32_t type=table[2]>>30u;
        uint32_t count=table[2]&0x3fffffffu;
        if(type>1u) return 0;
        uint32_t width=type==0u?2u:4u;
        uint32_t low=0u,high=count;
        while(low<high) {
            uint32_t middle=low+(high-low)/2u;
            uint32_t item=table[0]+middle*width;
            uint32_t item_left=type==0u?font_u8(item):font_u16(item);
            uint32_t item_right=type==0u?font_u8(item+1u):font_u16(item+2u);
            if(left<item_left||(left==item_left&&right<item_right)) high=middle;
            else if(left>item_left||(left==item_left&&right>item_right)) low=middle+1u;
            else return (int8_t)font_u8(table[1]+middle);
        }
        return 0;
    }
    uint32_t left_class=font_u8(table[1]+left);
    uint32_t right_class=font_u8(table[2]+right);
    if(left_class==0u||right_class==0u) return 0;
    uint32_t row_width=font_u8((uint32_t)(uintptr_t)table+0xdu);
    uint32_t value_address=table[0]+row_width*(left_class-1u)+right_class-1u;
    return (int8_t)font_u8(value_address);
}
