/* CMSIS osSemaphoreAcquire 0x44994e is already source-reduced as
 * audio_semaphore_acquire. Expose the UART caller name with identical ABI. */
#include <stdint.h>
extern int32_t audio_semaphore_acquire(void *semaphore, uint32_t timeout);

int32_t audio_uart_semaphore_take(void *semaphore, uint32_t timeout) {
    return audio_semaphore_acquire(semaphore, timeout);
}
