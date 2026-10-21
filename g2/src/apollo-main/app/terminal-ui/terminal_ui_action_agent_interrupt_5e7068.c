/* Terminal FSM agent-interrupt action, stock 0x5e7068..0x5e716b. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_terminal_ui_stop_service_d_5ec770(void);
extern uint32_t audio_terminal_agent_interrupt_encode_5cee08(void);
extern uint32_t audio_terminal_counter_b_get_5973dc(void);
extern void audio_td_record_timer_clear(uint32_t);
extern void audio_td_record_status_set_current_597452(uint32_t);
extern void audio_td_notify_state_clear(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);

static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_agent_interrupt";
static const char triggered[]="agent interrupt triggered";
static const char triggered_short[]="[terminal.ui]agent interrupt triggered";
static const char idle[]="agent interrupted, back to idle";
static const char idle_short[]="[terminal.ui]agent interrupted, back to idle";
static const char waiting[]="Waiting input";
static const char hint[]="[Tap & hold to input]";
static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void zero_word(uint32_t offset) {
    uint8_t *p=audio_terminal_ui_state_base+offset;
    p[0]=0u;p[1]=0u;p[2]=0u;p[3]=0u;
}

uint32_t audio_terminal_ui_action_5e7068(uint32_t old_state,uint32_t event_payload) {
    (void)old_state;(void)event_payload;
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x738u,triggered);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,triggered_short,triggered_short);
    audio_terminal_ui_stop_service_d_5ec770();
    audio_terminal_ui_state_base[0x280u]=0u;
    zero_word(0x284u);
    (void)audio_terminal_agent_interrupt_encode_5cee08();
    uint32_t session=audio_terminal_counter_b_get_5973dc();
    audio_td_record_timer_clear(session);
    audio_td_record_status_set_current_597452(3u);
    audio_td_notify_state_clear();
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),sub=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && sub!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,&audio_terminal_asset_7733a8);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,waiting);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)sub,hint);
        audio_terminal_elapsed_clear_5e4894();
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x748u,idle);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,idle_short,idle_short);
    return 0u;
}
