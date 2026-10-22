/* BLE application state accessors, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c.
 * Native 0x4b8122, 0x4b8128, APP_BleConnectPhoneTypeSet 0x4b8140..0x4b81ad and
 * 0x4b8204; literal pools 0x4b81fc..0x4b820f, 0x4b8374 ("IOS"), 0x4b8488,
 * 0x4b8730 and 0x4b87a4..0x4b87b3. APP_BleConnectTimeoutCheckEvt 0x4b81b8 is
 * in ble/ble-connect. */
#include <stdint.h>

#define APP_BLE_PHONE_IOS 3u

extern uint8_t audio_ble_comm_state[];          /* RAM 0x200727f0, BLE comm control block */
extern uint8_t audio_ble_comm_mode[];           /* RAM 0x200737b0, +0 phone type */
extern uint32_t audio_ble_ancc_connection_tick; /* RAM 0x200742f4, tick of the last link encryption */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char s_module[] = "ble.comm"; /* ROM 0x789ff8 */
static const char s_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble.c"; /* ROM 0x711d94 */
static const char s_phone_type_set[] = "APP_BleConnectPhoneTypeSet"; /* ROM 0x768bfc */
static const char s_phone_type_msg[] = "APP_BleConnectPhoneTypeSet phoneType = %s"; /* ROM 0x73ba60 */
static const char s_phone_type_short[] = "[ble.comm]APP_BleConnectPhoneTypeSet phoneType = %s"; /* ROM 0x726464 */
static const char s_ios[] = "IOS";         /* ROM 0x4b8374 */
static const char s_android[] = "ANDROID"; /* ROM 0x78c994 */

uint8_t *app_ble_comm_state_get_4b8122(void)
{
    return audio_ble_comm_state;
}

uint8_t app_ble_phone_type_get_4b8128(void)
{
    return audio_ble_comm_mode[0];
}

void app_ble_connect_phone_type_set_4b8140(uint8_t phone_type)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, s_module, s_path, s_phone_type_set, 0x38cu, s_phone_type_msg,
                           phone_type == APP_BLE_PHONE_IOS ? s_ios : s_android);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, s_phone_type_short, s_phone_type_short,
                                  phone_type == APP_BLE_PHONE_IOS ? s_ios : s_android);
    audio_ble_comm_mode[0] = phone_type;
}

uint32_t app_ble_connection_tick_get_4b8204(void)
{
    return audio_ble_ancc_connection_tick;
}
