/* Native WsfTrace 0x52a63c; formatter/print are selected Main providers. */
#include <stdint.h>
#include <stdarg.h>

extern int32_t g2_log_transport_vformat_unbounded(char *,const char *,va_list);
extern int32_t g2_log_transport_queue_failure(const char *,...); /* 0x4733ee */
extern void audio_ble_wsf_assert(const char *,uint32_t); /* 0x569a44 */

void audio_ble_wsf_trace(const char *format,...) {
    char buffer[1024];
    va_list args;
    va_start(args,format);
    (void)g2_log_transport_vformat_unbounded(buffer,format,args);
    va_end(args);
    uint32_t count=(uint32_t)g2_log_transport_queue_failure(buffer);
    if(count>0x3ffu)
        audio_ble_wsf_assert("D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\wsf\\sources\\port\\freertos\\wsf_trace.c",0x89u);
    (void)g2_log_transport_queue_failure("\n");
}
/* HCI/L2CAP users name this same native 0x52a63c entry. */
void audio_ble_hci_wsf_trace(const char *,...)
    __attribute__((alias("audio_ble_wsf_trace")));
