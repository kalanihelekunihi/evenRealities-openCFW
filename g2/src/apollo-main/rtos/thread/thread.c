/* Native UART service thread 0x5417d6..0x541a2d.
 * Product strings, handles, callback, and buffers are unresolved typed data.
 * Dependency ABI follows the authenticated call sites; downstream drivers and
 * an infinite event loop require separate execution qualification. */
#include <stdint.h>
#include <stddef.h>
extern void *g2_uart_thread_mutex; /* pointer cell 0x20074b18; osMutexNew */
extern void *g2_uart_thread_event; /* pointer cell 0x20074b10; osEventFlagsNew */
extern void *g2_uart_thread_transport; /* pointer cell 0x20074b14 */
extern void (*g2_uart_thread_initialize_callback)(void); /* pointer cell 0x20000658 */
extern uint8_t g2_uart_command[/* >= 11 */]; /* 0x20074080 */
extern uint8_t g2_uart_rx_buffer[1024]; /* 0x2006c930 */
extern const char g2_uart_log_module[],g2_uart_log_file[],g2_uart_log_function[];
extern const char g2_uart_event_error[],g2_uart_mutex_error[],g2_uart_transport_error[],g2_uart_ready_error[];
extern const char g2_uart_event_error_short[],g2_uart_mutex_error_short[],g2_uart_transport_error_short[],g2_uart_ready_error_short[];
extern const char g2_uart_command_log[],g2_uart_command_log_short[];
extern void *audio_uart_mutex_new(uint32_t); /* 0x44971c */
extern void *audio_uart_event_new(uint32_t); /* 0x449590 */
extern void *audio_uart_transport_new(uint32_t,uint32_t,uint32_t,void *,void *,uint32_t,uint32_t); /* 0x57df7c */
extern uint32_t audio_uart_ready(void); /* 0x45e8d0 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_uart_service_prepare0(void); /* 0x444720 */
extern void audio_uart_service_prepare1(void); /* 0x5417c4 */
extern void audio_uart_service_prepare2(void); /* 0x584e94 */
extern void audio_uart_service_prepare3(uint32_t); /* 0x4ac828 */
extern uint32_t audio_uart_service_mode(void); /* 0x45a570 */
extern void audio_uart_service_prepare4(void); /* 0x471528 */
extern void audio_uart_service_prepare5(void); /* 0x47e4a6 */
extern void audio_uart_service_prepare6(void); /* 0x47d818 */
extern void audio_uart_service_prepare7(void); /* 0x4ff99a */
extern uint32_t audio_uart_service_prepare8(void); /* 0x501d5c */
extern void audio_uart_service_prepare9(uint32_t); /* 0x501066 */
extern uint32_t audio_event_wait(void *,uint32_t,uint32_t,uint32_t); /* selected 0x44969c */
extern uint32_t audio_uart_event_clear(void *,uint32_t); /* 0x449642 */
extern uint32_t audio_uart_command_pending(void); /* 0x4abe60 */
extern uint32_t audio_uart_transport_receive(void *,void *,uint32_t,uint32_t); /* 0x57e136 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void audio_uart_process_receive(void *,uint32_t); /* 0x45d4dc */
extern void audio_uart_process_event2(void); /* 0x45e664 */
extern void audio_uart_process_event4(void); /* 0x45d4b8 */
static void failure_log(uint32_t line,const char *long_message,const char *short_message)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(1,g2_uart_log_module,g2_uart_log_file,g2_uart_log_function,line,long_message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        compressed_log_output(0x04000000u,short_message,short_message);
}
void uart_thread_handler(void *argument)
{
    (void)argument;
    g2_uart_thread_mutex=audio_uart_mutex_new(0);
    if (!g2_uart_thread_mutex) {failure_log(0x60,g2_uart_mutex_error,g2_uart_mutex_error_short);return;}
    g2_uart_thread_event=audio_uart_event_new(0);
    if (!g2_uart_thread_event) {failure_log(0x66,g2_uart_event_error,g2_uart_event_error_short);return;}
    g2_uart_thread_transport=audio_uart_transport_new(0x6000u,1u,0u,(void *)(uintptr_t)0x203195e4u,(void *)(uintptr_t)0x200738b8u,0u,0u);
    if (!g2_uart_thread_transport) {failure_log(0x71,g2_uart_transport_error,g2_uart_transport_error_short);return;}
    if (audio_uart_ready()!=0u) {failure_log(0x76,g2_uart_ready_error,g2_uart_ready_error_short);return;}
    g2_uart_thread_initialize_callback();
    audio_uart_service_prepare0();audio_uart_service_prepare1();audio_uart_service_prepare2();
    audio_uart_service_prepare3(3u);
    if (audio_uart_service_mode()==2u) audio_uart_service_prepare4();
    audio_uart_service_prepare5();audio_uart_service_prepare6();audio_uart_service_prepare7();
    (void)audio_uart_service_prepare8();audio_uart_service_prepare9(1u);
    for (;;) {
        uint32_t bits=audio_event_wait(g2_uart_thread_event,7u,2u,UINT32_MAX);
        if (bits&1u) {
            audio_uart_event_clear(g2_uart_thread_event,1u);
            if (audio_uart_command_pending()==1u && g2_uart_command[0]==1u) {
                g2_uart_command[0]=0;
                (void)audio_uart_transport_receive(g2_uart_thread_transport,g2_uart_command+1u,10u,0u);
                if (audio_log_flags()&2u)
                    audio_log_extended(3,g2_uart_log_module,g2_uart_log_file,g2_uart_log_function,0x9fu,g2_uart_command_log,g2_uart_command+1u);
                if ((audio_log_flags()&1u)||(audio_log_flags()&4u))
                    compressed_log_output(0x0c400000u,g2_uart_command_log_short,g2_uart_command_log_short,g2_uart_command+1u);
                continue;
            }
            uint32_t total=0u,iterations=0u;
            for (;;) {
                audio_uart_buffer_zero(g2_uart_rx_buffer,1024u,0u);
                uint32_t count=audio_uart_transport_receive(g2_uart_thread_transport,g2_uart_rx_buffer,1024u,0u);
                if (!count) break;
                total+=count;
                audio_uart_process_receive(g2_uart_rx_buffer,count);
                ++iterations;
                if (total>=32768u || iterations>=32u) break;
            }
        }
        if (bits&2u) {audio_uart_event_clear(g2_uart_thread_event,2u);audio_uart_process_event2();}
        if (bits&4u) {audio_uart_event_clear(g2_uart_thread_event,4u);audio_uart_process_event4();}
    }
}
