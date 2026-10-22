/* NVDB BLE MAC record, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb_mac.c.
 * Native 0x5d9f48..0x5da05f; literal pool 0x5da060..0x5da07f.
 *
 * Record "nvMAC" (10 bytes): version 1, 6-byte address at +1, CRC16 over 8
 * bytes at +8. Live copy RAM 0x200038e4. The default address is derived from
 * the Apollo chip ID: CRC32 of (ChipID1, ChipID0) gives mac[0..3], the CRC16
 * of the same 8 bytes gives mac[4] (high byte) and mac[5] (low byte), and
 * mac[5] is forced to 0b11xxxx00 (static-random address type). */
#include <stdint.h>
#include "nvdb_internal.h"

extern g2_nvdb_mac_t g2_nvdb_mac_record; /* RAM 0x200038e4 */

/* Mode 1 fills the am_hal_mcuctrl device record (ChipPN +0, ChipID0 +4, ChipID1 +8). */
extern uint32_t audio_ble_hci_radio_identifier_480d72(uint8_t mode, void *output);
/* Reflected CRC32 table walk, seed 0xffffffff when seed == NULL. */
extern uint32_t crc32_4d34c4(const void *data, uint32_t length, const uint32_t *seed);

static const char module_tag[] = "nv.mac"; /* ROM 0x78e624 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\NV\\service_nvdb_mac.c"; /* ROM 0x6e9e38 */
static const char key_mac[] = "nvMAC"; /* ROM 0x78e62c */
static const char update_fn[] = "_nvdbUpdataMac"; /* ROM 0x788c00 */
static const char debug_only[] = "!!This is only for program debugging"; /* ROM 0x74e074 */
static const char debug_only_short[] = "[nv.mac]!!This is only for program debugging"; /* ROM 0x7385c4 */

int32_t nvdbMacDefaultInitialize(void)
{
    uint32_t hash = 0u;
    uint8_t chip_id[8];
    uint32_t device[16];
    g2_nvdb_mac_t *rec = &g2_nvdb_mac_record;

    (void)audio_ble_hci_radio_identifier_480d72(1u, device);
    audio_uart_checksum_copy(&chip_id[0], &device[2], 4u);
    audio_uart_checksum_copy(&chip_id[4], &device[1], 4u);
    hash = crc32_4d34c4(chip_id, 8u, NULL);
    audio_uart_checksum_copy(&rec->mac[0], &hash, 4u);
    uint16_t crc = audio_uart_hand_checksum_49acd4(chip_id, 8u, NULL);
    rec->mac[4] = (uint8_t)(crc >> 8);
    rec->mac[5] = (uint8_t)crc;
    rec->mac[5] &= 0xfcu;
    rec->mac[5] |= 0xc0u;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 8u, NULL);
    return 0;
}

int32_t _nvdbUpdataMac(void)
{
    g2_nvdb_mac_t stored;
    NVDB_LOG(module_tag, source_file, 2u, update_fn, 0x41u, 0x08000000u, debug_only, debug_only_short);
    if (SVC_NvdbRead(key_mac, &stored, 10u) < 1)
        nvdbMacUpdate(g2_nvdb_mac_record.mac);
    else if (stored.crc != g2_nvdb_mac_record.crc && stored.version == 0u)
        nvdbMacUpdate(g2_nvdb_mac_record.mac);
    return 0;
}

void nvdbMacUpdate(const uint8_t *mac)
{
    g2_nvdb_mac_t *rec = &g2_nvdb_mac_record;
    audio_uart_checksum_copy(rec->mac, mac, 6u);
    rec->version = 1u;
    rec->crc = audio_uart_hand_checksum_49acd4(rec, 8u, NULL);
    (void)SVC_NvdbWrite(key_mac, rec, 10u);
}
