/* Stock source: D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\common\app_db.c
 * Native AppDbResolveAndConnectByAddr 0x47a8c4..0x47ab4e (product addition to
 * Cordio app_db.c; called from _bleMasterScanReport 0x49fcd2).
 *
 * Bond rows: ten 200-byte records at RAM 0x20067a30 (+0 BD address, +6 host
 * address type, +7 peer IRK, +0x2e key-valid mask, +0x2f in-use, +0x30 valid).
 * Returns 1 when a resolve was started or a bonded record matched. */
#include <stdint.h>
#include <stddef.h>

#define APP_DB_RECORDS      10u
#define APP_DB_RECORD_SIZE  200u
#define APP_DB_KEY_IRK      0x04u /* key-valid mask bit for the peer IRK */

extern uint8_t audio_ble_privacy_rows[APP_DB_RECORDS * APP_DB_RECORD_SIZE]; /* RAM 0x20067a30 */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void DmPrivResolveAddr(const uint8_t *pAddr, const uint8_t *pIrk, uint16_t param); /* 0x4d27f6 */
extern uint8_t DmHostAddrType(uint8_t); /* 0x4d2aa8 */
extern uint32_t audio_ble_privacy_compare_address(const uint8_t *, const uint8_t *); /* 0x4d294a */

static const char module[] = "ble.smpdb"; /* ROM 0x78a0d0 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c"; /* ROM 0x6d84bc */
static const char function[] = "AppDbResolveAndConnectByAddr"; /* ROM 0x75de50 */
static const char s_invalid[] =
    "AppDbResolveAndConnectByAddr: Invalid MAC address pointer"; /* ROM 0x7126b8 */
static const char c_invalid[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: Invalid MAC address pointer"; /* ROM 0x6f851c */
static const char s_rpa[] =
    "AppDbResolveAndConnectByAddr: Detected resolvable random address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6dc454 */
static const char c_rpa[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: Detected resolvable random address %02X:%02X:%02X:%02X:%02X:%02X"; /* ROM 0x6a6ee4 */
static const char s_try[] =
    "AppDbResolveAndConnectByAddr: Trying to resolve address with IRK of record[%d]"; /* ROM 0x6eb588 */
static const char c_try[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: Trying to resolve address with IRK of record[%d]"; /* ROM 0x6df600 */
static const char s_no_irk[] =
    "AppDbResolveAndConnectByAddr: No valid IRK found to resolve random address"; /* ROM 0x6f197c */
static const char c_no_irk[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: No valid IRK found to resolve random address"; /* ROM 0x6e2490 */
static const char s_found[] =
    "AppDbResolveAndConnectByAddr: Found paired record, can use LTK to connect"; /* ROM 0x6f19c8 */
static const char c_found[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: Found paired record, can use LTK to connect"; /* ROM 0x6e24e8 */
static const char s_none[] = "AppDbResolveAndConnectByAddr: No paired record found"; /* ROM 0x71c000 */
static const char c_none[] =
    "[ble.smpdb]AppDbResolveAndConnectByAddr: No paired record found"; /* ROM 0x7092a4 */

#define DB_LOG(level, line, code, plain, compact, ...) do {                         \
    if (audio_log_flags() & 2u)                                                     \
        audio_log_extended((level), module, path, function, (line), (plain), ##__VA_ARGS__); \
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                      \
        (void)compress_log_output((code), (compact), (compact), ##__VA_ARGS__);     \
} while (0)

uint32_t app_db_resolve_and_connect_by_addr_47a8c4(uint8_t addr_type, const uint8_t *addr)
{
    const uint8_t *row = audio_ble_privacy_rows;
    uint8_t found = 0u;
    uint8_t i;

    if (addr == NULL) {
        DB_LOG(1u, 0x3e6u, 0x04000000u, s_invalid, c_invalid);
        return 0u;
    }

    /* DM_ADDR_RANDOM with the resolvable-private-address marker (top bits 01). */
    if (addr_type == 1u && (addr[5] & 0xc0u) == 0x40u) {
        DB_LOG(4u, 0x3eeu, 0x11800000u, s_rpa, c_rpa,
               addr[5], addr[4], addr[3], addr[2], addr[1], addr[0]);
        for (i = 0u; i < APP_DB_RECORDS; i++, row += APP_DB_RECORD_SIZE) {
            if (row[0x2f] != 0u && row[0x30] != 0u && (row[0x2e] & APP_DB_KEY_IRK) != 0u) {
                DB_LOG(4u, 0x3f8u, 0x10400000u, s_try, c_try, i);
                /* First record with an IRK starts the asynchronous resolve. */
                DmPrivResolveAddr(addr, row + 7, (uint16_t)i);
                return 1u;
            }
        }
        DB_LOG(2u, 0x404u, 0x08000000u, s_no_irk, c_no_irk);
        return 0u;
    }

    {
        uint8_t host_type = DmHostAddrType(addr_type);
        for (i = 0u; i < APP_DB_RECORDS; i++, row += APP_DB_RECORD_SIZE) {
            if (row[0x2f] != 0u && row[0x30] != 0u && row[6] == host_type &&
                audio_ble_privacy_compare_address(row, addr) != 0u) {
                found = 1u;
                break;
            }
        }
    }
    if (found != 0u) {
        DB_LOG(4u, 0x419u, 0x10000000u, s_found, c_found);
        return 1u;
    }
    DB_LOG(2u, 0x41fu, 0x08000000u, s_none, c_none);
    return 0u;
}
