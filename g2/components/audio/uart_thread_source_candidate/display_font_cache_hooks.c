/* Source-defined FreeType cache hook tables at authenticated ROM addresses
 * 0x78ae74 (glyph), 0x78ae8c (bitmap), 0x78aeb0 (outline). */
#include <stdint.h>
extern uint32_t audio_uart_font_glyph_cache_initialize(void *,void *); /* 0x5295a8 */
extern uint32_t audio_uart_font_bitmap_cache_initialize(void *,void *); /* 0x529936 */
extern uint32_t audio_uart_font_outline_cache_initialize(void *,void *); /* 0x529cf8 */
extern void audio_uart_font_bitmap_release(void *); /* native 0x48b216 */
extern void *audio_uart_font_outline_context(void); /* native 0x4b1fcc */
extern void audio_uart_font_outline_release(void *,void *); /* native 0x52a264 */
int32_t audio_uart_font_cache_compare_pair(const void *left,const void *right) {
    const uint32_t *a=(const uint32_t *)left;
    const uint32_t *b=(const uint32_t *)right;
    if(a[0]!=b[0]) return a[0]>b[0]?1:-1;
    if(a[1]!=b[1]) return a[1]>b[1]?1:-1;
    return 0;
}
int32_t audio_uart_font_cache_compare_outline(const void *left,const void *right) {
    const uint32_t *a=(const uint32_t *)left;
    const uint32_t *b=(const uint32_t *)right;
    return a[0]==b[0]?0:(a[0]>b[0]?1:-1);
}
static void glyph_free(void *data) { (void)data; } /* native bx lr at 0x529778 */
static void bitmap_free(void *data) { /* native 0x529ae4 */
    audio_uart_font_bitmap_release(*(void **)(void *)((uint8_t *)data+8u));
}
static void outline_free(void *data) { /* native 0x529d40 */
    void *outline=*(void **)(void *)((uint8_t *)data+4u);
    void *context=audio_uart_font_outline_context();
    audio_uart_font_outline_release(context,outline);
}
const uintptr_t audio_uart_font_glyph_cache_hooks[3]={
    (uintptr_t)&audio_uart_font_cache_compare_pair,(uintptr_t)&audio_uart_font_glyph_cache_initialize,
    (uintptr_t)&glyph_free};
const uintptr_t audio_uart_font_bitmap_cache_hooks[3]={
    (uintptr_t)&audio_uart_font_cache_compare_pair,(uintptr_t)&audio_uart_font_bitmap_cache_initialize,
    (uintptr_t)&bitmap_free};
const uintptr_t audio_uart_font_outline_cache_hooks[3]={
    (uintptr_t)&audio_uart_font_cache_compare_outline,(uintptr_t)&audio_uart_font_outline_cache_initialize,
    (uintptr_t)&outline_free};
