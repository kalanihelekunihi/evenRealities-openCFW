/* Entire native getters44e42c..44e441,44e442..44e459,44fbe6..44fbfb.
 * Source lv_obj_scroll.c94-105 and lv_display.c430-436; native storage widths retained. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);
uint32_t audio_uart_lv_get_scrollbar_mode_44e42c(const void *object)
{
 const volatile uint32_t *slot=(const volatile uint32_t *)((const uint8_t *)object+8);
 if(*slot==0u)return 3u;
 return *(const volatile uint8_t *)((uintptr_t)*slot+50u)&3u;
}
uint32_t audio_uart_lv_get_scroll_dir_44e442(const void *object)
{
 const volatile uint32_t *slot=(const volatile uint32_t *)((const uint8_t *)object+8);
 if(*slot==0u)return 15u;
 return (*(const volatile uint16_t *)((uintptr_t)*slot+50u)>>6)&15u;
}
int32_t audio_uart_lv_display_dpi_44fbe6(void *display)
{
 if(display==0)display=audio_uart_display_default_get();
 if(display==0)return 130;
 return *(const volatile int32_t *)((const uint8_t *)display+24u);
}
