/* UART service send wrapper 0x541790. The native callee 0x584c98 returns
 * zero on success; the wrapper exposes 0 or UINT32_MAX. The third caller
 * word is ignored by this native entry, as verified from Thumb instructions. */
#include <stdint.h>
extern uint32_t audio_uart_sync_write(const void *,uint32_t); /* 0x584c98 */
uint32_t audio_uart_sync_send(const void *bytes,uint32_t size,uint32_t timeout) {
    (void)timeout;
    return audio_uart_sync_write(bytes,size)==0u ? 0u : UINT32_MAX;
}
