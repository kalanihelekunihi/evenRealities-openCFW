#include <stdint.h>

extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern void audio_ble_copy_address6_4d293c(void *, const void *);
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *);
extern uint8_t audio_ble_pair_record_validate(uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.smpdb";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[] = "AppDbSetKey";
static uint32_t compact_enabled(void)
{
    if ((audio_log_flags() & 1u) != 0u)
        return 1u;
    return (audio_log_flags() & 4u) != 0u;
}
#define LOG0(level, line, mask, plain, compact) do { \
    if ((audio_log_flags() & 2u) != 0u) \
        audio_log_extended(level, module, path, function, line, plain); \
    if (compact_enabled() != 0u) \
        (void)compressed_log_output(mask, compact, compact); \
} while (0)
#define LOG1(level, line, mask, plain, compact, value) do { \
    if ((audio_log_flags() & 2u) != 0u) \
        audio_log_extended(level, module, path, function, line, plain, value); \
    if (compact_enabled() != 0u) \
        (void)compressed_log_output(mask, compact, compact, value); \
} while (0)
#define LOG2(level, line, mask, plain, compact, first, second) do { \
    if ((audio_log_flags() & 2u) != 0u) \
        audio_log_extended(level, module, path, function, line, plain, first, second); \
    if (compact_enabled() != 0u) \
        (void)compressed_log_output(mask, compact, compact, first, second); \
} while (0)
#define KEY_VALUES(p) (p)[4],(p)[5],(p)[6],(p)[7],(p)[8],(p)[9],(p)[10],(p)[11], \
                      (p)[12],(p)[13],(p)[14],(p)[15],(p)[16],(p)[17],(p)[18],(p)[19]
static const char local_dump[] =
    "AppDbSetKey: LOCAL_LTK key: %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X";
static const char local_dump_compact[] =
    "[ble.smpdb]AppDbSetKey: LOCAL_LTK key: %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X";
static const char peer_dump[] =
    "AppDbSetKey: PEER_LTK key: %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X";
static const char peer_dump_compact[] =
    "[ble.smpdb]AppDbSetKey: PEER_LTK key: %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X";
static void log_key_dump(const uint8_t *key, uint32_t line, const char *plain,
                         const char *compact)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, line, plain, KEY_VALUES(key));
    if (compact_enabled() != 0u)
        (void)compressed_log_output(0x10000000u | ((uint32_t)(key[14] & 15u) << 22),
                                    compact, compact, KEY_VALUES(key));
}

/* Native AppDbSetKey 0x47aed4. */
void audio_ble_master_child_47aed4(uint32_t address, const void *message)
{
    uint8_t *record = (uint8_t *)(uintptr_t)address;
    const uint8_t *key = (const uint8_t *)message;
    LOG1(4u, 0x506u, 0x10400000u,
         "AppDbSetKey: type = 0x%02x",
         "[ble.smpdb]AppDbSetKey: type = 0x%02x", key[0x1eu]);
    switch (key[0x1eu]) {
    case 1u: /* local LTK */
        record[0x4eu] = key[0x1fu];
        (void)audio_queue_copy_bytes(record + 0x34u, key + 4u, 0x1au);
        record[0x2eu] |= 1u;
        LOG2(4u, 0x50fu, 0x10800000u,
             "AppDbSetKey: LOCAL_LTK stored - secLevel=%d, ediv=0x%04X",
             "[ble.smpdb]AppDbSetKey: LOCAL_LTK stored - secLevel=%d, ediv=0x%04X",
             key[0x1fu], *(const uint16_t *)(const void *)(key + 0x1cu));
        log_key_dump(key, 0x514u, local_dump, local_dump_compact);
        break;
    case 2u: /* peer LTK */
        record[0x6au] = key[0x1fu];
        (void)audio_queue_copy_bytes(record + 0x50u, key + 4u, 0x1au);
        record[0x2eu] |= 2u;
        LOG2(4u, 0x51cu, 0x10800000u,
             "AppDbSetKey: PEER_LTK stored - secLevel=%d, ediv=0x%04X",
             "[ble.smpdb]AppDbSetKey: PEER_LTK stored - secLevel=%d, ediv=0x%04X",
             key[0x1fu], *(const uint16_t *)(const void *)(key + 0x1cu));
        log_key_dump(key, 0x521u, peer_dump, peer_dump_compact);
        break;
    case 4u: /* peer IRK and address */
        (void)audio_queue_copy_bytes(record + 7u, key + 4u, 0x17u);
        record[0x2eu] |= 4u;
        record[6u] = key[0x1au];
        audio_ble_copy_address6_4d293c(record, key + 0x14u);
        LOG1(4u, 0x52au, 0x10400000u,
             "AppDbSetKey: IRK stored - addrType=%d",
             "[ble.smpdb]AppDbSetKey: IRK stored - addrType=%d", key[0x1au]);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x52du,
                "AppDbSetKey: IRK addr: %02X:%02X:%02X:%02X:%02X:%02X",
                key[0x19u], key[0x18u], key[0x17u], key[0x16u], key[0x15u], key[0x14u]);
        if (compact_enabled() != 0u) {
            static const char compact[] =
                "[ble.smpdb]AppDbSetKey: IRK addr: %02X:%02X:%02X:%02X:%02X:%02X";
            (void)compressed_log_output(0x11800000u, compact, compact,
                key[0x19u], key[0x18u], key[0x17u], key[0x16u], key[0x15u], key[0x14u]);
        }
        break;
    case 8u: /* CSRK */
        (void)audio_queue_copy_bytes(record + 0x1eu, key + 4u, 0x10u);
        record[0x2eu] |= 8u;
        *(uint32_t *)(void *)(record + 0x80u) = 0u;
        LOG0(4u, 0x535u, 0x10000000u,
             "AppDbSetKey: CSRK stored", "[ble.smpdb]AppDbSetKey: CSRK stored");
        break;
    default:
        LOG1(2u, 0x539u, 0x08400000u,
             "AppDbSetKey: Unknown key type = 0x%02x",
             "[ble.smpdb]AppDbSetKey: Unknown key type = 0x%02x", key[0x1eu]);
        break;
    }
    LOG1(4u, 0x53cu, 0x10400000u,
         "AppDbSetKey: IRK stored - keyValidMask=0x%02x",
         "[ble.smpdb]AppDbSetKey: IRK stored - keyValidMask=0x%02x", record[0x2eu]);
    if (record[0x30u] == 1u) {
        (void)audio_ble_privacy_rewrite_record(record);
        (void)audio_ble_pair_record_validate(record);
    }
}
