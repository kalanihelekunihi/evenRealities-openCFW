#include <stdint.h>

extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern void vListInitialise(void *);
extern void *xQueueGenericCreateStatic(uint32_t, uint32_t, uint8_t *, void *, uint8_t);

void audio_daemon_initialize_queue(void) {
    void * volatile * const queue = (void * volatile *)(uintptr_t)0x20074ab0u;
    stock_enter_critical();
    if (!*queue) {
        vListInitialise((void *)(uintptr_t)0x20073d60u);
        vListInitialise((void *)(uintptr_t)0x20073d74u);
        *(void * volatile *)(uintptr_t)0x20074aa8u = (void *)(uintptr_t)0x20073d60u;
        *(void * volatile *)(uintptr_t)0x20074aacu = (void *)(uintptr_t)0x20073d74u;
        *queue = xQueueGenericCreateStatic(50, 16,
            (uint8_t *)(uintptr_t)0x2006d7b4u,
            (void *)(uintptr_t)0x20072ee8u, 0);
    }
    stock_exit_critical();
}
