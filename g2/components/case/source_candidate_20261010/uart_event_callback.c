#include <stdint.h>

/* Original 0x08005e6a is exactly `bx lr`. Stock RX8/RX16 helpers branch
 * here for the HAL UART receive-event callback in TOIDLE mode. */
void HAL_UARTEx_RxEventCallback(void *uart,uint16_t size)
{
    (void)uart;
    (void)size;
}
