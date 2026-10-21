/* Native SyncModuleReceivedDataHandler 0x45d4dc..0x45d535. */
#include <stdint.h>
extern void *g2_uart_sync_module; /* pointer cell 0x200749c4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char g2_uart_sync_module_name[],g2_uart_sync_source_file[],g2_uart_sync_receive_function[];
extern const char g2_uart_sync_uninit_message[],g2_uart_sync_uninit_short[];
extern void audio_uart_module_receive(void *,const void *,uint32_t); /* 0x491b9a */
void audio_uart_process_receive(const void *bytes,uint32_t length)
{
    void *module=g2_uart_sync_module;
    if (module) {audio_uart_module_receive(module,bytes,length);return;}
    if (audio_log_flags()&2u)
        audio_log_extended(2,g2_uart_sync_module_name,g2_uart_sync_source_file,
                           g2_uart_sync_receive_function,0x477u,g2_uart_sync_uninit_message);
    if ((audio_log_flags()&1u)||(audio_log_flags()&4u))
        compressed_log_output(0x08000000u,g2_uart_sync_uninit_short,g2_uart_sync_uninit_short);
}
