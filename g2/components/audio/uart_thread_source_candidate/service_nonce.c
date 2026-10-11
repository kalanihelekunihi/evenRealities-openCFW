/* Native 0x4ac776 four-byte product nonce snapshot. */
#include <stdint.h>
extern volatile uint8_t g2_uart_service_nonce[4]; /* object 0x20074928 */
uint32_t audio_uart_service_nonce(uint8_t out[4])
{
    if (!out) return UINT32_MAX;
    for (uint32_t i=0;i<4u;i++) out[i]=g2_uart_service_nonce[i];
    return 0u;
}
