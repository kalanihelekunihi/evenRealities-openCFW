/* Native LV display root and field setters 0x44fa1a/3e/5e, 0x44fbfc,
 * 0x44fc18/2e. Root storage is authenticated RAM 0x2006f548. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* RAM 0x2006f548 */
extern void audio_uart_display_size_changed(void *); /* native 0x440656 */

static void *default_display(void) {
    return *(void **)(void *)(audio_uart_display_lv_root+0x14u);
}
void *audio_uart_display_default_get(void) { return default_display(); } /* native 0x44fa1a */
static void *resolve_display(void *display) {
    return display!=0 ? display : default_display();
}
void audio_uart_display_buffer_attach(void *display,void *buffer,uint32_t mode) {
    uint8_t *d=(uint8_t *)resolve_display(display);
    if(d==0) return;
    *(void **)(void *)(d+0x1cu)=buffer;
    *(uint32_t *)(void *)(d+0x20u)=mode;
    *(void **)(void *)(d+0x24u)=*(void **)(void *)(d+0x1cu);
}
void audio_uart_display_buffer_mode(void *display,uint32_t mode) {
    uint8_t *d=(uint8_t *)resolve_display(display);
    if(d!=0) d[0x39u]=(uint8_t)mode;
}
void audio_uart_display_flush_bind(void *display,const void *callback) {
    uint8_t *d=(uint8_t *)resolve_display(display);
    if(d!=0) *(const void **)(void *)(d+0x28u)=callback;
}
void audio_uart_display_buffer_size(void *display,uint32_t width,uint32_t height) {
    uint8_t *d=(uint8_t *)resolve_display(display);
    if(d==0) return;
    *(uint32_t *)(void *)(d+8u)=width;
    *(uint32_t *)(void *)(d+12u)=height;
    audio_uart_display_size_changed(*(void **)(void *)(d+700u));
}
void audio_uart_display_buffer_origin(void *display,uint32_t x,uint32_t y) {
    uint8_t *d=(uint8_t *)resolve_display(display);
    if(d==0) return;
    *(uint32_t *)(void *)(d+0x10u)=x;
    *(uint32_t *)(void *)(d+0x14u)=y;
    audio_uart_display_size_changed(*(void **)(void *)(d+700u));
}
