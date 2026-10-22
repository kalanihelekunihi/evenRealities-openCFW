/* Ambiq FreeRTOS STIMER tick and tickless idle for the ARM_CM55_NTZ port
 * (AmbiqSuite port.c, AM_FREERTOS_USE_STIMER_FOR_TICK lineage; no pinned copy
 * of the Apollo5 variant exists under third-party/upstream).
 * Native 0x456358..0x45655c, literal pool 0x45655c..0x45657f:
 *   0x456358 / 0x456374 / 0x456390  CMSIS __NVIC_EnableIRQ / __NVIC_ClearPendingIRQ /
 *                                   __NVIC_SetPriority out-of-line static copies
 *   0x4563b4  xPortStimerTickHandler  (STIMER compare-0 tick service)
 *   0x456426  STIMER interrupt entry  (status bit 0 -> clear -> tick service)
 *   0x45643e  vPortSetupTimerInterrupt (overrides the port's weak SysTick setup)
 *   0x456498  vPortSuppressTicksAndSleep (overrides the weak port version)
 * Stock names of the four port functions are the Ambiq ones above; rows have no
 * TSV name, so they carry an address suffix here.
 *
 * STIMER runs at 32.768 kHz; 32 counts per tick gives configTICK_RATE_HZ 1024.
 * STIMER is IRQ 32 (NVIC priority 0xff -> 0xf0, 4 priority bits). */
#include <stdint.h>

/* Ambiq HAL STIMER (am_hal_stimer.c) at their stock addresses. */
extern uint32_t am_hal_stimer_config_48d588(uint32_t config);     /* returns previous CFG */
extern uint32_t am_hal_stimer_counter_get_48d654(void);
extern uint32_t am_hal_stimer_compare_delta_set_48d670(uint32_t compare, uint32_t delta);
extern void am_hal_stimer_int_enable_48d6dc(uint32_t mask);
extern void am_hal_stimer_int_clear_48d6e6(uint32_t mask);
extern uint32_t am_hal_stimer_int_status_get_48d6f0(uint32_t enabled_only);

/* FreeRTOS kernel (tasks.c) and port (ARM_CM55_NTZ portasm) entries. */
extern uint32_t xTaskIncrementTick_45504c(void);
extern void vTaskStepTick_454fd8(uint32_t ticks_to_jump);
extern uint32_t eTaskConfirmSleepModeStatus_455648(void);      /* 0 = eAbortSleep */
extern uint32_t ulSetInterruptMask(void);                      /* 0x5fa0a4 */
extern void vClearInterruptMask(uint32_t mask);                /* 0x5fa0ba */

/* Product power hooks (g2-product-rtos). */
extern uint32_t am_freertos_sleep(uint32_t idle_time);         /* 0x46d836 */
extern void am_freertos_wakeup(uint32_t idle_time);            /* 0x46d856 */

extern uint32_t g2_port_last_stimer_value;         /* RAM 0x20074884 g_lastSTimerVal */
extern uint32_t g2_port_timer_counts_per_tick;     /* RAM 0x20074888 ulTimerCountsForOneTick */
extern uint32_t g2_port_max_suppressed_ticks;      /* RAM 0x2007488c xMaximumPossibleSuppressedTicks */

#define NVIC_ISER ((volatile uint32_t *)0xe000e100u)
#define NVIC_ICPR ((volatile uint32_t *)0xe000e280u)
#define NVIC_IP   ((volatile uint8_t *)0xe000e400u)
#define SCB_SHPR  ((volatile uint8_t *)0xe000ed18u)
#define SCB_ICSR  (*(volatile uint32_t *)0xe000ed04u)
#define SCB_ICSR_PENDSVSET 0x10000000u

#define STIMER_IRQ 32
#define STIMER_COMPARE_A 1u          /* AM_HAL_STIMER_INT_COMPAREA */
#define STIMER_CFG_FREEZE 0x80000000u
#define STIMER_CFG_KEEP_MASK 0x7ffffff0u
#define STIMER_CFG_RUN_XTAL_CMPA 0x103u  /* CLKSEL 3 (32 kHz XTAL) + COMPARE_A_EN */

/* Stock 0x456358 (__NVIC_EnableIRQ inline copy; CMSIS core_cm55.h) */
static void __NVIC_EnableIRQ(int16_t irq)
{
    if (irq >= 0)
        NVIC_ISER[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

/* Stock 0x456374 (__NVIC_ClearPendingIRQ inline copy; CMSIS core_cm55.h) */
static void __NVIC_ClearPendingIRQ(int16_t irq)
{
    if (irq >= 0)
        NVIC_ICPR[(uint32_t)irq >> 5] = 1u << ((uint32_t)irq & 31u);
}

/* Stock 0x456390 (__NVIC_SetPriority inline copy; CMSIS core_cm55.h) */
static void __NVIC_SetPriority(int16_t irq, uint32_t priority)
{
    if (irq >= 0)
        NVIC_IP[irq] = (uint8_t)(priority << 4);
    else
        SCB_SHPR[((uint32_t)irq & 15u) - 4u] = (uint8_t)(priority << 4);
}

/* STIMER counts since the last tick boundary, tolerating one counter wrap
 * (the wrap branch is off by one, as in the Ambiq port). */
static uint32_t stimer_elapsed(uint32_t now)
{
    if (now < g2_port_last_stimer_value)
        return now + (UINT32_MAX - g2_port_last_stimer_value);
    return now - g2_port_last_stimer_value;
}

/* Re-arms compare 0 at the next tick boundary and feeds every elapsed whole
 * tick to the kernel, requesting PendSV if any of them unblocked a task. */
void xPortStimerTickHandler_4563b4(void)
{
    uint32_t switch_required = 0u;
    uint32_t now = am_hal_stimer_counter_get_48d654();
    uint32_t elapsed = stimer_elapsed(now);
    uint32_t ticks = elapsed / g2_port_timer_counts_per_tick;
    uint32_t remainder = elapsed % g2_port_timer_counts_per_tick;

    g2_port_last_stimer_value = now - remainder;
    (void)am_hal_stimer_compare_delta_set_48d670(0u, g2_port_timer_counts_per_tick - remainder);
    (void)ulSetInterruptMask();
    while (ticks-- != 0u) {
        if (xTaskIncrementTick_45504c() != 0u)
            switch_required = 1u;
    }
    if (switch_required != 0u)
        SCB_ICSR = SCB_ICSR_PENDSVSET;
    vClearInterruptMask(0u);
}

/* STIMER interrupt service: only compare A drives the tick. */
void port_stimer_isr_456426(void)
{
    if ((am_hal_stimer_int_status_get_48d6f0(0u) & STIMER_COMPARE_A) != 0u) {
        am_hal_stimer_int_clear_48d6e6(STIMER_COMPARE_A);
        xPortStimerTickHandler_4563b4();
    }
}

void vPortSetupTimerInterrupt_45643e(void)
{
    uint32_t config;

    g2_port_timer_counts_per_tick = 32u;
    g2_port_max_suppressed_ticks = UINT32_MAX / g2_port_timer_counts_per_tick - 4u;
    am_hal_stimer_int_enable_48d6dc(STIMER_COMPARE_A);
    __NVIC_SetPriority(STIMER_IRQ, 0xffu);
    __NVIC_EnableIRQ(STIMER_IRQ);
    config = am_hal_stimer_config_48d588(STIMER_CFG_FREEZE);
    g2_port_last_stimer_value = am_hal_stimer_counter_get_48d654();
    (void)am_hal_stimer_compare_delta_set_48d670(0u, g2_port_timer_counts_per_tick);
    (void)am_hal_stimer_config_48d588((config & STIMER_CFG_KEEP_MASK) | STIMER_CFG_RUN_XTAL_CMPA);
}

/* Tickless idle: program compare 0 for the whole idle span, let the product
 * hook choose the sleep, then account for the ticks actually slept. */
void vPortSuppressTicksAndSleep_456498(uint32_t expected_idle)
{
    uint32_t now;
    uint32_t elapsed;
    uint32_t slept;
    uint32_t remainder;

    if (expected_idle > g2_port_max_suppressed_ticks)
        expected_idle = g2_port_max_suppressed_ticks;
    __asm__ volatile("cpsid i\n\tdsb sy\n\tisb sy" ::: "memory");
    if (eTaskConfirmSleepModeStatus_455648() == 0u) {
        __asm__ volatile("cpsie i" ::: "memory");
        return;
    }
    now = am_hal_stimer_counter_get_48d654();
    (void)am_hal_stimer_compare_delta_set_48d670(
        0u, expected_idle * g2_port_timer_counts_per_tick - stimer_elapsed(now));
    if (am_freertos_sleep(expected_idle) != 0u)
        __asm__ volatile("dsb sy\n\twfi\n\tisb sy" ::: "memory");
    am_freertos_wakeup(expected_idle);

    now = am_hal_stimer_counter_get_48d654();
    elapsed = stimer_elapsed(now);
    slept = elapsed / g2_port_timer_counts_per_tick;
    remainder = elapsed % g2_port_timer_counts_per_tick;
    g2_port_last_stimer_value = now - remainder;
    am_hal_stimer_int_clear_48d6e6(STIMER_COMPARE_A);
    __NVIC_ClearPendingIRQ(STIMER_IRQ);
    (void)am_hal_stimer_compare_delta_set_48d670(0u, g2_port_timer_counts_per_tick - remainder);
    vTaskStepTick_454fd8(slept < expected_idle ? slept : expected_idle);
    __asm__ volatile("cpsie i" ::: "memory");
}
