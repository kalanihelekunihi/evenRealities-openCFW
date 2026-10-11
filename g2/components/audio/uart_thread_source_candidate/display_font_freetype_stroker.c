/* Native FT_Stroker_New/Set/Done 0x5687b6/0x5687fe/0x568844 and
 * FT_Outline_Embolden wrapper 0x527bca. */
#include <stdint.h>
extern void *audio_uart_font_mem_alloc(void *,int32_t,int32_t *); /* 0x529148 */
extern void audio_uart_font_mem_free(void *,void *); /* 0x529256 */
extern int32_t audio_uart_font_embolden_xy(void *,uint32_t,uint32_t); /* 0x527bd6 */
static uint32_t word(const void *p,uint32_t o) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+o);
}
static void store(void *p,uint32_t o,uint32_t v) {
    *(uint32_t *)(void *)((uint8_t *)p+o)=v;
}
void audio_uart_font_stroker_subpath_init(void *path,void *memory) { /* 0x56865e */
    store(path,0x18u,(uint32_t)(uintptr_t)memory);
    store(path,8u,0u);store(path,0x0cu,0u);
    store(path,0u,0u);store(path,4u,0u);
    store(path,0x14u,0xffffffffu);
    ((uint8_t *)path)[0x1cu]=0u;
}
static void subpath_reset(void *path) { /* 0x56867c */
    store(path,0u,0u);store(path,0x14u,0xffffffffu);
    ((uint8_t *)path)[0x1cu]=0u;
}
void audio_uart_font_stroker_subpath_done(void *path) { /* 0x56868c */
    void *memory=(void *)(uintptr_t)word(path,0x18u);
    audio_uart_font_mem_free(memory,(void *)(uintptr_t)word(path,8u));
    store(path,8u,0u);
    audio_uart_font_mem_free(memory,(void *)(uintptr_t)word(path,0x0cu));
    store(path,0x0cu,0u);
    store(path,0u,0u);store(path,4u,0u);
    store(path,0x14u,0xffffffffu);
    ((uint8_t *)path)[0x1cu]=0u;
}
void audio_uart_font_stroker_reset(void *stroker) { /* 0x56882a */
    if(stroker==0) return;
    subpath_reset((uint8_t *)stroker+0x34u);
    subpath_reset((uint8_t *)stroker+0x54u);
}
int32_t audio_uart_font_stroker_create(void *library,void **out) {
    if(library==0) return 0x21;
    if(out==0) return 6;
    void *memory=(void *)(uintptr_t)word(library,0u);
    int32_t error=0;
    uint8_t *stroker=(uint8_t *)audio_uart_font_mem_alloc(memory,0x78,&error);
    if(error==0) {
        *(uint32_t *)(void *)(stroker+0x74u)=(uint32_t)(uintptr_t)library;
        audio_uart_font_stroker_subpath_init(stroker+0x34u,memory);
        audio_uart_font_stroker_subpath_init(stroker+0x54u,memory);
    }
    *out=stroker;
    return error;
}
void audio_uart_font_stroker_configure(void *stroker,uint32_t radius,
                                       uint8_t line_cap,uint8_t line_join,
                                       uint32_t miter_limit) {
    if(stroker==0) return;
    uint8_t *s=(uint8_t *)stroker;
    *(uint32_t *)(void *)(s+0x30u)=radius;
    s[0x29u]=line_cap;
    s[0x2au]=line_join;
    *(uint32_t *)(void *)(s+0x2cu)=miter_limit<0x10000u?0x10000u:miter_limit;
    s[0x2bu]=line_join;
    audio_uart_font_stroker_reset(stroker);
}
void audio_uart_font_stroker_destroy(void *stroker) {
    if(stroker==0) return;
    uint8_t *s=(uint8_t *)stroker;
    void *library=(void *)(uintptr_t)word(s,0x74u);
    void *memory=(void *)(uintptr_t)word(library,0u);
    audio_uart_font_stroker_subpath_done(s+0x34u);
    audio_uart_font_stroker_subpath_done(s+0x54u);
    *(uint32_t *)(void *)(s+0x74u)=0u;
    audio_uart_font_mem_free(memory,stroker);
}
int32_t audio_uart_font_embolden_outline(void *outline,uint32_t strength) {
    return audio_uart_font_embolden_xy(outline,strength,strength);
}
