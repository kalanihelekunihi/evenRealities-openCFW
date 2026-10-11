/* Native FreeType FT_Bitmap_Init 0x58ed20 and FT_Bitmap_Done 0x58f156.
 * The latter preserves the native error ordering and frees through the
 * supplied FT_Memory callback before clearing the bitmap buffer. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x48949c -> 0x43c0e4 */
extern void audio_uart_font_mem_free(void *,void *); /* 0x529256 */
static uint32_t get32(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void put32(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}
void audio_uart_font_bitmap_init(void *bitmap) {
    if(bitmap) audio_uart_buffer_zero(bitmap,24u,0u);
}
int32_t audio_uart_font_bitmap_done(void *library,void *bitmap) {
    if(!library) return 0x21;
    if(!bitmap) return 6;
    audio_uart_font_mem_free((void *)(uintptr_t)get32(library,0u),
                             (void *)(uintptr_t)get32(bitmap,12u));
    put32(bitmap,12u,0u);
    return 0;
}
