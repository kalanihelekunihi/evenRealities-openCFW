/* Ring GATT client service discovery, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\ble\profiles\ring\profile_ring.c.
 * Native 0x4c487c..0x4c48ac (APP_BleRingSvcDiscover); literal pool words
 * 0x4c4c98..0x4c4ca0. The ring service UUID is
 * BAE80001-4F05-4503-8E65-3AF1F7329D1F (ROM 0x7880b0, little-endian); its
 * three-entry characteristic list is RAM 0x200030d8. */
#include <stdint.h>

extern const uint8_t g2_ring_service_uuid[16]; /* ROM 0x7880b0 */
extern void *g2_ring_disc_char_list[3]; /* RAM 0x200030d8 attcDiscChar_t *[3] */

extern void audio_dump_hex(const char *label, uint32_t width, const uint8_t *data, uint32_t length); /* 0x43dacc elog hexdump */
extern void app_disc_find_service_5332b4(uint8_t connection, uint8_t uuid_length,
                                         const uint8_t *uuid, uint8_t list_length,
                                         void *characteristics, uint16_t *handles); /* AppDiscFindService */

static const char dump_label[] = "\r\n          -appDiscPrint Ring Dis Service, UUID"; /* ROM 0x72c034 */

void APP_BleRingSvcDiscover(uint8_t conn_id, uint16_t *handles)
{
    audio_dump_hex(dump_label, 16u, g2_ring_service_uuid, 16u);
    app_disc_find_service_5332b4(conn_id, 16u, g2_ring_service_uuid, 3u,
                                 g2_ring_disc_char_list, handles);
}
