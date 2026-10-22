/* GATT profile discovery, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\gatt\profile_gatt.c,
 * native 0x4B59C0..0x4B5A1D.
 *
 * Product copy of Cordio gatt_main.c. GattSetSvcChangedIdx 0x4B5A3A,
 * GattReadCback 0x4B5ADC and GattWriteCback 0x4B5B02 keep the public r20.05c
 * text; GattDiscover differs by logging the GATT service UUID before
 * AppDiscFindService (line 103 of the product file). */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* AppDiscFindService(connId, uuidLen, pUuid, listLen, pCharList, pHdlList) */
extern void app_disc_find_service_5332b4(uint8_t connection, uint8_t uuid_length,
                                         const uint8_t *uuid, uint8_t list_length,
                                         void *characteristics, uint16_t *handles);

extern const uint8_t g2_att_gatt_svc_uuid[2]; /* attGattSvcUuid, ROM 0x78F53A = {0x01, 0x18} */
extern void *g2_gatt_disc_char_list[];        /* gattDiscCharList, RAM 0x200030D0 (initialised data) */

static const char gatt_module[] = "ble.gatt"; /* ROM 0x78B810 */
static const char gatt_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\gatt\\profile_gatt.c"; /* ROM 0x6EF048 */
static const char gatt_discover_fn[] = "GattDiscover"; /* ROM 0x788040 */
static const char disc_service_text[] =
    " -appDiscPrint Dis Service, UUID :0x%04X"; /* ROM 0x7419F0 */
static const char disc_service_short[] =
    "[ble.gatt] -appDiscPrint Dis Service, UUID :0x%04X"; /* ROM 0x72BFCC */

void GattDiscover_4b59c0(uint8_t connection, uint16_t *handles)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, gatt_module, gatt_source, gatt_discover_fn, 103u,
                           disc_service_text,
                           *(const uint16_t *)(const void *)g2_att_gatt_svc_uuid);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x10400000u, disc_service_short, disc_service_short,
                                  *(const uint16_t *)(const void *)g2_att_gatt_svc_uuid);

    /* ATT_16_UUID_LEN = 2, GATT_HDL_LIST_LEN = 2 */
    app_disc_find_service_5332b4(connection, 2u, g2_att_gatt_svc_uuid, 2u,
                                 g2_gatt_disc_char_list, handles);
}
