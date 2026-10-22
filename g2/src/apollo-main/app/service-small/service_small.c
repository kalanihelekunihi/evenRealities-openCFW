/* Native service state getter 0x45a570 and transport reset 0x5417c4. */
#include <stdint.h>
extern volatile uint8_t g2_audio_service_mode; /* cell 0x20075024 */
extern uint32_t audio_uart_sync_reset0(void); /* 0x584bc0 */
extern void audio_uart_sync_reset1(void (*callback)(void)); /* 0x584c8c */
extern uint32_t audio_uart_sync_reset2(void); /* 0x584db6 */
extern void audio_uart_sync_callback(void); /* authenticated literal 0x5417a5 */
/* Stock 0x45A570 (service-mode byte getter, audio_uart_service_mode) */
uint32_t audio_uart_service_mode(void) {return g2_audio_service_mode;}
uint32_t audio_uart_service_version(void) {return g2_audio_service_mode;}
/* Stock 0x5417C4 (uart_sync_transport_reset) */
void audio_uart_service_prepare1(void)
{
    (void)audio_uart_sync_reset0();
    audio_uart_sync_reset1(audio_uart_sync_callback);
    (void)audio_uart_sync_reset2();
}
