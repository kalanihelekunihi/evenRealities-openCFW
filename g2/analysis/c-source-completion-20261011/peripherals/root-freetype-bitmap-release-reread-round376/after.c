/* Native FreeType slot bitmap release 0x5250a2 and glyph slot clear 0x5252bc. */
#include <stdint.h>
extern void audio_uart_font_mem_free(void *,void *); /* 0x529256 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
static void put32(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
void audio_uart_font_slot_bitmap_release(void *slot) {
    volatile uint32_t *s=(volatile uint32_t *)slot;
    volatile uint32_t *internal=(volatile uint32_t *)(uintptr_t)s[39];
    if(internal!=0 && (*(const volatile uint8_t *)((const uint8_t *)internal+4u)&1u)!=0u) {
        void *face=(void *)(uintptr_t)s[1];
        audio_uart_font_mem_free((void *)(uintptr_t)*(const volatile uint32_t *)((const uint8_t *)face+100u),(void *)(uintptr_t)s[22]);
        s[22]=0u;
        uint32_t flags=((const volatile uint32_t *)(uintptr_t)s[39])[1]&~1u;
        ((volatile uint32_t *)(uintptr_t)s[39])[1]=flags;
    } else s[22]=0u;
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
