/* Native 0x45d4b8..0x45d4d7: drain synchronization semaphore. */
#include <stdint.h>
extern void *g2_uart_sync_module; /* cell 0x200749c4 */
extern void *g2_uart_sync_semaphore; /* cell 0x200749d4 */
extern uint32_t audio_uart_semaphore_take(void *,uint32_t); /* 0x44994e */
extern void audio_uart_module_pump(void *); /* 0x492288 */
void audio_uart_process_event4(void)
{
    while (audio_uart_semaphore_take(g2_uart_sync_semaphore,0u)==0u)
        audio_uart_module_pump(g2_uart_sync_module);
}
