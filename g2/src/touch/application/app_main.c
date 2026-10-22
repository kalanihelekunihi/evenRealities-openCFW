/* SPDX-License-Identifier: MIT
 * Touch (PSoC 4000T) product main loop and CAPSENSE bring-up, official
 * 2.2.6.10 firmware_touch.bin native 0x38E0..0x3936 and 0x3CB4..0x3EA2.
 *
 * Application states (byte 0x200009CC) with budget u32 0x200009C8:
 *   1 ACT: active scan, sleep while busy, interval 7773 us; budget counts
 *          idle passes from 640, at 0 -> ALR (budget 160, 31211 us).
 *   2 ALR: active scan, deep sleep while busy; activity -> ACT; with a zero
 *          budget -> WOT. Budget is not decremented in this state.
 *   3 WOT: all four LP slots, deep sleep while busy; LP signal -> ACT,
 *          otherwise -> ALR. The LP launch status is discarded.
 * Not byte-identical by construction.
 */
#include <stdint.h>
#include <stddef.h>
#include "cy_syslib.h"
#include "cy_syspm.h"
#include "application.h"
#include "../calibration/calibration.h"
#include "../config-bootstrap/bootstrap.h"
#include "../pm-callbacks/callbacks.h"

typedef void (*g2_touch_isr)(void);

extern void *memset(void *dst, int value, size_t size);                                   /* 0xA9D4 */
extern uint32_t cybsp_init(void);                                                           /* 0x4650 (BSP) */
extern uint32_t touch_bootstrap_log(uint32_t format, uint32_t a, uint32_t b, uint32_t c);  /* 0x3EE0 */
extern void touch_deferred(void);                                                           /* 0x3A80 */
extern uint32_t touch_cap_init(uint8_t *context);                                           /* 0x4C7C Cy_CapSense_Init */
extern uint32_t touch_ilo_compensate(uint8_t *context);                                     /* 0x5DD8 */
extern uint32_t touch_set_active_interval(uint32_t microseconds, uint8_t *context);         /* 0x5D90 */
extern uint32_t touch_start_all_lp(uint8_t *context);                                       /* 0x7050 */
extern void touch_project_msclp_irq(void);                                                  /* 0x3948 */
extern uint32_t Cy_SysInt_Init(const g2_touch_sysint_config *config, g2_touch_isr handler); /* 0xA2A8 */
extern uint32_t Cy_CapSense_Enable(uint8_t *context);                                       /* 0x4AF4 */
extern uint32_t Cy_CapSense_ScanAllSlots(uint8_t *context);                                 /* 0x5C7A */
extern uint32_t Cy_CapSense_IsBusy(const uint8_t *context);                                 /* 0x5C8E */
extern uint32_t Cy_CapSense_ProcessAllWidgets(uint8_t *context);                            /* 0x4C04 */
extern uint32_t Cy_CapSense_IsAnyLpWidgetActive(const uint8_t *context);                    /* 0x7CF8 */

#define CTX              G2_TOUCH_CAPSENSE_CONTEXT
#define GPIO_P4_DR_SET   (*(volatile uint32_t *)0x40040440u)
#define NVIC_ISER        (*(volatile uint32_t *)0xE000E100u)
#define NVIC_ICPR        (*(volatile uint32_t *)0xE000E280u)

enum { STATE_ACT = 1u, STATE_ALR = 2u, STATE_WOT = 3u };
enum { BUDGET_ACT = 640u, BUDGET_ALR = 160u };
enum { INTERVAL_ACT_US = 7773u, INTERVAL_ALR_US = 31211u };   /* ROM 0x3EC0 / 0x3ECC */

static const char s_color_reset[] = "\x1b[0m";                         /* ROM 0xAA5C */
static const char s_version[] = "2.2.0.1";                             /* ROM 0xADA4 */
static const char s_tp_ver[] = "\x1b[36m[I] TP VER:%s%s\r\n";          /* ROM 0xADAC */
static const char s_act_alr[] = "\x1b[36m[I] ACT->ALR%s\r\n";          /* ROM 0xADC4 */
static const char s_alr_act[] = "\x1b[36m[I] ALR->ACT%s\r\n";          /* ROM 0xADDC */
static const char s_alr_wot[] = "\x1b[36m[I] ALR->WOT%s\r\n";          /* ROM 0xADF4 */
static const char s_wot_act[] = "\x1b[36m[I] WOT->ACT%s\r\n";          /* ROM 0xAE0C */
static const char s_wot_alr[] = "\x1b[36m[I] WOT->ALR%s\r\n";          /* ROM 0xAE24 */

/* MSCLP interrupt: IRQ8, priority 3 (ROM 0xB0F0). */
static const g2_touch_sysint_config touch_msclp_irq_config = {8, 3u};

static void log1(const char *format)
{
    (void)touch_bootstrap_log((uint32_t)(uintptr_t)format, (uint32_t)(uintptr_t)s_color_reset, 0u, 0u);
}

/* Stock 0x000038E0 (touch_product_05e0_bringup) - initialize_capsense:
 * Cy_CapSense_Init, MSCLP IRQ through 0x3948, then Cy_CapSense_Enable. */
void touch_product_05e0_bringup(void)
{
    g2_touch_sysint_config irq = touch_msclp_irq_config;

    if (touch_cap_init(CTX) != 0u) {
        return;
    }
    (void)Cy_SysInt_Init(&irq, touch_project_msclp_irq);
    if (irq.intrSrc >= 0) {
        NVIC_ICPR = 1u << ((uint32_t)irq.intrSrc & 31u);
    }
    if (irq.intrSrc >= 0) {
        NVIC_ISER = 1u << ((uint32_t)irq.intrSrc & 31u);
    }
    (void)Cy_CapSense_Enable(CTX);
}

/* Scan wait used by every state: critical section, sleep while the
 * CAPSENSE busy flag (status bit 0x80) is set. */
static void wait_scan(int deep)
{
    uint32_t mask = Cy_SysLib_EnterCriticalSection();

    while (Cy_CapSense_IsBusy(CTX) != 0u) {
        if (deep) {
            (void)touch_pm_deep_sleep();
        } else {
            (void)Cy_SysPm_CpuEnterSleep();
        }
        Cy_SysLib_ExitCriticalSection(mask);
        mask = Cy_SysLib_EnterCriticalSection();
    }
    Cy_SysLib_ExitCriticalSection(mask);
}

/* Stock 0x00003CB4 (touch_product_09b4_run) - main() */
int touch_product_09b4_run(void)
{
    uint32_t status = cybsp_init();

    touch_platform_0338_install(0u);
    if (status != 0u) {
        __asm volatile ("bkpt #1");   /* CY_ASSERT(0) */
    }
    (void)touch_bootstrap_log((uint32_t)(uintptr_t)s_tp_ver, (uint32_t)(uintptr_t)s_version,
                              (uint32_t)(uintptr_t)s_color_reset, 0u);
    __asm volatile ("cpsie i" ::: "memory");
    touch_config_bootstrap();
    touch_platform_0358_sample();
    touch_platform_09a4_start();
    G2_TOUCH_APP_STATE = STATE_ACT;
    G2_TOUCH_ACTIVE_BUDGET = BUDGET_ACT;
    GPIO_P4_DR_SET = 1u;   /* release attention P4.0 */
    GPIO_P4_DR_SET = 2u;   /* release P4.1 */
    i2c_slave_init();
    touch_product_05e0_bringup();
    (void)touch_ilo_compensate(CTX);
    (void)touch_set_active_interval(INTERVAL_ACT_US, CTX);

    for (;;) {
        touch_deferred();
        (void)memset(G2_TOUCH_REPORT, 0, 16u);
        switch (G2_TOUCH_APP_STATE) {
        case STATE_ALR:
            (void)Cy_CapSense_ScanAllSlots(CTX);
            wait_scan(1);
            (void)Cy_CapSense_ProcessAllWidgets(CTX);
            if (touch_widget_active(1u, CTX) != 0u) {
                G2_TOUCH_APP_STATE = STATE_ACT;
                G2_TOUCH_ACTIVE_BUDGET = BUDGET_ACT;
                log1(s_alr_act);
                (void)touch_set_active_interval(INTERVAL_ACT_US, CTX);
            } else if (G2_TOUCH_ACTIVE_BUDGET == 0u) {
                G2_TOUCH_APP_STATE = STATE_WOT;
                log1(s_alr_wot);
            }
            touch_calibration_report();
            break;
        case STATE_WOT:
            (void)touch_start_all_lp(CTX);
            wait_scan(1);
            if (Cy_CapSense_IsAnyLpWidgetActive(CTX) != 0u) {
                G2_TOUCH_APP_STATE = STATE_ACT;
                G2_TOUCH_ACTIVE_BUDGET = BUDGET_ACT;
                log1(s_wot_act);
                (void)touch_set_active_interval(INTERVAL_ACT_US, CTX);
            } else {
                G2_TOUCH_APP_STATE = STATE_ALR;
                G2_TOUCH_ACTIVE_BUDGET = BUDGET_ALR;
                log1(s_wot_alr);
                (void)touch_set_active_interval(INTERVAL_ALR_US, CTX);
            }
            break;
        case STATE_ACT:
            (void)Cy_CapSense_ScanAllSlots(CTX);
            wait_scan(0);
            (void)Cy_CapSense_ProcessAllWidgets(CTX);
            if (touch_widget_active(1u, CTX) != 0u) {
                G2_TOUCH_ACTIVE_BUDGET = BUDGET_ACT;
            } else if (--G2_TOUCH_ACTIVE_BUDGET == 0u) {
                G2_TOUCH_APP_STATE = STATE_ALR;
                G2_TOUCH_ACTIVE_BUDGET = BUDGET_ALR;
                log1(s_act_alr);
                (void)touch_set_active_interval(INTERVAL_ALR_US, CTX);
            }
            touch_calibration_report();
            break;
        default:
            __asm volatile ("bkpt #1");
            break;
        }
    }
}

int main(void) __attribute__((alias("touch_product_09b4_run")));
