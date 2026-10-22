/* Product RTOS glue, stock D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\rtos.c.
 * Native 0x46d6b6..0x46d70e, 0x46d7e6..0x46d816 and 0x46d836..0x46d8a0; literal pool
 * 0x46d878..0x46d897. The rest of the task-vote graph (0x46d67c..0x46d836) is in
 * rtos/task-vote/task_vote_runtime.c.
 *
 * Task-vote state RAM 0x200700e0: 32 eight-byte {task handle, voted} slots, the number of
 * active votes at +0x100 and an "initialised" byte at +0x104. Any active vote keeps the
 * idle hook in normal sleep instead of deep sleep. The FreeRTOS sleep, wakeup and idle
 * hooks each feed the MCU watchdog first (0x4b29f8 -> am_hal_wdt_restart, RSTRT = 0xB2). */
#include <stdint.h>

extern volatile uint8_t audio_task_vote_state_200700e0[]; /* RAM 0x200700e0, 0x108 bytes cleared */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t value); /* 0x43c0e4 memset */
extern uint32_t g2_main_critical_save_473940(void);       /* PRIMASK save + disable */
extern void watchdog_feed_4b29f8(void);                    /* am_hal_wdt_restart(AM_HAL_WDT_MCU) */
extern uint32_t am_hal_sysctrl_sleep_44ab42(uint32_t deep); /* 1 = deep sleep */
extern void audio_ble_hci_boot_log_4733ee(const char *fmt, ...); /* am_util_stdio_printf */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "rtos"; /* ROM 0x78e46c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\rtos.c"; /* ROM 0x70522c */
static const char vote_init_fn[] = "task_vote_init"; /* ROM 0x788630 */
static const char vote_init_msg[] = "Task vote system initialized"; /* ROM 0x764810 */
static const char vote_init_short[] = "[rtos]Task vote system initialized"; /* ROM 0x758f4c */
static const char malloc_failed_msg[] = "MallocFailed: cannot malloc memory\n"; /* ROM 0x758f70 */
static const char stack_overflow_msg[] = "task %s stack overflow\n"; /* ROM 0x77b1c4 */

static inline void set_primask(uint32_t value)
{
    __asm__ volatile("msr primask, %0" : : "r"(value) : "memory");
}

void task_vote_init(void)
{
    volatile uint8_t *state = audio_task_vote_state_200700e0;
    audio_uart_buffer_zero((void *)state, 0x108u, 0u);
    state[0x104] = 1u;
    *(volatile uint32_t *)(volatile void *)(state + 0x100) = 0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, vote_init_fn, 0x84u, vote_init_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, vote_init_short, vote_init_short);
}

uint8_t task_vote_blocks_deep_sleep(void)
{
    volatile uint8_t *state = audio_task_vote_state_200700e0;
    if (state[0x104] == 0u)
        return 0u;
    uint32_t primask = g2_main_critical_save_473940();
    uint8_t blocked = *(volatile uint32_t *)(volatile void *)(state + 0x100) != 0u;
    set_primask(primask);
    return blocked;
}

uint32_t am_freertos_sleep(uint32_t idle_time)
{
    (void)idle_time;
    watchdog_feed_4b29f8();
    if (task_vote_blocks_deep_sleep() != 0u)
        (void)am_hal_sysctrl_sleep_44ab42(0u);
    else
        (void)am_hal_sysctrl_sleep_44ab42(1u);
    return 0u;
}

void am_freertos_wakeup(uint32_t idle_time)
{
    (void)idle_time;
    watchdog_feed_4b29f8();
}

void vApplicationMallocFailedHook(void)
{
    audio_ble_hci_boot_log_4733ee(malloc_failed_msg);
    for (;;) {
    }
}

void vApplicationStackOverflowHook(void *task, char *task_name)
{
    (void)task;
    audio_ble_hci_boot_log_4733ee(stack_overflow_msg, task_name);
    for (;;)
        __asm__ volatile("bkpt #0");
}

void vApplicationIdleHook(void)
{
    watchdog_feed_4b29f8();
}
