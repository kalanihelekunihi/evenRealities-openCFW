/* Product RTOS objects of Apollo main: CMSIS-RTOS2 handles created by the
 * rtos-glue-gaps initialisers, FreeRTOS static idle-task memory supplied by
 * vApplicationGetIdleTaskMemory_48d558, the Apollo STIMER tick/tickless port
 * state (a-04, Ambiq port, not the pinned kernel) and UART sync error
 * counters. FreeRTOS kernel statics belong to the upstream kernel units.
 * All cells are zero-initialised; sizes match the referencing declarations
 * and the gap to the next stock object. */
#include <stdint.h>

/* CMSIS-RTOS2 handles. */
void *g2_elog_mutex;       /* RAM 0x20074578 (elog port mutex, osMutexNew) */
void *g2_menu_page_mutex;  /* RAM 0x200746e4 */
void *g2_navigation_mutex; /* RAM 0x2007471c */
void *g2_shell_thread;     /* RAM 0x200748b8 */
void *g2_shell_rx_stream;  /* RAM 0x200748bc StreamBufferHandle_t */

/* Idle task: StaticTask_t (G2 TCB is 0x70 B) and StackType_t[0x400]. */
uint8_t g2_idle_task_tcb_20071e30[0x70] __attribute__((aligned(8)));  /* RAM 0x20071e30 */
uint32_t g2_idle_task_stack_2005f154[0x400] __attribute__((aligned(8))); /* RAM 0x2005f154 */

/* Apollo STIMER tickless port (port_stimer_tickless.c). */
uint32_t g2_port_last_stimer_value;     /* RAM 0x20074884 g_lastSTimerVal */
uint32_t g2_port_timer_counts_per_tick; /* RAM 0x20074888 ulTimerCountsForOneTick */
uint32_t g2_port_max_suppressed_ticks;  /* RAM 0x2007488c xMaximumPossibleSuppressedTicks */

/* UART sync receive error counters (uart_sync_irq.c). */
volatile uint32_t g2_uart_sync_framing_errors; /* RAM 0x20074624 */
volatile uint32_t g2_uart_sync_parity_errors;  /* RAM 0x20074628 */
volatile uint32_t g2_uart_sync_break_errors;   /* RAM 0x2007462c */

/* SyncTimeoutDetectionThreadStartup 0x45d34c log module and source
 * (literal pool 0x45d7cc/0x45d7d0 -> ROM 0x705fb8 / 0x77c07c). The other
 * strings of that function are in system/log/sync-timer. */
const char audio_uart_timer_module[] = "sync.module.framework"; /* ROM 0x77c07c */
const char audio_uart_timer_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c"; /* ROM 0x705fb8 */
