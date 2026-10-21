/* Native LV style dispatcher 0x44be4c. Retains seven genuine lower effects. */
#include <stdint.h>
extern uint32_t audio_uart_page_style_selector_44b860(uint32_t);
extern uint32_t audio_uart_page_style_resolve_44ca18(void *,uint32_t,uint8_t,void *);
extern void *audio_uart_page_style_local_44c5d4(void *,uint32_t);
extern uint32_t audio_uart_page_style_needs_invalidate_44b844(uint32_t,uint32_t);
extern void audio_uart_display_size_changed(void *); /* selected 0x440656 */
extern void audio_uart_page_style_value_482868(void *,uint32_t,uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *,uint32_t,uint32_t);

void audio_uart_page_style_apply_44be4c(void *object,uint8_t property,
                                        uint32_t value,uint32_t selector) {
    uint32_t resolved=audio_uart_page_style_selector_44b860(selector);
    (void)audio_uart_page_style_resolve_44ca18(object,resolved,property,0);
    void *local=audio_uart_page_style_local_44c5d4(object,selector);
    if(selector==0u && audio_uart_page_style_needs_invalidate_44b844(property,0x20u)!=0u)
        audio_uart_display_size_changed(object);
    audio_uart_page_style_value_482868(local,property,value);
    audio_uart_page_style_refresh_44bc8c(object,selector,property);
}
