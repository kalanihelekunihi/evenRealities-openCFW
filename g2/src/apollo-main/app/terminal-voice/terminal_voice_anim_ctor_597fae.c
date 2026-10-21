/* LVGL animimage class constructor, stock 0x597fae..0x598003. */
#include <stdint.h>
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *,int32_t,int32_t);
extern void audio_terminal_voice_anim_exec_598008(void *,int32_t);
static void store_u32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
void audio_terminal_voice_anim_ctor_597fae(const void *class_record,void *object) {
    (void)class_record;
    uint8_t *s=(uint8_t *)object;
    store_u32(s+0xbcu,0u);
    s[0xc0u]=0xffu;
    uint8_t *animation=s+0x5cu;
    audio_uart_lv_anim_init_4503d6(animation);
    store_u32(animation,(uint32_t)(uintptr_t)object);
    store_u32(animation+0x30u,30u);
    store_u32(animation+4u,(uint32_t)(uintptr_t)&audio_terminal_voice_anim_exec_598008);
    audio_uart_lv_anim_values_4506ce(animation,0,1);
    store_u32(animation+0x44u,0xffffffffu);
}
