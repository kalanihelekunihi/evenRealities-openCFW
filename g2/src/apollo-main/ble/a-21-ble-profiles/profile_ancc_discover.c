/* ANCS client (ANCC) discovery and active-notification accessor, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\ancc\profile_ancc.c.
 * Native 0x4bf82c..0x4bf8ac (APP_BleAnccSvcDiscover) and 0x4bf8ac..0x4bf8b0
 * (profileAnccGetActive); literal pool 0x4bf900..0x4bf990.
 *
 * Discovery only runs while this device is the BLE master (role 1). It walks
 * the Apple ANCS service 7905F431-B5CE-4E99-A40F-4B1E122D00D0 (UUID at ROM
 * 0x787fc0, little-endian) with the five-entry characteristic list in RAM
 * 0x200030bc. */
#include <stdint.h>

extern uint8_t audio_ble_ancc_cache[]; /* RAM 0x2006ddd4, current ANCS notification */
extern const uint8_t g2_ancs_service_uuid[16]; /* ROM 0x787fc0 */
extern void *g2_ancc_disc_char_list[5]; /* RAM 0x200030bc attcDiscChar_t *[5] */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 1 master, 2 slave */
extern void app_disc_find_service_5332b4(uint8_t connection, uint8_t uuid_length,
                                         const uint8_t *uuid, uint8_t list_length,
                                         void *characteristics, uint16_t *handles); /* AppDiscFindService */

static const char module_tag[] = "ble.ancc"; /* ROM 0x78b7e0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c"; /* ROM 0x6eeeb8 */
static const char discover_fn[] = "APP_BleAnccSvcDiscover"; /* ROM 0x77a75c */
static const char discover_text[] =
    "[ANCS] Starting service discovery: connId=%d, deviceRole=%d (MASTER_ROLE)"; /* ROM 0x6f53ac */
static const char discover_short[] =
    "[ble.ancc][ANCS] Starting service discovery: connId=%d, deviceRole=%d (MASTER_ROLE)"; /* ROM 0x6e93b8 */

uint8_t APP_BleAnccSvcDiscover(uint8_t conn_id, uint16_t *handles)
{
    uint8_t role = audio_uart_device_role_get();
    if (role != 1u)
        return 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module_tag, source_file, discover_fn, 0x34fu, discover_text,
                           conn_id, role);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x0c800000u, discover_short, discover_short, conn_id, role);
    app_disc_find_service_5332b4(conn_id, 16u, g2_ancs_service_uuid, 5u,
                                 g2_ancc_disc_char_list, handles);
    return 1u;
}

uint8_t *profileAnccGetActive(void)
{
    return audio_ble_ancc_cache;
}
