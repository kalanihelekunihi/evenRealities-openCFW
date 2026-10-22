/* init_ui_modules native 0x4425a6: source table ROM0x6a44b0..0x6a4760
 * contains 43 sixteen-byte registrations. RAM rows are 0x20066230. */
#include <stdint.h>
extern const uint8_t audio_uart_display_registry_begin[]; /* ROM0x6a44b0 */
extern const uint8_t audio_uart_display_registry_end[]; /* ROM0x6a4760 */
extern volatile uint32_t audio_uart_user_registry_count; /* RAM0x200744d4 */
extern uint8_t audio_uart_user_registry_rows[]; /* RAM0x20066230 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="display_thread";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\display_thread.c";
static const char fn[]="init_ui_modules";
static const char extended[]="ui modules count = %d";
static const char compact[]="[display_thread]ui modules count = %d";
/* Stock 0x4425A6 (init_ui_modules) */
void audio_uart_display_service_init(void) {
    uintptr_t first=(uintptr_t)audio_uart_display_registry_begin;
    uintptr_t last=(uintptr_t)audio_uart_display_registry_end;
    uint32_t count=(uint32_t)((last-first)>>4u);
    if(count>128u) count=128u;
    audio_uart_user_registry_count=count;
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source,fn,0xabu,extended,count);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10400000u,compact,compact,count);
    (void)audio_queue_copy_bytes(audio_uart_user_registry_rows,
                                 audio_uart_display_registry_begin,count<<4u);
}
