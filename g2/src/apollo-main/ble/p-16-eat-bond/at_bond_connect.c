/* eAT BLE bond/connect command handlers (AT^CLEANBOND, AT^BLE_KEEPCONNECT).
 * Native 0x5a4fa4..0x5a4fc5, literal pool 0x5a4fc8..0x5a4fcf. No source path
 * string survives; the file sits between the PCM2.2 SPOT manager and
 * at_buzzer.c (0x5a4fd0) in link order, i.e. platform\service\eAT.
 *
 * Registry ROM 0x6c9260 rows {type, name, handler, 0}; each handler gets the
 * parameter text after the command. Both ignore it and return 0. */
#include <stdint.h>

extern void at_core_output(const char *fmt, ...);                  /* 0x541430 */
/* Cordio-app bond wipe: AppDbDeleteAllRecords 0x47acf8, DmPrivClearResList,
 * then clears bytes +0x6c/+0x74 and word +0x70 of RAM 0x200719c8. */
extern void app_clear_all_bonding_info_4b46ce(void);
extern void slave_adv_stop_flag_or_0046f2dc(uint32_t keep);

static const char o_cleanbond_ok[] = "CLEANBOND+OK\r\n";             /* ROM 0x7850d0 */
static const char o_keepconnect_ok[] = "BLE_KEEPCONNECT+OK\r\n";     /* ROM 0x77553c */

int32_t atCleanBondHandler(const char *param) {
    (void)param;
    app_clear_all_bonding_info_4b46ce();
    at_core_output(o_cleanbond_ok);
    return 0;
}

int32_t atBleKeepConnectHandler(const char *param) {
    (void)param;
    slave_adv_stop_flag_or_0046f2dc(1);
    at_core_output(o_keepconnect_ok);
    return 0;
}
