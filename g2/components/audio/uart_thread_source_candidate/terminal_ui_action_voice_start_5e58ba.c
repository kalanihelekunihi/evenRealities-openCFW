/* Terminal FSM voice-start action, stock 0x5e58ba..0x5e5989. */
#include <stdint.h>
struct terminal_voice_icon_descriptor {
    uint32_t header, dimensions, stride, data_size;
    const uint8_t *data;
    uint32_t reserved0, reserved1;
};
extern const struct terminal_voice_icon_descriptor
    audio_terminal_voice_icon_773044;
extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_td_notify_state_clear(void);
extern void audio_terminal_ui_voice_prepare_5ebd0e(void);
extern void audio_terminal_voice_timeout_start_5e7ed4(void);
extern void *audio_even_ai_app_acquire_54f380(uint32_t);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern void audio_uart_page_49942e(void *,const char *);
extern void audio_terminal_elapsed_clear_5e4894(void);
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern void audio_terminal_encode_voice_input_5cec72(const uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char recording[]="Recording...";
static const char release[]="[Release to stop]";
static const char module[]="terminal.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[]="terminal_ui_action_voice_start";
static const char message[]="voice start, timer armed";
static const char short_message[]="[terminal.ui]voice start, timer armed";
static uint32_t load_u32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
uint32_t audio_terminal_ui_action_5e58ba(uint32_t ignored,uint32_t ignored2,
                                          uint32_t ignored3,uint32_t ignored4) {
    (void)ignored;(void)ignored2;(void)ignored3;(void)ignored4;
    uint8_t *s=audio_terminal_ui_state_base;
    audio_td_notify_state_clear();
    audio_terminal_ui_voice_prepare_5ebd0e();
    audio_terminal_voice_timeout_start_5e7ed4();
    (void)audio_even_ai_app_acquire_54f380(6u);
    uint32_t icon=load_u32(s+0x1ccu),title=load_u32(s+0x1d0u);
    uint32_t hint=load_u32(s+0x1d4u),elapsed=load_u32(s+0x1dcu);
    if(icon!=0u && title!=0u && hint!=0u && elapsed!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_processing_prepare_5ea30c();
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,
                                         &audio_terminal_voice_icon_773044);
        audio_uart_page_49942e((void *)(uintptr_t)hint,recording);
        audio_uart_page_49942e((void *)(uintptr_t)elapsed,release);
        audio_terminal_elapsed_clear_5e4894();
    }
    uint8_t packet=0u;
    audio_uart_buffer_zero(&packet,1u,0u);
    packet=1u;
    audio_terminal_encode_voice_input_5cec72(&packet);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(3u,module,path,function,0x430u,message);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x0c000000u,short_message,short_message);
    return 0u;
}
