/* Product watchdog bring-up, stock D:\01_workspace\s200_ap510b_iar_git\driver\wdt\watchdog.c.
 * Native 0x52f2e0..0x52f36b (watchdog_init, watchdog_enable); literal pool
 * 0x52f36c..0x52f38b. The MCU WDT restart hook from the same file is
 * drivers/a-19-watchdog/watchdog_restart.c (0x4b29f8).
 *
 * watchdog_enable only arms the external PMIC watchdog: board option record 0
 * (0x50938e) byte 0 is the charger family, and family 1 (nPM1300) gets
 * npmx_watchdog_enable (timer task 0). Called from DEV_Init in device_mgr.c. */
#include <stdint.h>
#include "g2_npm1300.h"

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern const uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t index);

#define BOARD_CHARGER_NPM1300 1u

static const char module_tag[] = "watchdog"; /* ROM 0x78c92c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\wdt\\watchdog.c"; /* ROM 0x71b5ec */
static const char init_fn[] = "watchdog_init"; /* ROM 0x789f20 */
static const char init_msg[] = "watchdog_init"; /* ROM 0x789f30 */
static const char init_short[] = "[watchdog]watchdog_init"; /* ROM 0x77d87c */
static const char enable_fn[] = "watchdog_enable"; /* ROM 0x789f40 */
static const char enable_msg[] = "watchdog_enable"; /* ROM 0x789f50 */
static const char enable_short[] = "[watchdog]watchdog_enable"; /* ROM 0x774800 */

void watchdog_enable(void)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, enable_fn, 0x15u, enable_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, enable_short, enable_short);
    if (*audio_ble_hci_radio_mode_state_50938e(0u) == BOARD_CHARGER_NPM1300)
        npmx_watchdog_enable_511882();
}

void watchdog_init(void)
{
    watchdog_enable();
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, init_fn, 0x0eu, init_msg);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, init_short, init_short);
}
