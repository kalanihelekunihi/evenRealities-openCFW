/* Terminal pending selector prompt, stock 0x5ece4c..0x5eceb0. */
#include <stdint.h>
#include "terminal_reset_assets_20261016.h"

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern void audio_terminal_ui_stop_service_a_5eceb2(void);
extern void audio_terminal_session_root_hide_5ed1d6(void);
extern void audio_terminal_processing_prepare_5ea30c(void);
extern void audio_uart_page_43dfa4(void *,uint32_t);
extern void audio_terminal_image_set_5e47fe(void *,const void *);
extern const char *audio_uart_page_49942e(uint8_t *,const char *);

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

void audio_terminal_session_pending_prompt_5ece4c(const char *message) {
    audio_terminal_ui_stop_service_a_5eceb2();
    audio_terminal_session_root_hide_5ed1d6();
    audio_terminal_processing_prepare_5ea30c();
    uint32_t icon=word(0x1ccu),title=word(0x1d0u);
    uint32_t label=word(0x1d4u),hint=word(0x1dcu);
    if (icon!=0u && title!=0u && label!=0u && hint!=0u) {
        audio_uart_page_43dfa4((void *)(uintptr_t)icon,1u);
        audio_terminal_image_set_5e47fe((void *)(uintptr_t)title,&audio_terminal_asset_7733a8);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,message);
        (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)hint,"");
    }
    audio_terminal_ui_state_base[0x27du]=1u;
}
