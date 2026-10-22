/* KV record "kvRing" (paired R1 ring MAC and name), stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_ring.c.
 * Native 0x5d9b6c..0x5d9e87; literal pool 0x5d9e88..0x5d9ecf.
 * Record: g2_kvdb_ring_t, 24 bytes, version 1, CRC over the first 22 bytes.
 * The MAC is logged most-significant byte first (record bytes 6..1). */
#include "kvdb_private.h"

#define RECORD_VERSION 1u

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);     /* memcpy 0x439be4 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);          /* memset(p, n, c) 0x43c0e4 */
extern void *audio_settings_copy_text(void *, const void *, uint32_t);   /* strncpy 0x44b5a0 */

g2_kvdb_ring_t g2_kvdb_ring_record = { /* RAM 0x200037c8, stock default */
    1u, { 0xffu, 0xffu, 0xffu, 0xffu, 0xffu, 0xffu },
    { 'E', 'V', 'E', 'N', ' ', 'R', '1', '_', 'F', 'F', 'F', 'F', 'F', 'F' }, 0u, 0u
};

static const char key[] = "kvRing"; /* ROM 0x78e5a4 */
static const char module_tag[] = "kv.ring"; /* ROM 0x78e5ac */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_ring.c"; /* ROM 0x6e9d90 */
static const char update_fn[] = "_kvdbUpdataRing"; /* ROM 0x788ab0 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788ac0 */
static const char version_msg_short[] = "[kv.ring]version %d(%d)"; /* ROM 0x77b974 */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788ad0 */
static const char crc_msg_short[] = "[kv.ring]crc 0x%x(0x%x)"; /* ROM 0x77b98c */
static const char mac_msg[] = "mac %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x759b88 */
static const char mac_msg_short[] = "[kv.ring]mac %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x7433b8 */
static const char name_msg[] = "name %s"; /* ROM 0x78e5b4 */
static const char name_msg_short[] = "[kv.ring]name %s"; /* ROM 0x783384 */
static const char write_fn[] = "SVC_KvdbWriteRing"; /* ROM 0x783398 */
static const char check_msg[] = "record_check 0x%x"; /* ROM 0x7833ac */
static const char check_msg_short[] = "[kv.ring]record_check 0x%x"; /* ROM 0x771364 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbRingDefaultInitialize(void) {
    g2_kvdb_ring_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_ring_record, 22u, NULL);
    return 0;
}

int32_t _kvdbUpdataRing(void) {
    g2_kvdb_ring_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 45u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 46u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_ring_record.crc);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 48u, mac_msg, mac_msg_short, 0x11800000u,
                  stored.mac[5], stored.mac[4], stored.mac[3], stored.mac[2], stored.mac[1],
                  stored.mac[0]);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 49u, name_msg, name_msg_short, 0x10400000u,
                  stored.name);
        if (stored.crc != g2_kvdb_ring_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteRing(g2_kvdb_ring_record.mac, g2_kvdb_ring_record.name);
        return 0;
    }
    (void)SVC_KvdbWriteRing(g2_kvdb_ring_record.mac, g2_kvdb_ring_record.name);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataRing);

/* A NULL MAC or name erases that field to 0xff. */
int32_t SVC_KvdbWriteRing(const uint8_t *mac, const char *name) {
    if (mac != NULL)
        audio_queue_copy_bytes(g2_kvdb_ring_record.mac, mac, sizeof(g2_kvdb_ring_record.mac));
    else
        audio_uart_buffer_zero(g2_kvdb_ring_record.mac, sizeof(g2_kvdb_ring_record.mac), 0xffu);
    if (name != NULL) {
        audio_settings_copy_text(g2_kvdb_ring_record.name, name, sizeof(g2_kvdb_ring_record.name));
        g2_kvdb_ring_record.name[sizeof(g2_kvdb_ring_record.name) - 1u] = '\0';
    } else {
        audio_uart_buffer_zero(g2_kvdb_ring_record.name, sizeof(g2_kvdb_ring_record.name), 0xffu);
    }
    g2_kvdb_ring_record.version = RECORD_VERSION;
    g2_kvdb_ring_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_ring_record, 22u, NULL);
    G2_KV_LOG(4u, module_tag, source_file, write_fn, 75u, check_msg, check_msg_short, 0x10400000u,
              g2_kvdb_ring_record.crc);
    G2_KV_LOG(4u, module_tag, source_file, write_fn, 77u, mac_msg, mac_msg_short, 0x11800000u,
              g2_kvdb_ring_record.mac[5], g2_kvdb_ring_record.mac[4], g2_kvdb_ring_record.mac[3],
              g2_kvdb_ring_record.mac[2], g2_kvdb_ring_record.mac[1], g2_kvdb_ring_record.mac[0]);
    G2_KV_LOG(4u, module_tag, source_file, write_fn, 78u, name_msg, name_msg_short, 0x10400000u,
              g2_kvdb_ring_record.name);
    return audio_settings_kvdb_blob_write(key, &g2_kvdb_ring_record, sizeof(g2_kvdb_ring_record));
}
