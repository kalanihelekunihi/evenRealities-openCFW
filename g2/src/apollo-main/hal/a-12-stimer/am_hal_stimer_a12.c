/* AmbiqSuite HAL am_hal_stimer.c (Apollo510), stock variant.
 * Native 0x48d570..0x48d704, literal pool 0x48d704..0x48d723.
 *
 * Differs from the pinned third-party/upstream/ambiqhal-apollo510 copy:
 * is_running reads a different predicate, compare_delta_set validates the
 * instance after the first counter snapshot, and int_enable / int_clear /
 * int_status_get run without AM_CRITICAL sections. STIMER registers:
 * STCFG 0x40008800, STTMR 0x40008804, SCMPR0 0x40008820 (+4 per instance),
 * STMINTEN 0x40008900, STMINTSTAT 0x40008904, STMINTCLR 0x40008908. */
#include <stdint.h>
#include <stdbool.h>

#define STIMER_STCFG (*(volatile uint32_t *)0x40008800u)
#define STIMER_STTMR_ADDR 0x40008804u
#define STIMER_SCMPR(n) (((volatile uint32_t *)0x40008820u)[(n)])
#define STIMER_STMINTEN (*(volatile uint32_t *)0x40008900u)
#define STIMER_STMINTSTAT (*(volatile uint32_t *)0x40008904u)
#define STIMER_STMINTCLR (*(volatile uint32_t *)0x40008908u)

#define STIMER_STCFG_CLKSEL_MSK 0xfu
#define STIMER_STCFG_RUN_MSK 0xc0000000u /* FREEZE bit31 | CLEAR bit30 */
#define AM_HAL_CLKMGR_USER_ID_STIMER 50u
#define AM_HAL_STATUS_OUT_OF_RANGE 5u
#define AM_HAL_STIMER_DELTA_TOO_SMALL 0x08000000u

extern volatile bool g2_stimer_configured_20074f7a;   /* RAM 0x20074f7a, g_bStimerConfigured */
extern uint32_t g2_stimer_last_compare_20000318[8];   /* RAM 0x20000318, g_ui32LastStimer */

extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t clock_id, uint32_t user_id); /* am_hal_clkmgr_clock_request */
extern uint32_t g2_main_mspi_clock_release_4c4530(uint32_t clock_id, uint32_t user_id); /* am_hal_clkmgr_clock_release */
extern uint32_t g2_main_critical_save_473940(void);    /* am_hal_interrupt_master_disable */
extern void am_hal_triple_read_4d5888(uint32_t address, uint32_t values[3]);

uint32_t am_hal_stimer_clksrc_get_48d570(uint32_t clk);
uint32_t am_hal_stimer_config_48d588(uint32_t config);
bool am_hal_stimer_is_running_48d620(void);
uint32_t am_hal_stimer_counter_get_48d654(void);
uint32_t am_hal_stimer_compare_delta_set_48d670(uint32_t compare, uint32_t delta);
void am_hal_stimer_int_enable_48d6dc(uint32_t mask);
void am_hal_stimer_int_clear_48d6e6(uint32_t mask);
uint32_t am_hal_stimer_int_status_get_48d6f0(bool enabled_only);

/* 0x48d570: CLKSEL -> clock-manager id (HFRC 4, LFRC 0, none 7). */
uint32_t am_hal_stimer_clksrc_get_48d570(uint32_t clk)
{
    switch (clk) {
    case 1u: /* HFRC_6MHZ */
    case 2u: /* HFRC_375KHZ */
        return 4u;
    case 6u: /* LFRC_NOMINAL */
        return 0u;
    default:
        return 7u;
    }
}

/* 0x48d588: write STCFG, requesting the new clock and releasing the old one
 * across run/freeze transitions; returns the previous STCFG. */
uint32_t am_hal_stimer_config_48d588(uint32_t config)
{
    uint32_t current = STIMER_STCFG;
    uint32_t cfg_sel = config & STIMER_STCFG_CLKSEL_MSK;
    uint32_t pre_sel = current & STIMER_STCFG_CLKSEL_MSK;
    uint32_t cfg_src = am_hal_stimer_clksrc_get_48d570(cfg_sel);
    uint32_t pre_src = am_hal_stimer_clksrc_get_48d570(pre_sel);
    bool request;
    bool release;

    if ((config & STIMER_STCFG_RUN_MSK) == 0u) {
        if ((current & STIMER_STCFG_RUN_MSK) == 0u) {
            request = release = (cfg_src != pre_src);
        } else {
            request = true;
            release = false;
        }
    } else {
        request = false;
        release = true;
    }
    if (request && cfg_sel != 0u && cfg_sel < 7u)
        (void)g2_main_mspi_clock_acquire_4c44bc((uint8_t)cfg_src, AM_HAL_CLKMGR_USER_ID_STIMER);
    STIMER_STCFG = config;
    if (release && pre_sel != 0u && pre_sel < 7u)
        (void)g2_main_mspi_clock_release_4c4530((uint8_t)pre_src, AM_HAL_CLKMGR_USER_ID_STIMER);
    g2_stimer_configured_20074f7a = true;
    return current;
}

/* 0x48d620: configured, a clock selected, not frozen and not held clear. */
bool am_hal_stimer_is_running_48d620(void)
{
    if (!g2_stimer_configured_20074f7a || (STIMER_STCFG & STIMER_STCFG_CLKSEL_MSK) == 0u ||
        (STIMER_STCFG >> 31) != 0u)
        return false;
    return ((STIMER_STCFG >> 30) & 1u) == 0u;
}

/* 0x48d654: glitch-free STTMR read (two matching samples, else the third). */
uint32_t am_hal_stimer_counter_get_48d654(void)
{
    uint32_t values[3];

    am_hal_triple_read_4d5888(STIMER_STTMR_ADDR, values);
    if (values[0] == values[1])
        return values[1];
    return values[2];
}

/* 0x48d670 */
uint32_t am_hal_stimer_compare_delta_set_48d670(uint32_t compare, uint32_t delta)
{
    uint32_t status = 0u;
    uint32_t start = am_hal_stimer_counter_get_48d654();
    uint32_t now = start;
    uint32_t primask;

    if (compare >= 8u)
        return AM_HAL_STATUS_OUT_OF_RANGE;
    /* A COMPARE write needs two STIMER cycles to land; wait them out. */
    while (now == g2_stimer_last_compare_20000318[compare] ||
           now == g2_stimer_last_compare_20000318[compare] + 1u)
        now = am_hal_stimer_counter_get_48d654();
    primask = g2_main_critical_save_473940();
    now = am_hal_stimer_counter_get_48d654();
    if (now - start + 3u < delta) {
        delta = start + (delta - now) - 3u;
    } else {
        delta = 1u;
        status = AM_HAL_STIMER_DELTA_TOO_SMALL;
    }
    STIMER_SCMPR(compare) = delta;
    g2_stimer_last_compare_20000318[compare] = am_hal_stimer_counter_get_48d654();
    __asm__ volatile("msr primask, %0" : : "r"(primask) : "memory");
    return status;
}

/* 0x48d6dc */
void am_hal_stimer_int_enable_48d6dc(uint32_t mask)
{
    STIMER_STMINTEN |= mask;
}

/* 0x48d6e6: clear, then read back STMINTSTAT so the write completes. */
void am_hal_stimer_int_clear_48d6e6(uint32_t mask)
{
    STIMER_STMINTCLR = mask;
    (void)STIMER_STMINTSTAT;
}

/* 0x48d6f0 */
uint32_t am_hal_stimer_int_status_get_48d6f0(bool enabled_only)
{
    uint32_t status = STIMER_STMINTSTAT;

    if (enabled_only)
        status &= STIMER_STMINTEN;
    return status;
}
