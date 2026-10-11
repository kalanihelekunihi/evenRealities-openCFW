/* Native FreeType leaves 0x526f10 (char index), 0x567f88 (done glyph),
 * and 0x529256 (memory free). The class/allocator callbacks remain the
 * pointers held by the authenticated FreeType structures. */
#include <stdint.h>
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
uint32_t audio_uart_font_get_char_index(void *face,uint32_t codepoint) {
    if(face==0) return 0u;
    void *charmap=(void *)(uintptr_t)word(face,0x5cu);
    if(charmap==0) return 0u;
    void *clazz=(void *)(uintptr_t)word(charmap,0x0cu);
    uint32_t callback=word(clazz,0x0cu);
    uint32_t index=((uint32_t (*)(void *,uint32_t))(uintptr_t)callback)(charmap,codepoint);
    return index<word(face,0x10u)?index:0u;
}
void audio_uart_font_mem_free(void *memory,void *block) { /* 0x529256 */
    if(block!=0) {
        uint32_t callback=word(memory,8u);
        ((void (*)(void *,void *))(uintptr_t)callback)(memory,block);
    }
}
void audio_uart_font_done_glyph(void *glyph) { /* 0x567f88 */
    if(glyph==0) return;
    void *memory=(void *)(uintptr_t)word((void *)(uintptr_t)word(glyph,0u),0u);
    void *clazz=(void *)(uintptr_t)word(glyph,4u);
    uint32_t destroy=word(clazz,0x0cu);
    if(destroy!=0u) ((void (*)(void *))(uintptr_t)destroy)(glyph);
    audio_uart_font_mem_free(memory,glyph);
}
