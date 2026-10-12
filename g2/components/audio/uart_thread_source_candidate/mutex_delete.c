/* Native CMSIS osMutexDelete 0x44986e, used by thread-pool rollback.
 * Bit zero is the recursive-mutex tag; queue handle is the masked pointer. */
#include <stdint.h>
extern uint32_t audio_irq_context(void); /* selected IRQ_Context 0x44900e */
extern int32_t audio_queue_delete(void *); /* selected vQueueDelete 0x441ea2 */
int32_t audio_uart_mutex_delete(void *mutex) {
    uintptr_t q=(uintptr_t)mutex&~(uintptr_t)1u;
    if(audio_irq_context()!=0u) return -6;
    if(q==0u) return -4;
    (void)audio_queue_delete((void *)q);
    return 0;
}
