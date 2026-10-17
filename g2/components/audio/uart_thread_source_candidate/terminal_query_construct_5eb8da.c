/* Terminal query-panel constructor, stock 0x5eb8da..0x5ebb93. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_display_queue_handle;
extern uint32_t audio_uart_ring_secondary_head_cell;
extern const uint8_t audio_terminal_result_icon_773258;
extern uint8_t *audio_td_session_struct_ptr(void);
extern void audio_lv_style_opa_441488(void *,uint32_t,uint32_t);
extern void *audio_terminal_query_root_5e4f54(void *,uint32_t);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_44119c(void *,uint32_t,uint32_t);
extern void audio_uart_page_4411aa(void *,uint32_t,uint32_t);
extern void audio_uart_page_44120e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44122a(void *,uint32_t,uint32_t);
extern void audio_uart_page_441238(void *,uint32_t,uint32_t);
extern void audio_uart_page_44121c(void *,uint32_t,uint32_t);
extern void audio_uart_page_441246(void *,uint32_t,uint32_t);
extern void audio_uart_page_48ba78(void *,uint32_t);
extern void audio_uart_page_48ba92(void *,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44e3ca(void *,uint32_t);
extern void audio_uart_page_44e368(void *,uint32_t);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44131c(void *,uint32_t,uint32_t);
extern void audio_terminal_query_four_margins_5eb2bc(void *,uint32_t,uint32_t);
extern void audio_uart_page_441262(void *,uint32_t,uint32_t);
extern void *audio_uart_page_499416(void *);
extern void audio_uart_page_43f506(void *,uint32_t);
extern void audio_uart_page_49942e(void *,const char *);
extern void audio_uart_page_layout_499678(void *,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44140e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44145a(void *,uint32_t,uint32_t);
extern void audio_uart_page_44143e(void *,uint32_t,uint32_t);
extern void *audio_uart_page_498668(void *);
extern void audio_uart_page_498680(void *,const void *);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_uart_page_43f66c(void *);
extern void audio_terminal_display_status_44ea04(void *,uint32_t,uint32_t);
extern void audio_terminal_query_items_style_5eb3c6(uint32_t);
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern void audio_terminal_ui_event_5e5484(uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_441270(void *,uint32_t,uint32_t);

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void store_word(uint32_t offset,uint32_t v) {
    uint8_t *p=audio_terminal_ui_state_base+offset;
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}

void audio_terminal_query_construct_5eb8da(void) {
    if (audio_terminal_display_queue_handle==0u || word(0x214u)!=0u) return;
    uint8_t *session=audio_td_session_struct_ptr();
    if (session==0 || ((uint32_t)session[0x406u]|
                       ((uint32_t)session[0x407u]<<8))==0u) return;
    void *previous=(void *)(uintptr_t)word(0u);
    if (previous!=0) audio_lv_style_opa_441488(previous,0x33u,0u);
    void *root=audio_terminal_query_root_5e4f54(
        (void *)(uintptr_t)audio_terminal_display_queue_handle,0u);
    store_word(0x214u,(uint32_t)(uintptr_t)root);
    const uint32_t full=0x3fffffffu;
    audio_uart_page_43f4c0(root,0x22cu,full);
    audio_uart_page_44119c(root,0x78u,0u);
    audio_uart_page_4411aa(root,0x10au,0u);
    audio_uart_page_44120e(root,8u,0u);
    audio_uart_page_44122a(root,8u,0u);
    audio_uart_page_441238(root,8u,0u);
    audio_uart_page_44121c(root,8u,0u);
    audio_uart_page_441246(root,4u,0u);
    audio_uart_page_48ba78(root,1u);
    audio_uart_page_48ba92(root,0u,0u,0u);
    audio_uart_page_44e3ca(root,12u);
    audio_uart_page_44e368(root,0u);

    void *panel=audio_uart_page_43de82(root);
    audio_uart_page_43f4c0(panel,0x21cu,full);
    audio_uart_page_43dfa4(panel,0x10u);
    audio_uart_page_44129e(panel,0u,0u);
    audio_uart_page_44131c(panel,0u,0u);
    audio_terminal_query_four_margins_5eb2bc(panel,0u,0u);
    audio_uart_page_441262(panel,6u,0u);
    void *heading=audio_uart_page_499416(panel);
    store_word(0x218u,(uint32_t)(uintptr_t)heading);
    audio_uart_page_43f506(heading,0x21cu);
    audio_uart_page_49942e(heading,(const char *)(session+6u));
    audio_uart_page_layout_499678(heading,0u);
    audio_uart_page_44140e(heading,audio_uart_page_44104c(0x00ffffffu),0u);
    audio_uart_page_44145a(heading,1u,0u);
    audio_uart_page_44143e(heading,audio_uart_ring_secondary_head_cell,0u);

    void *list=audio_uart_page_43de82(root);
    store_word(0x21cu,(uint32_t)(uintptr_t)list);
    audio_uart_page_43f4c0(list,0x208u,full);
    audio_uart_page_43dfa4(list,0x10u);
    audio_uart_page_44129e(list,0u,0u);
    audio_uart_page_44131c(list,0u,0u);
    audio_terminal_query_four_margins_5eb2bc(list,0u,0u);
    audio_uart_page_441246(list,2u,0u);
    audio_uart_page_441270(list,20u,0u);
    audio_uart_page_48ba78(list,1u);
    audio_uart_page_48ba92(list,0u,0u,0u);
    audio_terminal_ui_state_base[0x279u]=0u;
    audio_terminal_ui_state_base[0x27cu]=0u;

    uint32_t count=(uint32_t)session[0x406u]|((uint32_t)session[0x407u]<<8);
    for (uint32_t i=0u;(uint16_t)i<count;++i) {
        void *row=audio_uart_page_499416(list);
        audio_uart_page_43f506(row,0x208u);
        audio_uart_page_layout_499678(row,0u);
        audio_uart_page_49942e(row,(const char *)(session+0x40eu+(uint16_t)i*0x88u));
        audio_uart_page_44140e(row,
            audio_uart_page_44104c(i==0u?0x00ffffffu:0x00333333u),0u);
        audio_uart_page_44143e(row,audio_uart_ring_secondary_head_cell,0u);
    }
    void *icon=audio_uart_page_498668(root);
    store_word(0x220u,(uint32_t)(uintptr_t)icon);
    audio_uart_page_498680(icon,&audio_terminal_result_icon_773258);
    audio_uart_page_43ded4(icon,0x20000u);
    audio_uart_page_43f66c(root);
    audio_terminal_display_status_44ea04(root,0u,0u);
    audio_terminal_query_items_style_5eb3c6((uint32_t)(uintptr_t)audio_terminal_ui_state_base);
    audio_terminal_ui_event_5e5484(4u,audio_terminal_counter_b_get_5973dc(),3u);
}
