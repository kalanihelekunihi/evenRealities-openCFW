/* Native FreeType slot bitmap release 0x5250a2 and glyph slot clear 0x5252bc. */
#include <stdint.h>
extern void audio_uart_font_mem_free(void *,void *); /* 0x529256 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
static uint32_t get32(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void put32(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
void audio_uart_font_slot_bitmap_release(void *slot) {
    uint8_t *internal=(uint8_t *)(uintptr_t)get32(slot,0x9cu);
    if(internal!=0 && (internal[4u]&1u)!=0u) {
        uint8_t *face=(uint8_t *)(uintptr_t)get32(slot,4u);
        audio_uart_font_mem_free((void *)(uintptr_t)get32(face,0x64u),
                                 (void *)(uintptr_t)get32(slot,0x58u));
        put32(slot,0x58u,0u);
        put32(internal,4u,get32(internal,4u)&~1u);
    } else put32(slot,0x58u,0u);
}
void audio_uart_font_glyphslot_clear(void *slot) {
    audio_uart_font_slot_bitmap_release(slot);
    audio_uart_buffer_zero((uint8_t *)slot+0x18u,0x20u,0u);
    audio_uart_buffer_zero((uint8_t *)slot+0x6cu,0x14u,0u);
    static const uint8_t words[]={0x50u,0x4cu,0x54u,0x64u,0x68u,0x80u,0x84u,
                                  0x88u,0x8cu,0x98u,0x48u,0x38u,0x3cu,0x90u,0x94u};
    for(uint32_t i=0;i<sizeof(words);i++) put32(slot,words[i],0u);
    ((uint8_t *)slot)[0x5eu]=0u;
}
