/* Terminal voice-input page constructor, stock 0x5ebd0e..0x5ebfaf. */
#include <stdint.h>
extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_display_queue_handle;
extern uint32_t audio_uart_ring_secondary_head_cell;
struct terminal_voice_frame_descriptor {
    uint32_t header, dimensions, stride, data_size;
    const uint8_t *data;
    uint32_t reserved0, reserved1;
};
extern const struct terminal_voice_frame_descriptor *
    audio_terminal_voice_style_200014e8[19]; /* initialized RAM table */
extern void audio_lv_style_opa_441488(void *,uint32_t,uint32_t);
extern void *audio_terminal_query_root_5e4f54(void *,uint32_t);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_44119c(void *,uint32_t,uint32_t);
extern void audio_uart_page_4411aa(void *,uint32_t,uint32_t);
extern void audio_terminal_ui_margins_5ebc5c(void *,uint32_t,uint32_t);
extern void audio_uart_page_48ba78(void *,uint32_t);
extern void audio_uart_page_48ba92(void *,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_441246(void *,uint32_t,uint32_t);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_uart_page_44e3ca(void *,uint32_t);
extern void audio_uart_page_44e368(void *,uint32_t);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44131c(void *,uint32_t,uint32_t);
extern void audio_uart_page_441254(void *,uint32_t,uint32_t);
extern void *audio_terminal_voice_anim_create_597e90(void *);
extern void audio_uart_page_4411e4(void *,uint32_t,uint32_t);
extern uint32_t audio_terminal_set_label_style_5e482a(uint32_t,const void *,uint32_t,uint32_t);
extern void *audio_uart_page_499416(void *);
extern void audio_uart_page_layout_499678(void *,uint32_t);
extern void audio_uart_page_49942e(void *,const char *);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44143e(void *,uint32_t,uint32_t);
extern void audio_uart_page_4412ec(void *,uint32_t,uint32_t);
extern void audio_uart_page_44132a(void *,uint32_t,uint32_t);
extern void audio_uart_page_44146a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441270(void *,uint32_t,uint32_t);
extern void audio_uart_page_43f6b8(void *,uint32_t,uint32_t,uint32_t);
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);

static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void store_u32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
static void *object_at(uint8_t *s,uint32_t offset) {
    return (void *)(uintptr_t)load_u32(s+offset);
}

void audio_terminal_ui_voice_prepare_5ebd0e(void) {
    uint8_t *s=audio_terminal_ui_state_base;
    if(audio_terminal_display_queue_handle==0u || load_u32(s+0x1f4u)!=0u)
        return;
    void *previous=object_at(s,0u);
    if(previous!=0)
        audio_lv_style_opa_441488(previous,0x7fu,0u);
    void *root=audio_terminal_query_root_5e4f54(
        (void *)(uintptr_t)audio_terminal_display_queue_handle,0u);
    store_u32(s+0x1f4u,(uint32_t)(uintptr_t)root);
    const uint32_t full=0x3fffffffu;
    audio_uart_page_43f4c0(root,0x22cu,full);
    audio_uart_page_44119c(root,0x50u,0u);
    audio_uart_page_4411aa(root,0xd8u,0u);
    audio_terminal_ui_margins_5ebc5c(root,0u,0u);
    audio_uart_page_48ba78(root,1u);
    audio_uart_page_48ba92(root,0u,0u,0u);
    audio_uart_page_44120e(root,8u,0u);
    audio_uart_page_44122a(root,8u,0u);
    audio_uart_page_441238(root,8u,0u);
    audio_uart_page_441246(root,4u,0u);
    audio_uart_page_43ded4(root,0x10u);
    audio_uart_page_44e3ca(root,0xcu);
    audio_uart_page_44e368(root,0u);
    void *panel=audio_uart_page_43de82(root);
    audio_uart_page_43f4c0(panel,0x21cu,full);
    audio_uart_page_43dfa4(panel,0x10u);
    audio_uart_page_44129e(panel,0u,0u);
    audio_uart_page_44131c(panel,0u,0u);
    audio_terminal_ui_margins_5ebc5c(panel,0u,0u);
    audio_uart_page_48ba78(panel,0u);
    audio_uart_page_48ba92(panel,0u,1u,0u);
    audio_uart_page_441254(panel,4u,0u);
    void *animation=audio_terminal_voice_anim_create_597e90(panel);
    store_u32(s+0x1f8u,(uint32_t)(uintptr_t)animation);
    audio_uart_page_43f4c0(animation,0x10u,0x10u);
    audio_uart_page_4411e4(animation,(uint32_t)-2,0u);
    (void)audio_terminal_set_label_style_5e482a(
        (uint32_t)(uintptr_t)animation,audio_terminal_voice_style_200014e8,
        0x13u,0x3cu);
    void *listening=audio_uart_page_499416(panel);
    store_u32(s+0x1fcu,(uint32_t)(uintptr_t)listening);
    audio_uart_page_43f4c0(listening,0x208u,full);
    audio_uart_page_layout_499678(listening,0u);
    audio_uart_page_49942e(listening,"Listening...");
    const uint32_t white=0x00ffffffu;
    audio_uart_page_44140e(listening,audio_uart_page_44104c(white),0u);
    uint32_t font=audio_uart_ring_secondary_head_cell;
    audio_uart_page_44143e(listening,font,0u);
    void *footer=audio_uart_page_43de82(root);
    store_u32(s+0x200u,(uint32_t)(uintptr_t)footer);
    audio_uart_page_43f4c0(footer,0x208u,0x28u);
    audio_uart_page_43dfa4(footer,0x10u);
    audio_uart_page_44129e(footer,0u,0u);
    audio_uart_page_44131c(footer,1u,0u);
    audio_uart_page_4412ec(footer,audio_uart_page_44104c(white),0u);
    audio_uart_page_44132a(footer,2u,0u);
    audio_uart_page_44146a(footer,0u,0u);
    audio_terminal_ui_margins_5ebc5c(footer,0u,0u);
    audio_uart_page_441270(footer,0x14u,0u);
    void *hint=audio_uart_page_499416(footer);
    store_u32(s+0x204u,(uint32_t)(uintptr_t)hint);
    audio_uart_page_43f6b8(hint,7u,0u,0u);
    audio_uart_page_49942e(hint,"[Release to finish recording]");
    audio_uart_page_44140e(hint,audio_uart_page_44104c(0x00333333u),0u);
    audio_uart_page_44143e(hint,font,0u);
    store_u32(s+0x208u,0u);
    store_u32(s+0x20cu,0u);
    store_u32(s+0x210u,0u);
    s[0x278u]=0u;
    audio_terminal_ui_event_5e5484(4u,audio_terminal_counter_b_get_5973dc(),2u);
}
