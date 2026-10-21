/* Native LVGL FreeType cmap glyph index resolver 0x4b2774. */
#include <stdint.h>
uint32_t audio_uart_font_glyph_index(void *font,uint32_t codepoint) {
    if(codepoint==0u) return 0u;
    const uint8_t *f=(const uint8_t *)font;
    const uint8_t *inner=*(const uint8_t *const *)(const void *)(f+0x18u);
    uint16_t mode=*(const uint16_t *)(const void *)(inner+0x12u);
    uint32_t count=mode&0x1ffu;
    uint32_t base=*(const uint32_t *)(const void *)(inner+8u);
    for(uint32_t i=0u;i<count;++i) {
        const uint8_t *range=(const uint8_t *)(uintptr_t)(base+i*20u);
        uint32_t first=*(const uint32_t *)(const void *)range;
        uint32_t delta=codepoint-first;
        uint16_t length=*(const uint16_t *)(const void *)(range+4u);
        if(delta>=length) continue;
        uint32_t start=*(const uint16_t *)(const void *)(range+6u);
        uint8_t type=range[0x12u];
        if(type==2u) return start+delta;
        if(type==0u) {
            uint32_t map=*(const uint32_t *)(const void *)(range+0xcu);
            uint32_t offset=*(const uint8_t *)(uintptr_t)(map+delta);
            if(offset!=0u||delta==0u) return start+offset;
            continue;
        }
        if(type!=1u&&type!=3u) return 0u;
        uint32_t unicode=*(const uint32_t *)(const void *)(range+8u);
        uint32_t entries=*(const uint16_t *)(const void *)(range+0x10u);
        uint32_t low=0u,high=entries;
        while(low<high) {
            uint32_t middle=low+(high-low)/2u;
            uint16_t value=*(const uint16_t *)(uintptr_t)(unicode+middle*2u);
            if(delta<(uint32_t)value) high=middle;
            else if(delta>(uint32_t)value) low=middle+1u;
            else {
                if(type==3u) return start+middle;
                uint32_t glyphs=*(const uint32_t *)(const void *)(range+0xcu);
                return start+*(const uint16_t *)(uintptr_t)(glyphs+middle*2u);
            }
        }
        return 0u;
    }
    return 0u;
}
