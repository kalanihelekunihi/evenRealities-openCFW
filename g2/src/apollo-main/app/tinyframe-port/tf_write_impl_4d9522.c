/* TinyFrame port: TF_WriteImpl, stock 0x4D9522..0x4D952F (sync framework
 * TU). TinyFrame eb75483e calls it for every composed chunk; stock forwards
 * (buffer, length) to the UART service send wrapper 0x541790 with the fixed
 * timeout 100 (movs r2, #100) and drops the result. */
#include <stdint.h>

struct TinyFrame_;
extern uint32_t audio_uart_sync_send(const void *bytes, uint32_t size,
                                     uint32_t timeout); /* 0x541790 */

void TF_WriteImpl(struct TinyFrame_ *tf, const uint8_t *buff, uint32_t len)
{
    (void)tf;
    (void)audio_uart_sync_send(buff, len, 100u);
}
