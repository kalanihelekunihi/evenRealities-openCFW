/* Native tracepoint deferred-flush helpers 0x47dce4, 0x47ddac..0x47de0a and
 * 0x47e232..0x47e272 (adjacent to the /log/tp tracepoint store, TPS1 state
 * record). No source path string survives for these functions.
 *
 * The one-shot FreeRTOS timer "tracepoint_defer" (handle RAM 0x20074acc,
 * static control block RAM 0x20073758) is re-armed with the timer command 4
 * (change period, which also starts it): 2000 ticks when logging may wake the
 * system, otherwise 5000 ticks while a pull is still pending, at most ten
 * times (retry counter RAM 0x20074ad0, cleared by 0x47dd92). Existing g2/src
 * names for these RAM words and callees carry a legacy "ring_persist" label. */
#include <stdint.h>

#define TIMER_CMD_CHANGE_PERIOD 4u

extern volatile uint32_t audio_uart_ring_persist_event_object;  /* RAM 0x20074acc timer handle */
extern volatile uint32_t audio_uart_ring_persist_event_pending; /* RAM 0x20074ad0 retry count */
extern uint8_t g2_tracepoint_defer_timer_buffer[44];             /* RAM 0x20073758 StaticTimer_t */

extern uint32_t audio_log_wake_allowed(void);                    /* 0x443484 */
extern int32_t audio_tracepoint_pull_ready_48eb90(void);         /* 0x48eb90 */
extern uint32_t audio_uart_ring_persist_wait_event_47e7b0(uint32_t timer, uint32_t command,
                                                          uint32_t value, void *isr_woken,
                                                          uint32_t wait_ticks); /* 0x47e7b0 xTimerGenericCommand */
extern uint32_t crc32_4d34c4(const void *data, uint32_t length, const uint32_t *seed); /* 0x4d34c4 */
extern void *audio_freertos_timer_create_static(const char *, uint32_t, uint32_t, uintptr_t,
                                                void (*)(void *), void *); /* 0x47e712 */
extern uint32_t audio_wsf_interrupt_mask_set(void);              /* 0x5fa0a4 ulSetInterruptMask */
extern void audio_uart_ring_persist_initialize_48eac8(void);     /* 0x48eac8 */
extern void audio_uart_ring_persist_notify_47dd92(void);         /* 0x47dd92 */
extern void audio_uart_ring_persist_event_set_47dd62(void);      /* 0x47dd62 */

static const char timer_name[] = "tracepoint_defer"; /* ROM 0x7844f0 */

/* 0x47dce4: MRS PRIMASK; CPSID i; returns the previous PRIMASK. */
__attribute__((naked)) uint32_t g2_irq_save_47dce4(void)
{
    __asm__ volatile("mrs r0, PRIMASK\n\tcpsid i\n\tbx lr");
}

/* 0x47ddac: timer re-arm used by elog_async_ext_flieStore_Init (0x448e48). */
void tracepoint_defer_rearm_47ddac(void)
{
    if (audio_log_wake_allowed() != 0u) {
        (void)audio_uart_ring_persist_wait_event_47e7b0(audio_uart_ring_persist_event_object,
                                                        TIMER_CMD_CHANGE_PERIOD, 2000u, (void *)0, 0u);
    } else if (audio_tracepoint_pull_ready_48eb90() != 0 &&
               (int32_t)audio_uart_ring_persist_event_pending < 10) {
        audio_uart_ring_persist_event_pending = audio_uart_ring_persist_event_pending + 1u;
        (void)audio_uart_ring_persist_wait_event_47e7b0(audio_uart_ring_persist_event_object,
                                                        TIMER_CMD_CHANGE_PERIOD, 5000u, (void *)0, 0u);
    }
}

/* 0x47ddfe: CRC-32 of the first 12 bytes of the 16-byte TPS1 state record
 * (called from the state writer 0x47df28 and reader 0x47df8a). */
uint32_t tracepoint_state_crc_47ddfe(const void *record)
{
    return crc32_4d34c4(record, 12u, 0);
}

/* 0x47dd8a (not in the function inventory): timer callback, 8 bytes. */
void tracepoint_defer_timer_callback_47dd8a(void *timer)
{
    (void)timer;
    audio_uart_ring_persist_event_set_47dd62();
}

/* 0x47e232: one-time setup, called from 0x4c951c. A failed static timer
 * create is fatal: mask interrupts, fault on a store to 0xffffffff, spin. */
void tracepoint_defer_init_47e232(void)
{
    if (audio_uart_ring_persist_event_object == 0u) {
        audio_uart_ring_persist_event_object = (uint32_t)(uintptr_t)
            audio_freertos_timer_create_static(timer_name, 2000u, 0u, 0u,
                                               tracepoint_defer_timer_callback_47dd8a,
                                               g2_tracepoint_defer_timer_buffer);
        if (audio_uart_ring_persist_event_object == 0u) {
            (void)audio_wsf_interrupt_mask_set();
            *(volatile uint32_t *)0xffffffffu = 0u;
            for (;;) {
            }
        }
        audio_uart_ring_persist_initialize_48eac8();
        audio_uart_ring_persist_notify_47dd92();
    }
}
