/* Experimental native reductions: ring transport write 0x57e05e and read
 * 0x57e136. Notification and task waiting remain real typed child contracts. */
#include <stdint.h>

extern void offline_assert(void) __attribute__((noreturn));
extern uint32_t audio_uart_ring_space(const void *);
extern uint32_t audio_uart_ring_available(const void *);
extern uint32_t audio_uart_ring_write(void *, const void *, uint32_t, uint32_t);
extern uint32_t audio_uart_ring_read(void *, void *, uint32_t, uint32_t);
extern uint32_t audio_port_mask_set(void);
extern void audio_port_mask_restore(uint32_t);
extern void stock_scheduler_suspend(void);
extern int32_t stock_scheduler_resume(void);
extern int32_t uart_notify_isr(void *, uint32_t, uint32_t, uint32_t,
                               uint32_t *, int32_t *); /* 0x455dc0 */
extern uint32_t audio_notify_task(void *, uint32_t, uint32_t,
                                  uint32_t, uint32_t *); /* 0x455c48 */
extern void *receiver_current_task(void); /* 0x45589c */
extern uint32_t audio_uart_wait_clear(void *, uint32_t); /* 0x455f5e */
extern int32_t audio_notify_wait(uint32_t, uint32_t, uint32_t,
                                 uint32_t *, uint32_t); /* 0x455b84 */

uint32_t audio_uart_transport_write(void *descriptor, const void *source,
                                    uint32_t length, uint32_t *wake) {
    if (source == 0 || descriptor == 0) offline_assert();
    uint8_t *d = (uint8_t *)descriptor;
    uint32_t written = audio_uart_ring_write(descriptor, source, length,
                                              audio_uart_ring_space(descriptor));
    if (written != 0u && *(uint32_t *)(d + 12u) <=
                         audio_uart_ring_available(descriptor)) {
        uint32_t mask = audio_port_mask_set();
        void *waiting = *(void **)(d + 16u);
        if (waiting != 0) {
            (void)uart_notify_isr(waiting, 0u, 0u, 0u, 0,
                                  (int32_t *)wake);
            *(uint32_t *)(d + 16u) = 0u;
        }
        audio_port_mask_restore(mask);
    }
    return written;
}

uint32_t audio_uart_transport_receive(void *descriptor, void *destination,
                                      uint32_t requested, uint32_t timeout) {
    if (destination == 0 || descriptor == 0) offline_assert();
    uint8_t *d = (uint8_t *)descriptor;
    uint32_t header = (d[28] & 1u) ? 4u : 0u;
    uint32_t available;
    if (timeout == 0u) {
        available = audio_uart_ring_available(descriptor);
    } else {
        stock_scheduler_suspend();
        available = audio_uart_ring_available(descriptor);
        if (available <= header) {
            (void)audio_uart_wait_clear(0, 0u);
            if (*(uint32_t *)(d + 16u) != 0u) offline_assert();
            *(uint32_t *)(d + 16u) =
                (uint32_t)(uintptr_t)receiver_current_task();
        }
        (void)stock_scheduler_resume();
        if (available <= header) {
            (void)audio_notify_wait(0u, 0u, 0u, 0, 0u);
            *(uint32_t *)(d + 16u) = 0u;
            available = audio_uart_ring_available(descriptor);
        }
    }
    uint32_t received = 0u;
    if (available > header) {
        received = audio_uart_ring_read(descriptor, destination, requested,
                                        available);
        if (received != 0u) {
            stock_scheduler_suspend();
            void *waiting = *(void **)(d + 20u);
            if (waiting != 0) {
                (void)audio_notify_task(waiting, 0u, 0u, 0u, 0);
                *(uint32_t *)(d + 20u) = 0u;
            }
            (void)stock_scheduler_resume();
        }
    }
    return received;
}
