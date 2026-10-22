/* Native 0x46cf56, ring-list head accessor. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char audio_uart_ring_head_module[]="font_manager"; /* ROM0x00787a50 */
static const char audio_uart_ring_head_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\lvgl_font_manager.c"; /* ROM0x006fb45c */
static const char audio_uart_ring_head_function[]="font_manager_get_font"; /* ROM0x0077958c */
static const char audio_uart_ring_head_error[]="Invalid manager handle"; /* ROM0x007795a4 */
static const char audio_uart_ring_head_short[]="[font_manager]Invalid manager handle"; /* ROM0x0074b16c */
/* Stock 0x46CF56 (font_manager_get_font) */
void *audio_uart_display_ring_head(const uint32_t *list) {
    if(list!=0) return (void *)(uintptr_t)list[0];
    if(audio_log_flags()&2u)
        audio_log_extended(1u,audio_uart_ring_head_module,
                           audio_uart_ring_head_source,
                           audio_uart_ring_head_function,0xc6u,
                           audio_uart_ring_head_error);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x04000000u,
              audio_uart_ring_head_short,audio_uart_ring_head_short);
    return 0;
}
