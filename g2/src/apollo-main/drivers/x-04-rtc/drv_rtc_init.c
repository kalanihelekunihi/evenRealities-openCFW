/* Stock source: D:\01_workspace\s200_ap510b_iar_git\driver\rtc\drv_rtc.c
 * Native RTC driver init 0x47ee60..0x47ee78 (no literal pool), the function
 * placed directly before DRV_RtcSetTime 0x47ee78 (drivers/p-06-rtc). It is
 * run from the prioritised init table (ROM 0x6d1e1c, priority 1), which
 * refers to it as g2_init_entry_47ee60 (manifest defsym).
 *
 * The callees are AmbiqSuite apollo510 HAL functions:
 *   0x4d3628 am_hal_clkgen_control (case 0 = AM_HAL_CLKGEN_CONTROL_RTC_SEL_XTAL
 *            clears CLKGEN OCTRL.OSEL bit 7),
 *   0x4d3cae am_hal_rtc_osc_select (0 = AM_HAL_RTC_OSC_XT, clears OCTRL bit 7
 *            at 0x4000400c),
 *   0x4d3acc am_hal_rtc_osc_enable (clears RTCCTL.RSTOP bit 4 at 0x40004800). */
#include <stdint.h>
#include <stddef.h>

extern uint32_t am_hal_clkgen_control_4d3628(uint8_t control, void *args);
extern void am_hal_rtc_osc_select_4d3cae(uint32_t osc);
extern uint32_t am_hal_rtc_osc_enable_4d3acc(void);

#define CLKGEN_CONTROL_RTC_SEL_XTAL 0u /* AM_HAL_CLKGEN_CONTROL_RTC_SEL_XTAL */
#define RTC_OSC_XT 0u                  /* AM_HAL_RTC_OSC_XT */

/* Select the 32 kHz crystal for the RTC and start the RTC oscillator. */
int32_t drv_rtc_init_47ee60(void)
{
    (void)am_hal_clkgen_control_4d3628(CLKGEN_CONTROL_RTC_SEL_XTAL, NULL);
    am_hal_rtc_osc_select_4d3cae(RTC_OSC_XT);
    (void)am_hal_rtc_osc_enable_4d3acc();
    return 0;
}
