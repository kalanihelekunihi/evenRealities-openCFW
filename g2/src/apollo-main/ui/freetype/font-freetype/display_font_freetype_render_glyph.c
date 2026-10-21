/* Native FT_Render_Glyph 0x527228. Renderer dispatch remains a typed lower. */
#include <stdint.h>
extern int32_t audio_uart_font_render_glyph_internal(void *,void *,uint8_t); /* 0x5271c0 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
int32_t audio_uart_font_render_glyph(void *slot,uint32_t mode) {
    if(slot==0 || word(slot,4u)==0u) return 6;
    void *face=(void *)(uintptr_t)word(slot,4u);
    void *driver=(void *)(uintptr_t)word(face,0x60u);
    void *library=(void *)(uintptr_t)word(driver,4u);
    return audio_uart_font_render_glyph_internal(library,slot,(uint8_t)mode);
}
