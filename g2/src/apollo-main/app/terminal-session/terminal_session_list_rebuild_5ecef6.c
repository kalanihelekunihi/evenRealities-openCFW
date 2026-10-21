/* Apollo terminal session selector rebuild, stock 0x5ecef6..0x5ed0b0. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_terminal_display_queue_handle;
extern uint8_t *audio_td_active_session(void);
extern uint32_t audio_terminal_session_count_5eca48(void);
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_page_43f4c0(void *,uint32_t,uint32_t);
extern void audio_uart_page_43f09a(void *,uint32_t,uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44127e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44129e(void *,uint32_t,uint32_t);
extern void audio_uart_page_44131c(void *,uint32_t,uint32_t);
extern void audio_terminal_session_four_margins_5eca00(void *,uint32_t,uint32_t);
extern void audio_uart_page_44146a(void *,uint32_t,uint32_t);
extern void audio_uart_page_48ba78(void *,uint32_t);
extern void audio_uart_page_48ba92(void *,uint32_t,uint32_t,uint32_t);
extern void audio_uart_page_441246(void *,uint32_t,uint32_t);
extern void audio_uart_page_43ded4(void *,uint32_t);
extern void audio_uart_page_44e368(void *,uint32_t);
extern void *audio_terminal_session_row_factory_5ecd06(void *,const char *,
                                                        uint32_t,uint32_t);
extern void audio_terminal_session_row_text_5ecc74(char *,uint32_t,const uint8_t *);
extern uint32_t audio_terminal_session_valid_5eca64(int32_t);
extern int32_t audio_td_current_session_index_signed(void);
extern void audio_terminal_session_apply_5ecb88(int32_t);
extern void audio_terminal_ui_scroll_to_view_44ea2e(void *,uint32_t);

static void store_word(uint32_t offset,uint32_t value) {
    uint8_t *p=audio_terminal_ui_state_base+offset;
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void audio_terminal_session_list_rebuild_5ecef6(int32_t requested) {
    int32_t selected=(int16_t)requested;
    uint8_t *active=audio_td_active_session();
    uint32_t count=audio_terminal_session_count_5eca48();
    audio_terminal_ui_stop_service_a_5eceb2();

    void *root=audio_uart_page_43de82(
        (void *)(uintptr_t)audio_terminal_display_queue_handle);
    store_word(0x240u,(uint32_t)(uintptr_t)root);
    audio_uart_page_43f4c0(root,0x240u,0x120u);
    audio_uart_page_43f09a(root,0u,0u);
    audio_uart_page_43dfa4(root,0x10u);
    audio_uart_page_44127e(root,audio_uart_page_44104c(0u),0u);
    audio_uart_page_44129e(root,0xffu,0u);
    audio_uart_page_44131c(root,0u,0u);
    audio_terminal_session_four_margins_5eca00(root,0u,0u);
    audio_uart_page_44146a(root,0u,0u);

    void *list=audio_uart_page_43de82(root);
    store_word(0x244u,(uint32_t)(uintptr_t)list);
    audio_uart_page_43f4c0(list,0x240u,0xc8u);
    audio_uart_page_43f09a(list,0u,0u);
    audio_uart_page_44129e(list,0u,0u);
    audio_uart_page_44131c(list,0u,0u);
    audio_terminal_session_four_margins_5eca00(list,0u,0u);
    audio_uart_page_48ba78(list,1u);
    audio_uart_page_48ba92(list,0u,0u,0u);
    audio_uart_page_441246(list,0u,0u);
    audio_uart_page_43ded4(list,0x10u);
    audio_uart_page_43dfa4(list,0x60u);
    audio_uart_page_44e368(list,0u);

    void *row=audio_terminal_session_row_factory_5ecd06(
        list,"New Session",0u,0u);
    store_word(0x248u,(uint32_t)(uintptr_t)row);
    for (uint32_t i=0u;i<count;++i) {
        char label[64];
        uint8_t *record=active+i*0x90u;
        audio_terminal_session_row_text_5ecc74(label,sizeof(label),record+0x9cu);
        row=audio_terminal_session_row_factory_5ecd06(
            list,label,1u,(uint32_t)record[0x122u]);
        store_word(0x24cu+i*4u,(uint32_t)(uintptr_t)row);
    }

    if (selected==-2 ||
        (selected!=-1 && audio_terminal_session_valid_5eca64(selected)==0u))
        selected=audio_td_current_session_index_signed();
    audio_terminal_session_apply_5ecb88((int16_t)selected);
    row=(void *)(uintptr_t)word((uint32_t)((int32_t)0x24c+selected*4));
    audio_terminal_ui_scroll_to_view_44ea2e(row,0u);
}
