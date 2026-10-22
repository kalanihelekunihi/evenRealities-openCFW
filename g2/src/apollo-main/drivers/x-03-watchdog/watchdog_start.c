/* MCU watchdog start helper, native 0x4b29d8..0x4b29f1 (literal 0x4b29f4),
 * stock D:\01_workspace\s200_ap510b_iar_git\driver\wdt\watchdog.c by placement
 * next to the watchdog restart hook 0x4b29f8 (drivers/a-19-watchdog).
 *
 * First call of the board init sequence 0x5cdd14 after the clock setup:
 * stop the MCU watchdog, program it from the initialised RAM config at
 * 0x20000950 and start it unlocked. The callees are AmbiqSuite
 * am_hal_wdt_stop 0x52a38a, am_hal_wdt_config 0x52a2d8 and
 * am_hal_wdt_start 0x52a32c (upstream am_hal_wdt.c). */
#include <stdint.h>
#include <stdbool.h>

#define AM_HAL_WDT_MCU 0u

/* am_hal_wdt_config_t. Stock initial value (RAM 0x20000950):
 * {LFRC_DIV64 (2), no interrupt, interrupt value 12, reset enabled,
 *  reset value 480}: a ~30 s reset timeout at LFRC/64 = 16 Hz. */
typedef struct {
    uint8_t clock_source;       /* +0x00 am_hal_wdt_clock_select_e */
    bool interrupt_enable;      /* +0x01 */
    uint8_t pad02[2];
    uint32_t interrupt_value;   /* +0x04 */
    bool reset_enable;          /* +0x08 */
    uint8_t pad09[3];
    uint32_t reset_value;       /* +0x0c */
} g2_wdt_config_t;
_Static_assert(sizeof(g2_wdt_config_t) == 16u, "am_hal_wdt_config_t");

extern g2_wdt_config_t g2_wdt_config_20000950; /* RAM 0x20000950 (initialised data) */

extern uint32_t am_hal_wdt_stop_52a38a(uint32_t timer);
extern uint32_t am_hal_wdt_config_52a2d8(uint32_t timer, void *config);
extern uint32_t am_hal_wdt_start_52a32c(uint32_t timer, bool lock);

void watchdog_start_4b29d8(void);

void watchdog_start_4b29d8(void)
{
    (void)am_hal_wdt_stop_52a38a(AM_HAL_WDT_MCU);
    (void)am_hal_wdt_config_52a2d8(AM_HAL_WDT_MCU, &g2_wdt_config_20000950);
    (void)am_hal_wdt_start_52a32c(AM_HAL_WDT_MCU, false);
}
