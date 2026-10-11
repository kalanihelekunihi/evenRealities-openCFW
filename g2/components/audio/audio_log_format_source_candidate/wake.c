/* Stock 0x443484,0x4487ac and 0x448f7c selected wake predicates/actions. */
#include <stdint.h>
extern volatile uint8_t g2_audio_log_wake_enabled; /* 0x20074f2c */
extern volatile uint8_t g2_audio_log_transport_bits; /* 0x20075043 */
extern volatile uint8_t g2_audio_log_transport_alt; /* 0x20072730 */
extern uint32_t g2_audio_log_event_handle; /* pointer cell 0x20074570 */
extern void g2_log_transport_signal(uint32_t event_handle,uint32_t bits);
uint32_t audio_log_wake_allowed(void)
{
    return g2_audio_log_wake_enabled==1u;
}
uint32_t audio_log_transport_ready(void)
{
    if(g2_audio_log_transport_bits&1u) return 1u;
    if(g2_audio_log_transport_bits&2u) return 1u;
    return g2_audio_log_transport_alt==1u;
}
void audio_log_transport_wake(void)
{
    if(g2_audio_log_event_handle)
        g2_log_transport_signal(g2_audio_log_event_handle,2u);
}
