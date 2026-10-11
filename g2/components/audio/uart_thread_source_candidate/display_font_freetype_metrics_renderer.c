/* Native FT_Grid_Fit_Metrics 0x5254c8 and slot renderer selector 0x527096. */
#include <stdint.h>
extern void *audio_uart_font_lookup_renderer(void *,uint32_t,void *); /* 0x52705a */
static uint32_t w(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void s(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
static uint32_t floor64(uint32_t v) { return v&~63u; }
static uint32_t ceil64(uint32_t v) { return (v+63u)&~63u; }
void audio_uart_font_grid_fit_metrics(void *slot,uint32_t vertical) {
    uint8_t *m=(uint8_t *)slot+0x18u;
    if((uint8_t)vertical!=0u) {
        s(m,8u,floor64(w(m,8u)));
        s(m,12u,ceil64(w(m,12u)));
        uint32_t right=ceil64(w(m,0u)+w(m,20u));
        uint32_t bottom=ceil64(w(m,4u)+w(m,24u));
        s(m,20u,floor64(w(m,20u)));
        s(m,24u,floor64(w(m,24u)));
        s(m,0u,right-w(m,20u));
        s(m,4u,bottom-w(m,24u));
    } else {
        s(m,20u,floor64(w(m,20u)));
        s(m,24u,floor64(w(m,24u)));
        uint32_t right=ceil64(w(m,0u)+w(m,8u));
        uint32_t bottom=floor64(w(m,12u)-w(m,4u));
        s(m,8u,floor64(w(m,8u)));
        s(m,12u,ceil64(w(m,12u)));
        s(m,0u,right-w(m,8u));
        s(m,4u,w(m,12u)-bottom);
    }
    s(m,16u,floor64(w(m,16u)+32u));
    s(m,28u,floor64(w(m,28u)+32u));
}
void *audio_uart_font_slot_renderer(void *slot) {
    uint8_t *face=(uint8_t *)(uintptr_t)w(slot,4u);
    uint8_t *driver=(uint8_t *)(uintptr_t)w(face,0x60u);
    uint8_t *library=(uint8_t *)(uintptr_t)w(driver,4u);
    uint8_t *renderer=(uint8_t *)(uintptr_t)w(library,0x9cu);
    uint32_t format=w(slot,0x48u);
    if(renderer!=0 && w(renderer,0x10u)==format) return renderer;
    return audio_uart_font_lookup_renderer(library,format,0);
}
